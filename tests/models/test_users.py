from unittest.mock import patch
from play.models.users import get_user, hash_password, LoginUser
from bcrypt import hashpw, gensalt


def test_has_roles():
    user = LoginUser({'_id': '12', 'roles': ['role1']})
    assert user.has_role(['role1'])
    assert not user.has_role(['role2'])
    assert user.has_role([])


def test_active():
    user = LoginUser({'_id': '12', 'active': True})
    assert user.is_active

    user = LoginUser({'_id': '12', 'active': False})
    assert not user.is_active


def test_get_id():
    user = LoginUser({'_id': 12})
    assert user.get_id() == '12'


def test_get(humongous):
    assert not get_user(humongous, 'Not AT Object Id')


def test_authenticate():
    user = LoginUser(
        {'_id': 123,
         'password': hashpw('123'.encode('UTF-8'), gensalt()).decode('UTF-8')})
    assert user.authenticate('123')
    assert not user.authenticate('1234')


def test_get_attr():
    user = LoginUser({'_id': 123, 'something': 'test'})
    assert user.none is None
    assert user._id == 123
    assert user.something == 'test'


@patch('play.models.users.gensalt')
@patch('play.models.users.hashpw')
def test_hash_pw(hashpw, gensalt):
    gensalt.return_value = 'some salt'
    hash_password('password')
    hashpw.assert_called_once_with(b'password', 'some salt')
    gensalt.assert_called_once_with()
