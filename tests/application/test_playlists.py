from pytest import raises
from webtest import AppError

from tests.conftest import auth

VALID_PLAYLIST = {
    'name': 'Some Playlist'
}


def test_get_resource_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/playlists')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert '401 UNAUTHORIZED' in str(context.value)


def test_post_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.post_json('/playlists', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_put_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.put_json('/playlists/aaff1bee2e21e1560a7dd000', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_patch_item_no_auth(testapp):
    with raises(AppError) as context:
        testapp.patch_json('/playlists/aaff1bee2e21e1560a7dd000', VALID_PLAYLIST)
    assert '401 UNAUTHORIZED' in str(context.value)


def test_get_item_user_is_owner(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert response.status_code == 200


def test_get_item_user_is_not_owner(testapp):
    with auth(testapp, user='admin_active'):
        with raises(AppError) as context:
            testapp.get('/playlists/aaff1bee2e21e1560a7dd000')
    assert '404 NOT FOUND' in str(context.value)


def test_get_item_user_is_not_owner_playlist_public(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response.status_code == 200


def test_get_resource_user_is_owner(testapp):
    with auth(testapp, user='user_active'):
        response = testapp.get('/playlists')
    assert response.status_code == 200
    items = [v['_id'] for v in response.json_body['_items']]
    assert ['aaff1bee2e21e1560a7dd000', 'aaff1bee2e21e1560a7dd001'] == items


def test_get_resource_public_playlists(testapp):
    with auth(testapp, user='admin_active'):
        response = testapp.get('/playlists')
    assert response.status_code == 200
    items = [v['_id'] for v in response.json_body['_items']]
    assert ['aaff1bee2e21e1560a7dd001'] == items


def test_post_item(testapp):
    with auth(testapp, user='admin_active'):
        response_post = testapp.post_json('/playlists', VALID_PLAYLIST)
        response_get = testapp.get('/' + response_post.json_body['_links']['self']['href'])
    assert response_post.status_code == 201
    assert response_get.status_code == 200
    response_get.json_body['owner'] == testapp.app.user['_id']


def test_patch_item_owner(testapp):
    with auth(testapp, user='user_active'):
        response_get = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
        response_post = testapp.patch_json('/playlists/aaff1bee2e21e1560a7dd001', VALID_PLAYLIST,
                                           headers=[('If-Match', response_get.headers['ETag'])])
        response_get_after_patch = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response_post.status_code == 200
    assert response_get.status_code == 200
    response_get_after_patch.json_body['owner'] == testapp.app.user['_id']


def test_patch_item_not_owner(testapp):
    with auth(testapp, user='admin_active'):
        response_get = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
        with raises(AppError) as context:
            testapp.patch_json('/playlists/aaff1bee2e21e1560a7dd001', VALID_PLAYLIST,
                               headers=[('If-Match', response_get.headers['ETag'])])
    assert '403 FORBIDDEN' in str(context.value)


def test_put_item_owner(testapp):
    with auth(testapp, user='user_active'):
        response_get = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
        response_post = testapp.put_json('/playlists/aaff1bee2e21e1560a7dd001', VALID_PLAYLIST,
                                         headers=[('If-Match', response_get.headers['ETag'])])
        response_get = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
    assert response_post.status_code == 200
    assert response_get.status_code == 200
    response_get.json_body['owner'] == testapp.app.user['_id']


def test_put_item_not_owner(testapp):
    with auth(testapp, user='admin_active'):
        response_get = testapp.get('/playlists/aaff1bee2e21e1560a7dd001')
        with raises(AppError) as context:
            testapp.put_json('/playlists/aaff1bee2e21e1560a7dd001', VALID_PLAYLIST,
                             headers=[('If-Match', response_get.headers['ETag'])])
    assert '403 FORBIDDEN' in str(context.value)
