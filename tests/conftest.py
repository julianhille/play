from celery.backends.mongodb import MongoBackend
from contextlib import contextmanager
from pyfakefs.fake_filesystem import FakeFilesystem
import pytest
from unittest.mock import Mock, patch
from webtest import TestApp
from flask.ext.login import AnonymousUserMixin


from play.api.wsgi import create_app as api
from play.task.application import application as task_app
from play.models.users import get_user_by_name
from play.mongo import ensure_indices
from play.static.wsgi import application as static_app

@pytest.fixture()
def testapp_api(request, mongodb):
    ensure_indices(mongodb)

    factory = api
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', api)
    with patch('eve.io.mongo.mongo.Mongo.pymongo'):
        app = factory()
    app.data.pymongo = Mock(return_value=Mock(db=mongodb))
    app.data.mongo_prefix = None
    app.debug = True
    return TestApp(app)


@contextmanager
def auth(testapp_api, user):
    def check_auth(*args, **kwargs):
        nonlocal user
        return (get_user_by_name(testapp_api.app.data.driver.db.users, user) or
                AnonymousUserMixin())
    with patch.object(testapp_api.app.login_manager, 'request_callback', check_auth):
        yield


@pytest.fixture()
def testapp_task(request, mongodb):
    ensure_indices(mongodb)
    MongoBackend._get_database = Mock(return_value=mongodb)
    factory = task_app
    marker = request.node.get_marker('app_factory')
    if marker:
        factory = marker.kwargs.get('factory', task_app)

    return factory


@pytest.fixture()
def file_system():
    fs = FakeFilesystem()
    fs.CreateDirectory('/tmp/open/')
    fs.CreateFile('/tmp/open/git.test', contents='Some_content')
    fs.CreateFile('/tmp/open/config.cfg', contents='OVERWRITE = \'overwritten\'')

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


@pytest.fixture()
def testapp_static(request):
    marker = request.node.get_marker('app_factory')
    factory = None
    if marker:
        factory = marker.kwargs.get('factory', None)
    app = static_app if not factory else factory()
    app.debug = True
    return TestApp(app)


def mongo_engine(pytestconfig):
    return pytest.config.getoption('mongodb_engine') or pytest.config.getini('mongodb_engine')

