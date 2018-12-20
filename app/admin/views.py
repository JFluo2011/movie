from datetime import datetime

from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, login_user, logout_user, current_user

from . import admin
from .forms import LoginForm, RegisterForm, TagForm, MovieForm, PreviewForm, ChangePasswordForm, PermissionForm, \
    RoleForm, AdminForm
from ..models import db, Admin, Tag, Movie, Preview, User, OpLog, AdminLog, UserLog, Permission, Role


@admin.context_processor
def inject_online_time():
    return {
        'online_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.index'))
        else:
            logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        admin_user = Admin.query.filter_by(email=email).first()
        if (admin_user is None) or not admin_user.check_password(password):
            flash('账号密码不匹配', category='error')
        else:
            login_user(admin_user, remember=True)
            admin_log = AdminLog()
            admin_log.add()
            next_ = request.args.get('next')
            # not next_.startswith('/') 防止重定向攻击
            if (next_ is None) or (not next_.startswith('/')):
                next_ = url_for('admin.index')

            return redirect(next_)

    return render_template('admin/login.html', form=form)


@admin.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        admin_user = Admin()
        msg, type_ = admin_user.add(form)
        flash(msg, type_)
        if type_ == 'error':
            return redirect(url_for('admin.register'))
        return redirect(url_for('admin.login'))

    return render_template('admin/register.html', form=form)


@admin.route('/logout/')
@login_required
def logout():
    # admin_log = AdminLog()
    # admin_log.add()
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        msg, type_ = current_user.change_password(form)
        flash(msg, type_)
        return redirect(url_for('admin.login'))
    return render_template('admin/change_password.html', form=form)


@admin.route('/tag/add', methods=['GET', 'POST'])
@login_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag()
        msg, type_ = tag.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.tag_add'))

    return render_template('admin/tag_add.html', form=form)


@admin.route('/tag/list/<int:page>')
@login_required
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/tag_list.html', page_data=page_data)


@admin.route('/tag/edit/<int:tag_id>/', methods=['GET', 'POST'])
@login_required
def tag_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm()
    if form.validate_on_submit():
        msg, type_ = tag.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.tag_edit', tag_id=tag.id))

    return render_template('admin/tag_edit.html', form=form, tag=tag)


