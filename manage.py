import stat

from flask_migrate import MigrateCommand
from flask_script import Manager, Server

from app import create_app
from app.libs.utils import make_dirs


def main():
    permission = stat.S_IREAD | stat.S_IWUSR
    app = create_app()
    make_dirs(app.config['UP_DIR'], permission=permission)
    make_dirs(app.config['MOVIE_PATH'], permission=permission)
    make_dirs(app.config['PREVIEW_PATH'], permission=permission)
    make_dirs(app.config['AVATAR_PATH'], permission=permission)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.add_command('runserver ', Server(host='localhost', port=5000, use_debugger=False))
    manager.run()


if __name__ == '__main__':
    main()
