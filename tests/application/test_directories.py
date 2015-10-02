from pytest import raises
from unittest.mock import Mock, patch
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/directories')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/directories/ddff19b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/directories')
    assert response.status_code == 200
    assert all('name' not in v['parent'] for v in response.json_body['_items'] if v.get('parent'))
    assert all('path' not in v for v in response.json_body['_items'])


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/directories/ddff19b92e21e1560a7dd000')
    assert response.status_code == 200
    assert 'name' in response.json_body
    assert 'path' not in response.json_body


def test_get_resource_admin(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response = testapp_api.get('/directories')
    assert response.status_code == 200
    assert all('name' not in v['parent'] for v in response.json_body['_items'] if v.get('parent'))
    assert all('path' in v for v in response.json_body['_items'])


def test_get_item_admin(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response = testapp_api.get('/directories/ddff19b92e21e1560a7dd000')
    assert response.status_code == 200
    assert 'path' in response.json_body


def test_get_resource_with_embedding_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/directories?embedded={"parent": 1}')
    assert response.status_code == 200
    assert all('name' in v['parent'] for v in response.json_body['_items'] if v.get('parent'))


def test_get_item_with_embedding_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/directories/ddff19b92e21e1560a7dd001?embedded={"parent": 1}')
    assert response.status_code == 200
    assert response.json_body['parent']['name'] == 'path'


def test_post_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response = testapp_api.post_json('/directories', {'path': '/abc/123', 'parent': None})
    assert response.status_code == 201


def test_put_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/directories/ddff19b92e21e1560a7dd001')
            response = testapp_api.put_json(
                '/directories/ddff19b92e21e1560a7dd001',
                {'path': '/abc/123', 'parent': None},
                headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200


def test_patch_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/directories/ddff19b92e21e1560a7dd001')
            response = testapp_api.patch_json(
                '/directories/ddff19b92e21e1560a7dd001', {},
                headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200


def test_post_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.post_json('/directories', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/directories', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '401 UNAUTHORIZED' in str(context.value)
