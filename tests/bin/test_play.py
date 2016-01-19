import errno
import os
from pytest import raises
from unittest.mock import patch, Mock

from pyfakefs.fake_filesystem import FakeFileOpen, FakeOsModule

from play.bin import play as cli


@patch('play.bin.play.sys.stderr.write')
def test_prints_help_on_unknown_command(stderr):
    with raises(SystemExit) as exits:
        cli.parser.parse_args('setup_NOTTHERE --MONGO_URI="http://test"'.split())
    assert exits.value.code == 2
    assert any('invalid choice' in str(param) for call in stderr.call_args_list for param in call)


@patch('play.bin.play.query_yes_no')
def test_cancel_write(query_yes_no, file_system):
    query_yes_no.return_value = False
    os_mock = FakeOsModule(file_system)
    with patch('play.bin.play.os', os_mock):
        with raises(SystemExit) as exits:
            args = cli.parser.parse_args('setup --config="/tmp/open/config2.ini"'.split())
            args.func(args)
    assert not os_mock.path.isfile('/tmp/open/config2.ini')
    assert 'Cancel to write config file' in exits.value.code


@patch('play.bin.play.query_yes_no')
def test_invalid_mongodb_uri(query_yes_no, file_system):
    query_yes_no.return_value = True
    os_mock = FakeOsModule(file_system)
    with patch('play.bin.play.os', os_mock):
        with raises(SystemExit) as exits:
            args = cli.parser.parse_args('setup --MONGO_URI="http://test"'.split())
            args.func(args)

    assert query_yes_no.call_count == 1
    assert 'Please correct the mongo URI' in exits.value.code


@patch('play.bin.play.query_yes_no')
def test_file_exists_no_overwrite(query_yes_no, file_system):
    query_yes_no.side_effect = [True, False]
    os_mock = FakeOsModule(file_system)
    with patch('play.bin.play.os', os_mock):
        with raises(SystemExit) as exits:
            args = cli.parser.parse_args('setup --config=/tmp/open/config.ini'.split())
            args.func(args)
    assert query_yes_no.call_count == 2
    assert 'Cancelled to write config' in exits.value.code


@patch('play.bin.play.query_yes_no')
def test_file_exists_overwrite_it(query_yes_no, file_system):
    query_yes_no.side_effect = [True, True]
    os_mock = FakeOsModule(file_system)
    open_mock = FakeFileOpen(file_system)
    with patch('play.bin.play.os', os_mock), \
            patch('play.bin.play.open', open_mock, create=True):
        args = cli.parser.parse_args('setup --SECRET_KEY=123KEY '
                                     '--config=/tmp/open/config.ini'.split())
        args.func(args)

    with open_mock('/tmp/open/config.ini') as fh:
        content = fh.read()
    assert '123KEY' in content
    assert query_yes_no.call_count == 2
    assert os_mock.path.isfile('/tmp/open/config.ini')


@patch('play.bin.play.query_yes_no')
def test_folder_creation_failes(query_yes_no, file_system):
    error = ''

    def raise_oserror(path):
        nonlocal error
        error = OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        raise error

    query_yes_no.return_value = True
    os_mock = FakeOsModule(file_system)
    os_mock.makedirs = Mock(side_effect=raise_oserror)
    with patch('play.bin.play.os', os_mock):
        with raises(SystemExit) as exits:
            args = cli.parser.parse_args('setup --config=/tmp/open/config2.ini'.split())
            args.func(args)
    assert query_yes_no.call_count == 1
    assert str(error) == exits.value.code


@patch('play.bin.play.query_yes_no')
def test_config_folder_already_exists(query_yes_no, file_system):
    query_yes_no.return_value = True
    open_mock = FakeFileOpen(file_system)

    def raise_oserror(path):
        raise OSError(errno.EEXIST, os.strerror(errno.EEXIST), path)

    os_mock = FakeOsModule(file_system)
    os_mock.makedirs = Mock(side_effect=raise_oserror)

    with patch('play.bin.play.os', os_mock), \
            patch('play.bin.play.open', open_mock, create=True):
        args = cli.parser.parse_args('setup --config=/tmp/open/config2.ini'.split())
        args.func(args)
    assert os_mock.path.isfile('/tmp/open/config2.ini') is True
    assert query_yes_no.call_count == 1
    with open_mock('/tmp/open/config2.ini') as f:
        content = f.read()
    assert '[DEFAULT]' in content
    assert 'mongo_uri' in content
    assert 'secret_key' in content
    assert 'wtf_csrf_secret_key' in content


@patch('play.bin.play.input', create=True)
def test_query_yes_input_valid(input_mock):
    input_mock.side_effect = ['Y', 'y', 'yes', '']
    for _ in range(1, 5):
        assert cli.query_yes_no('Question?', default='yes')


@patch('play.bin.play.input', create=True)
def test_query_no_input_valid(input_mock):
    input_mock.side_effect = ['N', 'n', 'no', '']
    for _ in range(1, 5):
        assert not cli.query_yes_no('Question?', default='no')


@patch('play.bin.play.input', create=True)
def test_query_yes_no_invalid_default(input_mock):
    with raises(ValueError):
        assert cli.query_yes_no('Question?', default='BAD')


def test_query_yes_no_invalid_choice():
    with patch('play.bin.play.input', Mock(side_effect=['', 'n']), create=True) as input_mock:
        assert not cli.query_yes_no('Question?', default=None)
        assert input_mock.call_count == 2

    with patch('play.bin.play.input', Mock(side_effect=['', 'y']), create=True) as input_mock:
        assert cli.query_yes_no('Question?', default=None)
        assert input_mock.call_count == 2
