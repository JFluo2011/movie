from flask import url_for, redirect, flash, request, render_template, current_app
from flask_login import current_user, logout_user, login_user, login_required

from . import auth
from .forms import LoginForm, RegisterForm, ChangePasswordForm, AdminForm
from app.models import AdminLog, User, UserLog
from ..libs.enums import AuthEnum
from ..libs.permissions import admin_required, user_admin_required, super_admin_required


def _login(user):
    login_user(user, remember=True)
    if (user.auth == AuthEnum.Admin) or (user.auth == AuthEnum.SuperAdmin):
        log = AdminLog()
    else:
        log = UserLog()
    log.add()
    next_ = request.args.get('next')
    # not next_.startswith('/') 防止重定向攻击
    if (next_ is None) or (not next_.startswith('/')):
        if (user.auth == AuthEnum.Admin) or (user.auth == AuthEnum.SuperAdmin):
            next_ = url_for('admin.index')
        else:
            next_ = url_for('home.index')
    return next_


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if (user is None) or not user.check_password(password):
            flash('账号密码不匹配', category='error')
        else:
            next_ = _login(user)
            return redirect(next_)

    return render_template('auth/login.html', form=form)


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        msg, type_ = user.add(form)
        flash(msg, type_)
        if type_ == 'error':
            return redirect(url_for('auth.register'))
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        msg, type_ = current_user.change_password(form)
        flash(msg, type_)
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/admin/user/list/<int:page>')
@login_required
@admin_required
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/user_list.html', page_data=page_data)


@auth.route('/admin/user/view/<int:uid>')
@login_required
@admin_required
def user_view(uid=None):
    user = User.query.get_or_404(uid)
    return render_template('admin/user_view.html', user=user)


@auth.route('/admin/user/del/<int:uid>')
@login_required
@user_admin_required
def user_del(uid=None):
    user = User.query.get_or_404(uid)
    user.delete()
    flash('删除成功', 'message')

    return render_template('admin/user_list.html', user=user)


@auth.route('/admin/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        admin_user = User()
        admin_user.is_super = 0
        msg, type_ = admin_user.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.admin_add'))

    return render_template('admin/admin_add.html', form=form)


@auth.route('/admin/list/<int:page>')
@login_required
@super_admin_required
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/admin_list.html', page_data=page_data)
