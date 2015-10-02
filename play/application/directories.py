from play.application.blueprint import Blueprint

SCHEMA = {
    'item_title': 'directory',
    'public_item_methods': [],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'allowed_read_roles': ['user', 'admin'],
    'allowed_write_roles': ['admin'],
    'allowed_item_read_roles': ['user', 'admin'],
    'allowed_item_write_roles': ['admin'],
    'schema': {
        'parent': {
            'type': 'objectid',
            'required': True,
            'nullable': True,
            'data_relation': {
                'resource': 'directories',
                'embeddable': True
            },
        },
        'path': {
            'type': 'string',
            'required': True,
            'roles': ['admin']
        },
        'name': {
            'type': 'string',
            'readonly': True
        }
    }
}


blueprint = Blueprint('directories', __name__, SCHEMA)
