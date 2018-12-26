from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField, FileField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired


from app.models import Tag


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
        label='编辑',
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

    def __init__(self):
        super().__init__()
        self.tag_id.choices = [(int(tag.id), tag.name) for tag in Tag.query.all()]


class PreviewForm(FlaskForm):
    title = StringField(
        label='预告标题',
        validators=[
            DataRequired(message='请输入预告标题！'),
        ],
        description='预告标题',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入预告标题！',
            'required': 'required',
        }
    )
    logo = FileField(
        label='封面',
        validators=[
            DataRequired(message='请上传封面！'),
        ],
        description='封面',
    )
    submit = SubmitField(
        label='编辑',
        render_kw={
            'class': 'btn btn-primary',
        }
    )
