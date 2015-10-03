from eve.render import render_json
from flask import current_app, Response
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect, generate_csrf

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
    CsrfProtect(app)
    login = LoginManager()
    login.init_app(app)
    login.user_loader(_user_loader)
    return app


application = create_app()


@application.route('/csrf', methods=['GET'])
def csrf():
    csrf = generate_csrf()
    response = Response(render_json({'csrf': csrf}), mimetype='application/json')
    response.set_cookie('XSRF-TOKEN', csrf)
    return response

if __name__ == '__main__':  # nocov
    application.run(debug=True, port=8002)
