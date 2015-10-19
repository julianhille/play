from play.api.blueprint import Blueprint

SCHEMA = {
    'datasource': {
        'default_sort': [('name', 1)]
    },
    'item_title': 'artist',
    'public_item_methods': [],
    'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'allowed_write_roles': ['admin'],
    'allowed_read_roles': ['admin', 'user'],
    'allowed_item_write_roles': ['admin'],
    'allowed_item_read_roles': ['admin', 'user'],
    'schema': {
        'discogs_id': {
            'type': 'integer',
            'nullable': True
        },
        'name': {
            'type': 'string',
            'required': True,
            'nullable': False,
            'empty': False
        },
        'profile': {
            'type': 'string',
            'nullable': True,
        },
        'realname': {
            'type': 'string',
            'nullable': True
        },
        'namevariations': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'aliases': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        }
    }
}


blueprint = Blueprint('artists', __name__, SCHEMA)
