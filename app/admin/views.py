import os

from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from . import admin
from .forms import LoginForm, RegisterForm, TagForm, MovieForm
from ..models import db, Admin, Tag, Movie
from ..libs.utils import gen_filename, make_dirs


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        admin_user = Admin.query.filter_by(email=email).first()
        if (admin_user is None) or not admin_user.check_password(password):
            flash('账号密码不匹配', category='err')
        else:
            login_user(admin_user, remember=True)
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
        admin_user.set_attrs(form.data)
        with db.auto_commit():
            db.session.add(admin_user)
        flash('注册成功', 'ok')
        return redirect(url_for('admin.login'))

    return render_template('admin/register.html', form=form)


@admin.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/change_password/')
@login_required
def change_password():
    return render_template('admin/change_password.html')


@admin.route('/tag/add', methods=['GET', 'POST'])
@login_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag()
        tag.set_attrs(form.data)
        if tag.add():
            flash('添加标签成功', 'ok')
        else:
            flash('添加标签失败', 'err')
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
        if not tag.update(form.name.data):
            flash('标签已经存在', 'err')
        else:
            flash('标签更新成功', 'ok')
        return redirect(url_for('admin.tag_edit', tag_id=tag.id))

    return render_template('admin/tag_edit.html', form=form, tag=tag)


@admin.route('/tag/del/<int:tag_id>/')
@login_required
def tag_del(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    with db.auto_commit():
        db.session.delete(tag)
    flash('删除标签成功', 'ok')
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


@admin.route('/movie/del/<int:movie_id>/')
@login_required
def movie_del(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    with db.auto_commit():
        db.session.delete(movie)
    flash('删除电影成功', 'ok')
    return redirect(url_for('admin.movie_list', page=1))


@admin.route('/movie/edit/<int:movie_id>/', methods=['GET', 'POST'])
@login_required
def movie_edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(movie)
    if form.validate_on_submit():
        if not movie.update(form.name.data):
            flash('电影已经存在', 'err')
        else:
            flash('电影更新成功', 'ok')
        return redirect(url_for('admin.movie_id_edit', movie_id=movie.id))

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


@admin.route('/preview/add')
@login_required
def preview_add():
    return render_template('admin/preview_add.html')


@admin.route('/preview/list')
@login_required
def preview_list():
    return render_template('admin/preview_list.html')


@admin.route('/user/list')
@login_required
def user_list():
    return render_template('admin/user_list.html')


@admin.route('/comment/list')
@login_required
def comment_list():
    return render_template('admin/comment_list.html')


@admin.route('/movie_col/list')
@login_required
def movie_col_list():
    return render_template('admin/movie_col_list.html')


@admin.route('/operator_log/list')
@login_required
def operator_log_list():
    return render_template('admin/operator_log_list.html')


@admin.route('/admin_login_log/list')
@login_required
def admin_login_log_list():
    return render_template('admin/admin_login_log_list.html')


@admin.route('/user_login_log/list')
@login_required
def user_login_log_list():
    return render_template('admin/user_login_log_list.html')


@admin.route('/permission/add')
@login_required
def permission_add():
    return render_template('admin/permission_add.html')


@admin.route('/permission/list')
@login_required
def permission_list():
    return render_template('admin/permission_list.html')


@admin.route('/role/add')
@login_required
def role_add():
    return render_template('admin/role_add.html')


@admin.route('/role/list')
@login_required
def role_list():
    return render_template('admin/role_list.html')


@admin.route('/admin/add')
@login_required
def admin_add():
    return render_template('admin/admin_add.html')


@admin.route('/admin/list')
@login_required
def admin_list():
    return render_template('admin/admin_list.html')
