#!/usr/bin/env python
# coding=utf-8

from app import create_app, db  # bgone为顶层包，不能再用相对路径
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Role, Post

app = create_app('production')
site = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


site.add_command('shell', Shell(make_context=make_shell_context))
site.add_command('db', MigrateCommand)

if __name__ == '__main__':
    site.run()
