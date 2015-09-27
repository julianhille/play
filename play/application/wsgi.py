from flask import current_app
from flask.ext.login import LoginManager

from play.application.application import Application
from play.application import albums, artists, directories, playlists, tracks, users
from play.models.users import LoginUser

settings = {
    'DOMAIN': {
    }
}


def _user_loader(user_id):
    return LoginUser.get(current_app.driver.db['users'], user_id)


def create_app():
    app = Application(settings=settings)
    app.register_blueprint(albums.blueprint)
    app.register_blueprint(artists.blueprint)
    app.register_blueprint(directories.blueprint)
    app.register_blueprint(playlists.blueprint)
    app.register_blueprint(tracks.blueprint)
    app.register_blueprint(users.blueprint)
    app = app.instantiate()

    login = LoginManager()
    login.init_app(app)
    login.user_loader(_user_loader)
    return app


application = create_app()

if __name__ == '__main__':
    application.run(debug=True, port=8002)
