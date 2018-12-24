from flask import Flask, render_template
from flask_migrate import Migrate

from app.models import db, login_manager


migrate = Migrate()


def page_not_found(error):
    return render_template('404.html'), 404


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.security')
    app.config.from_object('app.settings')

    db.init_app(app)
    migrate.init_app(app=app, db=db)
    login_manager.init_app(app=app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请登录或者注册帐号'

    register_bp(app=app)

    with app.app_context():
        db.create_all(app=app)

    app.errorhandler(404)(page_not_found)

    return app


def register_bp(app):
    from .home import home as home_bp
    from .admin import admin as admin_bp
    from .auth import auth as auth_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

