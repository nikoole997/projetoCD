"""
 Tests the application API

"""

import base64
import json
import unittest
from app import app, db


def auth_header(username, password):
    """Returns the authorization header."""
    credentials = f'{username}:{password}'
    b64credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {b64credentials}'}


class TestBase(unittest.TestCase):
    """Base for all tests."""

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.app_context().push()
        self.client = app.test_client()
        self.db = db
        self.db.recreate()

    def tearDown(self):
        pass

    """
    Helper methods
    """

    def post_test(self, route, data, requires_auth):
        """ Method to avoid code duplication on POST tests """
        if requires_auth is True:
            return self.client.post(route, data=json.dumps(data), content_type='application/json',
                                    headers=auth_header('homer', '1234'))
        return self.client.post(route, data=json.dumps(data), content_type='application/json')

    def get_test(self, route, data, requires_auth):
        """ Method to avoid code duplication on GET tests """
        if requires_auth is True:
            return self.client.get(route, data=json.dumps(data),
                                   content_type='application/json',
                                   headers=auth_header('homer', '1234'))
        return self.client.get(route, data=json.dumps(data), content_type='application/json')

    def put_test(self, route, data, requires_auth):
        """ Method to avoid code duplication on PUT tests """
        if requires_auth is True:
            return self.client.put(route, data=json.dumps(data),
                                   content_type='application/json',
                                   headers=auth_header('homer', '1234'))
        return self.client.put(route, data=json.dumps(data), content_type='application/json')

    def delete_test(self, route, data, requires_auth):
        """ Method to avoid code duplication on DELETE tests """
        if requires_auth is True:
            return self.client.delete(route, data=json.dumps(data),
                                      content_type='application/json',
                                      headers=auth_header('homer', '1234'))
        return self.client.delete(route, data=json.dumps(data), content_type='application/json')

    def create_mock_user(self, name, email, username, password):
        """ Method to avoid code duplication on tests requiring creation of a user """
        return dict(name=name, email=email, username=username, password=password)

    def create_mock_project(self, title, creation_date, last_updated):
        """ Method to avoid code duplication on tests requiring creation of a project """
        return dict(title=title, creation_date=creation_date, last_updated=last_updated)

    def create_mock_task(self, proj_id, title, creation_date, completed):
        """ Method to avoid code duplication on tests requiring creation of a task """
        return dict(proj_id=proj_id, title=title, creation_date=creation_date, completed=completed)

    def login(self):
        """ Logs a user """
        self.post_test('/api/user/login',
                       dict(username='homer',
                            password='1234'), True)

    def register(self):
        """ Registers a new user """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'testusername', 'testpassword')
        self.post_test('/api/user/register/', mockuser, False)

    def login_new_user(self):
        """ Creates and log a new user with no projects or tasks """
        self.register()
        self.client.post('/api/user/login',
                         data=json.dumps(dict(username='testusername', password='testpassword')),
                         content_type='application/json',
                         headers=auth_header('testusername', 'testpassword'))


