from eve import Eve

from play.application.auth import RolesAuth


class Application(object):

    def __init__(self, settings=None):
        self.settings = settings or {}
        if 'DOMAIN' not in self.settings:
            self.settings['DOMAIN'] = {}
        self._blueprints = []

    def instantiate(self, *args, **kwargs):
        app = Eve(settings=self.settings, auth=RolesAuth, **kwargs)
        for blueprint in self._blueprints:
            for event, function in blueprint.events.__dict__.items():
                if event.startswith('on_'):
                    setattr(app, '{}_{}'.format(event, blueprint.name), function)
            app.register_blueprint(blueprint)
        return app

    def register_blueprint(self, blueprint):
        self._blueprints.append(blueprint)
        self.settings['DOMAIN'][blueprint.name] = blueprint.domain
