from flask import Flask, send_from_directory
from play.utils import add_logging

application = Flask(__name__, static_folder='../static_files', static_url_path='/static')
add_logging(application)


@application.route('/')
def index():
    return send_from_directory(application.static_folder, 'index.html')


@application.route('/admin')
def admin():
    return send_from_directory(application.static_folder, 'admin.html')


if __name__ == '__main__':  # nocov
    application.run(debug=True, port=8001)
