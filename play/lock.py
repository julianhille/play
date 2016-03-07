from contextlib import contextmanager
from uuid import uuid4
from datetime import datetime, timedelta

from bson import ObjectId


@contextmanager
def lock(collection, id_):
    lock_id = uuid4()
    try:
        lock_ = collection.find_and_modify(
            query={'_id': ObjectId(id_), '$or': [
                {'_lock.id': {'$exists': False}},
                {'_lock.date': {'$lt': datetime.utcnow()}}]},
            update={'$set': {'_lock.id': lock_id, 'date': datetime.utcnow() + timedelta(1)}},
            fields={'_lock.id': 1},
            upsert=False,
            new=True
        )
        if lock_ and lock_['_lock']['id'] == lock_id:
            yield lock_id
        else:
            raise LockException('Lock could not acquire for item with id {}'.format(id_))
    finally:
        collection.update({'_id': id_, '_lock.id': lock_id}, {'$unset': {'_lock': ''}})


def release_all_locks(collection):
    collection.update({'$exists': {'_lock': True}}, {'$unset': {'_lock': 1}}, multi=True)


class LockException(Exception):  # nocov
    pass
