from flask import current_app
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect

from play.api.application import Application
from play.api import albums, artists, csrf, directories, me, playlists, tracks, users
from play.models.users import get_user

settings = {
    'DOMAIN': {
    }
}


def _user_loader(user_id):
    return get_user(current_app.data.driver.db['users'], user_id)


def create_app():
    app = Application(settings=settings)
    app.register_blueprint(albums.blueprint)
    app.register_blueprint(artists.blueprint)
    app.register_blueprint(directories.blueprint)
    app.register_blueprint(me.blueprint)
    app.register_blueprint(playlists.blueprint)
    app.register_blueprint(tracks.blueprint)
    app.register_blueprint(users.blueprint)
    app = app.instantiate()
    app.register_blueprint(csrf.blueprint)

    CsrfProtect(app)
    login = LoginManager()
    login.init_app(app)
    login.user_loader(_user_loader)

    return app


if __name__ == '__main__':  # nocov
    create_app().run(debug=True, port=8002)
