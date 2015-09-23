from play.application.blueprint import Blueprint

SCHEMA = {
    'item_title': 'track',
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': ['GET'],
    'allowed_roles': ['admin'],
    'allowed_item_read_roles': ['admin', 'user'],
    'allowed_item_write_roles': ['admin'],
    'schema': {
        'metadata': {
            'type': 'dict'
        },
        'length': {
            'type': 'integer'
        }
    }
}


blueprint = Blueprint('tracks', __name__, SCHEMA)
