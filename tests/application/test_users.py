from pytest import raises
from unittest.mock import patch, Mock
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/users/abb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/users/ccff1bee2e21e1560a7dd004')
    assert response.status_code == 200


def test_get_item_inactive_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/users/ccff1bee2e21e1560a7dd005')
    assert '404 NOT FOUND' in str(context.value)


def test_get_item_active_user_missing_role(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/users/ccff1bee2e21e1560a7dd001')
    assert '404 NOT FOUND' in str(context.value)


def test_post_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.post_json('/users', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/users', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_login_without_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post('/users/login', {'username': 'admin_active', 'password': 'password'})
    assert '400 BAD REQUEST' in str(context.value)


def test_login_with_wrong_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post(
            '/users/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
    assert '400 BAD REQUEST' in str(context.value)


def test_login_with_correct_csrf(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response = testapp_api.post(
            '/users/login', {'username': 'admin_active', 'password': 'password'},
            headers=[('X-CSRF-Token', '123123123')])
    assert response.json_body == {'_id': 'ccff1bee2e21e1560a7dd001'}
    assert validate.call_count == 1


def test_login_without_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post('/users/login', {'password': 'password'})
    assert 'username' in str(context.value)


def test_login_without_password(testapp_api):

    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post('/users/login', {'username': 'admin_active'})
    assert 'password' in str(context.value)


def test_logout_without_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post('/users/logout', {})
    assert '400 BAD REQUEST' in str(context.value)


def test_logout_with_wrong_csrf(testapp_api):
    with raises(AppError) as context:
        testapp_api.post(
            '/users/logout', {},
            headers=[('X-CSRF-Token', '123123123')])
    assert '400 BAD REQUEST' in str(context.value)


def test_logout_with_correct_csrf(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)) as validate:
        response = testapp_api.post(
            '/users/logout', {},
            headers=[('X-CSRF-Token', '123123123')])
    assert response.json_body == {}
    assert validate.call_count == 1
