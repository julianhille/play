from webtest import TestApp, AppError
from pytest import raises

from play.wsgi import application


def test_multiapp_dispatching():

    app = TestApp(application)
    response_index = app.get('/')
    assert response_index.status_code == 200

    response_static = app.get('/static/css/bootstrap.css')
    assert response_static.status_code == 200

    with raises(AppError) as response_api:
        app.get('/api/users/')
    assert '405 METHOD NOT ALLOWED' in str(response_api.value)
