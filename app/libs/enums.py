from enum import Enum


class AuthEnum(Enum):
    User = 0
    Admin = 1
    SuperAdmin = 99

    @classmethod
    def auth_str(cls, key):
        return {
            cls.User: '普通用户',
            cls.Admin: '管理员',
            cls.SuperAdmin: '超级管理员',
        }[key]


class RoleEnum(Enum):
    User = 0
    Admin = 1
    TagAdmin = 2
    MovieAdmin = 3
    PreviewAdmin = 4
    LogAdmin = 5
    UserAdmin = 6
    SuperAdmin = 99

    @classmethod
    def role_str(cls, key):
        return {
            cls.User: '普通用户',
            cls.Admin: '普通管理员',
            cls.TagAdmin: '标签管理员',
            cls.MovieAdmin: '影片管理员',
            cls.PreviewAdmin: '预告管理员',
            cls.LogAdmin: '日志管理员',
            cls.UserAdmin: '用户管理员',
            cls.SuperAdmin: '超级管理员',
        }[key]

    def __iter__(self):
        for attr in dir(self.__class__):
            if not callable(getattr(self.__class__, attr)) and not attr.startswith("__"):
                yield attr


def main():
    pass


if __name__ == '__main__':
    main()

