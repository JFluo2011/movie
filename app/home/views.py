import json

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, current_user, logout_user

from .forms import RegisterForm, LoginForm, UserInfoForm, ChangePasswordForm, CommentForm
from app.models import User, db, UserLog, Preview, Tag, Movie, Comment, MovieCol
from . import home


@home.route('/')
@home.route("/<int:page>/")
def index(page=None):
    if page is None:
        page = 1
    tags = Tag.query.all()
    page_data = Movie.query

    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))

    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))

    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(Movie.create_time.desc())
        else:
            page_data = page_data.order_by(Movie.create_time.asc())

    play_num = request.args.get("play_num", 0)
    if int(play_num) != 0:
        if int(play_num) == 1:
            page_data = page_data.order_by(Movie.play_num.desc())
        else:
            page_data = page_data.order_by(Movie.play_num.asc())

    comment_num = request.args.get("comment_num", 0)
    if int(comment_num) != 0:
        if int(comment_num) == 1:
            page_data = page_data.order_by(Movie.comment_num.desc())
        else:
            page_data = page_data.order_by(Movie.comment_num.asc())

    page_data = page_data.paginate(page=int(page), per_page=current_app.config['PER_PAGE'])
    params = {
        'tid': tid,
        'star': star,
        'time': time,
        'play_num': play_num,
        'comment_num': comment_num,
    }
    return render_template("home/index.html", tags=tags, params=params, page_data=page_data)


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

    return render_template('home/login.html', form=form)


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

    return render_template('home/register.html', form=form)


@home.route('/user/info/<int:uid>/', methods=['GET', 'POST'])
def user_info(uid):
    user = User.query.get_or_404(uid)
    form = UserInfoForm()
    form.avatar.validators = []
    form.avatar.flags.required = False

    if request.method == 'GET':
        form.intro.data = user.intro

    if form.validate_on_submit():
        msg, type_ = user.update(form)
        flash(msg, type_)
        return redirect(url_for('home.user_info', uid=user.id))

    return render_template('home/user_info.html', form=form, user=user)


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
    return render_template('home/change_password.html', form=form)


@home.route('/comment/list/<int:page>')
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('home/comment_list.html', page_data=page_data)


@home.route('/login_log/<int:page>')
def login_log(page=None):
    if page is None:
        page = 1
    page_data = UserLog.query.filter_by(user_id=current_user.id).order_by(
        UserLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('home/login_log.html', page_data=page_data)


@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)


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
        msg, type_ = movie_col.add()
        flash(msg, type_)
        result = {'ok': 1}

    return json.dumps(result)


@home.route('/search/<int:page>')
def search(page=None):
    if page is None:
        page = 1

    key = request.args.get('key', '')
    page_data = Movie.query.filter(Movie.title.ilike(f'%{key}%'))
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
        msg, type_ = comment.add(form)
        flash(msg, type_)
        return redirect(url_for('home.play', movie_id=movie.id, page=1))

    with db.auto_commit():
        movie.play_num += 1

    return render_template('home/play.html', movie=movie, form=form, page_data=page_data)



