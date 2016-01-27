import errno
import os
from pytest import mark, raises
from unittest.mock import call, Mock, patch

from pyfakefs.fake_filesystem import FakeFileOpen, FakeOsModule

from play import shell


@patch('play.shell.sys.stderr.write')
def test_setup_prints_help_on_unknown_command(stderr):
    with raises(SystemExit) as exits:
        shell.parser.parse_args('setup_NOTTHERE --MONGO_URI="http://test"'.split())
    assert exits.value.code == 2
    assert any('invalid choice' in str(param) for call in stderr.call_args_list for param in call)


@patch('play.shell.query_yes_no')
def test_setup_cancel_write(query_yes_no, file_system):
    query_yes_no.return_value = False
    os_mock = FakeOsModule(file_system)
    with patch('play.shell.os', os_mock):
        with raises(SystemExit) as exits:
            args = shell.parser.parse_args('setup --config="/tmp/open/config2.cfg"'.split())
            args.func(args)
    assert not os_mock.path.isfile('/tmp/open/config2.cfg')
    assert 'Cancel to write config file' in exits.value.code


@patch('play.shell.query_yes_no')
def test_setup_invalid_mongodb_uri(query_yes_no, file_system):
    query_yes_no.return_value = True
    os_mock = FakeOsModule(file_system)
    with patch('play.shell.os', os_mock):
        with raises(SystemExit) as exits:
            args = shell.parser.parse_args('setup --MONGO_URI="http://test"'.split())
            args.func(args)

    assert query_yes_no.call_count == 1
    assert 'Please correct the mongo URI' in exits.value.code


@patch('play.shell.query_yes_no')
def test_setup_file_exists_no_overwrite(query_yes_no, file_system):
    query_yes_no.side_effect = [True, False]
    os_mock = FakeOsModule(file_system)
    with patch('play.shell.os', os_mock):
        with raises(SystemExit) as exits:
            args = shell.parser.parse_args('setup --config=/tmp/open/config.cfg'.split())
            args.func(args)
    assert query_yes_no.call_count == 2
    assert 'Cancelled to write config' in exits.value.code


@patch('play.shell.query_yes_no')
def test_setup_file_exists_overwrite_it(query_yes_no, file_system):
    query_yes_no.side_effect = [True, True]
    os_mock = FakeOsModule(file_system)
    open_mock = FakeFileOpen(file_system)
    with patch('play.shell.os', os_mock), \
            patch('play.shell.open', open_mock, create=True):
        args = shell.parser.parse_args('setup --SECRET_KEY=123KEY '
                                       '--config=/tmp/open/config.cfg'.split())
        args.func(args)

    with open_mock('/tmp/open/config.cfg') as fh:
        content = fh.read()
    assert '123KEY' in content
    assert query_yes_no.call_count == 2
    assert os_mock.path.isfile('/tmp/open/config.cfg')


@patch('play.shell.query_yes_no')
def test_setup_folder_creation_failes(query_yes_no, file_system):
    error = ''

    def raise_oserror(path):
        nonlocal error
        error = OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        raise error

    query_yes_no.return_value = True
    os_mock = FakeOsModule(file_system)
    os_mock.makedirs = Mock(side_effect=raise_oserror)
    with patch('play.shell.os', os_mock):
        with raises(SystemExit) as exits:
            args = shell.parser.parse_args('setup --config=/tmp/open/config2.cfg'.split())
            args.func(args)
    assert query_yes_no.call_count == 1
    assert str(error) == exits.value.code


@patch('play.shell.query_yes_no')
def test_setup_config_folder_already_exists(query_yes_no, file_system):
    query_yes_no.return_value = True
    open_mock = FakeFileOpen(file_system)

    def raise_oserror(path):
        raise OSError(errno.EEXIST, os.strerror(errno.EEXIST), path)

    os_mock = FakeOsModule(file_system)
    os_mock.makedirs = Mock(side_effect=raise_oserror)

    with patch('play.shell.os', os_mock), \
            patch('play.shell.open', open_mock, create=True):
        args = shell.parser.parse_args('setup --config=/tmp/open/config2.cfg'.split())
        args.func(args)
    assert os_mock.path.isfile('/tmp/open/config2.cfg') is True
    assert query_yes_no.call_count == 1
    with open_mock('/tmp/open/config2.cfg') as f:
        content = f.read()
    assert 'MONGO_URI' in content
    assert 'SECRET_KEY' in content
    assert 'WTF_CSRF_SECRET_KEY' in content


