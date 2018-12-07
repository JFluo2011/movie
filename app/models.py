from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import INTEGER, DateTime, SMALLINT, String, Boolean, ForeignKey
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    id = db.Column(INTEGER, primary_key=True)
    create_time = db.Column(DateTime)
    status = db.Column(SMALLINT)


class User(Base):
    __tablename__ = 'users'
    nickname = db.Column(String(20), unique=True, nullable=False)
    email = db.Column(String(50), unique=True, nullable=False)
    confirm = db.Column(Boolean, default=False)
    _password = db.Column('password', String(128), nullable=False)

    @property
    def password(self):
        # return self._password
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, new_password):
        return check_password_hash(self._password, new_password)


movie_tags = db.Table(
    'movie_tags',
    db.Column('movie_id', INTEGER, ForeignKey('movies.id')),
    db.Column('tag_id', INTEGER, ForeignKey('tags.id')),
)


class Tag(Base):
    __tablename__ = 'tags'
    name = db.Column(String(50), unique=True, nullable=False)


class Movie(Base):
    __tablename__ = 'movies'
    name = db.Column(String(50), unique=True, nullable=False)
    tags = db.relationship('Movie', secondary=movie_tags, backref=backref('movies', lazy='dynamic'))
