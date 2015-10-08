import io
from pytest import raises
from unittest.mock import patch, MagicMock, Mock
from webtest import AppError

from tests.conftest import auth


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
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_patch_item_user(testapp_api):
    with patch('flask.ext.wtf.csrf.validate_csrf', Mock(return_value=True)):
        with auth(testapp_api, user='user_active'):
            with raises(AppError) as context:
                testapp_api.patch_json('/tracks/adf19b92e21e1560a7dd0000', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


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
            testapp_api.patch_json('/tracks', {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


def test_get_stream_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/stream/adf19b92e21e1560a7dd0000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_stream_id_not_valid(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/stream/WRONG')
    assert '404 NOT FOUND' in str(context.value)


def test_get_stream_id_not_found(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/stream/adf19b92e21e1560a7dd0001')
    assert '404 NOT FOUND' in str(context.value)


@patch('play.application.tracks.send_file')
def test_get_stream_id_found_valid_file(send_file, testapp_api):
    send_file.return_value = 'RESPONSE'
    with auth(testapp_api, user='user_active'):
        with patch('play.application.tracks.open', MagicMock(spec=io.IOBase), create=True) as open_:
            response = testapp_api.get('/stream/adf19b92e21e1560a7dd0000')
    open_.assert_called_once_with('/var/media/some_file.mp3', 'rb')
    assert send_file.call_count == 1
    assert response.body == b'RESPONSE'


def test_get_stream_id_found_invalid_file(testapp_api):
    with auth(testapp_api, user='user_active'):
        with raises(AppError) as context:
            testapp_api.get('/stream/adf19b92e21e1560a7dd0000')
    assert '500 INTERNAL SERVER ERROR' in str(context.value)


def test_fulltext_search(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/tracks/?where={"$text": {"$search":"some_fil"}}')
    assert len(response.json_body['_items']) == 1
