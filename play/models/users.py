from bcrypt import hashpw, gensalt
from bson.objectid import InvalidId, ObjectId
from flask_wtf import Form
from flask.ext.login import UserMixin
from hmac import compare_digest
from wtforms import validators, fields


def hash_password(password):
    password = password.encode('UTF-8')
    return hashpw(password, gensalt()).decode('UTF-8')


def get_user_by_name(db, username, allowed_roles=None):
    lookup = {'name': username}
    if allowed_roles:
        lookup['roles'] = {'$in': allowed_roles}
    user = db.find_one(lookup)
    return LoginUser(user) if user else None


def get_user(db, user_id):
    try:
        user = db.find_one({'_id': ObjectId(user_id)})
    except (InvalidId, TypeError):
        return False
    return LoginUser(user) if user else None


class LoginUser(UserMixin):

    def __init__(self, user):
        self.user = user
        self.user['_id'] = self.user['_id']

    @property
    def is_active(self):
        return self.user['active']

    @property
    def is_authenticated(self):
        return True

    def authenticate(self, password):
        password = password.encode('UTF-8')
        current_password = self.user['password'].encode('UTF-8')
        if compare_digest(hashpw(password, current_password), current_password):
            return True
        return False

    def get_id(self):
        return str(self.user['_id'])

    def has_role(self, roles):
        if not roles:
            return True

        return bool(set(self.roles).intersection(roles))

    def __getattr__(self, item):
        if item in self.user:
            return self.user[item]


class UserLoginForm(Form):
    username = fields.StringField('Login name', [validators.Length(min=5, max=255)])
    password = fields.PasswordField('Password', [validators.Length(min=5, max=255)])
    remember = fields.BooleanField('Remember', false_values=[None, 0, '0', False], default=False)
