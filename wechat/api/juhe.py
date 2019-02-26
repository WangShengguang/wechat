import re

import requests

from local_config import LocalConfig


class Juhe(object):
    def __init__(self):
        self.history_key = LocalConfig.juhe.history_key
        self.wechat_feature_key = LocalConfig.juhe.wechat_feature_key

    def get_history_today(self, month, day):
        """历史上的今天"""
        url = "http://api.juheapi.com/japi/toh?key={}&v=1.0&month={}&day={}".format(self.history_key, month, day)
        res = requests.get(url).json()
        re_year = re.compile("(\d{3,4})年\d{1,2}月\d{1,2}日")
        min = 2200
        des = ""
        for event in res["result"]:
            year = int(re_year.findall(event["des"])[0])
            if year < min:
                min = year
                des = event["des"]
        return des

    def wechat_choice(self):
        url = "http://v.juhe.cn/weixin/query?key={}".format(self.wechat_feature_key)
        res = requests.get(url).json()
        count = int(res["result"]["ps"])
        for article in res["result"]["list"]:
            # article["title"]
            # article["source"]
            # article["url"]
            print(article)
