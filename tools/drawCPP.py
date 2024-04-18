import numpy as np
from  tools.aDataSetting import *

color= np.array([
    '#fde9eb', '#fdd5de', '#e29baf', '#fc1408'
])

def drawCPP(y, yMax, yMin, yRamping_up, yRamping_down, State,title=None):
    import matplotlib.pyplot as plt
    x = np.zeros(len(y))
    for i in range(len(x)):
        x[i] = i + 1

    # 图片大小
    plt.figure(figsize=(pic_weight, pic_high))
    # 设置图片分辨率
    plt.rcParams['figure.dpi'] = pic_rc

    y_Ramping_max = np.zeros(len(y))
    y_Ramping_min = np.zeros(len(y))
    yMin = -yMax

    for i in range(len(y)):
        if y[i] + yRamping_up > yMax:
            y_Ramping_max[i] = yMax
        else:
            y_Ramping_max[i] = y[i] + yRamping_up

        if y[i] - yRamping_down < yMin:
            y_Ramping_min[i] = yMin
        else:
            y_Ramping_min[i] = y[i] - yRamping_down
    max_point = np.max(y_Ramping_max)
    min_point = np.min(y_Ramping_min)

    xS, yS = smooth(x, y, 96)
    xS, y_Ramping_maxS = smooth(x, y_Ramping_max, 96)
    xS, y_Ramping_minS = smooth(x, y_Ramping_min, 96)

    plt.fill_between(x, np.zeros(len(y)) + max_point, np.zeros(len(y)) + min_point, np.zeros(len(y)) + max_point > np.zeros(len(y)) + min_point, color=color[0], interpolate=True)
    plt.fill_between(xS, y_Ramping_maxS, y_Ramping_minS, y_Ramping_maxS > y_Ramping_minS, color=color[1],
                     interpolate=True)
    plt.plot(xS, yS, color=color[2], linewidth=3, alpha=0.7)

    ax = plt.gca()  # gca:get current axis得到当前轴
    # 设置图片的右边框和上边框为不显示
    # ax.spines['right'].set_color('none')
    # ax.spines['top'].set_color('none')
    ###设置坐标轴的粗细
    ax.spines['bottom'].set_linewidth(line_weight)  ###设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(line_weight)  ####设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细

    x_ticks_label = ["{hours}:00".format(hours=i % 24) for i in range(len(x))]
    # plt.xticks(rotation=60)
    plt.xticks(x[::5], x_ticks_label[::5], fontsize=font_size_tick, weight='bold')
    plt.yticks(fontsize=font_size_tick, weight='bold')
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("Power distribution(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    # plt.legend()

    plt.show()