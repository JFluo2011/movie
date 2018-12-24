from flask import flash, redirect, url_for, render_template, current_app
from flask_login import login_required

from app.admin import admin
from app.admin.forms import PermissionForm
from app.libs.permissions import super_admin_required
from app.models import Permission, db


@admin.route('/permission/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def permission_add():
    form = PermissionForm()
    if form.validate_on_submit():
        permission = Permission()
        msg, type_ = permission.add(form)
        flash(msg, type_)
        return redirect(url_for('admin.permission_add'))

    return render_template('admin/permission_add.html', form=form)


@admin.route('/permission/list/<int:page>/')
@login_required
@super_admin_required
def permission_list(page=None):
    if page is None:
        page = 1
    page_data = Permission.query.order_by(
        Permission.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/permission_list.html', page_data=page_data)


@admin.route('/permission/del/<int:permission_id>/', )
@login_required
@super_admin_required
def permission_del(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    with db.auto_commit():
        db.session.delete(permission)
    flash('删除权限成功', 'message')
    return redirect(url_for('admin.permission_list', page=1))


@admin.route('/permission/edit/<int:permission_id>/', methods=['GET', 'POST'])
@login_required
@super_admin_required
def permission_edit(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    form = PermissionForm()

    if form.validate_on_submit():
        msg, type_ = permission.update(form)
        flash(msg, type_)
        return redirect(url_for('admin.permission_edit', permission_id=permission.id))

    return render_template('admin/permission_edit.html', form=form, permission=permission)
