from datetime import datetime

from flask import Blueprint

admin = Blueprint('admin', __name__)

import app.admin.views


@admin.context_processor
def inject_online_time():
    return {
        'online_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
