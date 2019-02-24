import os

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import spline

from wechat.config import data_dir

# 获取所有的自带样式
# print(plt.style.available)

# 使用自带的样式进行美化
# plt.style.use("ggplot")
# plt.style.use("seaborn")
# 中文显示
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

weather_pic_name = os.path.join(data_dir, "weather.png")


def anotation_max_min(x, y):
    print(x, y)
    max_indx = np.argmax(y)  # max value index
    min_indx = np.argmin(y)  # min value index
    plt.plot(max_indx, y[max_indx], 'ks')
    show_max = " （{},{}%）".format(max_indx, y[max_indx])
    print(x[max_indx], y[max_indx])
    # plt.annotate(show_max, xytext=(max_indx, y[max_indx]), xy=(max_indx, y[max_indx]))
    # xytext 文本所在位置和 value所在位置，text通过剪头指向value
    plt.annotate(show_max, xytext=(x[max_indx] - 5, y[max_indx] - 5), xy=(x[max_indx], y[max_indx]),
                 arrowprops=dict(facecolor='black', shrink=0.05, frac=0.1, headwidth=7., width=1.5), )

    plt.plot(x[min_indx], y[min_indx], 'gs')


def test(title, x, pops, tmps):
    x = np.asarray(x)
    pops = np.asarray(pops)
    tmps = np.asarray(tmps)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.plot(x, pops, 'b-', label='降雨概率（%）')

    # ax.plot(range(10))
    ax1.set_xlabel('X-axis')
    ax1.set_ylabel('Y-axis')
    ax1.spines['bottom'].set_color('red')
    ax1.spines['top'].set_color('red')
    ax1.xaxis.label.set_color('red')
    ax1.tick_params(axis='x', colors='red')
    ax2 = ax1.twinx()
    ax2.plot(x, tmps, 'b-', label='降雨概率（%）')
    # plt.legend(handles=[ax1, ax2], loc='upper right')
    plt.show()


def draw_tmp_pop_picture(title, x, pops, tmps):
    """
    :param x: 时间
    :param pops: 降雨概率
    :param tmps: 温度
    :return:
    """
    print(x[0], x[-1])
    print("x: {}".format(x))
    print("pops: {}".format(pops))
    print("tmps: {}".format(tmps))
    x = np.asarray(x)
    pops = np.asarray(pops)
    tmps = np.asarray(tmps)
    # test(title, x, pops, tmps)
    x_smooth = np.linspace(x.min(), x.max(), 300)  # 300 represents number of points to make between T.min and T.max
    pops_smooth = spline(x, pops, x_smooth)
    # tmps_smooth = spline(x, tmps, x_smooth)
    plt.title(title)  # "未来12小时温度及降雨概率图"
    plt.xlabel('时间/整点')
    # plt.xticks(range(len(x)), x)
    # 降雨曲线
    # L1, = plt.plot(x, pops, 'b-', label='降雨概率（%）')
    L1, = plt.plot(x_smooth, pops_smooth, 'b-', label='降雨概率（%）')
    plt.axis([x[0], x[-1], 0, 100])
    # anotation_max_min(x, pops) #标记最值
    plt.fill_between(x_smooth, pops_smooth, facecolor="#1E90FF", alpha=0.25)  # 填充两个函数之间的区域
    # plt.fill(x, pops, color="g", alpha=0.3)  # 函数与坐标轴之间的区域
    plt.ylabel('降雨概率/%')  # , color="b")
    plt.yticks(color="b")
    # 标记概率为0的点
    _x = []
    _y = []
    for index, y in enumerate(pops):
        if y == 0:
            _x.append(x[index])
            _y.append(y)
    if _x:
        plt.scatter(_x, _y, c=np.cos(_x))  # 标记0点
    # 温度曲线
    plt.twinx()
    L2, = plt.plot(x, tmps, 'r-', label='温度（℃）')
    # plt.xticks(range(len(x)), x)
    # L2, = plt.plot(x_smooth, tmps_smooth, 'r-', label='降雨概率（%）')
    plt.axis([x[0], x[-1], 0, 40])
    plt.scatter(x, tmps, c=np.sin(x))
    plt.ylabel('温度/℃')  # , color="r")
    plt.yticks(color="r")
    # plt.tick_params(axis='y', colors='red') #刻度颜色
    # 合并图例
    plt.legend(handles=[L1, L2], loc='upper right')  # , loc=9)
    plt.savefig(weather_pic_name)
    # plt.show()
