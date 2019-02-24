import traceback
from functools import wraps

from wxpy import *


def login():
    return Bot(cache_path=True, logout_callback=login)


def try_catch_rebot(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            logging.error(traceback.format_exc())
            Bot(cache_path=True, logout_callback=Bot)

    return wrapper


class WechatRobot(object):
    def __init__(self):
        # 初始化机器人，扫码登陆
        self.bot = login()
        self.wsg = ensure_one(self.bot.friends().search('robot', sex=MALE))
        self.tyc = ensure_one(self.bot.friends().search('春春', province="辽宁", city="丹东"))

    def tyc_task(self):
        bot = self.bot

    def wsg_task(self):
        # 回复 my_friend 的消息 (优先匹配后注册的函数!)
        @self.bot.register(self.wsg)
        def reply_myself(msg):
            return 'received: {} ({})'.format(msg.text, msg.type)

    def xiaobing_task(self):
        # 微软小冰
        xiaobing = ensure_one(self.bot.mps().search("小冰", province="北京", city='海淀'))

        @self.bot.register(xiaobing)
        def print_others(msg):
            print("小冰：", msg)

    def general_task(self):
        # 自动接受新的好友请求
        @self.bot.register(msg_types=FRIENDS)
        def auto_accept_friends(msg):
            # 接受好友请求
            new_friend = msg.card.accept()
            # 向新的好友发送消息
            new_friend.send('哈哈，我自动接受了你的好友请求')

        # 打印来自其他好友、群聊和公众号的消息
        @self.bot.register()
        def print_others(msg):
            print(msg)

    def run(self):
        self.tyc_task()
        self.wsg_task()
        self.general_task()
        self.xiaobing_task()
        # while True:
        #     time.sleep(10)
        # 或者仅仅堵塞线程
        # bot.join()