@admin.route('/tag/del/<int:tag_id>/')
@login_required
def tag_del(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    msg, type_ = tag.delete()
    flash(msg, type_)
    return redirect(url_for('admin.tag_list', page=1))


@admin.route('/movie/add', methods=['GET', 'POST'])
@login_required
def movie_add():
    tags = Tag.query.all()
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie()
        msg, type_ = movie.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.movie_add'))

    return render_template('admin/movie_add.html', form=form, tags=tags)


@admin.route('/movie/del/<int:movie_id>/', )
@login_required
def movie_del(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    with db.auto_commit():
        db.session.delete(movie)
    flash('删除电影成功', 'message')
    return redirect(url_for('admin.movie_list', page=1))


@admin.route('/movie/edit/<int:movie_id>/', methods=['GET', 'POST'])
@login_required
def movie_edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm()
    form.url.flags.required = False
    form.logo.flags.required = False
    form.url.validators = []
    form.logo.validators = []

    if request.method == 'GET':
        form.intro.data = movie.intro
        form.star.data = int(movie.star)
        form.tag_id.data = movie.tag_id

    if form.validate_on_submit():
        msg, type_ = movie.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.movie_edit', movie_id=movie.id))

    return render_template('admin/movie_edit.html', form=form, movie=movie)


@admin.route('/movie/list/<int:page>/')
@login_required
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.order_by(
        Movie.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/movie_list.html', page_data=page_data)


@admin.route('/preview/add', methods=['GET', 'POST'])
@login_required
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        preview = Preview()
        msg, type_ = preview.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html', form=form)


@admin.route('/preview/list/<int:page>')
@login_required
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/preview_list.html', page_data=page_data)


@admin.route('/preview/del/<int:preview_id>/', )
@login_required
def preview_del(preview_id):
    preview = Preview.query.get_or_404(preview_id)
    with db.auto_commit():
        db.session.delete(preview)
    flash('删除电影预告成功', 'message')
    return redirect(url_for('admin.preview_list', page=1))


@admin.route('/preview/edit/<int:preview_id>/', methods=['GET', 'POST'])
@login_required
def preview_edit(preview_id):
    preview = Preview.query.get_or_404(preview_id)
    form = PreviewForm()
    form.logo.flags.required = False
    form.logo.validators = []

    if form.validate_on_submit():
        msg, type_ = preview.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.preview_edit', preview_id=preview.id))

    return render_template('admin/preview_edit.html', form=form, preview=preview)


@admin.route('/user/list/<int:page>')
@login_required
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/user_list.html', page_data=page_data)


@admin.route('/user/view/<int:uid>')
@login_required
def user_view(uid=None):
    user = User.query.get_or_404(uid)
    return render_template('admin/user_view.html', user=user)


@admin.route('/user/del/<int:uid>')
@login_required
def user_del(uid=None):
    user = User.query.get_or_404(uid)
    user.delete()
    flash('删除成功', 'message')

    return render_template('admin/user_list.html', user=user)


@admin.route('/oplog/list/<int:page>')
@login_required
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = OpLog.query.filter_by(admin_id=current_user.id).order_by(
        OpLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/oplog_list.html', page_data=page_data)


@admin.route('/admin_login_log/list/<int:page>')
@login_required
def admin_login_log_list(page=None):
    if page is None:
        page = 1
    page_data = AdminLog.query.filter_by(admin_id=current_user.id).order_by(
        AdminLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/admin_login_log_list.html', page_data=page_data)


@admin.route('/user_login_log/list/<int:page>/')
@login_required
def user_login_log_list(page=None):
    if page is None:
        page = 1
    page_data = UserLog.query.order_by(
        UserLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/user_login_log_list.html', page_data=page_data)


@admin.route('/permission/add', methods=['GET', 'POST'])
@login_required
def permission_add():
    form = PermissionForm()
    if form.validate_on_submit():
        permission = Permission()
        msg, type_ = permission.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.permission_add'))

    return render_template('admin/permission_add.html', form=form)


@admin.route('/permission/list/<int:page>/')
@login_required
def permission_list(page=None):
    if page is None:
        page = 1
    page_data = Permission.query.order_by(
        Permission.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/permission_list.html', page_data=page_data)


@admin.route('/permission/del/<int:permission_id>/', )
@login_required
def permission_del(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    with db.auto_commit():
        db.session.delete(permission)
    flash('删除权限成功', 'message')
    return redirect(url_for('admin.permission_list', page=1))


@admin.route('/permission/edit/<int:permission_id>/', methods=['GET', 'POST'])
@login_required
def permission_edit(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    form = PermissionForm()

    if form.validate_on_submit():
        msg, type_ = permission.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.permission_edit', permission_id=permission.id))

    return render_template('admin/permission_edit.html', form=form, permission=permission)


@admin.route('/role/add', methods=['GET', 'POST'])
@login_required
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role()
        msg, type_ = role.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.role_add'))

    return render_template('admin/role_add.html', form=form)


@admin.route('/role/list/<int:page>/')
@login_required
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/role_list.html', page_data=page_data)


@admin.route('/role/del/<int:role_id>/', )
@login_required
def role_del(role_id):
    role = Role.query.get_or_404(role_id)
    with db.auto_commit():
        db.session.delete(role)
    flash('删除角色成功', 'message')
    return redirect(url_for('admin.role_list', page=1))


@admin.route('/role/edit/<int:role_id>/', methods=['GET', 'POST'])
@login_required
def role_edit(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm()
    if request.method == 'GET':
        form.permissions.data = [int(p) for p in role.permissions.split(',')]

    if form.validate_on_submit():
        msg, type_ = role.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.role_edit', role_id=role.id))

    return render_template('admin/role_edit.html', form=form, role=role)


@admin.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        admin_user = Admin()
        admin_user.is_super = 0
        msg, type_ = admin_user.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.admin_add'))

    return render_template('admin/admin_add.html', form=form)


@admin.route('/admin/list/<int:page>')
@login_required
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.order_by(
        Admin.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/admin_list.html', page_data=page_data)
