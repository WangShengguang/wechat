import time
from _datetime import datetime

import schedule

from local_config import Persons
from wechat.api.funny import Funny
from wechat.api.juhe import Juhe
from wechat.tyc.draw_picture import weather_pic_name
from wechat.tyc.hefeng import Hefeng
from wechat.tyc.robot import WechatRobot
from wechat.tyc.tools import get_lot_lat


class Service(object):
    def __init__(self):
        self.wechat_robot = WechatRobot()
        self.juhe = Juhe()
        self.funny = Funny()

    def tyc_task(self):
        city_str = Persons.tyc.province + Persons.tyc.city
        hefeng = Hefeng(get_lot_lat(city_str))
        now_weather_str, morning_weather_str, afternoon_weather_str = hefeng.get_weather()
        print("now_weather_str： {}".format(now_weather_str))
        print("morning_weather_str： {}".format(morning_weather_str))
        print("afternoon_weather_str： {}".format(afternoon_weather_str))
        weather_strs = ["【{}】".format(city_str)]

        history_today = self.juhe.get_history_today(month=datetime.now().month, day=datetime.now().day)
        history_today_str = history_today.lstrip("在")
        poem = self.funny.get_today_poem()
        poem_content_str = "{}".format('\n'.join(poem['content']))
        fit = 32 - int(len(poem['title']) * 3 + len(poem["author"]) * 3)
        poem_end_line = "{}--{}·{}".format(' ' * fit, poem["author"], poem['title'])
        poem_str = "{}\n{}".format(poem_content_str, poem_end_line)
        funny_thing = "{}\n\n{}".format(history_today, poem_str)

        if datetime.now().hour < 18:
            weather_strs.append(morning_weather_str)
            # note = "以下为今天温度及降水概率图"
        else:
            weather_strs.append(afternoon_weather_str)
            # note = "以下为明天温度及降水概率图"
        # weather_strs.append(now_weather_str) #不播报当前状况
        # note = "\n{}\n{}".format('--' * 10, note)
        note = ""
        weather_str = "\n".join(weather_strs) + note
        self.wechat_robot.wsg.send(weather_str)
        self.wechat_robot.wsg.send_image(weather_pic_name)
        self.wechat_robot.wsg.send(history_today_str)
        self.wechat_robot.wsg.send(poem_str)
        # 陶盈春
        self.wechat_robot.tyc.send(weather_str)
        self.wechat_robot.tyc.send_image(weather_pic_name)
        self.wechat_robot.tyc.send(history_today_str)
        self.wechat_robot.tyc.send(poem_str)

    def test(self):
        pass

    def run(self):
        self.wechat_robot.run()  # 注册机器人等
        # schedule.every(10).minutes.do(job)
        # schedule.every().hour.do(job)
        schedule.every().day.at("06:00").do(self.tyc_task)
        schedule.every().day.at("18:00").do(self.tyc_task)
        # schedule.every(5).to(10).minutes.do(job)
        # schedule.every().monday.do(job)
        # schedule.every().wednesday.at("13:15").do(job)
        # schedule.every().minute.at(":17").do(job)
        print('** end while True')
        while True:
            schedule.run_pending()
            time.sleep(1)
