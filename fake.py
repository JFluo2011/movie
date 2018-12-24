import random

from .app.models import User
from .app.libs.enums import RoleEnum, AuthEnum
from .app import db


def create_super_admin():
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


def create_user(num):

    for i in range(num):
        user = User()
        user.name = f'test{i}'
        user.email = f'test{i}@test.com'
        # user.phone = f'131{}'
        user.confirm = 1
        user.intro = 'super admin'
        user.auth = AuthEnum.SuperAdmin
        user.role = RoleEnum.SuperAdmin
        user.password = '123asd'

    with db.auto_commit():
        pass


def main():
    create_super_admin()


if __name__ == '__main__':
    main()

