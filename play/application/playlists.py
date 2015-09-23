from play.application.blueprint import Blueprint
from flask import current_app, abort


SCHEMA = {
    'name': 'playlist',
    'public_item_methods': [],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'allowed_roles': ['admin'],
    'allowed_item_read_roles': ['admin', 'user'],
    'allowed_item_write_roles': ['admin', 'user'],
    'schema': {
        'name': {
            'type': 'string',
            'maxlength': 30,
            'required': True
        },
        'metadata': {
            'type': 'dict'
        },
        'length': {
            'type': 'integer'
        },
        'owner': {
            'type': 'objectid',
            #  'embeddable': True,
            'readonly': True
        }
    }
}


blueprint = Blueprint('playlists', __name__, SCHEMA)


@blueprint.hook('on_pre_GET')
def ensure_public_or_owner_on_get(request, lookup):
    lookup['$or'] = [{'owner': current_app.user['_id']}, {'public': True}]


@blueprint.hook('on_insert')
def add_user_on_create(items):
    for item in items:
        item['owner'] = current_app.user['_id']


@blueprint.hook('on_replace')
def ensure_user_is_owner_on_replace(item, original):
    if current_app.user['_id'] != original['owner']:
        abort(403)
    item['owner'] = current_app.user['_id']


@blueprint.hook('on_update')
def ensure_user_is_owner_on_update(updates, original):
    if current_app.user['_id'] != original['owner']:
        abort(403)
