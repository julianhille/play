from pytest import raises, mark
from unittest.mock import patch, Mock
from webtest import AppError
from play.models.users import get_user_by_name
from tests.conftest import auth


def test_login_without_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post('/me/login', {'username': 'admin_active', 'password': 'password'})
    assert '400 BAD REQUEST' in str(context.value)


def test_login_with_wrong_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post(
            '/me/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
    assert '400 BAD REQUEST' in str(context.value)


def test_login_with_correct_csrf_once(testapp_api):
    testapp_api.get('/me/login', status=401)
    csrf_token = testapp_api.cookies['XSRF-TOKEN']
    response = testapp_api.post(
        '/me/login', {'username': 'admin_active', 'password': 'password'},
        headers=[('XSRF-TOKEN', csrf_token)])

    assert response.status_code == 302
    followed = response.follow().json_body
    assert testapp_api.cookies['XSRF-TOKEN'] != csrf_token
    assert followed['_id'] == 'ccff1bee2e21e1560a7dd001'
    assert followed['name'] == 'admin_active'


def test_login_with_correct_csrf_twice(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response_login = testapp_api.post(
            '/me/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
        with raises(AppError) as logged_in_context:
            testapp_api.post(
                '/me/login', {'username': 'ANY', 'password': 'WRONG'},
                headers=[('X-CSRF-Token', '123123123')])

    assert response_login.status_code == 302
    followed = response_login.follow().json_body
    assert followed['name'] == 'admin_active'
    assert '409 CONFLICT' in str(logged_in_context.value)
    assert validate.call_count == 2


def test_login_without_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post('/me/login', {'password': 'password'})
    assert 'username' in str(context.value)


def test_login_without_password(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post('/me/login', {'username': 'admin_active'})
    assert 'password' in str(context.value)


def test_logout_without_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post('/me/logout', {})
    assert '400 BAD REQUEST' in str(context.value)


def test_logout_with_wrong_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post(
            '/me/logout', {},
            headers=[('X-CSRF-Token', '123123123')])
    assert '400 BAD REQUEST' in str(context.value)


def test_logout_with_correct_csrf(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response = testapp_api.post(
            '/me/logout', {},
            headers=[('X-CSRF-Token', '123123123')])
    assert response.status_code == 204
    assert '204 NO CONTENT' in str(response)
    assert validate.call_count == 1


def test_get_item_no_auth_without_cookie(testapp_api):
    with patch('play.api.me.generate_csrf') as csrf:
        csrf.return_value = "SOMETOKEN"
        testapp_api.get('/me', status=401)
    assert csrf.call_count == 1


def test_get_item_no_auth_with_cookie(testapp_api):
    with patch('play.api.me.generate_csrf') as csrf:
        csrf.return_value = "SOMETOKEN"
        testapp_api.get('/me', headers=[('Cookie', 'XSRF-TOKEN=ABC;')], status=401)
    assert csrf.call_count == 1


@mark.parametrize('user', ['admin_active', 'user_active', 'admin_user_active'])
def test_get_item_user(testapp_api, user):
    with auth(testapp_api, user=user):
        response = testapp_api.get('/me')
    assert response.status_code == 200
    assert '_id' in response.json_body
    assert response.json_body['name'] == user
    assert 'last_login' in response.json_body
    assert 'password' not in response.json_body
    assert 'roles' in response.json_body
    assert response.json_body['_links']['self']['href'] == '/me'


def test_patch_password_item_user(testapp_api, mongodb):
    user_before = get_user_by_name(mongodb.users, 'user_active')
    login_user = Mock(hash_password=Mock(return_value="some_password"))
    with auth(testapp_api, user='user_active'):
        with patch('play.api.me.users', login_user):
            with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
                response_get = testapp_api.get('/me')
                response = testapp_api.patch_json(
                    '/me', {'password': 'abcdef'},
                    headers=[('If-Match', response_get.headers['ETag'])])
    user_after = get_user_by_name(mongodb.users, 'user_active')
    login_user.hash_password.assert_called_once_with('abcdef')
    assert user_before.password != user_after.password
    assert user_after.password == 'some_password'
    assert response.status_code == 200
    assert response.json_body['_links']['self']['href'] == '/me'


def test_register(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        response = testapp_api.post_json('/me', {'name': '123ABC', 'password': '123456'})
    assert response.status_code == 201
    assert 'password' not in response.json_body
    assert 'active' not in response.json_body


def test_register_logged_in(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.post_json('/me', {'name': '123ABC', 'password': '123456'})
    assert '400 BAD REQUEST' in str(context.value)


def test_register_bulk(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json(
                '/me', [{'name': '123ABC', 'password': '123456'},
                        {'name': '123ABC12', 'password': '123456'}])
    assert '400 BAD REQUEST' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/me', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/me', {})
    assert '401 UNAUTHORIZED' in str(context.value)
