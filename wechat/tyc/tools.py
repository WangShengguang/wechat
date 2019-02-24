def get_lot_lat(area):
    """
    获得地区对应经纬度
    :param area:
    :return:
    """
    lot_lat = {"上海市虹口区": "31.26,121.49",  # 上海
               "丹东东港": ""  # 辽宁丹东
               }
    return lot_lat.get(area)
