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

    def __repr__(self):
        return f'{self.__class__} {self.name!r}'

    def set_attrs(self, form, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = ['id']
        else:
            ignore_fields.extend(['id'])

        for key, value in form.data.items():
            if hasattr(self, key) and (key not in ignore_fields):
                setattr(self, key, value)

    def _upload_media(self, field, add=True):
        path = gen_filename(field.data)
        if not add:
            data = getattr(self, field.name)
            if data:
                media_path = os.path.join(current_app.config['UP_DIR'], data)
                if os.path.exists(media_path):
                    os.remove(media_path)
        setattr(self, field.name, path)
        field.data.save(os.path.join(current_app.config['UP_DIR'], path))

    def delete(self):
        with db.auto_commit():
            # self.status = 1
            db.session.delete(self)

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

    @property
    def password(self):
        return self._password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, new_password):
        return check_password_hash(self._password, new_password)

    def add(self, form):
        if self.__class__.query.filter_by(email=form.email.data).first():
            return '用户名已被占用', 'error'
        self.set_attrs(form)
        with db.auto_commit():
            db.session.add(self)
        return '添加用户成功', 'message'

    def add_admin(self, form):
        if self.__class__.query.filter_by(email=form.email.data).first():
            return '用户名已被占用', 'error'
        self.set_attrs(form)
        self.auth = AuthEnum.Admin
        self.confirm = 1
        self.role = form.role.data
        self.intro = RoleEnum.role_str(form.role.data)
        with db.auto_commit():
            db.session.add(self)
        return '添加用户成功', 'message'

    def change_password(self, form):
        if not self.check_password(form.old_password.data):
            return '旧密码错误', 'error'

        if form.new_password.data == form.old_password.data:
            return '新旧密码相同', 'error'

        with db.auto_commit():
            self.password = form.new_password.data
        return '密码修改成功', 'message'

    def set_attrs(self, form, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = ['avatar', 'auth', 'role']
        else:
            ignore_fields.extend(['avatar', 'auth', 'role'])
        super().set_attrs(form, ignore_fields)

    def _handle_media_field(self, form, add=True):
        if form.avatar.data != '':
            self._upload_media(form.avatar, add=add)

    def update(self, form):
        if (self.name != form.name.data) and self.__class__.query.filter_by(name=form.name.data).first():
            return '昵称已经存在', 'error'
        with db.auto_commit():
            self._handle_media_field(form, add=False)
            self.set_attrs(form)
        return '更新成功', 'message'


class BaseLog(Base):
    __abstract__ = True
    ip = Column(String(20))

    def __init__(self, *args, **kwargs):
        self.user_id = current_user.id
        self.ip = request.remote_addr

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey('users.id'))

    def add(self):
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

    def update(self, form):
        if self.name == form.name.data:
            return '标签名未修改', 'error'
        if Tag.query.filter_by(name=form.name.data).first():
            return '修改标签失败', 'error'
        with db.auto_commit():
            op_log = OpLog(f'修改标签{self.name}-->{form.name.data}')
            db.session.add(op_log)
            self.name = form.name.data
        return '修改标签成功', 'message'

    def add(self, form):
        if Tag.query.filter_by(name=form.name.data).first():
            return '标签已存在', 'error'

        self.set_attrs(form)
        with db.auto_commit():
            op_log = OpLog(f'添加标签{self.name}')
            db.session.add(op_log)
            db.session.add(self)
        return '添加标签成功', 'message'

    def delete(self):
        with db.auto_commit():
            op_log = OpLog(f'删除标签{self.name}')
            db.session.add(op_log)
            db.session.delete(self)
        return '删除标签成功', 'message'


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

    def __repr__(self):
        return f'{self.__class__} {self.title!r}'

    def set_attrs(self, form, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = ['url', 'logo']
        else:
            ignore_fields.extend(['url', 'logo'])
        super().set_attrs(form, ignore_fields)

    def _handle_media_field(self, form, add=True):
        if form.url.data != '':
            self._upload_media(form.url, add=add)
        if form.logo.data != '':
            self._upload_media(form.logo, add=add)

    def add(self, form):
        if Movie.query.filter_by(title=form.title.data).first():
            return '片名已存在', 'error'
        self._handle_media_field(form)
        self.set_attrs(form)
        with db.auto_commit():
            op_log = OpLog(f'添加影片{self.title}')
            db.session.add(op_log)
            db.session.add(self)
        return '添加影片成功', 'message'

    def update(self, form):
        if (self.title != form.title.data) and Movie.query.filter_by(title=form.title.data).first():
            return '片名已经存在', 'error'
        with db.auto_commit():
            self._handle_media_field(form, add=False)
            self.set_attrs(form)
            op_log = OpLog(f'编辑影片信息{self.title}')
            db.session.add(op_log)
        return '编辑影片信息成功', 'message'

    def delete(self):
        with db.auto_commit():
            op_log = OpLog(f'删除影片{self.title}')
            db.session.add(op_log)
            db.session.delete(self)
        return '删除影片成功', 'message'


class Preview(Base):
    __tablename__ = 'previews'
    title = Column(String(255), unique=True, nullable=False)
    logo = Column(String(255))

    def __repr__(self):
        return f'{self.__class__} {self.title!r}'

    def set_attrs(self, form, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = ['logo']
        else:
            ignore_fields.extend(['logo'])
        super().set_attrs(form, ignore_fields)

    def _handle_media_field(self, form, add=True):
        if form.logo.data != '':
            self._upload_media(form.logo, add=add)

    def add(self, form):
        if Preview.query.filter_by(title=form.title.data).first():
            return '预告已存在', 'error'
        self._handle_media_field(form)
        self.set_attrs(form)
        with db.auto_commit():
            op_log = OpLog(f'添加预告{self.title}')
            db.session.add(op_log)
            db.session.add(self)
        return '添加预告成功', 'message'

    def update(self, form):
        if (self.title != form.title.data) and Preview.query.filter_by(title=form.title.data).first():
            return '预告已经存在', 'error'
        with db.auto_commit():
            self._handle_media_field(form, add=False)
            self.set_attrs(form)
            op_log = OpLog(f'编辑预告信息{self.title}')
            db.session.add(op_log)
        return '编辑预告信息成功', 'message'

    def delete(self):
        with db.auto_commit():
            op_log = OpLog(f'删除预告{self.title}')
            db.session.add(op_log)
            db.session.delete(self)
        return '删除预告成功', 'message'


class Comment(Base):
    __tablename__ = 'comments'
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))

    def add(self, form):
        self.set_attrs(form)
        with db.auto_commit():
            db.session.add(self)
        return '评论添加成功', 'message'

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class MovieCol(Base):
    __tablename__ = 'movie_cols'
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def add(self):
        with db.auto_commit():
            db.session.add(self)
        return '收藏电影成功', 'message'

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class Permission(Base):
    __tablename__ = 'permissions'
    name = Column(String(20), unique=True, nullable=False)
    url = Column(String(255))

    def add(self, form):
        if self.__class__.query.filter_by(name=form.name.data).first():
            return '权限已存在', 'error'
        with db.auto_commit():
            self.set_attrs(form)
            db.session.add(self)
            op_log = OpLog(f'添加权限{self.name}')
            db.session.add(op_log)
        return '添加权限成功', 'message'

    def update(self, form):
        if (self.name != form.name.data) and self.__class__.query.filter_by(name=form.name.data).first():
            return '权限已经存在', 'error'
        with db.auto_commit():
            op_log = OpLog(f'编辑权限{self.name}')
            db.session.add(op_log)
            self.set_attrs(form)
        return '编辑权限成功', 'message'

    def delete(self):
        with db.auto_commit():
            op_log = OpLog(f'删除权限{self.name}')
            db.session.add(op_log)
            db.session.delete(self)
        return '删除权限成功', 'message'

    def __repr__(self):
        return f'{self.__class__} {self.name!r}'


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
