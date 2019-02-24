import http.client
import urllib

from local_config import LocalConfig

# 服务地址
sms_host = "sms.yunpian.com"
# 端口号
port = 443
# 版本号
version = "v2"
# 模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_single_send.json"


class Pianyun(object):
    def __init__(self):
        pass

    def tpl_send_sms(self, tpl, mobile):
        """ 模板接口发短信
        :param tpl: Template对象
        :param mobile:  电话号码
        :return:
        """
        params = urllib.parse.urlencode({
            'apikey': tpl.apikey,
            'tpl_id': tpl.id,
            'tpl_value': urllib.parse.urlencode(tpl.value),
            'mobile': mobile
        })
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        conn = http.client.HTTPSConnection(sms_host, port=port, timeout=30)
        conn.request("POST", sms_tpl_send_uri, params, headers)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str

    def send(self, tpl, mobile):
        # 调用模板接口发短信
        res_msg = self.tpl_send_sms(tpl, mobile)
        return res_msg


class Template(object):
    def __init__(self):
        self.apikey = ""
        self.id = ""
        self.value = {}
        self.text = ""

    def __repr__(self):
        for k, v in self.value.items():
            self.text = self.text.replace(k, v)
        return self.text


class TycTpl(Template):
    def __init__(self):
        super().__init__()
        self.sub_account = "陶盈春"
        self.apikey = LocalConfig.pianyun.tyc_apikey


class WsgTpl(Template):
    def __init__(self):
        super().__init__()
        self.sub_account = "王胜广"
        self.apikey = LocalConfig.pianyun.wsg_apikey


class TplRain(TycTpl):
    def __init__(self, person):
        super().__init__()
        self.id = "2736830"
        self.value = {'#city#': '上海', '#day#': '今', '#weather#': '晴', '#temprature#': '0~3', '#level#': "优",
                      '#probability#': "25", "#place#": "出门"}
        self.text = ("【王胜广】#city##day#天天气：#weather#，温度#temperature#℃,空气质量#level#。"
                     "降雨概率为#probability#%,降雨概率较大，#place#记得带伞噢~")
        self.init(person)

    def init(self, person):
        """ 在此处理模板，变成可发送信息
        :param person: Person Object
        """
        parm = {'#city#': person.city}
