import os
import abc
from datetime import datetime
from contextlib import contextmanager

from flask import current_app, request, flash, abort
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, DateTime, SmallInteger, String, Boolean, Text, Date, BigInteger, Enum
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user

from app.libs.utils import gen_filename
from .libs.enums import AuthEnum, RoleEnum, OperatorEnum

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


class SubQuery(BaseQuery):
    def filter_by(self, use_base=False, **kwargs):
        if not use_base and ('status' not in kwargs.keys()):
            kwargs.update({'status': True})
        return super().filter_by(**kwargs)

    def get_or_404(self, ident):
        obj = super().get_or_404(ident)
        if obj.status:
            return obj
        abort(404)

    def first_or_404(self):
        # 避免取出已经被软删除的数据
        return super().filter_by().first_or_404()


db = SubSQLAlchemy(query_class=SubQuery)


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, index=True, default=datetime.now)
    status = Column(Boolean, default=True)

    def __repr__(self):
        return f'{self.__class__} {self.name!r}'

    @abc.abstractmethod
    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        pass

    def add(self, form=None, record_log=True):
        return self._upsert(form=form, operator=OperatorEnum.ADD, add=True, record_log=record_log)

    def update(self, form=None, record_log=True):
        return self._upsert(form=form, operator=OperatorEnum.UPDATE, add=False, record_log=record_log)

    def delete(self, record_log=True):
        with db.auto_commit():
            # 软删除
            self.status = False
            # db.session.delete(self)
            self._log(operator=OperatorEnum.DELETE, record_log=record_log)
        flash(f'删除成功', 'message')

    def set_attrs(self, form, ignore_fields):
        ignore_fields.append('id')
        for key, value in form.data.items():
            if hasattr(self, key) and (key not in ignore_fields):
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

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        return True

    def _handle_media_field(self, form, add=True):
        return []

    def _upsert(self, form=None, operator=OperatorEnum.ADD, add=True, record_log=True):
        if not self._can_operator(form=form, operator=operator):
            return False
        ignore_fields = self._handle_media_field(form=form, add=add)
        if form is not None:
            self.set_attrs(form, ignore_fields=ignore_fields)
        with db.auto_commit():
            db.session.add(self)
            self._log(operator=operator, record_log=record_log)
        flash(f'{OperatorEnum.operator_str(operator)}成功', 'message')
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

    # override
    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        pass

    def add(self, form=None, record_log=True):
        with db.auto_commit():
            db.session.add(self)

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class User(UserMixin, Base):
    __tablename__ = 'users'
    name = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(20))
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

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        if record_log:
            op_log = OpLog(f'{OperatorEnum.operator_str(operator)}用户{self.name}')
            db.session.add(op_log)

    @property
    def password(self):
        return self._password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, new_password):
        return check_password_hash(self._password, new_password)

    def change_password(self, form, record_log=True):
        if not self.check_password(form.old_password.data):
            flash('旧密码错误', 'error')
            return False
        if form.new_password.data == form.old_password.data:
            flash('新旧密码相同', 'error')
            return False

        with db.auto_commit():
            self.password = form.new_password.data
            if record_log:
                op_log = OpLog(f'修改密码')
                db.session.add(op_log)
        flash('密码已更新', 'message')
        return True

    def _handle_media_field(self, form, add=True):
        if (form.avatar.data is not None) and (form.avatar.data != ''):
            self._upload_media(form.avatar, current_app.config['AVATAR_PATH'], add=add)
        return super()._handle_media_field(form=form, add=add) + ['avatar']

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        if operator == OperatorEnum.UPDATE:
            if (self.name != form.name.data) and self.__class__.query.filter_by(email=form.email.data).first():
                flash('用户名已被占用', 'error')
                return False
        else:
            if self.__class__.query.filter_by(email=form.email.data).first():
                flash('用户名已被占用', 'error')
                return False
        return True


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


class Tag(Base):
    __tablename__ = 'tags'
    name = Column(String(50), nullable=False)
    movie = relationship('Movie', backref='tag')

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        if record_log:
            op_log = OpLog(f'{OperatorEnum.operator_str(operator)}标签{self.name}')
            db.session.add(op_log)

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        if self.__class__.query.filter_by(name=form.name.data).first():
            flash('标签已存在', 'error')
            return False
        return True


class Movie(Base):
    __tablename__ = 'movies'
    title = Column(String(255), nullable=False)
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

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        if record_log:
            op_log = OpLog(f'{OperatorEnum.operator_str(operator)}影片{self.title}')
            db.session.add(op_log)

    def _handle_media_field(self, form, add=True):
        if form.url.data != '':
            self._upload_media(form.url, current_app.config['MOVIE_PATH'], add=add)
        if form.logo.data != '':
            self._upload_media(form.logo, current_app.config['MOVIE_PATH'], add=add)

        return super()._handle_media_field(form=form, add=add) + ['url', 'logo']

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        if operator == OperatorEnum.UPDATE:
            if (self.title != form.title.data) and self.__class__.query.filter_by(title=form.title.data).first():
                flash('影片已存在', 'error')
                return False
        else:
            if self.__class__.query.filter_by(title=form.title.data).first():
                flash('影片已存在', 'error')
                return False
        return True


class Preview(Base):
    __tablename__ = 'previews'
    title = Column(String(255), nullable=False)
    logo = Column(String(255))

    def __repr__(self):
        return f'{self.__class__} {self.title!r}'

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        if record_log:
            op_log = OpLog(f'{OperatorEnum.operator_str(operator)}预告{self.title}')
            db.session.add(op_log)

    def _handle_media_field(self, form, add=True):
        if form.logo.data != '':
            self._upload_media(form.logo, current_app.config['PREVIEW_PATH'], add=add)

        return super()._handle_media_field(form=form, add=add) + ['logo']

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        if operator == OperatorEnum.UPDATE:
            if (self.title != form.title.data) and self.__class__.query.filter_by(title=form.title.data).first():
                flash('预告已存在', 'error')
                return False
        else:
            if self.__class__.query.filter_by(title=form.title.data).first():
                flash('预告已存在', 'error')
                return False
        return True


class Comment(Base):
    __tablename__ = 'comments'
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        pass

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


class MovieCol(Base):
    __tablename__ = 'movie_cols'
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def _log(self, operator=OperatorEnum.ADD, record_log=True):
        pass

    def _can_operator(self, form, operator=OperatorEnum.ADD):
        if self.__class__.query.filter_by(movie_id=self.movie_id, user_id=self.user_id).first():
            flash('影片已收藏', 'error')
            return False
        return True

    def __repr__(self):
        return f'{self.__class__} {self.id!r}'


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
