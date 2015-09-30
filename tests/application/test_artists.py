from pytest import raises
from unittest.mock import patch, Mock
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/artists')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/artists/acb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/artists')
    assert response.status_code == 200


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/artists/acb419b92e21e1560a7dd000')
    assert response.status_code == 200


def test_post_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.post_json('/artists', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/artists', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
