from flask import Flask

from .models import db


def create_app():
    app = Flask(__name__)

    db.init_app(app)

    register_bp(app=app)

    with app.app_context():
        db.create_all(app)

    return app


def register_bp(app):
    from .home import home as home_blueprint
    from .admin import admin as admin_blueprint

    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