class TestUsers(TestBase):
    """Tests for the user endpoints."""

    def setUp(self):
        super().setUp()

    def test_correct_credentials(self):
        """Tests the user with correct credentials."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_wrong_credentials(self):
        """Tests the user with incorrect credentials."""
        credentials = auth_header('no-user', 'no-password')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 403)

    def test_valid_user_registration_response(self):
        """ Tests if a user is registered successfully with the right information """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'testusername', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 201)

    def test_email_exists_registration_response(self):
        """ Tests if a user is registered successfully with a duplicate email """
        mockuser = self.create_mock_user('Test Name', 'homer@simpsons.org', 'testusername', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_username_exists_registration_response(self):
        """ Tests if a user is registered successfully with a duplicate username """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'homer', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_username_empty_registration_response(self):
        """ Tests if a user is registered successfully with a empty username """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', '', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_password_empty_registration_response(self):
        """ Tests if a user is registered successfully with a empty password """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'test', '')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_name_empty_registration_response(self):
        """ Tests if a user is registered successfully with a empty password """
        mockuser = self.create_mock_user('', 'test@email.com', 'test', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_email_empty_registration_response(self):
        """ Tests if a user is registered successfully with a empty email """
        mockuser = self.create_mock_user('testname', '', 'test', 'testpassword')
        res = self.post_test('/api/user/register/',
                             mockuser, False)
        self.assertEqual(res.status_code, 403)

    def test_login_wrong_info(self):
        """ Tests if a user can login with wrong information"""
        res = self.post_test('/api/user/login',
                             dict(username='testusername',
                                  password='testpassword'), True)
        self.assertEqual(res.status_code, 404)

    def test_login_correct_info(self):
        """ Tests if a user can login with correct information"""
        res = self.post_test('/api/user/login',
                             dict(username='homer',
                                  password='1234'), True)
        self.assertEqual(res.status_code, 200)

    def test_login_correct_info_incorrect_auth(self):
        """ Tests if a user can login with correct information but no authorization"""
        res = self.post_test('/api/user/login',
                             dict(username='homer',
                                  password='1234'), False)
        self.assertEqual(res.status_code, 403)

    def test_current_logged_user(self):
        """ Checks if the current logged user is correct (homer used in mock) """
        self.login()
        self.assertEqual(app.config['USERNAME'], 'homer')

    def test_edit_user_response_correct_credentials(self):
        """ Tests if a user is edited successfully """
        self.login()
        mockedit = self.create_mock_user('name_changed', 'email_changed', 'username_shouldnt_change',
                                         'password_changed')
        res = self.put_test('/api/user/', mockedit, True)
        self.assertEqual(res.status_code, 200)

    def test_edit_user_password_empty_response(self):
        """ Tests if a user is updated successfully with a empty password """
        self.login()
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'test', '')
        res = self.put_test('/api/user/', mockuser, True)
        self.assertEqual(res.status_code, 403)

    def test_edit_user_name_empty_response(self):
        """ Tests if a user is updated successfully with a empty password """
        self.login()
        mockuser = self.create_mock_user('', 'test@email.com', 'test', 'testpassword')
        res = self.put_test('/api/user/', mockuser, True)
        self.assertEqual(res.status_code, 403)

    def test_edit_user_email_empty_response(self):
        """ Tests if a user is updated successfully with a empty email """
        self.login()
        mockuser = self.create_mock_user('testname', '', 'test', 'testpassword')
        res = self.put_test('/api/user/', mockuser, True)
        self.assertEqual(res.status_code, 403)


class TestProjects(TestBase):
    """Tests for the project endpoints."""

    def setUp(self):
        super().setUp()

    def test_project_list_response(self):
        """ Tests if the access to list request is successfull """
        self.login()
        res = self.get_test('/api/projects/', '', True)
        self.assertEqual(res.status_code, 200)

    def test_project_create_project_response_ok(self):
        """ Tests  if the new project is created """
        self.login()
        mockproject = self.create_mock_project('test', '20/12/2020', '')
        res = self.post_test('/api/projects/', mockproject, True)
        self.assertEqual(res.status_code, 201)

    def test_project_list_wrong_method(self):
        """ Tests if the validation of the methods supported by the route is ok """
        self.login()
        mockproject = self.create_mock_project('test', '20/12/2020', '')
        res = self.put_test('/api/projects/', mockproject, True)
        self.assertEqual(res.status_code, 405)

    def test_project_get_project_response_ok(self):
        """ Tests if the access to list request is successfull """
        self.login()
        res = self.get_test('/api/projects/1/', '', True)
        self.assertEqual(res.status_code, 200)

    def test_project_get_non_existing_project_response(self):
        """ Tests if the access to list request is successfull """
        self.login()
        res = self.get_test('/api/projects/7/', '', True)
        self.assertEqual(res.status_code, 404)

    def test_edit_project_response_correct_information(self):
        """ Tests if a project is edited successfully - project Doughnuts"""
        self.login()
        mockproject = self.create_mock_project('test', '20/20/2020', '21/12/2020')
        res = self.put_test('/api/projects/1/', mockproject, True)
        self.assertEqual(res.status_code, 200)

    def test_edit_project_response_blank_title_information(self):
        """ Tests if a project is edited successfully when no title is inserted """
        self.login()
        mockproject = self.create_mock_project('', '20/20/2020', '21/12/2020')
        res = self.put_test('/api/projects/1/', mockproject, True)
        self.assertEqual(res.status_code, 403)

    def test_edit_task_response_incorrect_information(self):
        """ Tests the response of invalid data on project edition """
        self.login()
        res = self.put_test('/api/projects/1/', '', True)
        self.assertEqual(res.status_code, 500)

    def test_delete_project_response(self):
        """ Tests if a project is deleted successfully - project Doughnuts"""
        self.login()
        res = self.delete_test('/api/projects/1/', '', True)
        self.assertEqual(res.status_code, 200)


class TestTasks(TestBase):
    """Tests for the tasks endpoints."""

    def setUp(self):
        super().setUp()

    def test_task_list_response(self):
        """ Tests if the access to task list request is successfull """
        self.login()
        res = self.get_test('/api/projects/1/tasks/', '', True)
        self.assertEqual(res.status_code, 200)

    def test_task_create_task_response_ok(self):
        """ Tests if the new task for the project is created """
        self.login()
        mocktask = self.create_mock_task('1', 'test', '20/12/2020', 0)
        res = self.post_test('/api/projects/1/tasks/', mocktask, True)
        self.assertEqual(res.status_code, 201)

    def test_task_list_wrong_method(self):
        """ Tests if method validation of the route is correct   """
        self.login()
        mocktask = self.create_mock_task('1', 'test', '20/12/2020', 0)
        res = self.put_test('/api/projects/1/tasks/', mocktask, True)
        self.assertEqual(res.status_code, 405)

    def test_task_get_task_response_ok(self):
        """ Tests if the access to task list request is successfull """
        self.login()
        res = self.get_test('/api/projects/1/tasks/1/', '', True)
        self.assertEqual(res.status_code, 200)

    def test_task_get_non_existing_project_response(self):
        """ Tests the response of trying to access task from a non existing project"""
        self.login()
        res = self.get_test('/api/projects/4/tasks/1/', '', True)
        self.assertEqual(res.status_code, 404)

    def test_task_get_non_existing_task_response(self):
        """ Tests the response of trying to access a non existing task"""
        self.login()
        res = self.get_test('/api/projects/1/tasks/5/', '', True)
        self.assertEqual(res.status_code, 404)

    def test_edit_task_title_response_correct_information(self):
        """ Tests if a task title is edited successfully """
        self.login()
        mocktask = self.create_mock_task('1', 'test', '20/20/2020', 0)
        res = self.put_test('/api/projects/1/tasks/1/', mocktask, True)
        self.assertEqual(res.status_code, 200)

    def test_edit_task_completed_response_correct_information(self):
        """ Tests if a task completed field is edited successfully """
        self.login()
        mocktask = self.create_mock_task('1', 'test', '20/20/2020', 1)
        res = self.put_test('/api/projects/1/tasks/1/', mocktask, True)
        self.assertEqual(res.status_code, 200)

    def test_edit_task_response_incorrect_information(self):
        """ Tests the response of invalid data on task edition """
        self.login()
        res = self.put_test('/api/projects/1/tasks/1/', '', True)
        self.assertEqual(res.status_code, 500)

    def test_edit_task_response_blank_title_information(self):
        """ Tests if a project is edited successfully when no title is inserted """
        self.login()
        mocktask = self.create_mock_task('1', '', '20/20/2020', 1)
        res = self.put_test('/api/projects/1/tasks/1/', mocktask, True)
        self.assertEqual(res.status_code, 403)

    def test_delete_task_response(self):
        """ Tests if a task is deleted successfully - project Doughnuts"""
        self.login()
        res = self.delete_test('/api/projects/1/tasks/1/', '', True)
        self.assertEqual(res.status_code, 200)


class TestDBOps(TestBase):
    """ Tests for the database related operations"""

    def setUp(self):
        super().setUp()

    ##
    # User Table
    ##

    def test_get_user(self):
        """ Tests the return of an existing user """
        user = db.get_user('homer', '1234')
        self.assertEqual(user['name'], 'Homer Simpson')
        self.assertEqual(user['email'], 'homer@simpsons.org')
        self.assertEqual(user['username'], 'homer')
        self.assertEqual(user['password'], '1234')

    def test_insert_user_db(self):
        """ Tests if a user is registered successfully with the right information """
        mockuser = self.create_mock_user('Test Name', 'test@email.com', 'testusername', 'testpassword')
        db.insert_user(mockuser)
        user = db.get_user('testusername', 'testpassword')
        self.assertEqual(user['name'], mockuser['name'])
        self.assertEqual(user['email'], mockuser['email'])
        self.assertEqual(user['username'], mockuser['username'])
        self.assertEqual(user['password'], mockuser['password'])

    def test_edit_user_db(self):
        """ Tests if a user is edited successfully - Username is homer."""
        mockuser = self.create_mock_user('name_changed', 'email_changed', 'username_shouldnt_change',
                                         'password_changed')
        db.update_user(mockuser, 1)
        user = db.get_user('homer', mockuser['password'])
        self.assertEqual(user['name'], mockuser['name'])
        self.assertEqual(user['email'], mockuser['email'])
        self.assertEqual(user['username'], 'homer')
        self.assertEqual(user['password'], mockuser['password'])

    ##
    # Project table
    ##

    def test_get_project_db(self):
        """ Tests the return of an existing project """
        project = db.get_project(1)
        self.assertEqual(project['user_id'], 1)
        self.assertEqual(project['id'], 1)
        self.assertEqual(project['title'], 'Doughnuts')
        self.assertEqual(project['creation_date'], '2020-05-01')
        self.assertEqual(project['last_updated'], '2020-06-01')

    def test_get_projects_db(self):
        """ Tests the return of a projects list of a user """
        projects = db.get_projects(1)
        self.assertEqual(len(projects), 2)

    def test_insert_project_db(self):
        """ Tests if a project registered successfully with the right information """
        mockproject = self.create_mock_project('test', '20-12-2020', '')
        db.insert_project(1, mockproject)
        project = db.get_project(4)
        self.assertEqual(project['user_id'], 1)
        self.assertEqual(project['id'], 4)
        self.assertEqual(project['title'], mockproject['title'])
        self.assertEqual(project['creation_date'], mockproject['creation_date'])
        self.assertEqual(project['last_updated'], '')

    def test_edit_project_db(self):
        """ Tests if a project title and last_updated are edited successfully with the right information """
        mockproject = self.create_mock_project('title_changed', 'shouldnt_change', '20-12-2020')
        project_before = db.get_project(1)
        db.update_project(1, mockproject)
        project_after = db.get_project(1)
        self.assertEqual(project_after['user_id'], project_before['user_id'])
        self.assertEqual(project_after['id'], project_before['id'])
        self.assertEqual(project_after['title'], mockproject['title'])
        self.assertEqual(project_after['creation_date'], project_before['creation_date'])
        self.assertEqual(project_after['last_updated'], mockproject['last_updated'])

    def test_delete_project_db(self):
        """ Tests if a project is deleted successfully """
        db.delete_project(1)
        project = db.get_project(1)
        self.assertEqual(project, None)

    ##
    # Task table
    ##

    def test_get_task_db(self):
        """ Tests the return of an existing task """
        task = db.get_task(1, 1)
        self.assertEqual(task['id'], 1)
        self.assertEqual(task['project_id'], 1)
        self.assertEqual(task['title'], 'Search for doughnuts')
        self.assertEqual(task['creation_date'], '2020-05-05')
        self.assertEqual(task['completed'], 1)

    def test_get_tasks_db(self):
        """ Tests the return of a task list of a projects """
        tasks = db.get_tasks(1)
        self.assertEqual(len(tasks), 2)

    def test_insert_task_db(self):
        """ Tests if a task is created successfully with the right information """
        mocktask = self.create_mock_task(1, 'test', '20-12-2020', 0)
        db.insert_task(mocktask['proj_id'], mocktask)
        task = db.get_task(9, 1)
        self.assertEqual(task['id'], 9)
        self.assertEqual(task['project_id'], mocktask['proj_id'])
        self.assertEqual(task['title'], mocktask['title'])
        self.assertEqual(task['creation_date'], mocktask['creation_date'])
        self.assertEqual(task['completed'], mocktask['completed'])

    def test_edit_task_title_db(self):
        """ Tests if a task title is edited successfully with the right information """
        task_before = db.get_task(1, 1)
        db.update_task_title(1, 1, 'test')
        task_after = db.get_task(1, 1)
        self.assertEqual(task_after['id'], task_before['id'])
        self.assertEqual(task_after['project_id'], task_before['project_id'])
        self.assertEqual(task_after['title'], 'test')
        self.assertEqual(task_after['creation_date'], task_before['creation_date'])
        self.assertEqual(task_after['completed'], task_before['completed'])

    def test_edit_task_completed_status_db(self):
        """ Tests if a task completed status is edited successfully with the right information """
        task_before = db.get_task(1, 1)
        db.update_task_completed(1, 1, 1)
        task_after = db.get_task(1, 1)
        self.assertEqual(task_after['id'], task_before['id'])
        self.assertEqual(task_after['project_id'], task_before['project_id'])
        self.assertEqual(task_after['title'], task_before['title'])
        self.assertEqual(task_after['creation_date'], task_before['creation_date'])
        self.assertEqual(task_after['completed'], 1)

    def test_delete_task_db(self):
        """ Tests if a task is deleted successfully """
        db.delete_task(1, 1)
        task = db.get_task(1, 1)
        self.assertEqual(task, None)
