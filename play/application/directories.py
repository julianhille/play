from play.application.blueprint import Blueprint
from play.task.application import directory_scan

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
        'parents': {
            'type': 'list',
            'readonly': True,
            'schema': {
                'type': 'objectid',
                'required': True,
                'nullable': True,
                'data_relation': {
                    'resource': 'directories',
                    'embeddable': True
                },
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


@blueprint.hook('on_inserted')
def ensure_scan_on_insert(documents):
    for document in documents:
        directory_scan.delay(document['path'])


@blueprint.hook('on_replaced')
@blueprint.hook('on_updated')
def ensure_scan_on_update(update, original=None):
    if 'path' in update and update['path'] != original['path']:
        directory_scan.delay(update['path'])
