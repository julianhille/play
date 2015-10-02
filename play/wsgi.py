from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from play.application.wsgi import application as backend
from play.static.wsgi import application as frontend


application = DispatcherMiddleware(frontend, {'/api': backend})


if __name__ == '__main__':  # nocov
    run_simple('localhost', 8000, application, use_reloader=True)
