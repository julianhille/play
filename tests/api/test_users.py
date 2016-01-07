from uuid import uuid4

from bson import ObjectId
from pytest import mark, raises
from unittest.mock import patch, Mock
from webtest import AppError

from play.models.users import get_user_by_name
from tests.conftest import auth


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/users')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/users/abb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/users')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/users/ccff1bee2e21e1560a7dd004')
    assert 'password' not in response.json_body
    assert 'roles' not in response.json_body
    assert response.status_code == 200


def test_get_inactive_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/users/ccff1bee2e21e1560a7dd005')
    assert '404 NOT FOUND' in str(context.value)


def test_get_item_admin(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response = testapp_api.get('/users/ccff1bee2e21e1560a7dd005')
    assert 'password' not in response.json_body
    assert 'roles' in response.json_body
    assert response.status_code == 200


def test_get_resource_admin(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response = testapp_api.get('/users/')
    assert all('password' not in v for v in response.json_body['_items'])
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
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_admin(testapp_api, humongous):
    password = uuid4().hex
    with auth(testapp_api, user='admin_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            response = testapp_api.post_json(
                '/users/', {'name': 'SomeName', 'roles': ['admin'],
                            'active': True, 'password': password})
    assert response.status_code == 201
    user = get_user_by_name(humongous.users, 'SomeName')
    assert user.authenticate(password)


def test_put_item_admin(testapp_api, humongous):
    password = uuid4().hex
    with auth(testapp_api, user='admin_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            response_get = testapp_api.get('/users/ccff1bee2e21e1560a7dd000')
            response = testapp_api.put_json(
                '/users/ccff1bee2e21e1560a7dd000',
                {'name': 'SomeName', 'roles': ['admin'], 'active': True, 'password': password},
                headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200
    user = get_user_by_name(humongous.users, 'SomeName')
    assert user.authenticate(password)


def test_patch_item_admin(testapp_api, humongous):
    password = uuid4().hex
    with auth(testapp_api, user='admin_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            response_get = testapp_api.get('/users/ccff1bee2e21e1560a7dd000')
            response = testapp_api.patch_json(
                '/users/ccff1bee2e21e1560a7dd000', {'password': password},
                headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200
    user = get_user_by_name(humongous.users, response_get.json_body['name'])
    assert user.authenticate(password)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/users', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_projection_inverse(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/users/ccff1bee2e21e1560a7dd004?projection={"name":0}')
    assert 'password' not in response.json_body
    assert 'roles' not in response.json_body
    assert response.status_code == 200


@mark.parametrize('user', ['user_active', 'admin_active', 'admin_user_active'])
def test_delete_resource_user(testapp_api, user):
    with auth(testapp_api, user=user):
        with raises(AppError) as context:
            testapp_api.delete('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_delete_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.delete('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_delete_item(testapp_api):
    driver = testapp_api.app.data.driver
    with testapp_api.app.app_context():
        assert driver.db.playlists.find(
            {'owner': ObjectId('ccff1bee2e21e1560a7dd004')}).count() == 2
    with auth(testapp_api, user='admin_active'):
        response_get = testapp_api.get('/users/ccff1bee2e21e1560a7dd004')
        response = testapp_api.delete('/users/ccff1bee2e21e1560a7dd004',
                                      headers=[('If-Match', response_get.headers['ETag'])])

    assert response.status_code == 204
    with testapp_api.app.app_context():
        assert driver.db.playlists.find(
            {'owner': ObjectId('ccff1bee2e21e1560a7dd004')}).count() == 0
        assert driver.db.playlists.find(
            {'_id': ObjectId('aaff1bee2e21e1560a7dd002')}).count() == 1
