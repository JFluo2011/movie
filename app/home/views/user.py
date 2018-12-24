from flask import url_for, flash, request, render_template
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.utils import redirect

from app.auth.forms import LoginForm, RegisterForm, ChangePasswordForm
from app.home import home
from app.models import User, UserLog


@home.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), User):
            return redirect(url_for('home.index', page=1))
        else:
            logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if (user is None) or not user.check_password(password):
            flash('账号密码不匹配', category='error')
        else:
            login_user(user, remember=True)
            user_log = UserLog()
            user_log.add()
            next_ = request.args.get('next')
            # not next_.startswith('/') 防止重定向攻击
            if (next_ is None) or (not next_.startswith('/')):
                next_ = url_for('home.index', page=1)

            return redirect(next_)

    return render_template('home/../../templates/auth/login.html', form=form)


@home.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('home.login'))


@home.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        msg, type_ = user.add(form)
        flash(msg, type_)
        return redirect(url_for('home.login'))

    return render_template('home/../../templates/auth/register.html', form=form)


@home.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        msg, type_ = current_user.change_password(form)
        flash(msg, type_)
        if type_ == 'error':
            return redirect(url_for('home.change_password'))
        return redirect(url_for('home.login'))
    return render_template('home/../../templates/auth/change_password.html', form=form)
