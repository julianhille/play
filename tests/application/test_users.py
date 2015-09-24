from pytest import raises
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/users/abb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            response = testapp.get('/users')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_item_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/users/ccff1bee2e21e1560a7dd004')
    assert response.status_code == 200


def test_get_item_inactive_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.get('/users/ccff1bee2e21e1560a7dd005')
    assert '404 NOT FOUND' in str(context.value)


def test_get_item_acitve_user_missing_role(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.get('/users/ccff1bee2e21e1560a7dd001')
    assert '404 NOT FOUND' in str(context.value)

def test_post_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.post_json('/users', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.post_json('/users', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.put_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.patch_json('/users/ccff1bee2e21e1560a7dd000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
