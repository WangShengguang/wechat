import os
from datetime import datetime, timedelta

import requests

from wechat.config import Config, data_dir
from wechat.tyc.draw_picture import draw_tmp_pop_picture
from wechat.utils.decorators import try_except_with_logging

hefeng_dir = os.path.join(data_dir, "hefeng")
if not os.path.exists(hefeng_dir):
    os.makedirs(hefeng_dir)


class Hefeng(object):
    def __init__(self, location):
        self.parm = {"location": location, "lang": "zh", "unit": "m", "key": Config.hefeng_key}
        # location=31.26,121.49&lang=zh&unit=m&key=f6a9eb8710ba4a9695a0a8ded4ed44e3

    def load_from_local(self, info_name):
        weather_json_path = os.path.join(hefeng_dir, info_name)
        with open(weather_json_path, "r", encoding="utf-8") as f:
            return eval(f.read())

    def store_to_local(self, info_name, info):
        weather_json_path = os.path.join(hefeng_dir, info_name)
        with open(weather_json_path, "w", encoding="utf-8") as f:
            return f.write(str(info))

    def get_json(self, base_url):
        # print("&".join(["{}={}".format(k, v) for k, v in self.parm.items()]))
        url = base_url + "&".join(["{}={}".format(k, v) for k, v in self.parm.items()])
        res = requests.get(url)
        return res.json()

    def get_hourly_weather(self):
        # return self.load_from_local("hourly.json")
        base_url = "https://api.heweather.net/s6/weather/hourly?"
        grid_hourly = self.get_json(base_url)
        self.store_to_local("hourly.json", grid_hourly)  # 存储到本地
        return grid_hourly

    def get_air_quality(self):
        air_quality_url = "https://api.heweather.net/s6/air/now?"  # 空气质量实况
        air_quality = self.get_json(air_quality_url)
        return air_quality

    @try_except_with_logging
    def get_weather(self):
        """ 常规天气，weather.json
        https://www.heweather.com/documents/api/s6/weather-all
        :return:
        """
        weather_url = "https://api.heweather.net/s6/weather?"  # 常规天气
        weather = self.get_json(weather_url)
        # weather = self.load_from_local("weather.json")
        print(weather)
        self.store_to_local("weather.json", weather)
        # 基础信息
        # location:地区／城市名称,parent_city:该地区／城市的上级城市，admin_area:该地区／城市所属行政区域
        weather = weather["HeWeather6"][0]
        basic = weather["basic"]
        city_info = "{}市{}区".format(basic["admin_area"], basic["location"])
        now_msg = []
        morning_msg = []
        afternoon_msg = []
        # 当前天气
        # fl:体感温度,cond_txt:天气状况描述,tmp:温度,pcpn:降水量
        now = weather["now"]
        pcpn_str = "降水量{}mm".format(now["pcpn"]) if float(now["pcpn"]) > 0 else "无降雨"
        # now_weather = "当前{}，温度{}℃，体感温度{}℃，{}".format(
        #     now["cond_txt"], now["tmp"], now["fl"], pcpn_str)
        now_weather = "当前温度{}℃，体感温度{}℃".format(now["tmp"], now["fl"])
        now_msg.append(now_weather)
        # 解析daily_forecast，未来三天天气
        # date:预报日期,cond_txt_d:白天天气,cond_txt_n:夜间天气,tmp_max:最高温度,tmp_min:最低温度,pop:降水概率
        dailys = weather["daily_forecast"]  # 未来三天
        today, tomorrow, after_tomorrow = dailys[0], dailys[1], dailys[2]
        today_weather = "今天白天{}，夜间{}，温度{}~{}℃，降雨概率{}%".format(
            today["cond_txt_d"], today["cond_txt_n"], today["tmp_min"], today["tmp_max"], today["pop"])
        tomorrow_weather = "明天白天{}，夜间{}，温度{}~{}℃，降雨概率{}%".format(
            tomorrow["cond_txt_d"], tomorrow["cond_txt_n"], tomorrow["tmp_min"], tomorrow["tmp_max"], tomorrow["pop"])
        morning_msg.append(today_weather)
        afternoon_msg.append(tomorrow_weather)

        # # 解析，生活指数
        # indexes = {'舒适度指数': 'comf', '洗车指数': 'cw', '穿衣指数': 'drsg', '感冒指数': 'flu',
        #            '运动指数': 'sport', '旅游指数': 'trav', '紫外线指数': 'uv', '空气污染扩散条件指数': 'air',
        #            '空调开启指数': 'ac', '过敏指数': 'ag', '太阳镜指数': 'gl', '化妆指数': 'mu',
        #            '晾晒指数': 'airc', '交通指数': 'ptfc', '钓鱼指数': 'fsh', '防晒指数': 'spi'}
        # lifestyle = {index["type"]: index for index in weather["lifestyle"]}  # type,brf,txt
        # lifestyle_str = "穿衣指数：{}。{}".format(lifestyle["drsg"]["brf"], lifestyle["drsg"]["txt"])
        # morning_msg.append(lifestyle_str)

        # 解析hourly ，未来24小时每小时天气
        # tmp:温度，cond_txt:天气状况(多云)，pop:降雨概率，time:预报时间
        hourlys = weather["hourly"]
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
        # print("***hourlys:{}".format(hourlys))
        now = datetime.now()
        day = now.day if now.hour < 18 else (now + timedelta(days=1)).day
        day = day if day >= 10 else "0{}".format(day)
        month = now.month if now.month >= 10 else "0{}".format(now.month)
        date_str = "{}-{}-{}".format(now.year, month, day)
        self.draw_hourly_chart(city_info, date_str)
        return '\n\n'.join(now_msg) + hourly_weather, '\n\n'.join(morning_msg), '\n\n'.join(afternoon_msg)

    def draw_hourly_chart(self, city_info, date_str):
        hourlys = self.get_hourly_weather()["HeWeather6"][0]["hourly"]
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
        pic_title = "{}{}温度及降雨概率图".format(city_info, date_str)
        draw_tmp_pop_picture(pic_title, x, pops, tmps)

    def run(self):
        self.get_air_quality()
