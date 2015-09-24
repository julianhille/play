from play.application.application import Application
from play.application import albums, artists, directories, playlists, tracks

settings = {
    'DOMAIN': {
    }
}


def application():
    app = Application(settings=settings)
    app.register_blueprint(albums.blueprint)
    app.register_blueprint(artists.blueprint)
    app.register_blueprint(directories.blueprint)
    app.register_blueprint(playlists.blueprint)
    app.register_blueprint(tracks.blueprint)
    return app.instantiate()


if __name__ == '__main__':
    application().run(debug=True)
