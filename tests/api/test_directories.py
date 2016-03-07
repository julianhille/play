from bson import ObjectId
from pyfakefs.fake_filesystem import FakeOsModule
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


def test_post_item_dir_exists_admin(testapp_api, file_system):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with patch('play.api.application.os', FakeOsModule(file_system)):
            with auth(testapp_api, user='admin_active'):
                response = testapp_api.post_json(
                    '/directories', {'path': '/tmp/media/Album', 'name': 'some name'})
    assert response.status_code == 201


def test_post_item_dir_not_exists_admin(testapp_api, file_system):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with patch('play.api.application.os', FakeOsModule(file_system)):
            with auth(testapp_api, user='admin_active'):
                with raises(AppError) as context:
                    testapp_api.post_json(
                        '/directories', {'path': '/tmp/NOTTHERE', 'name': 'some name'})
    assert '422 UNPROCESSABLE ENTITY' in str(context.value)


@patch('play.api.directories.directory_scan')
def test_put_item_admin(scan, testapp_api, file_system):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with patch('play.api.application.os', FakeOsModule(file_system)):
            with auth(testapp_api, user='admin_active'):
                response_get = testapp_api.get('/directories/ddff19b92e21e1560a7dd000')
                response = testapp_api.put_json(
                    '/directories/ddff19b92e21e1560a7dd000',
                    {'path': '/tmp/media/', 'name': 'new name'},
                    headers=[('If-Match', response_get.headers['ETag'])])
    #  scan.apply_async.assert_called_once_with(
    #    arg=[ObjectId('ddff19b92e21e1560a7dd000')], exchange='play',
    #    routing_key='play.directory.ddff19b92e21e1560a7dd000')
    assert response.status_code == 200


@patch('play.api.directories.directory_scan')
def test_patch_item_admin(scan, testapp_api, file_system):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with patch('play.api.application.os', FakeOsModule(file_system)):
            with auth(testapp_api, user='admin_active'):
                response_get = testapp_api.get('/directories/ddff19b92e21e1560a7dd000')
                response = testapp_api.patch_json(
                    '/directories/ddff19b92e21e1560a7dd000', {'path': '/tmp/media/Album/'},
                    headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200
    #  scan.apply_async.assert_called_once_with(
    #    arg=[ObjectId('ddff19b92e21e1560a7dd000')], exchange='play',
    #    routing_key='play.directory.ddff19b92e21e1560a7dd000')


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
                testapp_api.put_json('/directories/ddff19b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/directories/ddff19b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/directories', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/directories/ddff19b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/directories/ddff19b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/directories', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/directories', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_delete_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.delete('/directories')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_rescan_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put('/directories/rescan')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_rescan_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/directories/rescan', {'_id': str(ObjectId())})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_rescan_invalid_id_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/directories/rescan', {'_id': 'INVALIDID'})
    assert '422 UNPROCESSABLE ENTITY' in str(context.value)


def test_put_rescan_not_found_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/directories/rescan', {'_id': 'aaff19b92e21e1560a7dd000'})
    assert '404 NOT FOUND' in str(context.value)


def test_put_rescan_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response = testapp_api.put_json(
                '/directories/rescan', {'_id': 'ddff19b92e21e1560a7dd000'})
    assert response.status_code == 204
