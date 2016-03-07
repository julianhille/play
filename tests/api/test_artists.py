from copy import deepcopy
from pytest import mark, raises
from unittest.mock import Mock, patch
from webtest import AppError

from tests.conftest import auth, mongo_engine

VALID_ARTIST = {
    'name': 'Some name'
}


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/artists')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/artists/acb419b92e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


@mark.parametrize('user', ['admin_active', 'user_active', 'admin_user_active'])
def test_get_resource_user(testapp_api, user):
    with auth(testapp_api, user=user):
        response = testapp_api.get('/artists')
    assert response.status_code == 200


@mark.parametrize('user', ['admin_active', 'user_active', 'admin_user_active'])
def test_get_item_user(testapp_api, user):
    with auth(testapp_api, user=user):
        response = testapp_api.get('/artists/acb419b92e21e1560a7dd000')
    assert response.status_code == 200


def test_post_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.post_json('/artists', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/artists', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/artists/acb419b92e21e1560a7dd000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_delete_item_resource(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.delete('/artists/', VALID_ARTIST)
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_post_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response = testapp_api.post_json('/artists', VALID_ARTIST)
    assert response.status_code == 201


@mark.parametrize('name_value', [None, ''])
def test_post_item_empty_name_admin(testapp_api, name_value):
    artist = deepcopy(VALID_ARTIST)
    artist = {'name': name_value}
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.post_json('/artists', artist)
    assert '422 UNPROCESSABLE ENTITY' in str(context.value)


def test_put_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/artists/acb419b92e21e1560a7dd000')
            response = testapp_api.put_json('/artists/acb419b92e21e1560a7dd000', VALID_ARTIST,
                                            headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200


def test_patch_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/artists/acb419b92e21e1560a7dd000')
            response = testapp_api.patch_json('/artists/acb419b92e21e1560a7dd000', VALID_ARTIST,
                                              headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200


def test_delete_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/artists/acb419b92e21e1560a7dd000')
            response = testapp_api.delete('/artists/acb419b92e21e1560a7dd000', VALID_ARTIST,
                                          headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 204


@mark.skipif(mongo_engine() == 'humongous', reason="mongomock does not support $text")
def test_fulltext_search(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/artists/?where={"$text": {"$search":"member"}}')
    assert len(response.json_body['_items']) == 1
