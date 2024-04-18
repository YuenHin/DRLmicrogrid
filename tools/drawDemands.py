import numpy as np
from  tools.aDataSetting import *
color_e = np.array([
    '#CDE5E9', '#A7CDD8', '#22748A', '#01AFF0'
])
color_th = np.array([
    '#fde9eb', '#fdd5de', '#e29baf', '#fc1408'
])
color_h = np.array([
    '#e3fbee', '#cbf6e2', '#a0d5bd', '#70ad47'
])
color_g = np.array([
    '#feedcf', '#fedf9e', '#d5b13e', '#ffc200'
])

color_price = np.array([
    '#ff00ff', '#10fe10'
])

def drawDemands(y, yMax, yMin, yRamping, type,title=None):
    import matplotlib.pyplot as plt
    color = None
    if type == 'e':
        color = color_e
    if type == 'g':
        color = color_g
    if type == 'th':
        color = color_th
    if type == 'h':
        color = color_h

    x = np.zeros(len(y))
    for i in range(len(x)):
        x[i] = i + 1

    #图片大小
    plt.figure(figsize=(pic_weight, pic_high))
    # 设置图片分辨率
    plt.rcParams['figure.dpi'] = pic_rc

    y_Ramping_max = np.zeros(len(y))
    y_Ramping_min = np.zeros(len(y))
    for i in range(len(y)):
        if y[i] + yRamping[i] > yMax[i]:
            y_Ramping_max[i] = yMax[i]
        else:
            y_Ramping_max[i] = y[i] + yRamping[i]

        if y[i] - yRamping[i] < yMin[i]:
            y_Ramping_min[i] = yMin[i]
        else:
            y_Ramping_min[i] = y[i] - yRamping[i]

    # plt.scatter(x, yReal[i].x, color= color[i], label = name[i])

    # plt.fill_between(x, yReal[0], yReal[i], yReal[0] < yReal[i], color='#CD5C5C', alpha=0.8, interpolate=True)

    # plt.plot(x, yMin, color=color[1])
    #
    # plt.plot(x, yMax, color=color[1])

    xS, yS = smooth(x, y, 96)
    xS, yMaxS = smooth(x, yMax, 96)
    xS, yMinS = smooth(x, yMin, 96)
    xS, y_Ramping_maxS = smooth(x, y_Ramping_max, 96)
    xS, y_Ramping_minS = smooth(x, y_Ramping_min, 96)

    plt.fill_between(xS, yMaxS, yMinS, yMaxS > yMinS, color=color[0], interpolate=True)
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