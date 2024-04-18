import numpy as np

from matplotlib.pyplot import MultipleLocator

from tools.aDataSetting import *

import matplotlib.pyplot as plt

from tools.aDataSetting import smooth

color_price = np.array([
    '#ff00ff', '#fff88b', '#10fe10', "#8064a1", '#9bbb58'
])
color_SL_e = np.array([
    "#77ac30", "#0072bd", "#ffc200", "#e29baf", "#7e2f8e", "#d95319", "#01aff0", "#fc1408", "#70ad47", "#cbf6e2"
])

color_SL_g = np.array([
    "#77ac30", "#d5b13e", "#0072bd", "#01AFF0"
])

color_SL_th = np.array([
    "#77ac30","#ffc200", "#01AFF0"
])
color_SL_h = np.array([
    "#77ac30","#ffc200", "#01AFF0"
])

def drawPrice(sell_pirce, sell_label, production_price, production_label, title):
    import matplotlib.pyplot as plt
    x = np.zeros(len(sell_pirce[0]))
    for i in range(len(x)):
        x[i] = i + 1

    # 图片大小
    plt.figure(figsize=(pic_weight + 1.5, pic_high))
    # 设置图片分辨率
    plt.rcParams['figure.dpi'] = pic_rc
    for i in range(len(production_label)):
        plt.plot(x, np.zeros(len(x)) + production_price[i], color=color_price[0 + i], marker='o', markeredgecolor=color_price[i + 1])
        plt.step(x, np.zeros(len(x)) + production_price[i], color=color_price[0 + i], label=production_label[i], where='mid')
    for i in range(len(sell_pirce)):
        plt.plot(x, sell_pirce[i], color=color_price[0], marker='o', linestyle=' ')
        plt.step(x, sell_pirce[i], color=color_price[0], linestyle='--', label=sell_label[i], where='mid')

    ax = plt.gca()  # gca:get current axis得到当前轴
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
    plt.ylabel("Real time price($/kwh)", fontsize=font_size_label, weight='bold')
    plt.grid(True)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick)

    plt.show()


