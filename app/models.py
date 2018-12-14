import os
from datetime import datetime
from contextlib import contextmanager

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, DateTime, SmallInteger, String, Boolean, Text, Date
from sqlalchemy.orm import backref, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user

from app.libs.utils import gen_filename, make_dirs

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

    def __repr__(self):
        return f'User {self.name!r}'

    def set_attrs(self, attrs_dict, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = ['id']
        else:
            ignore_fields.append('id')

        for key, value in attrs_dict.items():
            if hasattr(self, key) and (key not in ignore_fields):
                setattr(self, key, value)

    # def __init__(self):
    #     self.create_time = int(datetime.now().timestamp())

    # @property
    # def create_datetime(self):
    #     if self.create_time:
    #         return datetime.fromtimestamp(self.create_time)


class UserBase(UserMixin, Base):
    __abstract__ = True
    name = Column(String(20), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    confirm = Column(Boolean, default=False)
    intro = Column(Text)
    avatar = Column(String(255))
    _password = Column('password', String(128), nullable=False)

    @property
    def password(self):
        return self._password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, new_password):
        return check_password_hash(self._password, new_password)


class User(UserBase):
    __tablename__ = 'users'


class Admin(UserBase):
    __tablename__ = 'admins'
    is_super = Column(Boolean, default=False)


class UserLog(Base):
    __tablename__ = 'user_logs'
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='user_log')
    ip = Column(String(20))

    def __repr__(self):
        return f'User {self.id!r}'


class AdminLog(Base):
    __tablename__ = 'admin_logs'
    admin_id = Column(Integer, ForeignKey('admins.id'))
    admin = relationship('Admin', backref='admin_log')
    ip = Column(String(20))

    def __repr__(self):
        return f'User {self.id!r}'


class OperatorLog(Base):
    __tablename__ = 'operator_logs'
    admin_id = Column(Integer, ForeignKey('admins.id'))
    admin = relationship('Admin', backref='operator_log')
    reason = Column(String(512))
    ip = Column(String(20))

    def __repr__(self):
        return f'User {self.id!r}'


# movie_tags = db.Table(
#     'movie_tags',
#     db.Column('movie_id', Integer(), ForeignKey('movies.id')),
#     db.Column('tag_id', Integer(), ForeignKey('tags.id')),
# )


class Tag(Base):
    __tablename__ = 'tags'
    name = Column(String(50), unique=True, nullable=False)
    movie = relationship('Movie', backref='tag')

    def update(self, name):
        if (self.name != name) and Tag.query.filter_by(name=name).first():
            return False
        with db.auto_commit():
            self.name = name
        return True

    def add(self):
        if Tag.query.filter_by(name=self.name).first():
            return False
        with db.auto_commit():
            db.session.add(self)
        return True


class Movie(Base):
    __tablename__ = 'movies'
    title = Column(String(255), unique=True, nullable=False)
    url = Column(String(255))
    play_num = Column(Integer, default=0)
    intro = Column(Text)
    area = Column(String(50))
    publish_time = Column(Date)
    length = Column(String(20))
    star = Column(SmallInteger)
    logo = Column(String(255))
    tag_id = Column(Integer, ForeignKey('tags.id'))

    def __repr__(self):
        return f'Movie {self.title!r}'

    def set_attrs(self, attrs_dict, ignore_fields=None):
        ignore_fields = ['url', 'logo']
        super().set_attrs(attrs_dict, ignore_fields)

    def add(self, form):
        if Movie.query.filter_by(title=form.title.data).first():
            return '电影已存在，请勿重复上传', 'err'
        url = gen_filename(form.url.data)
        logo = gen_filename(form.logo.data)
        self.url = url
        self.logo = logo
        make_dirs(current_app.config['UP_DIR'], permission='rw')
        form.url.data.save(os.path.join(current_app.config['UP_DIR'], url))
        form.logo.data.save(os.path.join(current_app.config['UP_DIR'], logo))
        self.set_attrs(form.data)
        with db.auto_commit():
            db.session.add(self)
        return '电影添加成功', 'ok'


class Preview(Base):
    __tablename__ = 'previews'
    title = Column(String(255), unique=True, nullable=False)
    logo = Column(String(255))

    def __repr__(self):
        return f'User {self.title!r}'


class Comment(Base):
    __tablename__ = 'comments'
    content = Column(Text)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship('Movie', backref='comments')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='comments')

    def __repr__(self):
        return f'User {self.id!r}'


class MovieCol(Base):
    __tablename__ = 'movie_cols'
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship('Movie', backref='movie_col')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='movie_col')

    def __repr__(self):
        return f'User {self.id!r}'


class Permission(Base):
    __tablename__ = 'permissions'
    name = Column(String(20), unique=True, nullable=False)
    url = Column(String(255))

    def __repr__(self):
        return f'User {self.name!r}'


class Role(Base):
    __tablename__ = 'roles'
    name = Column(String(20), unique=True, nullable=False)
    permissions = Column(String(512))
    admin_id = Column(Integer, ForeignKey('admins.id'))
    admin = relationship('Admin', backref='role')

    def __repr__(self):
        return f'User {self.name!r}'


@login_manager.user_loader
def get_user(uid):
    return Admin.query.get(int(uid))
