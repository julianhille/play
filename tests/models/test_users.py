from play.models.users import LoginUser


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
