import random

from app.models import User
from app.libs.enums import RoleEnum, AuthEnum
from app import db, create_app


def create_super_admin():
    if User.query.filter_by(email='super_admin@admin.com').first():
        return
    user = User()
    with db.auto_commit():
        user.name = 'super_admin'
        user.email = 'super_admin@admin.com'
        user.phone = '98765432121'
        user.confirm = 1
        user.intro = 'super admin'
        user.auth = AuthEnum.SuperAdmin
        user.role = RoleEnum.SuperAdmin
        user.password = '123asd'
        db.session.add(user)


def create_admin_user(num):
    user_lst = []
    for i in range(1, num+1):
        user = User()
        user.name = f'admin{i}'
        user.email = f'admin{i}@admin.com'
        user.phone = '187' + ''.join(str(random.randint(0, 9)) for _ in range(8))
        user.confirm = 1
        user.intro = 'admin user'
        user.auth = AuthEnum.Admin
        user.role = RoleEnum.Admin
        user.password = '123asd'
        user_lst.append(user)

    with db.auto_commit():
        db.session.add_all(user_lst)


def create_user(num):
    user_lst = []
    for i in range(1, num+1):
        user = User()
        user.name = f'test{i}'
        user.email = f'test{i}@test.com'
        user.phone = '131' + ''.join(str(random.randint(0, 9)) for _ in range(8))
        user.confirm = 1
        user.intro = 'normal user'
        user.auth = AuthEnum.User
        user.role = RoleEnum.User
        user.password = '123asd'
        user_lst.append(user)

    with db.auto_commit():
        db.session.add_all(user_lst)


def main():
    app = create_app()
    with app.app_context():
        create_super_admin()
        create_admin_user(10)
        create_user(50)


if __name__ == '__main__':
    main()

