import os
import uuid
from datetime import datetime

from werkzeug.utils import secure_filename


def gen_filename(data):
    filename = secure_filename(data.filename)
    file_info = os.path.splitext(filename)
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4().hex) + file_info[-1]
    return filename


def make_dirs(path, permission=None):
    if not os.path.exists(path):
        os.makedirs(path)
        if permission is not None:
            os.chmod(path, permission)
