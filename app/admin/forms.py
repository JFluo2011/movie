import os

from flask import current_app
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from app.libs.utils import make_dirs, gen_filename
from ..models import Admin, Tag, Movie


class EmailForm(FlaskForm):
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired(message='请输入邮箱！'),
            Email(message='无效的邮箱地址'),
            Length(min=8, max=64, message='邮箱应在8-64个字符之间'),
        ],
        description='邮箱',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入邮箱！',
            'required': 'required',
        }
    )


class LoginForm(EmailForm):
    password = PasswordField(
        label='密码',
        validators=[
            DataRequired(message='请输入密码！'),
            Length(min=6, max=32, message='密码长度为:6-32位字符'),
        ],
        description='密码',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入密码！',
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='登陆',
        render_kw={
            'class': 'btn btn-primary btn-block btn-flat',
        }
    )


class RegisterForm(EmailForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired(message='请输入昵称！'),
            Length(min=5, max=20, message='昵称应在5-20个字符之间'),
        ],
        description='昵称',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入昵称！',
            'required': 'required',
        }
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired(message='请输入手机号！'),
            Length(min=11, max=11, message='请输入11位手机号'),
        ],
        description='手机',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入手机号！',
            'required': 'required',
        }
    )
    password = PasswordField(
        label='密码',
        validators=[
            DataRequired(message='请输入密码！'),
            Length(min=6, max=32, message='密码长度为:6-32位字符'),
            EqualTo('repassword', message='两次输入的密码不匹配')
        ],
        description='密码',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入密码！',
            'required': 'required',
        }
    )
    repassword = PasswordField(
        label='确认密码',
        validators=[
            DataRequired(message='请输入确认密码！'),
            Length(min=6, max=32, message='密码长度为:6-32位字符'),
        ],
        description='确认密码',
        render_kw={
            'id': 'input_repassword',
            'class': 'form-control input-lg',
            'placeholder': '请输入确认密码！',
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='注册',
        render_kw={
            'class': 'btn btn-lg btn-success btn-block',
        }
    )

    def validate_email(self, field):
        if Admin.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_name(self, field):
        if Admin.query.filter_by(name=field.data).first():
            raise ValidationError('昵称被占用')

    def validate_phone(self, field):
        if Admin.query.filter_by(phone=field.data).first():
            raise ValidationError('手机已经被使用')


class TagForm(FlaskForm):
    name = StringField(
        label='编辑',
        validators=[
            DataRequired(message='请输入标签！'),
        ],
        description='标签',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入标签！',
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='添加',
        render_kw={
            'class': 'btn btn-primary',
        }
    )


class MovieForm(FlaskForm):
    title = StringField(
        label='片名',
        validators=[
            DataRequired(message='请输入片名！'),
        ],
        description='片名',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入片名！',
            'required': 'required',
        }
    )
    url = FileField(
        label='文件',
        validators=[
            DataRequired(message='请上传文件！'),
        ],
        description='文件',
    )
    intro = TextAreaField(
        label='简介',
        validators=[
            DataRequired(message='请输入简介！'),
        ],
        description='简介',
        render_kw={
            'class': 'form-control',
            'rows': 10,
        }
    )
    logo = FileField(
        label='封面',
        validators=[
            DataRequired(message='请上传封面！'),
        ],
        description='封面',
    )
    star = SelectField(
        label='星级',
        validators=[
            DataRequired(message='请选择星级！'),
        ],
        coerce=int,
        choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星'), ],
        description='星级',
        render_kw={
            'class': 'form-control',
        }
    )
    tag_id = SelectField(
        label='标签',
        validators=[
            DataRequired(message='请输入标签！'),
        ],
        coerce=int,
        choices=[],
        description='标签',
        render_kw={
            'class': 'form-control',
        }
    )
    area = StringField(
        label='地区',
        validators=[
            DataRequired(message='请输入地区！'),
        ],
        description='地区',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入地区！',
        }
    )
    length = StringField(
        label='片长',
        validators=[
            DataRequired(message='请输入片长！'),
        ],
        description='片长',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入片长！',
        }
    )
    publish_time = StringField(
        label='上映日期',
        validators=[
            DataRequired(message='请选择上映日期！'),
        ],
        description='上映日期',
        render_kw={
            'class': 'form-control',
            'placeholder': '请选择上映日期！',
            'id': 'input_publish_time',
        }
    )
    submit = SubmitField(
        label='编辑',
        render_kw={
            'class': 'btn btn-primary',
        }
    )

    def __init__(self, movie=None):
        super().__init__()
        self.tag_id.choices = [(int(tag.id), tag.name) for tag in Tag.query.all()]
        if movie is not None:
            self.intro.data = movie.intro
            self.star.data = int(movie.star)
            self.tag_id.data = movie.tag_id
            pass

    def validate_name(self, field):
        if Movie.query.filter_by(name=field.data).first():
            raise ValidationError('昵称被占用')