@patch('play.shell.input', create=True)
def test_query_yes_input_valid(input_mock):
    input_mock.side_effect = ['Y', 'y', 'yes', '']
    for _ in range(1, 5):
        assert shell.query_yes_no('Question?', default='yes')


@patch('play.shell.input', create=True)
def test_query_no_input_valid(input_mock):
    input_mock.side_effect = ['N', 'n', 'no', '']
    for _ in range(1, 5):
        assert not shell.query_yes_no('Question?', default='no')


@patch('play.shell.input', create=True)
def test_query_yes_no_invalid_default(input_mock):
    with raises(ValueError):
        assert shell.query_yes_no('Question?', default='BAD')


def test_query_yes_no_invalid_choice():
    with patch('play.shell.input', Mock(side_effect=['', 'n']), create=True) as input_mock:
        assert not shell.query_yes_no('Question?', default=None)
        assert input_mock.call_count == 2

    with patch('play.shell.input', Mock(side_effect=['', 'y']), create=True) as input_mock:
        assert shell.query_yes_no('Question?', default=None)
        assert input_mock.call_count == 2


@patch('play.shell.os')
def test_initdb_config_does_not_exists(os_mock, file_system):
    os_mock.path.isfile = Mock(return_value=False)
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('initdb --config=/tmp/NOTEXISTENT'.split())
        args.func(args)
    assert 'Config file' in exits.value.code and 'does not exist' in exits.value.code
    os_mock.path.isfile.assert_called_once_with('/tmp/NOTEXISTENT')


@patch('play.shell.os')
def test_initdb_throw_exception(os_mock, file_system):
    test_exception = 'Test Exception'
    os_mock.path.isfile = Mock(side_effect=Exception(test_exception))
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('initdb --config=/tmp/NOTEXISTENT'.split())
        args.func(args)
    assert test_exception in exits.value.code


@patch('play.shell.sys.stderr.write')
def test_initdb_not_allowed_collections(stderr):
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('initdb --collections abc'.split())
        args.func(args)
    assert exits.value.code == 2
    assert any(
        'invalid choice' in str(param) for call in stderr.call_args_list for param in call)


@patch('play.shell._get_config')
@patch('play.shell.os')
@patch('play.shell.query_yes_no')
@patch('play.shell.pymongo')
def test_initdb_collections_exists_no_force(pymongo_mock, query_yes_no, os_mock,
                                            config_mock, file_system):
    db_mock = pymongo_mock.MongoClient().get_default_database()
    db_mock.collection_names.return_value = shell.default_collections
    query_yes_no.return_value = False
    config_mock.return_value = {'MONGO_URI': 'mongo_uri'}
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('initdb --config=/tmp/open/config.cfg'.split())
        args.func(args)
    assert 'Cancel recreate' in exits.value.code


@patch('play.shell._get_config')
@patch('play.shell.os')
@patch('play.shell.query_yes_no')
@patch('play.shell.pymongo')
@patch('play.shell.ensure_indices')
def test_initdb_collections_exists_no_force_answer_true(ensure_indices_mock, pymongo_mock,
                                                        query_yes_no, os_mock, config_mock,
                                                        file_system):
    db_mock = pymongo_mock.MongoClient().get_default_database()
    db_mock.collection_names.return_value = shell.default_collections
    query_yes_no.return_value = True
    config_mock.return_value = {'MONGO_URI': 'mongo_uri'}
    args = shell.parser.parse_args('initdb --config=/tmp/open/config.cfg'.split())
    args.func(args)
    db_mock.drop_collection.assert_has_calls(
        (call(collection) for collection in shell.default_collections), any_order=True)
    db_mock.create_collection.assert_has_calls(
        (call(collection) for collection in shell.default_collections), any_order=True)
    ensure_indices_mock.assert_called_once_with(db_mock)


