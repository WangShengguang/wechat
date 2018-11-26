# -*- coding:utf-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = "进行此操作前需要登录账号."


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object(config[config_name])
    # config[config_name].init_app()
    # # 以上为原配置,下为采用本地配置
    app.config.from_object(config)
    # app.config.from_pyfile('config.py')  # 是否启用instance的配置

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint, url_prefix='/wechat')  ## 如果使用了这个参数，注册后蓝本中定义的 所有路由都会加上指定的前缀，即这个例子中的 /wechat

    return app
