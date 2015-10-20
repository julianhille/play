from flask import Flask, send_from_directory


def create_application():
    return Flask(__name__, static_folder='static', static_url_path='/static')


application = create_application()


@application.route('/')
def index():
    return send_from_directory(application.static_folder, 'index.html')


@application.route('/admin')
def admin():
    return send_from_directory(application.static_folder, 'admin.html')


if __name__ == '__main__':  # nocov
    application.run(debug=True, port=8001)