@patch('play.shell._get_config')
@patch('play.shell.os')
@patch('play.shell.query_yes_no')
@patch('play.shell.pymongo')
@patch('play.shell.ensure_indices')
def test_initdb_collections_exists_force_true(ensure_indices_mock, pymongo_mock, query_yes_no,
                                              os_mock, config_mock, file_system):
    db_mock = pymongo_mock.MongoClient().get_default_database()
    db_mock.collection_names.return_value = shell.default_collections
    config_mock.return_value = {'MONGO_URI': 'mongo_uri'}
    args = shell.parser.parse_args('initdb --force --config=/tmp/open/config.cfg'.split())
    args.func(args)
    assert query_yes_no.call_count == 0
    db_mock.drop_collection.assert_has_calls((call(collection) for collection in
                                              shell.default_collections), any_order=True)
    db_mock.create_collection.assert_has_calls((call(collection) for collection in
                                                shell.default_collections), any_order=True)
    ensure_indices_mock.assert_called_once_with(db_mock)


@patch('play.shell._get_config')
@patch('play.shell.os')
@patch('play.shell.query_yes_no')
@patch('play.shell.pymongo')
@patch('play.shell.ensure_indices')
def test_initdb_collections_set(ensure_indices_mock, pymongo_mock, query_yes_no, os_mock,
                                config_mock, file_system):
    db_mock = pymongo_mock.MongoClient().get_default_database()
    db_mock.collection_names.return_value = []
    config_mock.return_value = {'MONGO_URI': 'mongo_uri'}
    first_item = shell.default_collections.copy().pop()
    args = shell.parser.parse_args(
        ('initdb --collections {}  --config=/tmp/open/config.cfg'.format(first_item)).split())
    args.func(args)
    assert query_yes_no.call_count == 0
    db_mock.drop_collection.assert_called_once_with(first_item)
    db_mock.create_collection.assert_called_once_with(first_item)
    ensure_indices_mock.assert_called_once_with(db_mock)


@patch('play.shell.sys.stderr.write')
def test_add_user_(stderr):
    with raises(SystemExit) as error:
        args = shell.parser.parse_args(
            ('adduser'.split()))
        args.func(args)
    assert error.value.code == 2
    assert any('required' in str(param) and 'name' in str(param)
               for call in stderr.call_args_list for param in call)


@patch('play.shell._get_config')
def test_add_user_exceptions_catched(config_mock):
    config_mock.side_effect = Exception('Exception handling test')
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('adduser username'.split())
        args.func(args)
    assert 'Exception handling test' in exits.value.code


@patch('play.shell.pymongo')
@patch('play.shell._get_config')
def test_add_user_no_user_collection(config_mock, pymongo_mock):
    config_mock.return_value = {'MONGO_URI': 'mongodb_connection_string'}
    get_default_db = Mock(return_value=Mock(collection_names=Mock(return_value=['not_users'])))
    pymongo_mock.MongoClient.return_value = Mock(get_default_database=get_default_db)
    with raises(SystemExit) as exits:
        args = shell.parser.parse_args('adduser username'.split())
        args.func(args)
    assert 'Users collection does not exist' in exits.value.code
    config_mock.assert_called_once_with(shell.default_config_path)
    pymongo_mock.MongoClient.assert_called_once_with('mongodb_connection_string')
    assert get_default_db.call_count == 1
    assert get_default_db().collection_names.call_count == 1


@patch('play.shell.hash_password')
@patch('play.shell._get_password')
@patch('play.shell.pymongo')
@patch('play.shell._get_config')
def test_add_user_no_password_set(config_mock, pymongo_mock, password_mock, hash_password):
    config_mock.return_value = {'MONGO_URI': 'mongodb_connection_string'}
    get_default_db = Mock(return_value=Mock(collection_names=Mock(return_value=['users'])))
    pymongo_mock.MongoClient.return_value = Mock(get_default_database=get_default_db)
    password_mock.return_value = 'password'
    hash_password.return_value = 'hashed_password'
    args = shell.parser.parse_args('adduser username'.split())
    args.func(args)
    config_mock.assert_called_once_with(shell.default_config_path)
    pymongo_mock.MongoClient.assert_called_once_with('mongodb_connection_string')
    password_mock.assert_called_once_with()
    assert get_default_db.call_count == 1
    assert get_default_db().collection_names.call_count == 1
    hash_password.assert_called_once_with(password_mock())


