from flask import Flask, render_template, current_app
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager, login_required
from eve.flaskapp import RegexConverter

from play.administration import account
from play.administration import directories
from play.models.users import LoginUser


def _user_loader(user_id):
    return LoginUser.get(current_app.mongo.db.users, user_id)


def create_app():
    app = Flask(__name__)
    app.url_map.converters['regex'] = RegexConverter
    app.register_blueprint(account.blueprint)
    app.register_blueprint(directories.blueprint)
    # TODO: get this config from a real config file
    app.config.update(
        {'MONGO_DBNAME': 'humongous', 'WTF_CSRF_SECRET_KEY': 'abcabc', 'SECRET_KEY': '123'})
    mongo = PyMongo(app)
    app.mongo = mongo

    login = LoginManager()
    login.init_app(app)
    login.login_view = 'account.login'
    login.user_loader(_user_loader)

    return app


application = create_app()


@application.route('/', methods=['GET'])
@login_required
def home():
    return render_template('index.html')


if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0", port=8080)
