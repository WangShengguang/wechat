import time
from _datetime import datetime
from datetime import timedelta

import schedule

from local_config import Persons
from wechat.api.funny import Funny
from wechat.api.hefeng import Hefeng
from wechat.api.juhe import Juhe
from wechat.tyc.draw_picture import weather_pic_name, draw_tmp_pop_picture
from wechat.tyc.robot import WechatRobot
from wechat.tyc.tools import get_lot_lat


class Service(object):
    def __init__(self):
        self.wechat_robot = WechatRobot()
        self.juhe = Juhe()
        self.funny = Funny()

    def draw_hourly_chart(self, city_str, date_str):
        """绘制逐小时降雨图路"""
        hefeng = Hefeng(get_lot_lat(city_str))
        hourlys = hefeng.get_hourly_weather()["HeWeather6"][0]["hourly"]
        tmps = []
        pops = []
        x = []
        for hour_weather in hourlys:
            # print("date_str: {}".format(date_str))
            # print(hour_weather["time"].split(" ")[0])
            if date_str == hour_weather["time"].split(" ")[0]:
                hour, minute = hour_weather["time"].split(" ")[1].split(':')
                x.append(int(hour))
                tmps.append(int(hour_weather["tmp"]))
                pops.append(int(hour_weather["pop"]))
        date_str = "{}月{}日".format(*date_str.split("-")[1:])
        pic_title = "{}{}温度及降雨概率图".format(city_str, date_str)
        draw_tmp_pop_picture(pic_title, x, pops, tmps)
        return hourlys, pops

    def parse_hourlys(self, hourlys):
        """
        解析hourly ，未来24小时每小时天气
        tmp:温度，cond_txt:天气状况(多云)，pop:降雨概率，time:预报时间
        :param hourlys:
        :return:  hourly_weather_str
        """
        print("** common hourlys： {}".format(hourlys))
        hourly_weather = ""
        for hour_weather in hourlys:
            pop = int(hour_weather["pop"])
            if pop >= 50:  # 降雨概率
                hour, minute = hour_weather["time"].split(" ")[1].split(':')
                offset = (24 + int(hour) - int(datetime.now().hour)) % 24
                if offset < 5:
                    # doto 降雨概率图
                    hourly_weather = "，未来{}小时（{}）可能有降雨，降雨概率{}%，请注意携带雨具".format(
                        offset, hour + ":00", pop)
                # now_msg.append(hourly_weather)
                break
        hourly_weather = hourly_weather if hourly_weather else "，未来5小时内降雨概率小于50%"
        return hourly_weather

    def parse_days(self, daily_forecast, draw_hourly_pops, date_str):
        """
        解析指定天的天气预报返回
        :param daily_forecast: list未来三天天气
        :param draw_hourly_pops: 逐小时天气
        :param date_str: 指定日期
        :return:
        """
        # 当前天气
        # fl:体感温度,cond_txt:天气状况描述,tmp:温度,pcpn:降水量
        # now_weather = "当前{}，温度{}℃，体感温度{}℃，{}".format(
        #     now["cond_txt"], now["tmp"], now["fl"], pcpn_str)
        # now_weather = "当前温度{}℃，体感温度{}℃".format(now["tmp"], now["fl"])
        # now_msg.append(now_weather)
        # 解析daily_forecast，未来三天天气
        # date:预报日期,cond_txt_d:白天天气,cond_txt_n:夜间天气,tmp_max:最高温度,tmp_min:最低温度,pop:降水概率
        # strptime(timestring, '%Y-%m-%d %H:%M:%S')
        selected_date = datetime.strptime(date_str, '%Y-%m-%d')
        offset_days = (selected_date - datetime.now()).days
        date_human = ["今天", "明天", "后天"][offset_days]
        for day in daily_forecast:
            if day["date"] == date_str:
                selected_day = day
        icon_dic = {"晴": "🌤", "雨": "🌧", "阴": " ️🌥️"}
        icon = ""
        if "雨" in selected_day["cond_txt_d"]:
            icon = icon_dic["雨"]
        elif "阴" in selected_day["cond_txt_d"] or "云" in selected_day["cond_txt_d"]:
            icon = icon_dic["阴"]
        elif "晴" in selected_day["cond_txt_d"]:
            icon = icon_dic["晴"]
        # today["pop"] 不准
        day_pop = max(draw_hourly_pops)
        day_weather = "{}{}{}，温度{}~{}℃".format(
            date_human, selected_day["cond_txt_d"], icon.strip(), selected_day["tmp_min"],
            selected_day["tmp_max"])
        if day_pop > 0:
            day_weather += "，降雨概率{}%".format(day_pop)
        if day_pop > 10:
            day_weather += " 🌂"
        return selected_day, day_weather

    def orginize_weather(self, city_str, date_str):
        """
        绘制逐小时降雨图；
        将接口信息重新组织为适合阅读的形式，返回
        """
        hefeng = Hefeng(get_lot_lat(city_str))
        # 绘制温度降雨小时图
        hourlys, draw_hourly_pops = self.draw_hourly_chart(city_str, date_str)  # 描绘出date_str指定日期的逐小时降雨图
        basic, now, lifestyle, dailys = hefeng.get_weather()
        # 指定 date_str 的天气信息
        selected_day, day_weather_str = self.parse_days(dailys, draw_hourly_pops, date_str)
        # 未来几小时的天气情况
        hourly_weather_str = self.parse_hourlys(hourlys)
        # 生活指数
        lifestyle_str = self.parse_lifestyle(lifestyle)
        # sr日出 ss日落
        return selected_day, hourly_weather_str, day_weather_str, lifestyle_str

    def parse_lifestyle(self, lifestyle):
        # # 解析，生活指数
        indexes = {'舒适度指数': 'comf', '洗车指数': 'cw', '穿衣指数': 'drsg', '感冒指数': 'flu',
                   '运动指数': 'sport', '旅游指数': 'trav', '紫外线指数': 'uv', '空气污染扩散条件指数': 'air',
                   '空调开启指数': 'ac', '过敏指数': 'ag', '太阳镜指数': 'gl', '化妆指数': 'mu',
                   '晾晒指数': 'airc', '交通指数': 'ptfc', '钓鱼指数': 'fsh', '防晒指数': 'spi'}
        lifestyle = {index["type"]: index for index in lifestyle}  # type,brf,txt
        lifestyle_str = "穿衣指数：{}。{}".format(lifestyle["drsg"]["brf"], lifestyle["drsg"]["txt"].split("。")[0])
        return lifestyle_str

    def parse_poem(self):
        """解析诗词api返回可读字符串"""
        poem = self.funny.get_today_poem()
        # poem_content_str = "{}".format('\n'.join(poem['content']))
        poem_content_li = poem['content']
        if len(poem["content"]) <= 2:
            poem_content_li = poem["content"]
        else:
            pos = poem_content_li.index(poem['bref'])
            if pos == 0:
                poem_content_li = poem_content_li[:2]
            else:
                poem_content_li = poem_content_li[pos - 1:pos + 1]
        if poem["dynasty"] not in ["现代", "五代"]:
            dynasty = poem["dynasty"].rstrip("代")
        else:
            dynasty = poem["dynasty"]
        # if dynasty == "宋":
        #     poem_content_str = "    ".join(poem_content_li)
        # else:
        #     poem_content_str = "\n".join(poem_content_li)
        poem_content_str = "\n".join(poem_content_li)
        fit = 32 - int((len(poem['title']) + len(dynasty) + len(poem["author"])) * 3)
        dynasty = "{}·".format(dynasty)
        poem_end_line = "{}--{}{}·{}".format(' ' * fit, dynasty, poem["author"], poem['title'])
        poem_str = "{}\n\n{}".format(poem_content_str, poem_end_line)
        return poem_str

    def get_date_str(self, date_hum):
        now = datetime.now()
        if date_hum == "今天":
            selected_day = now.day
        elif date_hum == "明天":
            selected_day = (now + timedelta(days=1)).day
        elif date_hum == "后天":
            selected_day = (now + timedelta(days=2)).day
        selected_day = selected_day if selected_day >= 10 else "0{}".format(selected_day)
        month = now.month if now.month >= 10 else "0{}".format(now.month)
        date_str = "{}-{}-{}".format(now.year, month, selected_day)
        return date_str

    def message_to_user(self, needed_send_users=None):
        """获取天气信息发送给tyc"""
        if not needed_send_users:
            needed_send_users = self.needed_send_users
        assert isinstance(needed_send_users, (list, tuple))
        text_msgs, img_paths = self.get_messages()
        # text_msgs, img_paths = (["test"], [weather_pic_name])
        for user_alias in needed_send_users:
            self.wechat_robot.send_msg_to_someone(user_alias, pictute_msgs=img_paths)
        for user_alias in needed_send_users:
            self.wechat_robot.send_msg_to_someone(user_alias, text_msgs=text_msgs)

    def get_messages(self):
        """
        获取各种需要发送的信息字符串
        :return:
        """
        # 城市名，用以获取天气预报
        city_str = Persons.tyc.province + Persons.tyc.city
        # 某一天 date_str ; >18时选择预报明天，<18时预报今天
        date_hum = "今天" if datetime.now().hour < 18 else "明天"
        date_str = self.get_date_str(date_hum)
        print("*** get_messages  date_hum: {}, date_str: {}".format(date_hum, date_str))
        selected_day, hourly_weather_str, selected_day_weather_str, lifestyle_str = self.orginize_weather(
            city_str, date_str)
        if date_hum == "今天" or date_hum == "明天":
            selected_day_weather_str += "\n---\n" + lifestyle_str
        selected_day_sr, selected_day_ss = selected_day["sr"], selected_day["ss"]
        morning_greeting_str = "早上好呀~  ,今天上海日出时间{}，日落时间{}。".format(selected_day_sr, selected_day_ss)
        # 历史上的今天
        history_today = self.juhe.get_history_today(month=datetime.now().month, day=datetime.now().day)
        history_today_str = history_today.lstrip("在")
        history_today_str = history_today_str.rstrip("。")  # + "[奸笑]"
        # 诗词
        poem_str = self.parse_poem()
        # msgs 待发送消息列表
        # text_msgs = [morning_greeting_str, hourly_weather_str, history_today_str, selected_day_weather_str, poem_str]
        note_str = "\n---\n".join([morning_greeting_str, history_today_str])
        text_msgs = [note_str, selected_day_weather_str, poem_str]
        image_paths = [weather_pic_name]
        return text_msgs, image_paths

    def tyc_task(self, message_time_str="", needed_send_users=("wsg", "tyc"), robot=False):
        """
        新增定时任务
        :param message_time_str:  定时任务触发时间，没有则选择日出
        :return:
        """
        if robot:
            self.wechat_robot.run()  # 注册机器人等
        if not isinstance(needed_send_users, (list, tuple)):
            needed_send_users = [needed_send_users]
        self.needed_send_users = needed_send_users
        # self.message_time_str= ""  # "06:03" ,日出时间，发送信息的时间
        if not message_time_str:
            city_str = Persons.tyc.province + Persons.tyc.city
            # 某一天 date_str ; >18时选择预报明天，<18时预报今天
            date_hum = "今天" if datetime.now().hour < 18 else "明天"
            date_str = self.get_date_str(date_hum)
            selected_day = self.orginize_weather(city_str, date_str)[0]
            selected_day_sr, selected_day_ss = selected_day["sr"], selected_day["ss"]
            message_time_str = selected_day_sr  # 日出发送消息
        print("** tyc_task message_time_str: {}".format(message_time_str))
        schedule.every().day.at(message_time_str).do(self.message_to_user)

    def test(self):
        selected_time = datetime.now() + timedelta(minutes=1)
        # selected_day = selected_time.day if selected_time.day >= 10 else "0{}".format(selected_time.day)
        # month = selected_time.month if selected_time.month >= 10 else "0{}".format(selected_time.month)
        hour = selected_time.hour if selected_time.hour >= 10 else "0{}".format(selected_time.hour)
        minute = selected_time.minute if selected_time.minute >= 10 else "0{}".format(selected_time.minute)
        message_time_str = "{}:{}".format(hour, minute)
        print("*** test message_time_str: {}".format(message_time_str))
        self.tyc_task(message_time_str=message_time_str, needed_send_users=("wsg"), robot=False)
        print('** end while True')
        while True:
            schedule.run_pending()
            time.sleep(1)

    def test_robot(self):
        self.wechat_robot.run()  # 注册机器人等
        while True:
            time.sleep(10)

    def run(self):
        self.tyc_task()
        schedule.every().day.at("03:00").do(self.wechat_robot.run)
        print('** end while True')
        while True:
            schedule.run_pending()
            time.sleep(1)


"""
梅花雪，梨花月，总相思。
--清·张惠言·相见欢·年年负却花期

春犹浅，柳初芽，杏初花。杨柳杏花交影处，有人家。
玉窗明暖烘霞。小屏上、水远山斜。昨夜酒多春睡重，莫惊他。
--宋·程垓·愁倚阑·春犹浅
"""
