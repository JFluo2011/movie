from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


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
