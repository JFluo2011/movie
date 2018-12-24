from flask import render_template, current_app
from flask_login import login_required, current_user

from .. import admin
from ...models import UserLog, AdminLog, OpLog
from ...libs.permissions import log_admin_required, admin_required


@admin.route('/oplog/list/<int:page>')
@login_required
@log_admin_required
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = OpLog.query.filter_by(admin_id=current_user.id).order_by(
        OpLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/oplog_list.html', page_data=page_data)


@admin.route('/admin_login_log/list/<int:page>/')
@login_required
@log_admin_required
def admin_login_log_list(page=None):
    if page is None:
        page = 1
    page_data = AdminLog.query.filter_by(admin_id=current_user.id).order_by(
        AdminLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/admin_login_log_list.html', page_data=page_data)


@admin.route('/user_login_log/list/<int:page>/')
@login_required
@admin_required
def user_login_log_list(page=None):
    if page is None:
        page = 1
    page_data = UserLog.query.order_by(
        UserLog.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/user_login_log_list.html', page_data=page_data)

