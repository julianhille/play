from configparser import ConfigParser
from os import path
from uuid import uuid4

from bson import BSON
from flask.helpers import get_root_path
from kombu.serialization import register
from pymongo.uri_parser import parse_uri


class BaseConfig(object):
    SECRET_KEY = str(uuid4())
    WTF_CSRF_SECRET_KEY = str(uuid4())

    # INTERNAL SETTINGS
    _settings_file = path.join(get_root_path(__name__), 'settings.ini')

    def __init__(self):

        try:
            self.read()
        except:
            self.init()

    def read(self):
        parser = ConfigParser()
        parser.read(self._settings_file)
        items = [item for item in dir(BaseConfig) if item.isupper() and not item.startswith('_')]
        for item in items:
            setattr(self, item.upper(), parser.get('DEFAULT', item))

    def init(self):
        items = [item for item in dir(BaseConfig) if item.isupper() and not item.startswith('_')]
        parser = ConfigParser()
        for item in items:
            parser.set('DEFAULT', item, str(getattr(self, item)))
        with open(self._settings_file, 'w') as fh:
            parser.write(fh)


class Config(BaseConfig):

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
