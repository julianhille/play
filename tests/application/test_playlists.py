from pytest import raises
from webtest import AppError

from tests.conftest import auth

VALID_PLAYLIST = {
    'name': 'Some Playlist'
}


def test_get_resource_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/playlists')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.post_json('/playlists', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.put_json('/playlists/aaff1bee2e21e1560a7dd000', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.patch_json('/playlists/aaff1bee2e21e1560a7dd000', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_user_is_owner(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert response.status_code == 200


def test_get_item_user_is_not_owner(testapp_api):
    with auth(testapp_api, user='admin_active'):
        with raises(AppError) as context:
            testapp_api.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert '404 NOT FOUND' in str(context.value)


def test_get_item_user_is_not_owner_playlist_public(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response.status_code == 200


def test_get_resource_user_is_owner(testapp_api):
    with auth(testapp_api, user='user_active'):
        response = testapp_api.get('/playlists')
    assert response.status_code == 200
    items = [v['_id'] for v in response.json_body['_items']]
    assert ['aaff1bee2e21e1560a7dd000', 'aaff1bee2e21e1560a7dd001'] == items


def test_get_resource_public_playlists(testapp_api):
    with auth(testapp_api, user='admin_user_active'):
        response = testapp_api.get('/playlists')
    assert response.status_code == 200
    items = [v['_id'] for v in response.json_body['_items']]
    assert ['aaff1bee2e21e1560a7dd001'] == items


def test_post_item(testapp_api):
    with auth(testapp_api, user='admin_user_active'):
        response_post = testapp_api.post_json('/playlists', VALID_PLAYLIST)
        response_get = testapp_api.get('/' + response_post.json_body['_links']['self']['href'])
    assert response_post.status_code == 201
    assert response_get.status_code == 200
    assert response_get.json_body['owner'] == 'ccff1bee2e21e1560a7dd000'


def test_patch_item_owner(testapp_api):
    with auth(testapp_api, user='user_active'):
        response_get = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
        response_post = testapp_api.patch_json(
            '/playlists/aaff1bee2e21e1560a7dd001',
            VALID_PLAYLIST,
            headers=[('If-Match', response_get.headers['ETag'])])
        response_get_after_patch = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_get_after_patch.json_body['owner'] == response_get.json_body['owner']


def test_patch_item_not_owner(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response_get = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
        with raises(AppError) as context:
            testapp_api.patch_json(
                '/playlists/aaff1bee2e21e1560a7dd001',
                VALID_PLAYLIST,
                headers=[('If-Match', response_get.headers['ETag'])])
    assert '403 FORBIDDEN' in str(context.value)


def test_put_item_owner(testapp_api):
    with auth(testapp_api, user='user_active'):
        response_get = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
        response_post = testapp_api.put_json(
            '/playlists/aaff1bee2e21e1560a7dd001',
            VALID_PLAYLIST,
            headers=[('If-Match', response_get.headers['ETag'])])
        response_get_after = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response_post.status_code == 200
    assert response_get.status_code == 200
    assert response_get_after.status_code == 200
    assert response_get.json_body['owner'] == response_get_after.json_body['owner']


def test_put_item_not_owner(testapp_api):
    with auth(testapp_api, user='admin_active'):
        response_get = testapp_api.get('/playlists/aaff1bee2e21e1560a7dd001')
        with raises(AppError) as context:
            testapp_api.put_json(
                '/playlists/aaff1bee2e21e1560a7dd001',
                VALID_PLAYLIST,
                headers=[('If-Match', response_get.headers['ETag'])])
    assert '403 FORBIDDEN' in str(context.value)
