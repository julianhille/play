from uuid import uuid4

from bson import BSON
from kombu.serialization import register
from pymongo.uri_parser import parse_uri


class Config(object):
    # This should be configured
    SECRET_KEY = str(uuid4())
    WTF_CSRF_SECRET_KEY = str(uuid4())
    MONGO_URI = 'mongodb://localhost:27017/play'

    # CELERY / KOMBU SETTINGS
    CELERY_TIMEZONE = 'Europe/London'
    CELERY_ENABLE_UTC = True
    CELERY_IGNORE_RESULT = True
    CELERY_ACCEPT_CONTENT = ['bson']
    CELERY_TASK_SERIALIZER = 'bson'
    CELERY_RESULT_SERIALIZER = 'bson'

    # WTF SETTINGS
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token', 'X-XSRFToken', 'X-XSRF-Token']
    WTF_CSRF_TIME_LIMIT = None

    # EVE SETTINGS
    PAGINATION_LIMIT = 300

    def __init__(self):
        super().__init__()
        # Register bson serializer methods into kombu
        register('bson', BSON.encode, BSON.decode,
                 content_type='application/bson',
                 content_encoding='utf-8')

    @property
    def BROKER_URL(self):
        return self.MONGO_URI

    @property
    def CELERY_RESULT_BACKEND(self):
        return self.MONGO_URI

    @property
    def CELERY_MONGODB_BACKEND_SETTINGS(self):
        return {'database': parse_uri(self.MONGO_URI)['database']}


config = Config()
