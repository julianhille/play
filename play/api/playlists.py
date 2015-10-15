from play.api.blueprint import Blueprint
from flask import abort
from flask.ext.login import current_user


SCHEMA = {
    'name': 'playlist',
    'public_item_methods': [],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'allowed_roles': ['user', 'admin'],
    'schema': {
        'name': {
            'type': 'string',
            'maxlength': 30,
            'required': True
        },
        'length': {
            'type': 'integer',
            'readonly': True,
        },
        'metadata': {
            'type': 'dict'
        },
        'owner': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'embeddable': True,
            },
            'readonly': True
        },
        'tracks': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'tracks',
                    'embeddable': True
                }
            }
        },
    }
}


blueprint = Blueprint('playlists', __name__, SCHEMA)


@blueprint.hook('on_pre_GET')
def ensure_public_or_owner_on_get(request, lookup):
    lookup['$or'] = [{'owner': current_user._id}, {'public': True}]


@blueprint.hook('on_insert')
def add_user_on_create(items):
    for item in items:
        item['owner'] = current_user._id
        item.setdefault('tracks', [])


@blueprint.hook('on_replace')
def ensure_user_is_owner_on_replace(item, original):
    if current_user._id != original['owner']:
        abort(403)
    item['owner'] = current_user._id


@blueprint.hook('on_update')
def ensure_user_is_owner_on_update(updates, original):
    if current_user._id != original['owner']:
        abort(403)
    updates['owner'] = current_user._id
