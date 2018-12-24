# from flask import abort
#
#
# class Role:
#     allow_endpoint = set()
#     allow_bp = set()
#     forbidden_bp = set()
#     forbidden_endpoint = set()
#
#     def __init__(self):
#         self._valid()
#
#     def _valid(self):
#         for rule in self.allow_endpoint:
#             if (not rule.startswith('/')) or (not rule.endswith('/')):
#                 abort(404)
#
#         for rule in self.forbidden_endpoint:
#             if (not rule.startswith('/')) or (not rule.endswith('/')):
#                 abort(404)
#
#         for rule in self.allow_bp:
#             if rule.startswith('/') or rule.endswith('/'):
#                 abort(404)
#
#         for rule in self.forbidden_bp:
#             if rule.startswith('/') or rule.endswith('/'):
#                 abort(404)
#
#     def __add__(self, other):
#         self.allow_endpoint += other.allow_endpoint
#         self.allow_bp += other.allow_bp
#         self.forbidden_endpoint += other.forbidden_endpoint
#         return self
#
#
# class User(Role):
#     allow_endpoint = {
#         '/login/',
#         '/logout/',
#         '/register/',
#         '/change_password/',
#         '/user_login_log/list/',
#     }
#     allow_bp = {'home'}
#     forbidden_bp = {'admin'}
#
#
# class Admin(Role):
#     allow_endpoint = {
#         '/login/',
#         '/logout/',
#         '/register/',
#         '/change_password/',
#         '/admin/user/list/',
#     }
#     allow_bp = {'home'}
#
#
# class SuperAdmin(Role):
#     allow_bp = {'user', 'admin', 'home'}
#
#
# class UserAdmin(Role):
#     allow_endpoint = {
#         '/admin/user/view/',
#         '/admin/user/del/',
#     }
#
#     def __init__(self):
#         self + Admin()
#         super().__init__()
#
#
# class TagAdmin(Role):
#     allow_endpoint = {
#         '/admin/tag/add/',
#         '/admin/tag/edit/',
#         '/admin/tag/del/',
#         '/admin/tag/list/',
#     }
#
#     def __init__(self):
#         self + Admin()
#         super().__init__()
#
#
# class MovieAdmin(Role):
#     allow_endpoint = {
#         '/admin/movie/add/',
#         '/admin/movie/edit/',
#         '/admin/movie/del/',
#         '/admin/movie/list/',
#     }
#
#     def __init__(self):
#         self + Admin()
#         super().__init__()
#
#
# class PreviewAdmin(Role):
#     allow_endpoint = {
#         '/admin/preview/add/',
#         '/admin/preview/edit/',
#         '/admin/preview/del/',
#         '/admin/preview/list/',
#     }
#
#     def __init__(self):
#         self + Admin()
#         super().__init__()
#
#
# class PermissionAdmin(Role):
#     allow_endpoint = {
#         '/admin/permission/add/',
#         '/admin/permission/edit/',
#         '/admin/permission/del/',
#         '/admin/permission/list/',
#     }
#
#     def __init__(self):
#         self + Admin()
#         super().__init__()
#

from functools import wraps

from flask import current_app, abort

from .enums import RoleEnum


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role not in [RoleEnum.User]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def tag_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.TagAdmin, RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def movie_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.MovieAdmin, RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def preview_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.PreviewAdmin, RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def log_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.LogAdmin, RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def user_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.UserAdmin, RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator


def super_admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.role in [RoleEnum.SuperAdmin]:
            return f(args, kwargs)
        raise abort(403)

    return decorator

