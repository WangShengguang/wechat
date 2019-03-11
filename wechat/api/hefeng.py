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
    def get_3_days_weather(self):
        """ 日出时间
        """
        weather_url = "https://api.heweather.net/s6/weather?"  # 常规天气
        weather = self.get_json(weather_url)
        self.store_to_local("weather.json", weather)
        # 基础信息
        # location:地区／城市名称,parent_city:该地区／城市的上级城市，admin_area:该地区／城市所属行政区域
        weather = weather["HeWeather6"][0]
        dailys = weather["daily_forecast"]  # 未来三天
        today, tomorrow, after_tomorrow = dailys[0], dailys[1], dailys[2]
        return today, tomorrow, after_tomorrow

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
        now = weather["now"]
        lifestyle = weather["lifestyle"]
        dailys = weather["daily_forecast"]  # 未来三天
        hourlys = weather["hourly"]  # 不精确，改用专门的hourly接口
        # today, tomorrow, after_tomorrow = dailys[0], dailys[1], dailys[2]
        return basic, now, lifestyle, dailys

    def run(self):
        self.get_air_quality()
