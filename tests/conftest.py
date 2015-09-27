from contextlib import contextmanager
import pytest
from unittest.mock import patch, Mock
from webtest import TestApp
from flask.ext.login import AnonymousUserMixin

from play.application.wsgi import application as api
from play.administration.wsgi import application as admin
from play.models.users import LoginUser

def app_api_factory():
    return api


@pytest.fixture(autouse=True)
def testapp_api(request, humongous):
    factory = app_api_factory
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', app_api_factory)
    with patch('pymongo.mongo_client', Mock(return_value=humongous)):
        app = factory()
    app.debug = True
    return TestApp(app)


@contextmanager
def auth(testapp_api, user):

    def check_auth(*args, **kwargs):
        nonlocal user
        return (LoginUser.get_by_name(testapp_api.app.data.driver.db.users, user) or
                AnonymousUserMixin())

    with patch.object(testapp_api.app.login_manager, 'request_callback', check_auth):
        yield


def app_admin_factory():
    return admin


@pytest.fixture(autouse=True)
def testapp_admin(request, humongous):
    factory = app_admin_factory
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', app_admin_factory)
    with patch('pymongo.mongo_client', Mock(return_value=humongous)):
        app = factory()
    app.debug = True
    return TestApp(app)
