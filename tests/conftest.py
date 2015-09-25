from contextlib import contextmanager
import pytest
from unittest.mock import patch, Mock
from webtest import TestApp

from play.application.wsgi import application


def app_factory():
    return application


@pytest.fixture(autouse=True)
def testapp_api(request, humongous):
    factory = app_factory
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', app_factory)
    with patch('pymongo.mongo_client', Mock(return_value=humongous)):
        app = factory()
    app.debug = True
    return TestApp(app)


@contextmanager
def auth(testapp_api, user, roles=None):

    def check_auth(username, password, allowed_roles, resource, method):
        testapp_api.app.user = testapp_api.app.data.driver.db.users.find_one({'name': user})
        return True

    testapp_api.authorization = ('Basic', ('user', 'password'))
    with patch.object(testapp_api.app.auth, 'check_auth', check_auth):
        yield
