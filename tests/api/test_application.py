from pyfakefs.fake_filesystem import FakeOsModule, FakeFileOpen
from play.api import application
from unittest.mock import Mock, patch


def test_roles_validator_roles_not_list():
    validator = application.Validator({})
    validator._error = Mock()
    validator._validate_roles(None, 'field', None)
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_roles_validator_roles_list_not_str():
    validator = application.Validator({})
    validator._error = Mock()
    validator._validate_roles([None], 'field', [1])
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_invalid_path(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator({})
        validator._error = Mock()
        validator._validate_path(True, 'field', '/invalid')
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_valid_file(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator({})
        validator._error = Mock()
        validator._validate_path(True, 'field', '/tmp/open/git.test')
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_valid_path(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator({})
        validator._error = Mock()
        validator._validate_path(True, 'field', '/tmp/open/')
    assert validator._error.call_count == 0


def test_sentdfile_partial_no_range_header(testapp_api, file_system):
    with patch('flask.helpers.os', FakeOsModule(file_system), create=True):
        with patch('flask.helpers.open', FakeFileOpen(file_system), create=True):
            with testapp_api.app.test_request_context('/stream/123123123123123123123123'):
                response = application.send_file_partial(
                    '/tmp/media/Album/John Bovi/01.mp3', 'etag-Test')
    assert response.headers['ETag'] == '"etag-Test"'
    assert response.direct_passthrough is True
    assert b'Some_content' in list(response.response)


def test_send_file_partial_with_range_header(testapp_api, file_system):
    with patch.object(application, 'os', FakeOsModule(file_system), create=True):
        with patch.object(application, 'open', FakeFileOpen(file_system), create=True):
            with testapp_api.app.test_request_context('/stream/123123123123123123123123',
                                                      headers=[('Range', '1-12')]):
                response = application.send_file_partial(
                    '/tmp/media/Album/John Bovi/01.mp3', 'etag-Test')
    assert response.headers['ETag'] == '"etag-Test"'
    assert response.headers['Content-Range'] == 'bytes 1-11/12'
    assert response.headers['Cache-Control'] == 'no-cache'
    assert response.direct_passthrough is True
    assert b'ome_content' in list(response.response)
