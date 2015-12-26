from bson import BSON
from kombu.serialization import register

_DB = 'play'

MONGO_URI = 'mongodb://127.0.0.1:27017/{}'.format(_DB)
WTF_CSRF_SECRET_KEY = 'abcabcabcabc'
WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token', 'X-XSRFToken', 'X-XSRF-Token']
WTF_CSRF_TIME_LIMIT = None
SECRET_KEY = 'sdklfjoi4o2ij34foi23j'

CELERY_TIMEZONE = 'Europe/London'
CELERY_ENABLE_UTC = True
BROKER_URL = MONGO_URI
CELERY_IGNORE_RESULT = True
CELERY_RESULT_BACKEND = MONGO_URI
CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': _DB
}

PAGINATION_LIMIT = 300

# Register bson serializer methods into kombu
register('bson', BSON.encode, BSON.decode,
         content_type='application/bson',
         content_encoding='utf-8')

CELERY_ACCEPT_CONTENT = ['bson']
CELERY_TASK_SERIALIZER = 'bson'
CELERY_RESULT_SERIALIZER = 'bson'
