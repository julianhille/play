from play import lock
from pytest import raises
from bson import ObjectId


def test_lock_exception(mongodb):
    with lock.lock(mongodb.directories, 'ddff19b92e21e1560a7dd000'):
        with raises(lock.LockException) as context:
            with lock.lock(mongodb.directories, 'ddff19b92e21e1560a7dd000'):
                pass
        assert 'ddff19b92e21e1560a7dd000' in str(context.value)


def test_lock(mongodb):
    directory_id = ObjectId('ddff19b92e21e1560a7dd000')
    assert '_lock' not in mongodb.directories.find_one({'_id': directory_id}), \
        'There should be no lock'
    with lock.lock(mongodb.directories, directory_id):
        assert '_lock' in mongodb.directories.find_one({'_id': directory_id}), \
            'Lock should be set'
    assert '_lock' not in mongodb.directories.find_one({'_id': directory_id}), \
        'Lock should be released'
