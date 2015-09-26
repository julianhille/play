from unittest.mock import Mock, patch
from collections import OrderedDict
from pytest import mark


def _get_template_errors(template):
    return template.call_args_list[0][1]['form'].errors


def test_get_login_not_logged_in(testapp_admin):
    response = testapp_admin.get('/account/login')
    assert response.status_code == 200
    assert 'error' not in str(response.body)
    assert 'input' in str(response.body)


def test_post_login_login_without_csrf(testapp_admin):
    with patch('play.administration.account.render_template', Mock(return_value='')) as template:
        response = testapp_admin.post('/account/login', {'username': '12345', 'password': '12345'})
    assert response.status_code == 200
    assert _get_template_errors(template) == {'csrf_token': ['CSRF token missing']}


def test_post_wrong_login_with_csrf(testapp_admin):
    with patch('play.administration.account.render_template', Mock(return_value='')) as template:
        response = testapp_admin.post(
            '/account/login',
            OrderedDict([('csrf_token', 'sometoken'),
                         ('password', 'password'),
                         ('username', 'admin_active')]))
    assert response.status_code == 200
    assert _get_template_errors(template) == {'csrf_token': ['CSRF token missing']}


def test_post_correct_login_with_csrf(testapp_admin):
    with patch('flask.ext.wtf.form.validate_csrf', Mock(return_value=True)):
        response = testapp_admin.post(
            '/account/login', OrderedDict([('password', 'password'), ('username', 'admin_active')]))
    assert response.status_code == 302


@mark.parametrize('username_password', [('admin_active', 'password-wrong'),
                                        ('user_active', 'password'),
                                        ('user_not_existent', 'password')])
def test_post_wrong_login(testapp_admin, username_password):
    username, password = username_password
    with patch('play.administration.account.render_template', Mock(return_value='')) as template:
        with patch('flask.ext.wtf.form.validate_csrf', Mock(return_value=True)):
            response = testapp_admin.post(
                '/account/login', OrderedDict([('password', password), ('username', username)]))
    assert response.status_code == 200
    errors = _get_template_errors(template)

    assert 'username' in errors
    assert 'Username/password combination unknown' in errors['username']


def test_post_redirect_for_logged_in_user(testapp_admin):
    with patch('play.administration.account.current_user', Mock(is_authenticated=True)):
        response = testapp_admin.post(
            '/account/login',
            OrderedDict([('password', 'password'),
                         ('username', 'admin_active')]))
    assert response.status_code == 302


def test_get_redirect_for_logged_in_user(testapp_admin):
    with patch('play.administration.account.current_user', Mock(is_authenticated=True)):
        response = testapp_admin.get('/account/login')
    assert response.status_code == 302


def test_logout_not_logged_in_user(testapp_admin):
    response = testapp_admin.get('/account/logout')
    assert response.status_code == 302


def test_logout_logged_in(testapp_admin):
    with patch('flask.ext.wtf.form.validate_csrf', Mock(return_value=True)):
        response_login = testapp_admin.post(
            '/account/login', OrderedDict([('password', 'password'), ('username', 'admin_active')]))
    response_home = testapp_admin.post(
        '/account/login', OrderedDict([('password', 'password'), ('username', 'admin_active')]))
    assert response_home.headers['Set-Cookie'] == response_login.headers['Set-Cookie']
    response_logout = testapp_admin.get('/account/logout')
    assert response_logout.status_code == 302
    assert response_home.headers['Set-Cookie'] != response_logout.headers['Set-Cookie']
