from bson import ObjectId
from pytest import mark, raises
from unittest.mock import Mock, patch
from webtest import AppError

from tests.conftest import auth, mongo_engine


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/tracks')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/tracks/adf19b92e21e1560a7dd0000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_resource_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/tracks')
    assert response.status_code == 200


def test_get_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/tracks/adf19b92e21e1560a7dd0000')
    assert response.status_code == 200


def test_get_inactive_item_user(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/tracks/adf19b92e21e1560a7dd0001')
    assert '404 NOT FOUND' in str(context.value)


def test_get_inactive_item_admin(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response = testapp_api.get('/tracks/adf19b92e21e1560a7dd0001')
    assert response.status_code == 200


def test_post_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.post_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/tracks/adf19b92e21e1560a7dd0000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/tracks/adf19b92e21e1560a7dd0000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


@mark.parametrize('user', ['user_active', 'admin_active'])
def test_patch_resource_user(testapp_api, user):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user=user):
            with raises(AppError) as context:
                testapp_api.patch_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


@mark.parametrize('user', ['user_active', 'admin_active'])
def test_put_resource_user(testapp_api, user):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user=user):
            with raises(AppError) as context:
                testapp_api.put_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


@mark.parametrize('user', ['user_active', 'admin_active'])
def test_post_resource_user(testapp_api, user):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user=user):
            with raises(AppError) as context:
                testapp_api.post_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


@mark.parametrize('user', ['user_active', 'admin_active'])
def test_delete_resource_user(testapp_api, user):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user=user):
            with raises(AppError) as context:
                testapp_api.delete('/tracks')
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response_get = testapp_api.get('/tracks/adf19b92e21e1560a7dd0000')
            response = testapp_api.patch_json(
                '/tracks/adf19b92e21e1560a7dd0000', {'active': True},
                headers=[('If-Match', response_get.headers['ETag'])])
    assert response.status_code == 200


def test_post_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.post_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/tracks/adf19b92e21e1560a7dd0000', {})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.patch_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_put_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_delete_resource_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.delete_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_stream_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/tracks/stream/adf19b92e21e1560a7dd0000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_stream_id_not_valid(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/tracks/stream/WRONG')
    assert '404 NOT FOUND' in str(context.value)


def test_get_stream_id_not_found(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/tracks/stream/adf19b92e21e1560a7dd0001')
    assert '404 NOT FOUND' in str(context.value)


@patch('play.api.tracks.send_file_partial')
def test_get_stream_id_found_valid_file(send_file, testapp_api):
    send_file.return_value = 'RESPONSE'
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/tracks/stream/adf19b92e21e1560a7dd0000')
    assert send_file.call_count == 1
    assert response.body == b'RESPONSE'


def test_get_stream_id_found_invalid_file(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/tracks/stream/adf19b92e21e1560a7dd0000')
    assert '500 INTERNAL SERVER ERROR' in str(context.value)


@mark.skipif(mongo_engine() == 'mongomock', reason="mongomock does not support $text")
def test_fulltext_search(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/tracks/?where={"$text": {"$search":"file"}}')
    assert len(response.json_body['_items']) == 1


def test_put_rescan_no_auth(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with raises(AppError) as context:
            testapp_api.put('/tracks/rescan')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_rescan_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/tracks/rescan', {'_id': str(ObjectId())})
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_rescan_invalid_id_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/tracks/rescan', {'_id': 'INVALIDID'})
    assert '422 UNPROCESSABLE ENTITY' in str(context.value)


def test_put_rescan_not_found_admin(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            with raises(AppError) as context:
                testapp_api.put_json('/tracks/rescan', {'_id': 'adf19b92e21e1560a7dd000A'})
    assert '404 NOT FOUND' in str(context.value)


@patch('play.api.tracks.audio_scan')
def test_put_rescan_admin(audio_scan, testapp_api):

    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='admin_active'):
            response = testapp_api.put_json(
                '/tracks/rescan', {'_id': 'adf19b92e21e1560a7dd0000'})
    assert response.status_code == 204
    audio_scan.apply_async.assert_called_once_with(
        arg=[ObjectId('adf19b92e21e1560a7dd0000')], exchange='play',
        routing_key='play.directory.ddff19b92e21e1560a7dd000')
