from bcrypt import hashpw
from eve.auth import BasicAuth
from flask import current_app
from hmac import compare_digest


class RolesAuth(BasicAuth):

    def check_auth(self, username, password, allowed_roles, resource, method):
        # use Eve's own db driver; no additional connections/resources are used
        users = current_app.data.driver.db['users']
        lookup = {'name': username, 'active': True}
        if allowed_roles:
            # only retrieve a user if his roles match ``allowed_roles``
            lookup['roles'] = {'$in': allowed_roles}
        user = users.find_one(lookup)
        if not user:
            return False
        password = password.encode('UTF-8')
        current_password = user['password'].encode('UTF-8')
        if user and compare_digest(hashpw(password, current_password), current_password):
            current_app.user = user
            return True
