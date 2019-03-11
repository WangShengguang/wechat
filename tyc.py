from wechat.tyc.service import Service
from wechat.utils.logger import logging_config


def run_server():
    logging_config('tyc.log', "..")
    Service().test_robot()
    # Service().test()
    # Service().run()


def deploy():
    from wechat.tyc.dao.models.wx_models import create_all
    create_all()


if __name__ == "__main__":
    run_server()
