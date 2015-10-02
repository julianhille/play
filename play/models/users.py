from bcrypt import hashpw
from bson.objectid import InvalidId, ObjectId
from flask_wtf import Form
from flask.ext.login import UserMixin
from hmac import compare_digest
from wtforms import validators, fields


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

        return set(self.roles).intersection(roles)

    @staticmethod
    def get_by_name(db, username, allowed_roles=None):
        lookup = {'name': username}
        if allowed_roles:
            lookup['roles'] = {'$in': allowed_roles}
        user = db.find_one(lookup)
        return LoginUser(user) if user else None

    def __getattr__(self, item):
        if item in self.user:
            return self.user[item]

    @staticmethod
    def get(db, user_id):
        try:
            user = db.find_one({'_id': ObjectId(user_id)})
        except (InvalidId, TypeError):
            return False
        return LoginUser(user) if user else None


class UserLoginForm(Form):
    username = fields.StringField('Login name', [validators.Length(min=5, max=255)])
    password = fields.PasswordField('Password', [validators.Length(min=5, max=255)])
    remember = fields.BooleanField('Remember', false_values=[None, 0, '0', False], default=False)
