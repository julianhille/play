from pytest import mark
from tests.conftest import auth


@mark.parametrize('user', [None, 'admin_active', 'user_active', 'admin_user_active'])
def test_csrf_auth(testapp_api, user):
    with auth(testapp_api, user=user):
        response = testapp_api.get('/csrf')
    assert response.status_code == 200
    assert 'csrf' in response.json_body
    assert response.json_body['csrf']