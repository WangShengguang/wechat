import os
from datetime import datetime

from pyecharts import Line, Overlap

from local_config import data_dir

weather_pic_name = os.path.join(data_dir, "weather.png")

from PIL import Image


def IsValidImage(img_path):
    """
    判断文件是否为有效（完整）的图片
    :param img_path:图片路径
    :return:True：有效 False：无效
    """
    bValid = True
    try:
        Image.open(img_path).verify()
    except:
        bValid = False
    return bValid


def draw_line_chart(x, y1, y2=None):
    """
    :param x:
    :param y1: 温度值
    :param y2: 降水概率
    :return:
    """
    chart_name = str(datetime.now().date()) + "降雨温度曲线图"
    overlap = Overlap()
    line = Line(chart_name)
    line.add("温度", x_axis=x, y_axis=y1, is_fill=True, line_opacity=1, symbol=None, is_label_show=True,
             mark_point=["min", "max", "average"], yaxis_pos="right", yaxis_formatter="℃",  # mark_line=["average"],
             yaxis_min=0, yaxis_max=40, yaxis_line_color="red")
    overlap.add(line)

    line1 = Line(chart_name)
    line1.add("降雨概率", x_axis=x, y_axis=y2, is_fill=True, area_color='#1E90FF', area_opacity=0.2, is_smooth=True,
              mark_point=["min", "max", "average"], yaxis_formatter="%",  # mark_line=["average"],
              yaxis_min=0, yaxis_max=100)

    overlap.add(line1, yaxis_index=1, is_add_yaxis=True)
    overlap.render(path=weather_pic_name)
    # transimg(weather_pic_name)
