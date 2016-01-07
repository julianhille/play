from flask import current_app
from flask.ext.login import current_user
from play.api.blueprint import Blueprint
from play.models.users import hash_password

SCHEMA = {
    'item_title': 'user',
    'public_item_methods': [],
    'item_methods': ['GET', 'DELETE', 'PATCH', 'PUT'],
    'resource_methods': ['GET', 'POST'],
    'allowed_item_read_roles': ['user', 'admin'],
    'allowed_item_write_roles': ['admin'],
    'allowed_roles': ['admin'],
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 3,
            'maxlength': 30
        },
        'roles': {
            'type': 'list',
            'schema': {
                'type': 'string'
            },
            'required': True,
            'roles': ['admin']
        },
        'active': {
            'type': 'boolean',
            'required': True,
            'roles': ['admin']
        },
        'password': {
            'type': 'string',
            'roles': ['admin'],
            'minlength': 7,
            'maxlength': 200,
            'required': True,
        }
    }
}


blueprint = Blueprint('users', __name__, SCHEMA, url_prefix='/users')


@blueprint.hook('on_pre_GET')
def add_search(request, lookup):
    if lookup and not current_user.has_role(['admin']):
        lookup.update({'active': True, 'roles': {'$in': ['user']}})


@blueprint.hook('on_fetched_resource')
def remove_password_from_resource(response):
    for item in response['_items']:
        item.pop('password', None)


@blueprint.hook('on_fetched_item')
def remove_password_from_item(response):
    response.pop('password', None)


@blueprint.hook('on_deleted_item')
def ensure_deleted_playlists(original):
    current_app.data.driver.db.playlists.remove({'owner': original['_id']})


@blueprint.hook('on_insert')
def on_insert_update_password(items):
    for item in items:
        item['password'] = hash_password(item['password'])


@blueprint.hook('on_replace')
def on_replace_update_password(item, original):
    item['password'] = hash_password(item['password'])


@blueprint.hook('on_update')
def on_update_update_password(updates, original):
    if 'password' in updates:
        updates['password'] = hash_password(updates['password'])
