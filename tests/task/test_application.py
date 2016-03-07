from unittest.mock import MagicMock, patch
from bson import ObjectId

from pyfakefs.fake_filesystem import FakeFileOpen, FakeOsModule
from play.task import application


def walk_fix(func):
    #  this is only needed as long as pyfakefs does not support followlinks
    def inner(top, topdown=True, onerror=None, followlinks=False):
        return func(top, topdown=topdown, onerror=onerror)
    return inner


def test_walk_dir(testapp_task, file_system):
    os_mock = FakeOsModule(file_system)
    os_mock.walk = walk_fix(os_mock.walk)
    testapp_task.backend.database.directories.remove({})
    directory_id = testapp_task.backend.database.directories.insert(
        {'path': '/tmp/media/Album/John Bovi', 'parents': []})
    with patch('play.task.application.os', os_mock):
        with patch('play.task.application.audio_scan.apply_async') as scan:
            application.directory_scan(directory_id)
        assert scan.call_count == 3
        for call_arg in scan.call_args_list:
            assert isinstance(call_arg[1]['args'][0], ObjectId)
            assert call_arg[1]['queue'] == 'play'


def test_scan_not_existent_dir(testapp_task, file_system):
    id_ = testapp_task.backend.database.directories.insert(
        {'path': '/tmp/media/Album/Unknown', 'parents': []})
    os_mock = FakeOsModule(file_system)
    os_mock.walk = walk_fix(os_mock.walk)
    with patch('play.task.application.os', os_mock):
        with patch('play.task.application.audio_scan.apply_async') as scan:
            application.directory_scan(id_)
            assert scan.call_count == 0
            item = testapp_task.backend.database.directories.find_one(
                {'_id': id_})
            assert item['active'] is False


@patch('play.task.application.lock')
def test_scan_dir_missing_db_entry(lock, testapp_task):
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    application.directory_scan(ObjectId())
    assert testapp_task.backend.database.directories.find().count() == 0
    assert testapp_task.backend.database.tracks.find().count() == 0
    assert lock.call_count == 0


@patch('play.task.application.add_audio_information')
def test_scan_audio(audio_information, testapp_task, file_system):
    os_mock = FakeOsModule(file_system)
    os_mock.walk = walk_fix(os_mock.walk)
    open_mock = FakeFileOpen(file_system)
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    dir_id = testapp_task.backend.database.directories.insert(
        {'parents': [], 'path': '/tmp/media/Album/John Bovi'})
    id_ = testapp_task.backend.database.tracks.insert(
        {'directory': dir_id, 'path': '/tmp/media/Album/John Bovi/01.mp3'})
    with patch('play.task.application.os', os_mock),\
            patch('play.task.utils.open', open_mock, create=True):
        application.audio_scan(id_)
    assert testapp_task.backend.database.directories.find().count() == 1
    assert testapp_task.backend.database.tracks.find().count() == 1
    assert audio_information.call_count == 1


@patch('play.task.application.lock')
def test_scan_audio_missing_db_entry(lock, testapp_task, file_system):
    testapp_task.backend.database.tracks.remove({})
    application.directory_scan(ObjectId())
    assert testapp_task.backend.database.directories.find().count() == 1
    assert testapp_task.backend.database.tracks.find().count() == 0
    assert lock.call_count == 0


def test_scan_audio_missing_file(testapp_task, file_system):
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})

    os_mock = FakeOsModule(file_system)
    os_mock.walk = walk_fix(os_mock.walk)
    open_mock = MagicMock()
    dir_id = testapp_task.backend.database.directories.insert(
        {'parents': [], 'path': '/tmp/media/Album/John Bovi'})
    id_ = testapp_task.backend.database.tracks.insert(
        {'directory': dir_id, 'path': '/tmp/media/Album/John Bovi/NOTEXISTS.mp3'})
    with patch('play.task.application.os', os_mock),\
            patch('play.task.application.open', open_mock, create=True):
        application.audio_scan(id_)
    assert testapp_task.backend.database.directories.find().count() == 1
    assert testapp_task.backend.database.tracks.find_one({'_id': id_})['active'] is False
    assert open_mock.call_count == 0


def test_scan_audio_missing_directory(testapp_task, file_system):
    os_mock = FakeOsModule(file_system)
    os_mock.walk = walk_fix(os_mock.walk)
    open_mock = FakeFileOpen(file_system)
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})

    id_ = testapp_task.backend.database.tracks.insert(
        {'directory': ObjectId(), 'path': '/tmp/media/Album/John Bovi/01.mp3'})
    with patch('play.task.application.os', os_mock),\
            patch('play.task.utils.open', open_mock, create=True):
        application.audio_scan(id_)
    assert testapp_task.backend.database.directories.find().count() == 0
    assert testapp_task.backend.database.tracks.find_one({'_id': id_})['active'] is False


@patch('play.task.application.File')
def test_missing_tags(File):

    File.return_value = MagicMock(
        info=MagicMock(bitrate=256431,
                       length=200.120,
                       sample_rate=44100,
                       track_gain=100,
                       track_peak=110),
        tags={}
    )
    data = {'search': {'file': 'is in'}}

    application.add_audio_information('/some/path', data)
    assert 'length' in data
    assert 'lossless' in data
    assert 'sample_rate' in data
    assert 'bitrate' in data
    assert data['meta_original'] == {}
    assert data['type'] == 'MP3'
    assert 'search' in data
    assert 'artist' in data['search']
    assert 'title' in data['search']
    assert data['search']['file'] == 'is in'
    assert data['search']['artist'] == ''
    assert data['search']['title'] == ''

    data = {}
    application.add_audio_information('/some/path', data)
    assert 'file' not in data['search']


@patch('play.task.application.File')
def test_with_tags(File):
    tags = {'artist': ['someone'], 'title': ['title']}
    File.return_value = MagicMock(
        info=MagicMock(bitrate=256431,
                       length=200.120,
                       sample_rate=44100,
                       track_gain=100,
                       track_peak=110),
        tags=tags
    )
    data = {'search': {'file': 'is in'}}

    application.add_audio_information('/some/path', data)
    assert data['meta_original'] == {'artist': ['someone'], 'title': ['title']}
    assert 'search' in data
    assert 'artist' in data['search']
    assert 'title' in data['search']
    assert data['search']['file'] == 'is in'
    assert data['search']['artist'] == 'someone'
    assert data['search']['title'] == 'title'
