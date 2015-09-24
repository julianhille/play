from play.application.blueprint import Blueprint

SCHEMA = {
    'item_title': 'directory',
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': ['GET'],
    'allowed_roles': ['user'],
    'schema': {
        'parent': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'directories',
                'embeddable': True
            },
        },
        'name': {
            'type': 'string'
        }
    }
}


blueprint = Blueprint('directories', __name__, SCHEMA)
