# -*- coding:utf-8 -*-

import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guss string.'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = '1085092799@qq.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = os.environ.get('FLASKY_POSTS_PER_PAGE') or 20

    # whoosh索引数据库位置
    # WHOOSH_BASE = 'mysql://root:password@localhost/search.db'

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '1085092799@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    whiski_db_uri = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8'.format(**DBConfig.local)
    SQLALCHEMY_DATABASE_URI = whiski_db_uri


config = DevelopmentConfig()
