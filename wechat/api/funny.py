import requests

poem_headers = {
    "X-User-Token": "RgU1rBKtLym/MhhYIXs42WNoqLyZeXY3EkAcDNrcfKkzj8ILIsAP1Hx0NGhdOO1I"
}


class Funny():
    def __init__(self):
        headers = {}

    def get_random_poem(self):
        # url = "https://api.gushi.ci/"  # 分类地址
        # url = "https://api.gushi.ci/{一级分类}/{二级分类(可选)}.{返回格式(可选)}"
        url = "https://api.gushi.ci/all.json"
        res = requests.get(url, headers=poem_headers).json()
        print(res)
        poem = {"content": [res["content"]],
                "title": res["origin"],
                "bref": res["content"],
                "author": res["author"],
                "dynasty": "",
                "category": res["category"]
                }
        return poem

    def get_today_poem(self):
        url = 'https://v2.jinrishici.com/one.json'
        res = requests.get(url, headers=poem_headers).json()
        print(res)
        if res.get('warning'):
            poem = self.get_random_poem()
        else:
            poem = res['data']['origin']
            poem["bref"] = res['data']["content"]
            # poem['title']
            # poem['author']
            # poem['content']
            # poem['translate']
            # poem['dynasty']
        return poem
