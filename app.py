"""
 Flask REST application

"""
import functools
import os
from flask import Flask, request, jsonify, make_response, session, send_from_directory
from models import Database

# ==========
#  Settings
# ==========

app = Flask(__name__)
app.config['STATIC_FOLDER'] = '/static'
app.config['DEBUG'] = True
app.config['USERNAME'] = "SUPERSECUREUSERNAME"
app.config['PASSWORD'] = "SUPERSECUREPASSWORD"
app.secret_key = os.urandom(24)
# ==========
#  Database
# ==========

# Creates an sqlite database in memory
db = Database(filename=':memory:', schema='schema.sql')
db.recreate()


# ===========
#  Authentication
# ===========
def ok_user_and_password(username, password):
    """Checks if user and password corresponds to the current user"""
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']


def authenticate():
    """ Authenticates user """
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    return resp


def requires_authorization(func):
    """ Authorization function wraper """

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not ok_user_and_password(auth.username, auth.password):
            session.pop('id', None)
            return authenticate()
        return func(*args, **kwargs)

    return decorated

def validate_user_fields(user):
    """ Validates user has no empty fields"""
    if user['username'] == '':
        return "Invalid username"
    if user['email'] == '':
        return "Invalid email"
    if user['name'] == '':
        return "Invalid name"
    if user['password'] == '':
        return "Invalid password"

    return "OK"


def validate_duplicates(user):
    """ Validates if username and email doesnt exist in the database """
    if db.get_user_by_email(user['email']) is not None:
        return "Email already exists"
    if db.get_user_by_username(user['username']) is not None:
        return "Username already exists"
    return "OK"

# ===========
#  Web views
# ===========

@app.route('/api/')
def index():
    """ Shoes index page """
    return send_from_directory('static', 'index.html')


# ===========
#  API views
# ===========


@app.route('/authorization/getusername', methods=['GET'])

def user_getusername():
    """
    Returns current username information
    Requires authorization.
    """
    if request.method == 'GET':
        return make_response(jsonify(app.config["USERNAME"]), 201)

    return make_response({}, 403)


@app.route('/authorization/getpassword', methods=['GET'])

def user_getpassword():
    """
     Returns current password information
     Requires authorization.
    """
    if request.method == 'GET':
        return make_response(jsonify(app.config["PASSWORD"]), 201)

    return make_response({}, 403)


@app.route('/api/user/register/', methods=['POST'])
def user_register():
    """ Register a user """
    if request.method == 'POST':
        new_user = request.get_json()
        res = validate_user_fields(new_user)
        if res == "OK":
            res = validate_duplicates(new_user)
            if res == "OK":
                db.insert_user(new_user)
                return make_response({}, 201)
            return make_response(jsonify(res), 403)
        return make_response(jsonify(res), 403)
    return make_response({}, 405)


@app.route('/api/user/login', methods=['POST'])
def user_login():
    """ Logs a user into the application """
    if request.method == 'POST':
        login_user = request.get_json()
        query = db.get_user(login_user['username'], login_user['password'])
        if query is not None:
            app.config['USERNAME'] = login_user["username"]
            app.config['PASSWORD'] = login_user["password"]
            session["id"] = query["id"]
            session["username"] = query["username"]
            session["password"] = query["password"]
            query.update({"session" : session["id"]})
            return make_response(query, 200)
        return make_response({}, 404)

    return make_response({}, 405)

@app.route('/api/user/logout', methods=['GET'])
def user_logout():
    if 'id' in session:
        session.pop('id', None)
        return make_response({}, 200)
    else:
        return make_response({}, 400)


@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    """
    Returns or updates current user.
    Requires authorization.
    """
    user = db.get_user(session["username"], session["password"])

    if user is None:
        return make_response({}, 403)

    if request.method == 'GET':
        # Returns user data
        return make_response(jsonify(user))

    if request.method == 'PUT':
        edit_user = request.get_json()
        res = validate_user_fields(edit_user)
        if res == "OK":
            db.update_user(edit_user, session['id'])
            app.config['PASSWORD'] = edit_user['password']
            return make_response(jsonify(edit_user), 200)
        return make_response(jsonify(res), 403)
    return make_response({}, 405)


@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    """
    Project list.
    Requires authorization.
    """
    projects = db.get_projects(int(session["id"]))
    if projects is None:
        return make_response({}, 404)
    if request.method == 'GET':
        # Returns the list of projects of a user
        return make_response(jsonify(projects), 200)

    if request.method == 'POST':
        new_project = request.get_json()
        if new_project['title'] == '':
            return make_response(jsonify("Project title can't be empty"), 403)
        try:
            db.insert_project(session["id"], new_project)
            return make_response(jsonify(new_project), 201)
        except:
            return make_response({}, 500)

    return make_response({}, 405)


@app.route('/api/projects/<int:project_id>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(project_id):
    """
    Project detail.
    Requires authorization.
    """
    project = db.get_project(project_id)

    if project is None:
        return make_response({}, 404)
    if request.method == 'GET':
        # Returns a project
        return make_response(jsonify(project), 200)
    if request.method == 'PUT':
        edit_project = request.get_json()
        try:
            if edit_project['title'] == '':
                return make_response(jsonify("Project title can't be empty"), 403)
            db.update_project(project_id, edit_project)
            return make_response(jsonify(edit_project), 200)
        except:
            return make_response(jsonify(edit_project), 500)

    if request.method == 'DELETE':
        db.delete_project(project_id)
        return make_response({}, 200)

    return make_response({}, 405)


@app.route('/api/projects/<int:project_id>/tasks/', methods=['GET', 'POST'])
def task_list(project_id):
    """
    Task list.
    Requires authorization.
    """
    tasks = db.get_tasks(project_id)
    if tasks is None:
        return make_response({}, 404)
    if request.method == 'GET':
        # Returns the list of tasks of a project
        return make_response(jsonify(tasks))
    if request.method == 'POST':
        new_task = request.get_json()
        if new_task['title'] == '':
            return make_response(jsonify("Task title can't be empty"), 403)
        try:
            db.insert_task(project_id, new_task)
            return make_response(jsonify(new_task), 201)
        except:
            return make_response({}, 500)
    return make_response({}, 405)


@app.route('/api/projects/<int:project_id>/tasks/<int:task_id>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(project_id, task_id):
    """
    Task detail.
    Requires authorization.

    """
    task = db.get_task(task_id, project_id)

    if task is None:
        return make_response({}, 404)
    if request.method == 'GET':
        # Returns a task
        return make_response(jsonify(task))
    if request.method == 'PUT':
        edit_task = request.get_json()
        try:
            if 'title' in edit_task:
                if edit_task['title'] == '':
                    return make_response(jsonify("Task title can't be empty"), 403)
                db.update_task_title(task_id, project_id, edit_task['title'])
            else:
                db.update_task_completed(task_id, project_id, edit_task['completed'])
            return make_response(jsonify(edit_task), 200)
        except:
            return make_response({}, 500)
    if request.method == 'DELETE':
        db.delete_task(task_id, project_id)
        return make_response({}, 200)

    return make_response({}, 405)


if __name__ == "__main__":
    app.run()
