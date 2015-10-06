from eve.render import render_json
from flask import abort, current_app
from flask.ext.login import current_user, login_user, logout_user

from play.application.blueprint import Blueprint
from play.models.users import UserLoginForm, LoginUser

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


blueprint = Blueprint('users', __name__, SCHEMA, url_prefix='/users')