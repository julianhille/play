from play.models.users import LoginUser
from eve.auth import BasicAuth
from flask import current_app


class RolesAuth(BasicAuth):

    def check_auth(self, username, password, allowed_roles, resource, method):
        # use Eve's own db driver; no additional connections/resources are used
        user_db = current_app.data.driver.db['users']

        user = LoginUser.get_by_name(user_db, username, allowed_roles)
        if user and user.is_active and user.authenticate(password):
            current_app.user = user.user
            return True
