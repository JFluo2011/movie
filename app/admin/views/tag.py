from flask import flash, redirect, url_for, render_template, current_app
from flask_login import login_required

from .. import admin
from ..forms import TagForm
from ...models import Tag
from ...libs.permissions import tag_admin_required


@admin.route('/tag/add', methods=['GET', 'POST'])
@login_required
@tag_admin_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag()
        tag.add(form, record_log=True)
        flash(tag.message, tag.type_)
        return redirect(url_for('admin.tag_add'))

    return render_template('admin/tag_add.html', form=form)


@admin.route('/tag/list/<int:page>')
@login_required
@tag_admin_required
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.create_time.desc()
    ).paginate(page=page, per_page=current_app.config['PER_PAGE'])
    return render_template('admin/tag_list.html', page_data=page_data)


@admin.route('/tag/edit/<int:tag_id>/', methods=['GET', 'POST'])
@login_required
@tag_admin_required
def tag_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm()
    if form.validate_on_submit():
        tag.update(form, record_log=True)
        flash(tag.message, tag.type_)
        return redirect(url_for('admin.tag_edit', tag_id=tag.id))

    return render_template('admin/tag_edit.html', form=form, tag=tag)


@admin.route('/tag/del/<int:tag_id>/')
@login_required
@tag_admin_required
def tag_del(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.delete(record_log=True)
    flash(tag.message, tag.type_)
    return redirect(url_for('admin.tag_list', page=1))
