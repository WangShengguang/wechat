class Person(object):
    def __init__(self, province, city, phone):
        """
        :param province: 现居省份或直辖市
        :param city: 现居城市或直辖市区域
        :param phone: 电话号码
        """
        self.province = province
        self.city = city
        self.phone = phone
        self.wechat = None
