import json

from flask import current_app, render_template, request, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import and_

from app.home import home
from app.home.forms.main import CommentForm
from app.models import MovieCol, Movie, Comment, db


@home.route('/movie_col/list/<int:page>')
def movie_col_list(page=None):
    if page is None:
        page = 1
    page_data = MovieCol.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('home/movie_col_list.html', page_data=page_data)


@home.route('/movie_col/add')
def movie_col_add():
    uid = request.args.get('uid', '')
    mid = request.args.get('mid', '')
    movie_col = MovieCol.query.filter_by(user_id=int(uid), movie_id=int(mid)).first()
    if movie_col:
        result = {'ok': 0}
    else:
        movie_col = MovieCol()
        movie_col.user_id = uid
        movie_col.movie_id = mid
        movie_col.add()
        result = {'ok': 1}

    return json.dumps(result)


@home.route('/search/<int:page>')
def search(page=None):
    if page is None:
        page = 1

    key = request.args.get('key', '')
    page_data = Movie.query.filter(Movie.title.ilike(f'%{key}%', Movie.status == True))
    count = page_data.count()
    page_data = page_data.paginate(
        page=page, per_page=current_app.config['PER_PAGE'])
    page_data.key = key
    return render_template('home/search.html', key=key, count=count, page_data=page_data)


@home.route('/play/<int:movie_id>/<int:page>/', methods=['GET', 'POST'])
def play(movie_id=None, page=None):
    if page is None:
        page = 1
    movie = Movie.query.get_or_404(movie_id)
    page_data = Comment.query.filter_by(movie_id=movie_id).paginate(
        page=page, per_page=current_app.config['PER_PAGE'])
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.movie_id = movie_id
        comment.user_id = current_user.id
        with db.auto_commit():
            movie.comment_num += 1
        comment.add(form)
        return redirect(url_for('home.play', movie_id=movie.id, page=1))

    with db.auto_commit():
        movie.play_num += 1

    return render_template('home/play.html', movie=movie, form=form, page_data=page_data)


@home.route('/comment/list/<int:page>')
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('home/comment_list.html', page_data=page_data)

