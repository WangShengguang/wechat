from wechat.tyc.service import Service
from wechat.utils.logger import logging_config


def run_server():
    logging_config('tyc.log', "..")
    Service().run()


def test():
    pass


if __name__ == "__main__":
    run_server()