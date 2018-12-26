import os
from datetime import datetime
from contextlib import contextmanager

from flask import current_app, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, DateTime, SmallInteger, String, Boolean, Text, Date, BigInteger, Enum
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user

from app.libs.utils import gen_filename
from .libs.enums import AuthEnum, RoleEnum

login_manager = LoginManager()


class SubSQLAlchemy(SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            raise err


db = SubSQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, index=True, default=datetime.now)
    status = Column(SmallInteger, default=1)

    def __init__(self):
        self.name = ''
        self.title = ''
        self.message = ''
        self.type_ = 'message'
        self.identity = ''
        self.ignore_fields = []

    def __repr__(self):
        return f'{self.__class__} {self.name!r}'

    def set_attrs(self, form):
        self.ignore_fields.append('id')
        for key, value in form.data.items():
            if hasattr(self, key) and (key not in self.ignore_fields):
                setattr(self, key, value)

    def _upload_media(self, field, up_dir, add=True):
        path = gen_filename(field.data)
        if not add:
            data = getattr(self, field.name)
            if data:
                media_path = os.path.join(up_dir, data)
                if os.path.exists(media_path):
                    os.remove(media_path)
        setattr(self, field.name, path)
        field.data.save(os.path.join(up_dir, path))

    def _can_operator(self, form, operator='添加'):
        return True

    def _handle_media_field(self, form, add=True):
        pass

    def _log(self, operator='添加', record_log=False):
        if record_log:
            op_log = OpLog(f'{operator}{self.identity}{self.name if self.name else self.title}')
            db.session.add(op_log)

    def add(self, form=None, operator='添加', add=True, record_log=False):
        if not self._can_operator(form=form, operator=operator):
            return
        self._handle_media_field(form=form, add=add)
        if form is not None:
            self.set_attrs(form)
        with db.auto_commit():
            db.session.add(self)
            self._log(operator=operator, record_log=record_log)
        self.message = f'{operator}{self.identity}成功'
        self.type_ = 'message'

    def update(self, form=None, record_log=False):
        self.add(form=form, operator='编辑', add=False, record_log=record_log)

    def delete(self, operator='删除', record_log=False):
        with db.auto_commit():
            # self.status = 1
            db.session.delete(self)
            self._log(operator=operator, record_log=record_log)
        self.message = f'{operator}{self.identity}成功'
        self.type_ = 'message'

    # def __init__(self):
    #     self.create_time = int(datetime.now().timestamp())

    # @property
    # def create_datetime(self):
    #     if self.create_time:
    #         return datetime.fromtimestamp(self.create_time)


class User(UserMixin, Base):
    __tablename__ = 'users'
    name = Column(String(20), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    confirm = Column(Boolean, default=False)
    intro = Column(Text)
    avatar = Column(String(255))
    auth = Column('auth', Enum(AuthEnum), server_default='User')
    role = Column('role', Enum(RoleEnum), server_default='User')
    comment = relationship('Comment', backref='user')
    movie_col = relationship('MovieCol', backref='user')
    admin_log = relationship('AdminLog', backref='user')
    user_log = relationship('UserLog', backref='user')
    op_log = relationship('OpLog', backref='user')
    _password = Column('password', String(128), nullable=False)

    def __init__(self):
        super().__init__()
        self.identity = '用户'
        self.ignore_fields = ['avatar', 'auth']

    @property
    def password(self):
        return self._password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, new_password):
        return check_password_hash(self._password, new_password)

    def change_password(self, form, record_log=False):
        if not self.check_password(form.old_password.data):
            return '旧密码错误', 'error'
        if form.new_password.data == form.old_password.data:
            return '新旧密码相同', 'error'

        with db.auto_commit():
            self.password = form.new_password.data
            if record_log:
                op_log = OpLog(f'修改密码')
                db.session.add(op_log)
        self.message = '修改密码成功'
        self.type_ = 'message'

    def _handle_media_field(self, form, add=True):
        if (form.avatar.data is not None) and (form.avatar.data != ''):
            self._upload_media(form.avatar, current_app.config['AVATAR_PATH'], add=add)

    def _can_operator(self, form, operator='添加'):
        self.message = '用户名已经存在'
        self.type_ = 'error'
        if operator == '编辑':
            if (self.name != form.name.data) and self.__class__.query.filter_by(email=form.email.data).first():
                return False
        else:
            if self.__class__.query.filter_by(email=form.email.data).first():
                return False
        return True


