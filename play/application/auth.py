from eve.auth import TokenAuth
from flask import abort
from flask.ext.login import current_user


class SessionAuth(TokenAuth):
    """ Implements Session AUTH logic.

    .. versionadded:: 0.0.1
    """
    def authenticate(self):
        """ Returns a standard a 401 response that enables basic auth.
        Override if you want to change the response and/or the realm.
        """
        abort(401, description='Please provide proper credentials')

    def authorized(self, allowed_roles, resource, method):
        """ Validates the the current request is allowed to pass through.

        :param allowed_roles: allowed roles for the current request, can be a
                              string or a list of roles.
        :param resource: resource being requested.
        """
        if current_user and current_user.is_authenticated:
            if not allowed_roles:
                return True
            return set(current_user.roles) & set(allowed_roles)
