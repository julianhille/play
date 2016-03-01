from uuid import uuid4

from pymongo.uri_parser import parse_uri
from flask import Config
from flask.helpers import get_root_path

from kombu import Exchange, Queue


class DefaultConfig(object):
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
    CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
    CELERY_DEFAULT_EXCHANGE = 'play'
    CELERY_DEFAULT_ROUTING_KEY = 'play.directory.*'
    CELERY_DEFAULT_QUEUE = 'play.directory'

    CELERY_ROUTES = {
        'play.task.application.directory_scan':
            {'queue': 'play.directory', 'exchange': 'play', 'routing_key': 'play.directory.*'},
        'play.task.application.audio_scan':
            {'queue': 'play.directory', 'exchange': 'play', 'routing_key': 'play.directory.*'}}
    CELERY_QUEUES = (Queue('play.directory',
                           routing_key='play.directory.*',
                           exchange=Exchange('play', type='topic')),)

    # WTF SETTINGS
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token', 'X-XSRFToken', 'X-XSRF-Token']
    WTF_CSRF_TIME_LIMIT = None

    # EVE SETTINGS
    PAGINATION_LIMIT = 300


config = Config(get_root_path(__name__))
config.from_object(DefaultConfig)
config.from_envvar('PLAY_CONFIGURATION', silent=True)
config['BROKER_URL'] = config['MONGO_URI']
config['CELERY_RESULT_BACKEND'] = config['MONGO_URI']
config['CELERY_MONGODB_BACKEND_SETTINGS'] = {
    'database': parse_uri(config['MONGO_URI'])['database']}
