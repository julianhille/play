from flask.ext.login import current_user
from play.application.blueprint import Blueprint


SCHEMA = {
    'item_title': 'user',
    'public_item_methods': [],
    'item_methods': ['GET', 'DELETE', 'PATCH'],
    'resource_methods': ['GET', 'POST'],
    'allowed_item_read_roles': ['user', 'admin'],
    'allowed_item_write_roles': ['admin'],
    'allowed_roles': ['admin'],
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
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
