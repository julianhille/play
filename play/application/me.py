from eve.methods import getitem, patch
from eve.auth import requires_auth
from eve.render import send_response

from flask import abort, current_app, request, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user
from flask.ext.wtf.csrf import generate_csrf

from play.application.blueprint import Blueprint
from play.models.users import UserLoginForm, LoginUser

SCHEMA = {
    'item_title': 'me',
    'datasource': {
        'source': 'users',
        'projection': {
            'name': 1,
            'last_login': 1
        }
    },
    'public_methods': ['POST'],
    'item_methods': ['GET', 'PATCH'],
    'resource_methods': ['POST'],
    'allowed_roles': ['user'],
    'schema': {
        'name': {
            'unique': True,
            'type': 'string',
            'minlength': 5,
            'maxlength': 12,
            'required': True
        },
        'last_login': {
            'type': 'datetime'
        },
        'password': {
            'type': 'string',
            'minlength': 6,
            'required': True
        }
    }
}


blueprint = Blueprint('me', __name__, SCHEMA, url_prefix='/me')


@blueprint.after_request
def add_csrf_token(response):
    print(request.headers, request.cookies)
    if not request.cookies.get('XSRF-TOKEN'):
        response.set_cookie('XSRF-TOKEN', generate_csrf())
    return response


@blueprint.hook('on_insert')
def ensure_password_encoding(documents):
    if current_user.is_authenticated:
        abort(400, 'already registered')
    if len(documents) > 1:
        abort(400, 'no bulk insertion is allowed')
    for document in documents:
        document['password'] = LoginUser.hash_password(document['password'])
        document['active'] = False
        document['roles'] = ['user']


@blueprint.route('', methods=['GET', 'PATCH'])
@requires_auth('me')
def home():
    lookup = {'_id': current_user._id}
    if request.method == 'GET':
        response, last_modified, etag, code = getitem('me', lookup)
    elif request.method == 'PATCH':
        response, last_modified, etag, code = patch('me', lookup)
    if '_links' in response:
        response['_links']['self']['href'] = url_for('me.home')
    response.pop('password', None)
    return send_response('me', (response, last_modified, etag, code))


@blueprint.hook('on_update')
def replace_password(document, original):
    if 'password' in document:
        document['password'] = LoginUser.hash_password(document['password'])


@blueprint.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        abort(409, 'user already logged in')
    form = UserLoginForm()
    if form.validate_on_submit():
        user = LoginUser.get_by_name(
            current_app.data.driver.db.users, form.username.data)
        if user and user.authenticate(form.password.data) and login_user(user):
            return redirect(url_for('me.home'))
        form.username.errors.append('Username/password combination unknown')
    errors = {}
    for field_name, field_errors in form.errors.items():
        errors[field_name] = field_errors

    abort(401, errors)


@blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return '', 204
