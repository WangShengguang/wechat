import time
from _datetime import datetime

import schedule

from local_config import Persons
from wechat.tyc.draw_picture import weather_pic_name
from wechat.tyc.hefeng import Hefeng
from wechat.tyc.robot import WechatRobot, try_catch_rebot
from wechat.tyc.tools import get_lot_lat


class Service(object):
    def __init__(self):
        self.wechat_robot = WechatRobot()

    def tyc_task(self):
        city_str = Persons.tyc.province + Persons.tyc.city
        hefeng = Hefeng(get_lot_lat(city_str))
        now_weather_str, morning_weather_str, afternoon_weather_str = hefeng.get_weather()
        print("now_weather_str： {}".format(now_weather_str))
        print("morning_weather_str： {}".format(morning_weather_str))
        print("afternoon_weather_str： {}".format(afternoon_weather_str))
        self.wechat_robot.tyc_task()
        self.wechat_robot.run()
        self.wechat_robot.wsg_task()
        weather_strs = ["【{}】".format(city_str), now_weather_str]
        if datetime.now().hour < 18:
            weather_strs.append(morning_weather_str)
            note = "以下为今天温度及降水概率图"
        else:
            weather_strs.append(afternoon_weather_str)
            note = "以下为明天温度及降水概率图"
        note = "\n{}\n{}".format('--' * 10, note)
        weather_str = "\n\n".join(weather_strs) + note
        self.wechat_robot.wsg.send(weather_str)
        self.wechat_robot.wsg.send_image(weather_pic_name)
        # self.wechat_robot.tyc.send(weather_str)
        # self.wechat_robot.tyc.send_image(weather_pic_name)

    @try_catch_rebot
    def run(self):
        self.tyc_task()
        # schedule.every(10).minutes.do(job)
        # schedule.every().hour.do(job)
        schedule.every().day.at("08:00").do(self.tyc_task)
        # schedule.every(5).to(10).minutes.do(job)
        # schedule.every().monday.do(job)
        # schedule.every().wednesday.at("13:15").do(job)
        # schedule.every().minute.at(":17").do(job)
        print('** end while True')
        while True:
            schedule.run_pending()
            time.sleep(1)
