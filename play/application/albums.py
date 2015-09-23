from play.application.blueprint import Blueprint

SCHEMA = {
    'item_title': 'album',
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': ['GET'],
    'allowed_roles': ['user'],
    'schema': {
        'artist': {
            'type': 'objectid'
        },
        'length': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'tracks': {
            'type': 'list',
            'schema': {
                'type': 'objectid'
            }
        },
        'year': {
            'type': 'integer'
        }
    }
}


blueprint = Blueprint('albums', __name__, SCHEMA)
