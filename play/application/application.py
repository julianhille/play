from eve import Eve
from flask import Config
from flask.helpers import get_root_path
from play.application.auth import SessionAuth


class Application(object):

    def __init__(self, settings=None):

        self.settings = Config(get_root_path(__name__))
        self.settings.from_object('play.task.default_settings')
        if 'DOMAIN' not in self.settings:
            self.settings['DOMAIN'] = {}
        self._blueprints = []

    def instantiate(self, *args, **kwargs):
        app = Eve(__name__, settings=dict(self.settings), auth=SessionAuth, **kwargs)

        for blueprint in self._blueprints:
            for event, function in blueprint.events.__dict__.items():
                if event.startswith('on_'):
                    setattr(app, '{}_{}'.format(event, blueprint.name), function)
            app.register_blueprint(blueprint)
        return app

    def register_blueprint(self, blueprint):
        self._blueprints.append(blueprint)
        self.settings['DOMAIN'][blueprint.name] = blueprint.domain
