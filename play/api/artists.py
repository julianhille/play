from play.api.blueprint import Blueprint

SCHEMA = {
    'item_title': 'artist',
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': ['GET'],
    'allowed_roles': ['user'],
    'schema': {
        'genre': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'media': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'name': {
            'type': 'string'
        }
    }
}


blueprint = Blueprint('artists', __name__, SCHEMA)
