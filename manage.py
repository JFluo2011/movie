from flask_migrate import MigrateCommand
from flask_script import Manager, Server

from app import create_app


def main():
    app = create_app()
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.add_command('runserver ', Server(host='localhost', port=5000, use_debugger=False))
    manager.run()


if __name__ == '__main__':
    main()
