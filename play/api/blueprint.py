from events import Events
import flask


class Blueprint(flask.Blueprint):

    def __init__(self, name, import_name, domain=None, **kwargs):
        super().__init__(name, import_name, **kwargs)
        self.domain = domain
        self.events = Events()

    def hook(self, event):
        def decorator(function):
            e = getattr(self.events, event)
            e += function
            return function
        return decorator
