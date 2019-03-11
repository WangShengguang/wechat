import os
import platform
import queue
import time

from wxpy import *

from local_config import LocalConfig
from wechat.config import data_dir

platform_name = platform.system()

xiaobing_queue = queue.Queue()  # 先进先出；线程安全


def login():
    console_qr = False
    if platform_name == "Linux":
        console_qr = 2
    bot = Bot(cache_path=True, console_qr=console_qr)
    return bot


class RecordTool():
    def __init__(self):
        self.media_path = os.path.join(data_dir, "media")

    def store_media(self, msg):
        picture_raw = msg.raw["Text"]()
        with open(self.media_path, "wb") as f:
            f.write(picture_raw)


class WechatRobot(object):
    def __init__(self):
        self.record_tool = RecordTool()
        self.tuling = Tuling(LocalConfig.tuling.WX_robot_apikey)  # 自己key一天100
        self.tuling = Tuling()
        # self.xiaoi = XiaoI(LocalConfig.xiaoi.key, LocalConfig.xiaoi.Secret)
        # 初始化机器人，扫码登陆
        self.bot = login()
        wsg_name = "robot" if self.bot.self.name == "王胜广" else "王胜广"
        self.wsg = ensure_one(self.bot.friends().search(wsg_name, sex=MALE))
        self.tyc = ensure_one(self.bot.friends().search('春春', province="辽宁", city="丹东"))
        self.xiaobing = ensure_one(self.bot.mps().search("小冰", province="北京", city='海淀'))

    def chat_bot(self):
        wechats = [self.wsg, self.tyc]

        # @self.bot.register(chats=wechats)
        def tuling_bot(msg):
            if msg.type == "Text":
                self.tuling.do_reply(msg)

        @self.bot.register(chats=wechats)
        def xiaobing_bot(msg):
            print(msg)
            if msg.type == "Text":
                self.xiaobing.send(msg.text)
            else:
                self.record_tool.store_media(msg)
                if msg.type == "Picture":
                    self.xiaobing.send_image(self.record_tool.media_path)  # msg.raw["Text"]())
            # 从小冰获取结果
            while xiaobing_queue.empty():
                time.sleep(0.01)  # 0.1秒则代表休眠100毫秒
            while not xiaobing_queue.empty():
                result_msg = xiaobing_queue.get()
                if result_msg.type == "Text":
                    msg.reply_msg(result_msg.text)
                else:
                    self.record_tool.store_media(result_msg)  #
                    msg.reply_image(self.record_tool.media_path)  # 回复图片，给msg发送者回复消息

    def tyc_task(self):
        bot = self.bot

    def wsg_task(self):
        # 回复 my_friend 的消息 (优先匹配后注册的函数!)
        @self.bot.register(self.wsg)
        def reply_myself(msg):
            result = 'received: {} ({})'.format(msg.text, msg.type)
            return msg.text

    def xiaobing_task(self):
        # 微软小冰
        @self.bot.register(self.xiaobing)
        def handle(msg):
            # print("小冰：", msg)
            xiaobing_queue.put(msg)

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

    def send_msg_to_someone(self, user_name, text_msgs=(), pictute_msgs=()):
        user = {"tyc": self.tyc, "wsg": self.wsg}.get(user_name)
        print("** user_name:{} send to {}".format(user_name, user))
        for text in text_msgs:
            user.send_msg(text)
        for pic_path in pictute_msgs:
            if os.path.exists(pic_path):
                user.send_image(pic_path)

    def run(self):
        print("微信任务注册成功")
        # 后注册会覆盖前者注册结果
        self.general_task()  # 通用注册函数需要放在第一个
        self.chat_bot()
        # self.wsg_task()
        self.tyc_task()
        self.xiaobing_task()
        # while True:
        #     time.sleep(10)
        # 或者仅仅堵塞线程
        # bot.join()
