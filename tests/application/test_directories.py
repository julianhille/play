from pytest import raises
from webtest import AppError

from tests.conftest import auth


def test_get_resource_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/directories')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/directories/ddff19b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/directories')
    assert response.status_code == 200
    assert all('name' not in v['parent'] for v in response.json_body['_items'] if v.get('parent'))


def test_get_item_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/directories/ddff19b92e21e1560a7dd000')
    assert response.status_code == 200


def test_get_resource_with_embedding_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/directories?embedded={"parent": 1}')
    assert response.status_code == 200
    assert all('name' in v['parent'] for v in response.json_body['_items'] if v.get('parent'))


def test_get_item_with_embedding_user(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/directories/ddff19b92e21e1560a7dd001?embedded={"parent": 1}')
    assert response.status_code == 200
    assert response.json_body['parent']['name'] == 'path'


def test_post_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.post_json('/directories', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.put_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.patch_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.post_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.put_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.patch_json('/directories/ddff19b92e21e1560a7dd001', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
