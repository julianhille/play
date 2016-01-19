from unittest.mock import call, patch, MagicMock

from pyfakefs.fake_filesystem import FakeOsModule, FakeFileOpen
from scandir import GenericDirEntry

from play.task import application


def test_scan_dir(testapp_task, file_system):
    os = FakeOsModule(file_system)

    def scandir(path):
        for name in os.listdir(path):
            yield GenericDirEntry(path, name)
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.directories.insert(
        {'path': '/tmp/media/Album/John Bovi', 'parents': []})
    with patch('scandir.os', os), patch('scandir.listdir', os.listdir), \
            patch('scandir.stat', os.stat), patch('scandir.lstat', os.lstat),\
            patch('scandir.strerror', os.strerror), patch('scandir.islink', os.path.islink),\
            patch('scandir.join', os.path.join), patch('play.task.application.os', os), \
            patch('play.task.application.scandir', scandir):
        with patch('play.task.application.scan_audio.delay') as scan,\
                patch('celery.app.task.Task.delay') as delay:
            application.directory_scan('/tmp/media/Album/John Bovi/')
        delay.assert_called_once_with('/tmp/media/Album/John Bovi/SubDir')
        scan.assert_has_calls([
            call('/tmp/media/Album/John Bovi/01.mp3'),
            call('/tmp/media/Album/John Bovi/02-music-in-the-air.mp3')])
        assert testapp_task.backend.database.directories.find().count() == 2


def test_scan_not_existent_dir(testapp_task, file_system):
    os = FakeOsModule(file_system)

    def scandir(path):
        nonlocal os
        for name in os.listdir(path):
            yield GenericDirEntry(path, name)

    testapp_task.backend.database.directories.insert(
        {'path': '/tmp/media/Album/Unknown', 'parents': []})
    with patch('scandir.os', os), patch('scandir.listdir', os.listdir),\
            patch('scandir.stat', os.stat), patch('scandir.lstat', os.lstat),\
            patch('scandir.strerror', os.strerror), patch('scandir.islink', os.path.islink),\
            patch('scandir.join', os.path.join), patch('play.task.application.scandir', scandir):
        with patch('play.task.application.scan_audio.delay') as scan, \
                patch('celery.app.task.Task.delay') as directory_delay:
            application.directory_scan('/tmp/media/Album/Unknown')
            assert directory_delay.call_count == 0
            assert scan.call_count == 0
            item = testapp_task.backend.database.directories.find_one(
                {'path': '/tmp/media/Album/Unknown'})
            assert item['status'] is False


def test_scan_dir_missing_db_entry(testapp_task, file_system):
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    with patch('play.task.application.scandir') as scan, \
            patch('celery.app.task.Task.delay') as delay:
        application.directory_scan('/tmp/media/Album/John Bovi/')
    assert delay.call_count == 0
    assert scan.call_count == 0
    assert testapp_task.backend.database.directories.find().count() == 0
    assert testapp_task.backend.database.tracks.find().count() == 0


@patch('play.task.application.add_audio_information')
def test_scan_audio(audio_information, testapp_task, file_system):

    os = FakeOsModule(file_system)
    open_ = FakeFileOpen(file_system)
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    testapp_task.backend.database.directories.insert(
        {'parents': [], 'path': '/tmp/media/Album/John Bovi'})
    with patch('play.task.application.os', os),\
            patch('play.task.utils.open', open_, create=True):
        application.scan_audio('/tmp/media/Album/John Bovi/01.mp3')
    assert testapp_task.backend.database.directories.find().count() == 1
    assert testapp_task.backend.database.tracks.find().count() == 1
    assert audio_information.call_count == 1


def test_scan_audio_missing_directory(testapp_task, file_system):
    os = FakeOsModule(file_system)
    open_ = FakeFileOpen(file_system)
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    with patch('play.task.application.os', os),\
            patch('play.task.utils.open', open_, create=True):
        application.scan_audio('/tmp/media/Album/John Bovi/01.mp3')
    assert testapp_task.backend.database.directories.find().count() == 0
    assert testapp_task.backend.database.tracks.find().count() == 0


def test_scan_audio_missing_file(testapp_task, file_system):
    testapp_task.backend.database.directories.remove({})
    testapp_task.backend.database.tracks.remove({})
    testapp_task.backend.database.directories.insert(
        {'parents': [], 'path': '/tmp/media/Album/John Bovi'})
    os = FakeOsModule(file_system)
    open_ = FakeFileOpen(file_system)
    with patch('play.task.application.os', os),\
            patch('play.task.utils.open', open_, create=True):
        application.scan_audio('/tmp/media/Album/John Bovi/01111.mp3')
    assert testapp_task.backend.database.directories.find().count() == 1
    assert testapp_task.backend.database.tracks.find().count() == 0


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
