from eve.render import render_json
from flask import abort, current_app, jsonify
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


@blueprint.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return render_json({'_id': str(current_user._id)})
    form = UserLoginForm()
    if form.validate_on_submit():
        user = LoginUser.get_by_name(current_app.data.driver.db.users, form.username.data, ['admin'])
        if user and user.authenticate(form.password.data):
            login_user(user)
            return render_json({'_id': str(current_user._id)})
        form.username.errors.append('Username/password combination unknown')
    errors = {}
    for field_name, field_errors in form.errors.items():
        errors[field_name] = field_errors

    abort(401, errors)


@blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return render_json({})
