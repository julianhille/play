import io
from pytest import raises
from webtest import AppError
from unittest.mock import patch, MagicMock

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
        response = testapp.get('/tracks/adf19b92e21e1560a7dd0000')
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


def test_get_stream_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/stream/adf19b92e21e1560a7dd0000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_stream_id_not_valid(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.get('/stream/WRONG')
    assert '404 NOT FOUND' in str(context.value)


def test_get_stream_id_not_found(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.get('/stream/adf19b92e21e1560a7dd0001')
    assert '404 NOT FOUND' in str(context.value)


@patch('play.application.tracks.send_file')
def test_get_stream_id_found_valid_file(send_file, testapp):
    send_file.return_value = 'RESPONSE'
    with auth(testapp, user='user_active'):
        with patch('play.application.tracks.open', MagicMock(spec=io.IOBase), create=True) as open_:
            response = testapp.get('/stream/adf19b92e21e1560a7dd0000')
    open_.assert_called_once_with('/var/media/some_file.mp3', 'rb')
    assert send_file.call_count == 1
    assert response.body == b'RESPONSE'


def test_get_stream_id_found_invalid_file(testapp):
    with auth(testapp, user='user_active'):
        with raises(AppError) as context:
            testapp.get('/stream/adf19b92e21e1560a7dd0000')
    assert '500 INTERNAL SERVER ERROR' in str(context.value)
