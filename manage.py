# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/30
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import app
from models import db

migrate = Migrate(app, db, compare_type=True, compare_server_default=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()