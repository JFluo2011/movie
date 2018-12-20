from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from ..models import User


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
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('昵称被占用')

    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).first():
            raise ValidationError('手机已经被使用')


class UserInfoForm(EmailForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired(message='请输入昵称！'),
            Length(min=5, max=20, message='昵称应在5-20个字符之间'),
        ],
        description='昵称',
        render_kw={
            'class': 'form-control',
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
            'class': 'form-control',
            'placeholder': '请输入手机号！',
            'required': 'required',
        }
    )
    avatar = FileField(
        label='头像',
        validators=[
            DataRequired(message='请上传头像！'),
        ],
        description='头像',
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

    submit = SubmitField(
        label='保存修改',
        render_kw={
            'class': 'btn btn-success',
        }
    )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        label='旧密码',
        validators=[
            DataRequired(message='请输入旧密码！'),
        ],
        description='旧密码',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入旧密码！',
        }
    )
    new_password = PasswordField(
        label='新密码',
        validators=[
            DataRequired(message='请输入新密码！'),
            Length(min=6, max=32, message='密码长度为:6-32位字符'),
        ],
        description='新密码',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入新密码！',
        }
    )
    submit = SubmitField(
        label='编辑',
        render_kw={
            'class': 'btn btn-success',
        }
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label='内容',
        validators=[
            DataRequired(message='请输入内容！'),
        ],
        description='内容',
        render_kw={
            'id': 'input_content',
        }
    )
    submit = SubmitField(
        label='提交',
        render_kw={
            'class': 'btn btn-success',
            'id': 'btn-sub',
        }
    )