@patch('play.shell.hash_password')
@patch('play.shell._get_password')
@patch('play.shell.pymongo')
@patch('play.shell._get_config')
def test_add_user_password_set(config_mock, pymongo_mock, password_mock, hash_password):
    config_mock.return_value = {'MONGO_URI': 'mongodb_connection_string'}
    get_default_db = Mock(return_value=Mock(collection_names=Mock(return_value=['users'])))
    pymongo_mock.MongoClient.return_value = Mock(get_default_database=get_default_db)
    password_mock.return_value = 'password'
    hash_password.return_value = 'hashed_password'

    args = shell.parser.parse_args('adduser username --password=password_with_argument'.split())
    args.func(args)
    config_mock.assert_called_once_with(shell.default_config_path)
    pymongo_mock.MongoClient.assert_called_once_with('mongodb_connection_string')
    assert password_mock.call_count == 0
    assert get_default_db.call_count == 1
    assert get_default_db().collection_names.call_count == 1
    hash_password.assert_called_once_with('password_with_argument')

    get_default_db().users.insert_one.assert_called_once_with(
        {'name': 'username', 'roles': ['admin'], 'password': 'hashed_password', 'active': True})


@patch('play.shell.hash_password')
@patch('play.shell._get_password')
@patch('play.shell.pymongo')
@patch('play.shell._get_config')
@mark.parametrize('parameter', [('--active', ('active', True)), ('--inactive', ('active', False)),
                                ('--roles admin user', ('roles', ['admin', 'user'])),
                                ('--roles', ('roles', []))])
def test_add_user_test_set_values(config_mock, pymongo_mock, password_mock, hash_password,
                                  parameter):
    argument, (test_key, test_value) = parameter
    config_mock.return_value = {'MONGO_URI': 'mongodb_connection_string'}
    get_default_db = Mock(return_value=Mock(collection_names=Mock(return_value=['users'])))
    pymongo_mock.MongoClient.return_value = Mock(get_default_database=get_default_db)
    password_mock.return_value = 'password'
    hash_password.return_value = 'hashed_password'

    args = shell.parser.parse_args(
        'adduser username {argument} '
        '--password=password_with_argument'.format(argument=argument).split())
    args.func(args)
    config_mock.assert_called_once_with(shell.default_config_path)

    pymongo_mock.MongoClient.assert_called_once_with('mongodb_connection_string')
    assert password_mock.call_count == 0
    assert get_default_db.call_count == 1
    assert get_default_db().collection_names.call_count == 1
    hash_password.assert_called_once_with('password_with_argument')
    default_user = {'name': 'username', 'roles': ['admin'], 'password': 'hashed_password',
                    'active': True, }
    default_user[test_key] = test_value
    get_default_db().users.insert_one.assert_called_once_with(default_user)


@patch('play.shell.getpass')
@patch('play.shell.sys')
def test_get_password_do_not_match(sys_mock, getpass_mock):
    getpass_mock.side_effect = ['a', 'b', 'c', 'c']

    password = shell._get_password()
    assert password == 'c'
    assert getpass_mock.call_count == 4


@patch('play.shell.getpass')
@patch('play.shell.sys')
def test_get_password_empty_password(sys_mock, getpass_mock):
    getpass_mock.side_effect = ['', '', 'c', 'c']

    password = shell._get_password()
    assert password == 'c'
    assert getpass_mock.call_count == 4


@patch('play.shell.BaseConfig')
def test_get_config_without_file(config_mock):
    config_mock.SOME_CONFIG_VALUE = 'value'
    config = shell._get_config(None)
    assert config['SOME_CONFIG_VALUE'] == 'value'


@patch('play.shell.BaseConfig')
def test_get_config_with_file_overwrite(config_mock, file_system):
    config_mock.SOME_CONFIG_VALUE = 'value'
    config_mock.OVERWRITE = 'value'
    os_mock = FakeOsModule(file_system)
    open_mock = FakeFileOpen(file_system)
    with patch('play.shell.os', os_mock), patch('flask.config.open', open_mock, create=True):
        config = shell._get_config('/tmp/open/config.cfg')
    assert config['SOME_CONFIG_VALUE'] == 'value'
    assert config['OVERWRITE'] == 'overwritten'
