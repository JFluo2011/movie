import time
import stat
import random

from werkzeug.datastructures import FileStorage
from werkzeug.test import EnvironBuilder

from app.models import User, Movie, Tag, Preview
from app.libs.enums import RoleEnum, AuthEnum
from app import db, create_app
from app.admin.forms import MovieForm, TagForm, PreviewForm
from app.auth.forms import RegisterForm
from app.libs.utils import make_dirs

permission = stat.S_IREAD | stat.S_IWUSR
movie_lst = ['复仇者联盟4--预告片.mp4', '星球大战8预告片.mp4']
movie_logo_lst = ['星球大战8.jpg', '复仇者联盟4封面.jpg']
title_lst = [
    ('星球大战', '科幻', '美国'),
    ('环太平洋', '科幻', '美国'),
    ('变形金刚', '科幻', '美国'),
    ('谍影重重', '动作', '美国'),
    ('碟中谍', '动作', '美国'),
    ('复仇者联盟', '科幻', '美国'),
    ('神探夏洛克', '悬疑', '英国'),
    ('洛奇', '动作', '美国'),
    ('第一滴血', '热血', '美国'),
    ('魔戒', '魔幻', '美国'),
    ('三傻大闹宝莱坞', '喜剧', '印度'),
    ('爱乐之城', '爱情', '美国'),
    ('逍遥法外', '喜剧', '美国'),
    ('金蝉脱壳', '动作', '美国'),
    ('拯救大兵瑞恩', '战争', '美国'),
    ('血战钢锯岭', '战争', '美国'),
    ('楚门的世界', '喜剧', '美国'),
    ('生化危机', '恐怖', '美国'),
    ('后天', '灾难', '美国'),
    ('2012', '灾难', '美国'),
    ('星际迷航', '科幻', '美国'),
    ('异形', '恐怖', '美国'),
    ('真实的谎言', '爱情', '美国'),
    ('人在囧途', '喜剧', '中国'),
]


def gen_date():
    a1 = (1976, 1, 1, 0, 0, 0, 0, 0, 0)
    a2 = (1990, 12, 31, 23, 59, 59, 0, 0, 0)
    start = time.mktime(a1)
    end = time.mktime(a2)

    return time.strftime("%Y-%m-%d", time.localtime(random.randint(start, end)))


class Create:
    def __init__(self, app):
        self.app = app
        with self.app.app_context():
            make_dirs(app.config['UP_DIR'], permission=permission)
            make_dirs(app.config['MOVIE_PATH'], permission=permission)
            make_dirs(app.config['PREVIEW_PATH'], permission=permission)
            make_dirs(app.config['AVATAR_PATH'], permission=permission)

    def __call__(self, *args, **kwargs):
        func_lst = []
        for attr in dir(self.__class__):
            func = getattr(self.__class__, attr)
            if callable(func) and attr.startswith("create"):
                func_lst.append(func)

        with self.app.app_context():
            with self.app.request_context(EnvironBuilder('/', 'http://localhost/').get_environ()):
                for func in func_lst:
                    func(self)


class CreateUser(Create):
    def create_super_admin(self):
        if User.query.filter_by(email='super_admin@admin.com').first():
            return
        file_name = f'media\\avatar\\{random.randint(1, 43)}.jpg'
        with open(file_name, 'rb') as f:
            user = User()
            form = RegisterForm()
            form.name.data = 'super_admin'
            form.email.data = 'super_admin@admin.com'
            form.phone.data = '98765432121'
            form.avatar.data = FileStorage(f)
            form.password.data = '123asd'
            form.repassword.data = '123asd'
            user.confirm = 1
            user.intro = 'super admin'
            user.auth = AuthEnum.SuperAdmin
            user.role = RoleEnum.SuperAdmin
            user.add(form, record_log=False)

    def create_admin_user(self, num=10):
        role_lst = [
            ('会员管理员', RoleEnum.UserAdmin),
            ('日志管理员', RoleEnum.LogAdmin),
            ('影片管理员', RoleEnum.MovieAdmin),
            ('预告管理员', RoleEnum.PreviewAdmin),
            ('标签管理员', RoleEnum.TagAdmin),
        ]
        for i in range(1, num + 1):
            file_name = f'media\\avatar\\{random.randint(1, 43)}.jpg'
            with open(file_name, 'rb') as f:
                user = User()
                form = RegisterForm()
                intro, role = random.choice(role_lst)
                form.name.data = f'admin{i}'
                form.email.data = f'admin{i}@admin.com'
                form.phone.data = '187' + ''.join(str(random.randint(0, 9)) for _ in range(8))
                form.avatar.data = FileStorage(f)
                form.password.data = '123asd'
                form.repassword.data = '123asd'
                user.confirm = 1
                user.intro = intro
                user.auth = AuthEnum.Admin
                user.role = role
                user.add(form, record_log=False)

    def create_user(self, num=50):
        for i in range(1, num + 1):
            file_name = f'media\\avatar\\{random.randint(1, 43)}.jpg'
            with open(file_name, 'rb') as f:
                user = User()
                form = RegisterForm()
                form.name.data = f'test{i}'
                form.email.data = f'test{i}@test.com'
                form.phone.data = '131' + ''.join(str(random.randint(0, 9)) for _ in range(8))
                form.avatar.data = FileStorage(f)
                form.password.data = '123asd'
                form.repassword.data = '123asd'
                user.confirm = 1
                user.intro = 'normal user'
                user.auth = AuthEnum.User
                user.role = RoleEnum.User
                user.add(form, record_log=False)


class CreateTag(Create):
    def create_tag(self):
        name_lst = ['战争', '科幻', '喜剧', '动作', '灾难', '魔幻', '热血', '爱情', '恐怖', '悬疑']
        for name in name_lst:
            tag = Tag()
            form = TagForm()
            form.name.data = name
            tag.add(form, record_log=False)


class CreateMovie(Create):
    def create_movie(self, num=20):
        star_lst = []
        for i in range(1, 6):
            star_lst.extend([i] * i)
        for i in range(1, num + 1):
            file_name = f'media\\{random.choice(movie_lst)}'
            file_name_logo = f'media\\{random.choice(movie_logo_lst)}'
            with open(file_name, 'rb') as f, open(file_name_logo, 'rb') as f_logo:
                movie = Movie()
                form = MovieForm()
                title, tag_name, area = random.choice(title_lst)
                form.title.data = f'{title}-{i}'
                form.tag_id.data = Tag.query.filter_by(name=tag_name).first().id
                form.url.data = FileStorage(f)
                form.logo.data = FileStorage(f_logo)
                form.area.data = area
                form.intro.data = f'{title}-{i}'
                form.star.data = random.choice(star_lst)
                form.length.data = random.randint(90, 150)
                form.publish_time.data = gen_date()
                movie.add(form, record_log=False)


class CreatePreview(Create):
    def create_preview(self, num=20):
        for i in range(1, num + 1):
            file_name = f'media\\{random.choice(movie_logo_lst)}'
            with open(file_name, 'rb') as f:
                preview = Preview()
                form = PreviewForm()
                form.title.data = f'{random.choice(title_lst)[0]}-{i}'
                form.logo.data = FileStorage(f)
                preview.add(form, record_log=False)


def main():
    app = create_app()
    cls_lst = [CreateUser, CreateTag, CreateMovie, CreatePreview]
    # cls_lst = [CreateMovie, CreatePreview]
    for cls in cls_lst:
        cls(app)()


if __name__ == '__main__':
    main()
