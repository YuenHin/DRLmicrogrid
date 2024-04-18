import numpy as np

from  tools.aDataSetting import *

from tools.aDataSetting import smooth

color = np.array([
    '#d9541b', '#2987c7'
])

def drawStorage(y, p, title):
    import matplotlib.pyplot as plt
    x = np.zeros(len(y))
    for i in range(len(x)):
        x[i] = i + 1

    # 图片大小
    plt.figure(figsize=(pic_weight + 2 , pic_high))
    # 设置图片分辨率
    plt.rcParams['figure.dpi'] = pic_rc
    y_aim = np.zeros(23)
    x_aim = np.zeros(23)
    p_aim = np.zeros(23)
    for i in range(23):
        # y_aim[i] = y[i * 4]
        y_aim[i] = y[i]
        # x_aim[i] =  i * 4
        x_aim[i] = i
        # p_aim[i] = p[ i * 4]
        p_aim[i] = p[i]
    y_aim = np.append(y_aim, y[-1])
    x_aim = np.append(x_aim, 95)
    p_aim = np.append(p_aim, p[-1])



    plt.plot(x_aim, y_aim, color=color[1], marker = 'o' , linestyle=' ')
    plt.step(x_aim, y_aim, color=color[1], linestyle='--', where='mid', label = 'E')

    ax = plt.gca()  # gca:get current axis得到当前轴
    ###设置坐标轴的粗细
    ax.spines['bottom'].set_linewidth(line_weight)  ###设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(line_weight)  ####设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细

    ax.spines['left'].set_color(color[1])
    ax.spines['right'].set_color(color[0])

    plt.grid(True, axis='y', linestyle='dashed', linewidth=1)  # 只显示y轴网格线
    plt.xticks(np.append(x[::6], 96), fontsize=font_size_tick, weight='bold')

    x_ticks_label = ["{hours}:00".format(hours=i % 24) for i in range(len(x))]
    plt.yticks(fontsize=font_size_tick, weight='bold', color = color[1])
    plt.ylabel("Storage Value(kwh)", fontsize=font_size_label, weight='bold', color = color[1])
    plt.legend(fontsize=font_size_tick)

    z_ax = ax.twinx()
    z_ax.invert_yaxis()


    z_ax.plot(x_aim, p_aim, color = color[0], marker = 'o', linestyle = " ")
    # z_ax.step(x, p, color = color[0], where='mid', linestyle = "--")
    z_ax.bar(x_aim, p_aim, width = 0.15, color = color[0])
    z_ax.plot(x_aim, np.zeros(len(x_aim)), color=color[0], linestyle = "-", label = 'E')

    ###设置坐标轴的粗细
    z_ax.spines['bottom'].set_linewidth(line_weight)  ###设置底部坐标轴的粗细
    z_ax.spines['left'].set_linewidth(line_weight)  ####设置左边坐标轴的粗细
    z_ax.spines['right'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细
    z_ax.spines['top'].set_linewidth(line_weight)  ###设置右边坐标轴的粗细

    z_ax.spines['left'].set_color(color[1])
    z_ax.spines['right'].set_color(color[0])

    ax = plt.gca()
    # plt.xticks(rotation=60)
    plt.xticks(np.append(x[::6], 96), fontsize=font_size_tick, weight='bold', color = color[1])


    plt.yticks(fontsize=font_size_tick, weight='bold', color = color[0])
    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    plt.xlabel("Time(h)", fontsize=font_size_label, weight='bold')
    plt.ylabel("SOC(kw)", fontsize=font_size_label, weight='bold', color = color[0])
    plt.grid(True)
    plt.title(title, fontsize=font_size_title, weight='bold', pad=pad)
    plt.legend(fontsize=font_size_tick)

    plt.show()