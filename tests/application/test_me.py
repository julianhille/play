from pytest import raises
from unittest.mock import patch, Mock
from webtest import AppError

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


def test_login_with_correct_csrf(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response = testapp_api.post(
            '/me/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
    assert response.json_body == {'_id': 'ccff1bee2e21e1560a7dd001'}
    assert validate.call_count == 1


def test_login_with_correct_csrf_twice(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response_login = testapp_api.post(
            '/me/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
        response_logged_in = testapp_api.post(
            '/me/login', {'username': 'ANY', 'password': 'WRONG'},
            headers=[('X-CSRF-Token', '123123123')])
    assert response_login.json_body == {'_id': 'ccff1bee2e21e1560a7dd001'}
    assert response_login.json_body['_id'] == response_logged_in.json_body['_id']
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
    assert response.json_body == {}
    assert validate.call_count == 1


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/me')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/me')
    assert response.status_code == 200
    assert response.json_body['_id'] == 'ccff1bee2e21e1560a7dd004'
    assert response.json_body['name'] == 'user_active'
    assert 'last_login' in response.json_body
    assert 'password' not in response.json_body
    assert response.json_body['_links']['self']['href'] == 'me/'


def test_patch_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
                response_get = testapp_api.get('/me')
                response = testapp_api.patch_json(
                    '/me', {'password': 'abc'},
                    headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200
    assert response.json_body['_links']['self']['href'] == 'me/'


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/me', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


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
