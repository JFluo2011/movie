from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required

from .. import admin
from ..forms import PreviewForm
from ...models import Preview, db
from ...libs.permissions import preview_admin_required


@admin.route('/preview/add', methods=['GET', 'POST'])
@login_required
@preview_admin_required
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        preview = Preview()
        preview.add(form, record_log=True)
        flash(preview.message, preview.type_)
        return redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html', form=form)


@admin.route('/preview/list/<int:page>')
@login_required
@preview_admin_required
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/preview_list.html', page_data=page_data)


@admin.route('/preview/del/<int:preview_id>/', )
@login_required
@preview_admin_required
def preview_del(preview_id):
    preview = Preview.query.get_or_404(preview_id)
    preview.delete(record_log=True)
    flash(preview.message, preview.type_)
    return redirect(url_for('admin.preview_list', page=1))


@admin.route('/preview/edit/<int:preview_id>/', methods=['GET', 'POST'])
@login_required
@preview_admin_required
def preview_edit(preview_id):
    preview = Preview.query.get_or_404(preview_id)
    form = PreviewForm()
    form.logo.flags.required = False
    form.logo.validators = []

    if form.validate_on_submit():
        preview.update(form, record_log=True)
        flash(preview.message, preview.type_)
        return redirect(url_for('admin.preview_edit', preview_id=preview.id))

    return render_template('admin/preview_edit.html', form=form, preview=preview)
