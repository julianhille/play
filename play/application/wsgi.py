from play.application.application import Application
from play.application import tracks, playlists

settings = {
    'DOMAIN': {
    }
}


def application():
    app = Application(settings=settings)
    app.register_blueprint(tracks.blueprint)
    app.register_blueprint(playlists.blueprint)
    return app.instantiate()


if __name__ == '__main__':
    application().run(debug=True)
