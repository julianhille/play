from contextlib import contextmanager
from fake_filesystem import FakeFilesystem
import pytest
from unittest.mock import Mock, patch
from webtest import TestApp
from flask.ext.login import AnonymousUserMixin

from play.application.wsgi import application as api
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


@pytest.fixture(autouse=True)
def file_system():
    fs = FakeFilesystem()
    fs.CreateDirectory('/tmp/open/')
    fs.CreateFile('/tmp/open/git.test', contents='Some_content')

    return fs
