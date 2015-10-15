from pytest import raises
from unittest.mock import Mock, patch
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/albums')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/albums/abb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/albums')
    assert response.status_code == 200


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/albums/abb419b92e21e1560a7dd000')
    assert response.status_code == 200


def test_post_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.post_json('/albums', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.put_json('/albums/abb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
            with raises(AppError) as context:
                testapp_api.patch_json('/albums/abb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/albums', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/albums/abb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/albums/abb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
