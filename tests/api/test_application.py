from fake_filesystem import FakeOsModule
from play.api import application
from unittest.mock import Mock, patch


def test_roles_validator_roles_not_list():
    validator = application.Validator()
    validator._error = Mock()
    validator._validate_roles(None, 'field', None)
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_roles_validator_roles_list_not_str():
    validator = application.Validator()
    validator._error = Mock()
    validator._validate_roles([None], 'field', [1])
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_invalid_path(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator()
        validator._error = Mock()
        validator._validate_path(True, 'field', '/invalid')
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_valid_file(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator()
        validator._error = Mock()
        validator._validate_path(True, 'field', '/tmp/open/git.test')
    assert validator._error.call_count == 1
    assert validator._error.call_args[0][0] == 'field'


def test_path_validator_valid_path(file_system):
    with patch('play.api.application.os', FakeOsModule(file_system)):
        validator = application.Validator()
        validator._error = Mock()
        validator._validate_path(True, 'field', '/tmp/open/')
    assert validator._error.call_count == 0
