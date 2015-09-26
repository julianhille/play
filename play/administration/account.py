from flask import Blueprint, current_app, redirect, render_template, url_for
from flask.ext.login import current_user, login_user, logout_user

from play.models.users import LoginUser, UserLoginForm

blueprint = Blueprint('account', __name__, url_prefix='/account')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(next or url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        user = LoginUser.get_by_name(current_app.mongo.db.users, form.username.data, ['admin'])
        if user and user.authenticate(form.password.data):
            login_user(user)
            return redirect(next or url_for('home'))
        form.username.errors.append('Username/password combination unknown')
    return render_template('account/login.html', form=form)


@blueprint.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('account.login')) # TODO(add home)
