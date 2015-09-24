from play.application.blueprint import Blueprint

SCHEMA = {
    'item_title': 'user',
    'datasource': {
        'filter': {'active': True, 'roles': {'$in': ['user']}}
    },
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': [],
    'allowed_roles': ['user'],
    'schema': {
        'name': {
            'type': 'string'
        }
    }
}


blueprint = Blueprint('users', __name__, SCHEMA)
