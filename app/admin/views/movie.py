from flask import render_template, current_app, redirect, url_for, flash, request
from flask_login import login_required

from .. import admin
from ..forms import MovieForm
from ...models import Movie, db, Tag
from ...libs.permissions import movie_admin_required


@admin.route('/movie/add', methods=['GET', 'POST'])
@login_required
@movie_admin_required
def movie_add():
    tags = Tag.query.all()
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie()
        msg, type_ = movie.add(form, record_log=True)
        flash(msg, type_)
        return redirect(url_for('admin.movie_add'))

    return render_template('admin/movie_add.html', form=form, tags=tags)


@admin.route('/movie/del/<int:movie_id>/', )
@login_required
@movie_admin_required
def movie_del(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie.delete(record_log=True)
    flash(movie.message, movie.type_)
    return redirect(url_for('admin.movie_list', page=1))


@admin.route('/movie/edit/<int:movie_id>/', methods=['GET', 'POST'])
@login_required
@movie_admin_required
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
        movie.update(form, record_log=True)
        flash(movie.message, movie.type_)
        return redirect(url_for('admin.movie_edit', movie_id=movie.id))

    return render_template('admin/movie_edit.html', form=form, movie=movie)


@admin.route('/movie/list/<int:page>/')
@login_required
@movie_admin_required
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.order_by(
        Movie.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/movie_list.html', page_data=page_data)
