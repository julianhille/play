from play.application.application import Application
from play.application import albums, artists, directories, playlists, tracks, users

settings = {
    'DOMAIN': {
    }
}


def _application():
    app = Application(settings=settings)
    app.register_blueprint(albums.blueprint)
    app.register_blueprint(artists.blueprint)
    app.register_blueprint(directories.blueprint)
    app.register_blueprint(playlists.blueprint)
    app.register_blueprint(tracks.blueprint)
    app.register_blueprint(users.blueprint)
    app = app.instantiate(static_url_path='/static')
    return app


application = _application()

if __name__ == '__main__':
    application.run(debug=True)
