"""
 Implements a simple database of users.

"""

import sqlite3


class Database:
    """Database connectivity."""

    def __init__(self, filename, schema):
        self.filename = filename
        self.schema = schema
        self.conn = sqlite3.connect(filename, check_same_thread=False)

        def dict_factory(cursor, row):
            """Converts table row to dictionary."""
            res = {}
            for idx, col in enumerate(cursor.description):
                res[col[0]] = row[idx]
            return res

        self.conn.row_factory = dict_factory

    def __enter__(self):
        return self

    def recreate(self):
        """Recreates the database from the schema file."""
        with open(self.schema) as fin:
            self.conn.cursor().executescript(fin.read())

    def execute_query(self, stmt, args=()):
        """Executes a query."""
        res = self.conn.cursor().execute(stmt, args)
        return res

    def execute_update(self, stmt, args=()):
        """Executes an insert or update and returns the last row id."""
        print(stmt)
        print(args)
        with self.conn.cursor() as cursor:
            cursor.execute(stmt, args)
            self.conn.commit()
            return cursor.lastrowid

    ##
    #       Users CRUD
    ##

    def get_user(self, username, password):
        """ Returns a user from the database"""
        return self.execute_query(
            "SELECT * FROM user WHERE username='%s' AND password='%s'" %
            (username, password)
        ).fetchone()

    def insert_user(self, user):
        """ Inserts a user in the database"""
        return self.execute_query(
            "INSERT INTO user VALUES (null, '%s','%s', '%s', '%s')" %
            (user['name'], user['email'], user['username'], user['password'])
        )

    def update_user(self, user_details, user_id):
        """ Updates the details of a user in the database """
        return self.execute_query(
            "UPDATE user SET name= '%s', email='%s', password='%s' WHERE id='%s'" %
            (user_details['name'], user_details['email'], user_details['password'], user_id)
        )

    def update_user_name(self, user_id, name):
        """ Updates the name of a user in the database """
        return self.execute_query(
            "UPDATE user SET name= '%s'WHERE id='%s'" %
            (name, user_id)
        )

    def update_user_email(self, user_id, email):
        """ Updates the email of a user in the database """
        return self.execute_query(
            "UPDATE user SET email= '%s'WHERE id='%s'" %
            (email, user_id)
        )

    def update_user_password(self, user_id, password):
        """ Updates the password of a user in the database """
        return self.execute_query(
            "UPDATE user SET password= '%s'WHERE id='%s'" %
            (password, user_id)
        )

    ##
    #       Projects CRUD
    ##

    def get_projects(self, user_id):
        """ Returns all projects from given user"""
        return self.execute_query(
            "SELECT * FROM project where user_id = '%s' order by last_updated DESC" %
            int(user_id)
        ).fetchall()

    def get_project(self, project_id):
        """ Returns a project with the requested id"""
        return self.execute_query(
            "SELECT * FROM project where id = '%s'" %
            int(project_id)
        ).fetchone()

    def get_project_confirmation(self, project_title, project_creation_date):
        """
         Returns a project with the requested title and creation date
         Used to validate project insertion in the database
        """
        return self.execute_query(
            "SELECT * FROM project where title = '%s' AND creation_date = '%s'" %
            (project_title, project_creation_date)
        ).fetchone()

    def insert_project(self, user_id, project_details):
        """ Inserts a project in the database"""
        return self.execute_query(
            "INSERT INTO project VALUES(null, '%s', '%s', '%s','%s')" %
            (user_id, project_details['title'],
             project_details['creation_date'], project_details['last_updated'])
        )

    def update_project(self, project_id, project_details):
        """ Updates a project values"""
        return self.execute_query(
            "Update project SET title='%s', last_updated='%s' WHERE id='%s'" %
            (project_details['title'], project_details['last_updated'], project_id)
        )

    def delete_project(self, project_id):
        """Deletes a project"""
        return self.execute_query(
            "DELETE FROM project WHERE id='%s'" %
            project_id
        )

    ##
    #       Tasks CRUD
    ##

    def get_tasks(self, project_id):
        """ Returns all tasks of a given project """
        return self.execute_query(
            "SELECT * FROM task where project_id = '%s'" %
            project_id
        ).fetchall()

    def insert_task(self, project_id, task_details):
        """ Inserts a task in the database"""
        return self.execute_query(
            "INSERT INTO task VALUES(null, '%s', '%s', '%s','%s')" %
            (project_id, task_details['title'],
             task_details['creation_date'], task_details['completed'])
        )

    def get_task(self, task_id, project_id):
        """ Returns a task with given task id and project id"""
        return self.execute_query(
            "SELECT * FROM task where project_id = '%s' AND id = '%s'" %
            (project_id, task_id)
        ).fetchone()

    def get_task_confirmation(self, task_title, project_id, creation_date):
        """
        Returns a task with given task title and creation date and project id
        Used for insert validation
        """
        return self.execute_query(
            "SELECT * FROM task where project_id = '%s' AND title = '%s' AND creation_date = '%s'" %
            (project_id, task_title, creation_date)
        ).fetchone()

    def update_task_title(self, task_id, project_id, title):
        """ Updates the given task title """
        return self.execute_query(
            "Update task SET title='%s' WHERE id='%s' AND project_id = '%s'" %
            (title, task_id, project_id)
        )

    def update_task_completed(self, task_id, project_id, completed):
        """ Changes a task to completed """
        return self.execute_query(
            "Update task SET completed='%s' WHERE id='%s' AND project_id = '%s'" %
            (completed, task_id, project_id)
        )

    def delete_task(self, task_id, project_id):
        """ Deletes a task """
        return self.execute_query(
            "DELETE FROM task WHERE id='%s' AND project_id = '%s'" %
            (task_id, project_id))