class BaseLog(Base):
    __abstract__ = True
    ip = Column(String(20))

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.user_id = current_user.id
        self.ip = request.remote_addr

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey('users.id'))

    def _log(self, operator='添加', record_log=True):
        pass

    def add(self, form=None, operator='添加', add=True, record_log=False):
        with db.auto_commit():
            db.session.add(self)

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class UserLog(BaseLog):
    __tablename__ = 'user_logs'


class AdminLog(BaseLog):
    __tablename__ = 'admin_logs'


class OpLog(BaseLog):
    __tablename__ = 'op_logs'
    reason = Column(String(512))

    def __init__(self, reason, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason


# movie_tags = db.Table(
#     'movie_tags',
#     db.Column('movie_id', Integer(), ForeignKey('movies.id')),
#     db.Column('tag_id', Integer(), ForeignKey('tags.id')),
# )


class Tag(Base):
    __tablename__ = 'tags'
    name = Column(String(50), unique=True, nullable=False)
    movie = relationship('Movie', backref='tag')

    def __init__(self):
        super().__init__()
        self.identity = '标签'

    def _can_operator(self, form, operator='添加'):
        if self.__class__.query.filter_by(name=form.name.data).first():
            self.message = f'{self.identity}已经存在'
            self.type_ = 'error'
            return False
        return True


class Movie(Base):
    __tablename__ = 'movies'
    title = Column(String(255), unique=True, nullable=False)
    url = Column(String(255))
    play_num = Column(BigInteger, default=0)
    comment_num = Column(BigInteger, default=0)
    intro = Column(Text)
    area = Column(String(50))
    publish_time = Column(Date)
    length = Column(String(20))
    star = Column(SmallInteger)
    logo = Column(String(255))
    tag_id = Column(Integer, ForeignKey('tags.id'))
    comment = relationship('Comment', backref='movie')
    movie_col = relationship('MovieCol', backref='movie')

    def __init__(self):
        super().__init__()
        self.identity = '影片'
        self.ignore_fields = ['url', 'logo']

    def __repr__(self):
        return f'{self.__class__} {self.title!r}'

    def _handle_media_field(self, form, add=True):
        if form.url.data != '':
            self._upload_media(form.url, current_app.config['MOVIE_PATH'], add=add)
        if form.logo.data != '':
            self._upload_media(form.logo, current_app.config['MOVIE_PATH'], add=add)

    def _can_operator(self, form, operator='添加'):
        if operator == '编辑':
            if (self.title != form.title.data) and self.__class__.query.filter_by(title=form.title.data).first():
                self.message = f'{self.identity}已存在'
                self.type_ = 'error'
                return False
        else:
            if self.__class__.query.filter_by(title=form.title.data).first():
                return False
        return True


class Preview(Base):
    __tablename__ = 'previews'
    title = Column(String(255), unique=True, nullable=False)
    logo = Column(String(255))

    def __init__(self):
        super().__init__()
        self.identity = '预告'
        self.ignore_fields = ['logo']

    def __repr__(self):
        return f'{self.__class__} {self.title!r}'

    def _handle_media_field(self, form, add=True):
        if form.logo.data != '':
            self._upload_media(form.logo, current_app.config['PREVIEW_PATH'], add=add)

    def _can_operator(self, form, operator='添加'):
        self.message = f'{self.identity}已存在'
        self.type_ = 'error'
        if operator == '编辑':
            if (self.title != form.title.data) and self.__class__.query.filter_by(title=form.title.data).first():
                return False
        else:
            if self.__class__.query.filter_by(title=form.title.data).first():
                return False
        return True


class Comment(Base):
    __tablename__ = 'comments'
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))

    def __init__(self):
        super().__init__()
        self.identity = '评论'

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class MovieCol(Base):
    __tablename__ = 'movie_cols'
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self):
        super().__init__()
        self.identity = '收藏'

    def _can_operator(self, form, operator='添加'):
        if self.__class__.query.filter_by(movie_id=self.movie_id, user_id=self.user_id).first():
            return False
        return True

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