def drawSource_Load_e(Source, Load, title):
    x = np.zeros(len(Load))
    for i in range(len(x)):
        x[i] = x[i] + 1 + i
    # 图片大小
    plt.figure(figsize=(pic_weight * 1.5, pic_high))
    """
    风力 - 光伏 - DG - S - CPP
    """
    label_Source = np.array([
        "WT", "PV", "DG", "S", "MG", "CTP", "TP", "EL", "h_e"
    ])
    temp_negative = np.zeros(len(Source) * len(Source[0]))
    temp_positive = np.zeros(len(Source) * len(Source[0]))
    temp_negative = temp_negative.reshape((len(Source), len(Source[0])))
    temp_positive = temp_positive.reshape((len(Source), len(Source[0])))

    for i in range(len(Source)):
        for j in range(len(Source[i])):
            if Source[i][j] > 0:
                temp_positive[i][j] += Source[i][j]
            else:
                temp_negative[i][j] += Source[i][j]
    for i in range(len(Source) - 1):
        temp_positive[i + 1] += temp_positive[i]
        temp_negative[i + 1] += temp_negative[i]

    for i in range(len(Source)):
        plt.bar(x, temp_positive[-1 - i], color=color_SL_e[-1 - i], label=label_Source[-1 - i], width=1,
                edgecolor="#ffffff", zorder=100)
        plt.bar(x, temp_negative[-1 - i], color=color_SL_e[-1 - i], width=1, edgecolor="#ffffff", zorder=100)

    plt.plot(x, np.zeros(len(Source[0])), color="#ffffff", linewidth=2, zorder=100)
    "最后一个画负荷"
    xS, LoadS = smooth(x, Load, 96)
    plt.plot(xS, LoadS, color=color_SL_e[0], label="Load", linestyle="--", linewidth=3, zorder=100)
    plt.plot(xS, np.zeros(len(LoadS)), color="#000000", linewidth= 3, zorder=100)
    x_ticks_label = ["{hours}".format(hours=i % 24) for i in range(len(x))]
    # plt.xticks(rotation=60)
    plt.xticks(np.append(x[::6], 96), fontsize=font_size_tick, weight='bold')

    plt.grid(True, axis='y', linestyle='dashed', linewidth=1)  # 只显示y轴网格线


    plt.yticks(fontsize=font_size_tick, weight='bold')
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("Power(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True, color="#e4e4e4", zorder=0)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick * 0.7, ncol=1, loc="center", bbox_to_anchor=(1.06, 0.7) )


def drawSource_Load_g(Source, Load, title):
    x = np.zeros(len(Load))
    for i in range(len(x)):
        x[i] = x[i] + 1 + i
    # 图片大小
    plt.figure(figsize=(pic_weight * 1.5, pic_high))
    """
    风力 - 光伏 - DG - S - CPP
    """
    label_Source = np.array([
        "MG", "S", "CTP"
    ])
    temp_negative = np.zeros(len(Source) * len(Source[0]))
    temp_positive = np.zeros(len(Source) * len(Source[0]))
    temp_negative = temp_negative.reshape((len(Source), len(Source[0])))
    temp_positive = temp_positive.reshape((len(Source), len(Source[0])))

    for i in range(len(Source)):
        for j in range(len(Source[i])):
            if Source[i][j] > 0:
                temp_positive[i][j] += Source[i][j]
            else:
                temp_negative[i][j] += Source[i][j]
    for i in range(len(Source) - 1):
        temp_positive[i + 1] += temp_positive[i]
        temp_negative[i + 1] += temp_negative[i]

    for i in range(len(Source)):
        plt.bar(x, temp_positive[-1 - i], color=color_SL_g[-1 - i], label=label_Source[-1 - i], width=0.80,
                edgecolor="#000000", zorder=100)
        plt.bar(x, temp_negative[-1 - i], color=color_SL_g[-1 - i], width=0.80, edgecolor="#000000", zorder=100)

    plt.plot(x, np.zeros(len(Source[0])), color="#000000", linewidth=2, zorder=100)
    "最后一个画负荷"
    xS, LoadS = smooth(x, Load, 96)
    plt.plot(xS, LoadS, color=color_SL_g[0], label="Load", linestyle="--", linewidth=1.5, zorder=100)

    x_ticks_label = ["{hours}".format(hours=i % 24) for i in range(len(x))]
    # plt.xticks(rotation=60)
    plt.xticks(x[::1], x_ticks_label[::1], fontsize=font_size_tick, weight='bold')
    plt.yticks(fontsize=font_size_tick, weight='bold')
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("Power(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True, color="#e4e4e4", zorder=0)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick * 0.7, ncol=1, loc="center", bbox_to_anchor=(1.06, 0.7) )


def drawSource_Load_th(Source, Load, title):
    x = np.zeros(len(Load))
    for i in range(len(x)):
        x[i] = x[i] + 1 + i
    # 图片大小
    plt.figure(figsize=(pic_weight * 1.5, pic_high))
    """
    风力 - 光伏 - DG - S - CPP
    """
    label_Source = np.array([
        "CTP", "TP"
    ])
    temp_negative = np.zeros(len(Source) * len(Source[0]))
    temp_positive = np.zeros(len(Source) * len(Source[0]))
    temp_negative = temp_negative.reshape((len(Source), len(Source[0])))
    temp_positive = temp_positive.reshape((len(Source), len(Source[0])))

    for i in range(len(Source)):
        for j in range(len(Source[i])):
            if Source[i][j] > 0:
                temp_positive[i][j] += Source[i][j]
            else:
                temp_negative[i][j] += Source[i][j]
    for i in range(len(Source) - 1):
        temp_positive[i + 1] += temp_positive[i]
        temp_negative[i + 1] += temp_negative[i]

    for i in range(len(Source)):
        plt.bar(x, temp_positive[-1 - i], color=color_SL_th[-1 - i], label=label_Source[-1 - i], width=0.80,
                edgecolor="#000000", zorder=100)
        plt.bar(x, temp_negative[-1 - i], color=color_SL_th[-1 - i], width=0.80, edgecolor="#000000", zorder=100)

    plt.plot(x, np.zeros(len(Source[0])), color="#000000", linewidth=2, zorder=100)
    "最后一个画负荷"
    xS, LoadS = smooth(x, Load, 96)
    plt.plot(xS, LoadS, color=color_SL_th[0], label="Load", linestyle="--", linewidth=1.5, zorder=100)

    x_ticks_label = ["{hours}".format(hours=i % 24) for i in range(len(x))]
    # plt.xticks(rotation=60)
    plt.xticks(x[::1], x_ticks_label[::1], fontsize=font_size_tick, weight='bold')
    plt.yticks(fontsize=font_size_tick, weight='bold')
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("Power(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True, color="#e4e4e4", zorder=0)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick * 0.7, ncol=1, loc="center", bbox_to_anchor=(1.06, 0.7) )


def drawSource_Load_h(Source, Load, title):
    x = np.zeros(len(Load))
    for i in range(len(x)):
        x[i] = x[i] + 1 + i
    # 图片大小
    plt.figure(figsize=(pic_weight * 1.5, pic_high))
    """
    风力 - 光伏 - DG - S - CPP
    """
    label_Source = np.array([
        "EL", "S", "h_e"
    ])
    temp_negative = np.zeros(len(Source) * len(Source[0]))
    temp_positive = np.zeros(len(Source) * len(Source[0]))
    temp_negative = temp_negative.reshape((len(Source), len(Source[0])))
    temp_positive = temp_positive.reshape((len(Source), len(Source[0])))

    for i in range(len(Source)):
        for j in range(len(Source[i])):
            if Source[i][j] > 0:
                temp_positive[i][j] += Source[i][j]
            else:
                temp_negative[i][j] += Source[i][j]
    for i in range(len(Source) - 1):
        temp_positive[i + 1] += temp_positive[i]
        temp_negative[i + 1] += temp_negative[i]

    for i in range(len(Source)):
        plt.bar(x, temp_positive[-1 - i], color=color_SL_h[-1 - i], label=label_Source[-1 - i], width=0.80,
                edgecolor="#000000", zorder=100)
        plt.bar(x, temp_negative[-1 - i], color=color_SL_h[-1 - i], width=0.80, edgecolor="#000000", zorder=100)

    plt.plot(x, np.zeros(len(Source[0])), color="#000000", linewidth=2, zorder=100)
    "最后一个画负荷"
    xS, LoadS = smooth(x, Load, 96)
    plt.plot(xS, LoadS, color=color_SL_h[0], label="Load", linestyle="--", linewidth=1.5, zorder=100)

    x_ticks_label = ["{hours}".format(hours=i % 24) for i in range(len(x))]
    # plt.xticks(rotation=60)
    plt.xticks(x[::1], x_ticks_label[::1], fontsize=font_size_tick, weight='bold')
    plt.yticks(fontsize=font_size_tick, weight='bold')
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("Power(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True, color="#e4e4e4", zorder=0)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick * 0.7, ncol=1, loc="center", bbox_to_anchor=(1.06, 0.7) )


def drawInteraction(MG_P_Array, MG_P_Array_name, CPP, MG_name):
    temp = len(CPP)
    if MG_name != None and temp < len(MG_P_Array[0]):
        temp = len(MG_P_Array[0])
    x = np.zeros(temp)
    for i in range(len(x)):
        x[i] = x[i] + 1 + i
    # 图片大小
    plt.figure(figsize=(pic_weight, pic_high))

    for i in range(len(MG_P_Array_name)):
        plt.plot(x, MG_P_Array[i], color=color_price[i + 1], label=MG_P_Array_name[i], marker='o', linestyle="--",
                 markeredgecolor="#ffffff")
    plt.plot(x, CPP, color=color_price[0], label="CPPto" + MG_name, marker='o', linestyle="--",
             markeredgecolor="#ffffff")

    ax = plt.gca()  # gca:get current axis得到当前轴
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
    plt.ylabel("Shared Electricity(kW)", fontsize=font_size_label, weight='bold')
    plt.grid(True)
    plt.title(MG_name, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick)

    plt.show()

def getYticks(self, y):
    y_min = np.min(y)

    y_max = np.max(y)

    y_min = y_min // 0.01 * 0.01
    y_max = y_max // 0.01 * 0.01 + 0.01

    inter_val = round((y_max - y_min) / 4, 2)
    y = np.array([y_min])
    for i in range(4):
        y = np.append(y, inter_val * (i + 1) + y_min)