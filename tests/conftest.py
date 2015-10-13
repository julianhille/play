from celery.backends.mongodb import MongoBackend
from contextlib import contextmanager
from fake_filesystem import FakeFilesystem
import pytest
from unittest.mock import Mock, patch
from webtest import TestApp
from flask.ext.login import AnonymousUserMixin

from play.application.wsgi import application as api
from play.task.application import application as task_api
from play.models.users import LoginUser
from play.mongo import ensure_indices


@pytest.fixture(autouse=True)
def testapp_api(request, humongous):
    ensure_indices(humongous)
    with patch('pymongo.mongo_client', Mock(return_value=humongous)):
        factory = api
        marker = request.node.get_marker('app_factory')
        if marker:
            factory = marker.kwargs.get('factory', api)
    factory.debug = True

    return TestApp(factory)


@contextmanager
def auth(testapp_api, user):
    def check_auth(*args, **kwargs):
        nonlocal user
        return (LoginUser.get_by_name(testapp_api.app.data.driver.db.users, user) or
                AnonymousUserMixin())
    with patch.object(testapp_api.app.login_manager, 'request_callback', check_auth):
        yield


@pytest.fixture(autouse=True)
def testapp_task(request, humongous):
    ensure_indices(humongous)
    MongoBackend._get_database = Mock(return_value=humongous)
    factory = task_api
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', task_api)
    return factory


@pytest.fixture(autouse=True)
def file_system():
    fs = FakeFilesystem()
    fs.CreateDirectory('/tmp/open/')
    fs.CreateFile('/tmp/open/git.test', contents='Some_content')

    fs.CreateDirectory('/tmp/media/')
    fs.CreateDirectory('/tmp/media/Album')
    fs.CreateDirectory('/tmp/media/Album/John Bovi')
    fs.CreateFile('/tmp/media/Album/John Bovi/01.mp3', contents='Some_content')
    fs.CreateFile('/tmp/media/Album/John Bovi/02-music-in-the-air.mp3', contents='Some_content')
    fs.CreateFile('/tmp/media/Album/John Bovi/album.jpg', contents='Some_content')
    fs.CreateFile('/tmp/media/Album/John Bovi/anything.txt', contents='Some_content')
    fs.CreateDirectory('/tmp/media/Album/John Bovi/SubDir')

    fs.CreateDirectory('/tmp/media/Album/Allica Mett')
    fs.CreateFile('/tmp/media/Album/Allica Mett01.mp3', contents='Some_content')
    fs.CreateFile('/tmp/media/Album/~.swo', contents='Some_content')

    return fs
