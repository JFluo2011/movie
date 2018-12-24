from flask import render_template
from flask_login import login_required

from .. import admin
from ...libs.permissions import admin_required


@admin.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')
