from flask import render_template, request, url_for, current_app, flash, redirect
from flask_login import current_user, login_required

from app.auth.forms import UserInfoForm
from ...models import Tag, Movie, Preview, User, UserLog
from .. import home


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


@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)


@home.route('/user/info/<int:uid>/', methods=['GET', 'POST'])
@login_required
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


@home.route('/login_log/<int:page>')
@login_required
def login_log(page=None):
    if page is None:
        page = 1
    page_data = UserLog.query.filter_by(user_id=current_user.id).order_by(
        UserLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('home/login_log.html', page_data=page_data)
