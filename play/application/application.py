from eve import Eve
from eve.io import mongo
from eve.utils import config
from flask import Config
from flask.helpers import get_root_path
from flask.ext.login import current_user

from play.application import default_settings
from play.application.auth import SessionAuth


class Validator(mongo.Validator):

    def _validate_roles(self, roles, field, value):
        if not isinstance(roles, list):
            self._error(field, "Schema error '%s' must be a list" % field)


class Mongo(mongo.Mongo):

    def _datasource_ex(self, resource, query=None, client_projection=None,
                       client_sort=None):
        datasource, query, fields, sort = super()._datasource_ex(
            resource, query=query, client_projection=client_projection, client_sort=client_sort)
        if fields:
            excludes = 0 in fields.values()
            for field_name, schema_field in config.DOMAIN[resource]['schema'].items():
                if 'roles' in schema_field and not current_user.has_role(schema_field['roles']):
                    if excludes:
                        fields[field_name] = 0
                    else:
                        for field in dict(fields):
                            if field.split('.')[0] == field_name:
                                fields.pop(field)

        return datasource, query, fields, sort


class Application(object):

    def __init__(self, settings=None):
        self.settings = Config(get_root_path(__name__))
        self.settings.from_object(default_settings)
        if 'DOMAIN' not in self.settings:
            self.settings['DOMAIN'] = {}
        self._blueprints = []

    def instantiate(self, *args, **kwargs):
        app = Eve(__name__, data=Mongo, validator=Validator, settings=dict(self.settings),
                  auth=SessionAuth, **kwargs)

        for blueprint in self._blueprints:
            for event, function in blueprint.events.__dict__.items():
                if event.startswith('on_'):
                    setattr(app, '{}_{}'.format(event, blueprint.name), function)
            app.register_blueprint(blueprint)
        return app

    def register_blueprint(self, blueprint):
        self._blueprints.append(blueprint)
        self.settings['DOMAIN'][blueprint.name] = blueprint.domain
