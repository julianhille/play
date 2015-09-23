from pytest import raises
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/tracks')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/tracks/adf19b92e21e1560a7dd0000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/tracks')
    assert response.status_code == 200


def test_get_item_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/tracks')
    assert response.status_code == 200


def test_post_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.post_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.put_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.patch_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.post_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.put_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.patch_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
