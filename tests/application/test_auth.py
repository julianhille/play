from eve import Eve
from play.application.auth import RolesAuth
import pytest
from pytest import raises
from webtest import AppError


def app_factory():
    settings = {
        'DOMAIN': {
            'noroles': {
                'allowed_roles': []
            },
            'roles_1': {
                'allowed_item_roles': ['admin', 'user']
            },
            'roles_2': {
                'allowed_roles': ['admin']
            }
        }
    }
    return Eve(settings=settings, auth=RolesAuth())


@pytest.mark.app_factory(factory=app_factory)
def test_no_auth(testapp_api):
    with raises(AppError) as context:
        testapp_api.get('/noroles')
    assert 'Bad response: 401 UNAUTHORIZED' in str(context.value)


@pytest.mark.app_factory(factory=app_factory)
def test_wrong_password_no_role_active(testapp_api):
    testapp_api.authorization = ('Basic', ('admin_user_active', 'WRONG'))
    with raises(AppError) as context:
        testapp_api.get('/noroles')
    assert 'Bad response: 401 UNAUTHORIZED' in str(context.value)


@pytest.mark.app_factory(factory=app_factory)
def test_correct_password_no_roles_active(testapp_api):
    testapp_api.authorization = ('Basic', ('admin_user_active', 'password'))
    response = testapp_api.get('/noroles')
    assert response.status_code == 200


@pytest.mark.app_factory(factory=app_factory)
@pytest.mark.parametrize('password', ['WRONG', 'password'])
def test_wrong_password_no_role_inactive(testapp_api, password):
    testapp_api.authorization = ('Basic', ('admin_user_inactive', password))
    with raises(AppError) as context:
        testapp_api.get('/noroles')
    assert 'Bad response: 401 UNAUTHORIZED' in str(context.value)


@pytest.mark.app_factory(factory=app_factory)
def test_missing_role(testapp_api):
    testapp_api.authorization = ('Basic', ('user_active', 'password'))
    with raises(AppError) as context:
        testapp_api.get('/roles_2')
    assert 'Bad response: 401 UNAUTHORIZED' in str(context.value)
