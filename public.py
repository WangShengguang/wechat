#!/usr/bin/env python

import os

from flask_script import Manager, Shell

from wechat.public import create_app, db
from wechat.public.models import Message
from wechat.utils.logger import logging_config

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Message=Message)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def deploy():
    db.create_all()


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    logging_config('wechat.log')
    manager.run()
