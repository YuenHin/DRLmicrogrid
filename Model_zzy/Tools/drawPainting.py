import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties

"""
获取决策变量求解结果
"""
def getDecisionVariableResult(params_name, params, results):
    params_name_ = np.array([''])

    # 为变量名加上时间尺度
    for i in range(24):
        params_name_ = np.append(params_name_, f"{params_name}{i + 1}")
    params_name_ = params_name_[1:]
    print(params_name_)

    # 找到对应变量名保存的结果
    params_result = np.array([''])
    for i in range(len(params)):
        for j in range(len(params_name_)):
            if params_name_[j] == params[i]:
                params_result = np.append(params_result, results[i])
    params_result = params_result[1:]
    params_result = np.array(params_result, dtype=float)
    return params_result

"""
获取不同能源子系统数据
"""
def getEnergySystemData(type, params, results):
    if type == "e":
        # 需求侧
        load = "load_e_01P"
        storage_ch = "storage_e_01CP"
        eb = "eb_01output_e"
        er = "er_01output_e"
        hp = "hp_01input_e"

        # 供给侧
        storage_dis = "storage_e_01DP"
        flex_load = "fl_e_01RP"
        pv = "pv_01P"
        wt = "wt_01P"
        cchp = "cchp_01output_e"
        cpp = "cpp_01P"

        load = getDecisionVariableResult(load, params, results)
        storage_ch = getDecisionVariableResult(storage_ch, params, results)
        eb = getDecisionVariableResult(eb, params, results)
        er = getDecisionVariableResult(er, params, results)
        hp = getDecisionVariableResult(hp, params, results)
        storage_dis = getDecisionVariableResult(storage_dis, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)
        pv = getDecisionVariableResult(pv, params, results)
        wt = getDecisionVariableResult(wt, params, results)
        cchp = getDecisionVariableResult(cchp, params, results)
        cpp = getDecisionVariableResult(cpp, params, results)

        return load, storage_ch, eb, er, hp, storage_dis, flex_load, pv, wt, cchp, cpp

    if type == "g":
        # 需求侧
        load = "load_g_01P"
        cchp = "cchp_01input_g"

        # 供给侧
        flex_load = "fl_g_01RP"
        gw = "gw_01P"

        load = getDecisionVariableResult(load, params, results)
        cchp = getDecisionVariableResult(cchp, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)
        gw = getDecisionVariableResult(gw, params, results)

        return load, cchp, flex_load, gw

    if type == "th":
        # 需求侧
        load = "load_h_01P"
        storage_ch = "storage_h_01CP"

        # 供给侧
        storage_dis = "storage_h_01DP"
        flex_load = "fl_h_01RP"
        hp = "hp_01output_h"
        eb = "eb_01output_h"

        load = getDecisionVariableResult(load, params, results)
        storage_ch = getDecisionVariableResult(storage_ch, params, results)
        storage_dis = getDecisionVariableResult(storage_dis, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)
        hp = getDecisionVariableResult(hp, params, results)
        eb = getDecisionVariableResult(eb, params, results)

        return load, storage_ch, storage_dis, flex_load, hp, eb

    if type == "c":
        # 需求侧
        load = "load_c_01P"
        storage_ch = "storage_c_01CP"

        # 供给侧
        storage_dis = "storage_c_01DP"
        er = "er_01output_c"

        load = getDecisionVariableResult(load, params, results)
        storage_ch = getDecisionVariableResult(storage_ch, params, results)
        storage_dis = getDecisionVariableResult(storage_dis, params, results)
        er = getDecisionVariableResult(er, params, results)

        return load, storage_ch, storage_dis, er

"""
得到各子系统的灵活性供给与灵活性需求
"""
def getFlexibility(type, state, params, results):
    if type == "e" and state == "up":
        # 需求侧
        fd_ud = "fd_eUD"

        # 供给侧
        storage_ch_ds = "storage_e_01ch_ds"
        storage_dis_us = "storage_e_01dis_us"
        flex_load = "fl_e_01RP"
        cchp_us = "cchp_01e_us"
        eb_ds = "eb_01e_ds"
        er_ds = "er_01e_ds"

        fd_ud = getDecisionVariableResult(fd_ud, params, results)
        storage_ch_ds = getDecisionVariableResult(storage_ch_ds, params, results)
        storage_dis_us = getDecisionVariableResult(storage_dis_us, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)
        cchp_us = getDecisionVariableResult(cchp_us, params, results)
        eb_ds = getDecisionVariableResult(eb_ds, params, results)
        er_ds = getDecisionVariableResult(er_ds, params, results)

        return fd_ud, storage_ch_ds, storage_dis_us, flex_load, cchp_us, eb_ds, er_ds

    if type == "e" and state == "down":
        # 需求侧
        fd_dd = "fd_eDD"

        # 供给侧
        storage_ch_us = "storage_e_01ch_us"
        storage_dis_ds = "storage_e_01dis_ds"
        cchp_ds = "cchp_01e_ds"
        eb_us = "eb_01e_us"
        er_us = "er_01e_us"

        fd_dd = getDecisionVariableResult(fd_dd, params, results)
        storage_ch_us = getDecisionVariableResult(storage_ch_us, params, results)
        storage_dis_ds = getDecisionVariableResult(storage_dis_ds, params, results)
        cchp_ds = getDecisionVariableResult(cchp_ds, params, results)
        eb_us = getDecisionVariableResult(eb_us, params, results)
        er_us = getDecisionVariableResult(er_us, params, results)

        return fd_dd, storage_ch_us, storage_dis_ds, cchp_ds, eb_us, er_us

    if type == "g" and state == "up":
        # 需求侧
        fd_ud = "fd_gUD"

        # 供给侧
        cchp_ds = "cchp_01g_ds"
        flex_load = "fl_g_01RP"

        fd_ud = getDecisionVariableResult(fd_ud, params, results)
        cchp_ds = getDecisionVariableResult(cchp_ds, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)

        return fd_ud, cchp_ds, flex_load

    if type == "g" and state == "down":
        # 需求侧
        fd_dd = "fd_gDD"

        # 供给侧
        cchp_ds = "cchp_01g_ds"

        fd_dd = getDecisionVariableResult(fd_dd, params, results)
        cchp_ds = getDecisionVariableResult(cchp_ds, params, results)

        return fd_dd, cchp_ds

    if type == "th" and state == "up":
        # 需求侧
        fd_ud = "fd_hUD"

        # 供给侧
        flex_load = "fl_h_01RP"
        cchp_us = "cchp_01h_us"
        eb_us = "eb_01h_us"
        storage_ch_ds = "storage_h_01ch_ds"
        storage_dis_us = "storage_h_01dis_us"

        fd_ud = getDecisionVariableResult(fd_ud, params, results)
        flex_load = getDecisionVariableResult(flex_load, params, results)
        cchp_us = getDecisionVariableResult(cchp_us, params, results)
        eb_us = getDecisionVariableResult(eb_us, params, results)
        storage_ch_ds = getDecisionVariableResult(storage_ch_ds, params, results)
        storage_dis_us = getDecisionVariableResult(storage_dis_us, params, results)

        return fd_ud, flex_load, cchp_us, eb_us, storage_ch_ds, storage_dis_us

    if type == "th" and state == "down":
        # 需求侧
        fd_dd = "fd_hDD"

        # 供给侧
        cchp_ds = "cchp_01h_ds"
        eb_ds = "eb_01h_ds"
        storage_ch_us = "storage_h_01ch_us"
        storage_dis_ds = "storage_h_01dis_ds"

        fd_dd = getDecisionVariableResult(fd_dd, params, results)
        cchp_ds = getDecisionVariableResult(cchp_ds, params, results)
        eb_ds = getDecisionVariableResult(eb_ds, params, results)
        storage_ch_us = getDecisionVariableResult(storage_ch_us, params, results)
        storage_dis_ds = getDecisionVariableResult(storage_dis_ds, params, results)

        return fd_dd, cchp_ds, eb_ds, storage_ch_us, storage_dis_ds

    if type == "c" and state == "up":
        # 需求侧
        fd_ud = "fd_cUD"

        # 供给侧
        storage_ch_ds = "storage_c_01ch_ds"
        storage_dis_us = "storage_c_01dis_us"
        er_us = "er_01c_us"

        fd_ud = getDecisionVariableResult(fd_ud, params, results)
        storage_ch_ds = getDecisionVariableResult(storage_ch_ds, params, results)
        storage_dis_us = getDecisionVariableResult(storage_dis_us, params, results)
        er_us = getDecisionVariableResult(er_us, params, results)

        return fd_ud, storage_ch_ds, storage_dis_us, er_us

    if type == "c" and state == "down":
        # 需求侧
        fd_dd = "fd_cDD"

        # 供给侧
        storage_ch_us = "storage_c_01ch_us"
        storage_dis_ds = "storage_c_01dis_ds"
        er_ds = "er_01c_ds"

        fd_dd = getDecisionVariableResult(fd_dd, params, results)
        storage_ch_us = getDecisionVariableResult(storage_ch_us, params, results)
        storage_dis_ds = getDecisionVariableResult(storage_dis_ds, params, results)
        er_ds = getDecisionVariableResult(er_ds, params, results)

        return fd_dd, storage_ch_us, storage_dis_ds, er_ds

"""
获取各储能装置的决策变量
"""
# 得到对应能源子系统的储能装置的决策变量名
def getStorageResult(type, params, results):
    if type == "e":
        charging_params = "storage_e_01CP"
        discharging_params = "storage_e_01DP"
        charging_us = "storage_e_01ch_us"
        charging_ds = "storage_e_01ch_ds"
        discharging_us = "storage_e_01dis_us"
        discharging_ds = "storage_e_01dis_ds"
        storage_power = "storage_e_01E"

        charging = getDecisionVariableResult(params_name=charging_params, params=params, results=results)
        discharging = getDecisionVariableResult(params_name=discharging_params, params=params, results=results)
        charging_us = getDecisionVariableResult(params_name=charging_us, params=params, results=results)
        charging_ds = getDecisionVariableResult(params_name=charging_ds, params=params, results=results)
        discharging_us = getDecisionVariableResult(params_name=discharging_us, params=params, results=results)
        discharging_ds = getDecisionVariableResult(params_name=discharging_ds, params=params, results=results)
        storage_power = getDecisionVariableResult(params_name=storage_power, params=params, results=results)

        return charging, discharging, charging_us, charging_ds, discharging_us, discharging_ds, storage_power

    if type=="th":
        charging_params = "storage_h_01CP"
        discharging_params = "storage_h_01DP"
        charging_us = "storage_h_01ch_us"
        charging_ds = "storage_h_01ch_ds"
        discharging_us = "storage_h_01dis_us"
        discharging_ds = "storage_h_01dis_ds"
        storage_power = "storage_h_01E"

        charging = getDecisionVariableResult(params_name=charging_params, params=params, results=results)
        discharging = getDecisionVariableResult(params_name=discharging_params, params=params, results=results)
        charging_us = getDecisionVariableResult(params_name=charging_us, params=params, results=results)
        charging_ds = getDecisionVariableResult(params_name=charging_ds, params=params, results=results)
        discharging_us = getDecisionVariableResult(params_name=discharging_us, params=params, results=results)
        discharging_ds = getDecisionVariableResult(params_name=discharging_ds, params=params, results=results)
        storage_power = getDecisionVariableResult(params_name=storage_power, params=params, results=results)

        return charging, discharging, charging_us, charging_ds, discharging_us, discharging_ds, storage_power

    if type == "c":
        charging_params = "storage_c_01CP"
        discharging_params = "storage_c_01DP"
        charging_us = "storage_c_01ch_us"
        charging_ds = "storage_c_01ch_ds"
        discharging_us = "storage_c_01dis_us"
        discharging_ds = "storage_c_01dis_ds"
        storage_power = "storage_c_01E"

        charging = getDecisionVariableResult(params_name=charging_params, params=params, results=results)
        discharging = getDecisionVariableResult(params_name=discharging_params, params=params, results=results)
        charging_us = getDecisionVariableResult(params_name=charging_us, params=params, results=results)
        charging_ds = getDecisionVariableResult(params_name=charging_ds, params=params, results=results)
        discharging_us = getDecisionVariableResult(params_name=discharging_us, params=params, results=results)
        discharging_ds = getDecisionVariableResult(params_name=discharging_ds, params=params, results=results)
        storage_power = getDecisionVariableResult(params_name=storage_power, params=params, results=results)

        return charging, discharging, charging_us, charging_ds, discharging_us, discharging_ds, storage_power


"""
——————————————实验1——————————————
"""

"""
不同不确定集下，各个设备的运行功率及灵活性供给能力
"""

# 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path, size=12.5)
#
# # 处理数据
# path = r"C:\software\Github\DRLmicrogrid\Model_zzy\results_ro.xlsx"
# dataset = pd.read_excel(path)
#
# params = dataset.iloc[:, 0]
# results = dataset.iloc[:, 1]
#
# series_array = pd.Series(params)
# params = series_array[~series_array.isna() & (series_array != '')].values
#
# series_array0 = pd.Series(results)
# results = series_array0[~series_array0.isna() & (series_array0 != '')].values
#
# # 数据准备
# x = np.arange(0, 24)  # 24个柱体的x坐标
# y1 = np.random.randint(10, 30, size=24)  # 第一根折线的y值
# y2 = np.random.randint(5, 25, size=24)   # 第二根折线的y值

"电力子系统"
# # 向上灵活性供需
# fd_ud, storage_ch_ds, storage_dis_us, flex_load, cchp_us, eb_ds, er_ds = getFlexibility(type="e", state="up",
#                                                                                         params=params, results=results)
# # fd_ud_color = np.array(["#14517C", "#96C37D", "#9DC3E7", "#8481BA", "#C497B2", "#A9B8C6"])
# fd_ud_color = np.array(["#e5e2b8", "#6f9fb7", "#c2d8de", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_ud_name = np.array(["充电", "放电", "柔性负荷", "CCHP", "EB", "ER"])
# # print(f"flex_load:{flex_load}")
# # 向下灵活性供需
# fd_dd, storage_ch_us, storage_dis_ds, cchp_ds, eb_us, er_us = getFlexibility(type="e", state="down",
#                                                                              params=params, results=results)
# fd_dd_color = np.array(["#e5e2b8", "#6f9fb7", "#c2d8de", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_dd_name = np.array(["充电", "放电", "CCHP", "EB", "ER"])
#
# up_layers = np.concatenate((storage_ch_ds, storage_dis_us, flex_load, cchp_us, eb_ds, er_ds))
# up_layers = up_layers.reshape(-1, 24)
# up_layers = up_layers.T
#
# down_layers = np.concatenate((storage_ch_us, storage_dis_ds, cchp_ds, eb_us, er_us))
# down_layers = down_layers.reshape(-1, 24)
# down_layers = down_layers.T

"天然气子系统"
# 向上灵活性供需
# fd_ud, cchp_ds, flex_load = getFlexibility(type="g", state="up", params=params, results=results)
# # 向下灵活性供需
# fd_dd, cchp_us = getFlexibility(type="g", state="down", params=params, results=results)
#
# fd_ud_color = np.array(["#6f9fb7", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_ud_name = np.array(["CCHP", "柔性负荷"])
#
# fd_dd_color = np.array(["#6f9fb7", "#c2d8de", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_dd_name = np.array(["CCHP"])
#
# up_layers = np.concatenate((cchp_ds, flex_load))
# up_layers = up_layers.reshape(-1, 24)
# up_layers = up_layers.T
#
# down_layers = cchp_us
# down_layers = down_layers.reshape(-1, 24)
# down_layers = down_layers.T

"热能子系统"
# # 向上灵活性供需
# fd_ud, flex_load, cchp_us, eb_us, storage_ch_ds, storage_dis_us = getFlexibility(type="th", state="up",
#                                                                                    params=params, results=results)
# # 向下灵活性供需
# fd_dd, cchp_ds, eb_ds, storage_ch_us, storage_dis_ds = getFlexibility(type="th", state="down",
#                                                                  params=params, results=results)
#
# fd_ud_color = np.array(["#6f9fb7", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_ud_name = np.array(["柔性负荷", "CCHP", "EB", "充能", "放能"])
#
# fd_dd_color = np.array(["#6f9fb7", "#c2d8de", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_dd_name = np.array(["CCHP", "EB", "充能", "放能"])
#
# up_layers = np.concatenate((flex_load, cchp_us, eb_us, storage_ch_ds, storage_dis_us))
# up_layers = up_layers.reshape(-1, 24)
# up_layers = up_layers.T
#
# down_layers = np.concatenate((cchp_ds, eb_ds, storage_ch_us, storage_dis_ds))
# down_layers = down_layers.reshape(-1, 24)
# down_layers = down_layers.T

"冷能子系统"
# # 向上灵活性供需
# fd_ud, storage_ch_ds, storage_dis_us, er_us = getFlexibility(type="c", state="up", params=params, results=results)
# # 向下灵活性供需
# fd_dd, storage_ch_us, storage_dis_ds, er_ds = getFlexibility(type="c", state="down", params=params, results=results)
#
# fd_ud_color = np.array(["#6f9fb7", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_ud_name = np.array(["充能", "放能", "ER"])
#
# fd_dd_color = np.array(["#6f9fb7", "#c2d8de", "#e3ae7b", "#c6624b", "#970529", "#305287"])
# fd_dd_name = np.array(["充能", "放能", "ER"])
#
# up_layers = np.concatenate((storage_ch_ds, storage_dis_us, er_us))
# up_layers = up_layers.reshape(-1, 24)
# up_layers = up_layers.T
#
# down_layers = np.concatenate((storage_ch_us, storage_dis_ds, er_ds))
# down_layers = down_layers.reshape(-1, 24)
# down_layers = down_layers.T
#
# # 绘图
# fig, ax = plt.subplots(figsize=(6, 3))
#
# bottom = np.zeros(24)  # 叠加的底部起始位置
#
# for i in range(up_layers.shape[1]):
#     ax.bar(x, up_layers[:, i], bottom=bottom, label=fd_ud_name[i], color=fd_ud_color[i])
#     bottom += up_layers[:, i]
#
# bottom_down = np.zeros(24)  # 负半轴叠加的底部起始位置
#
# # for i in range(down_layers.shape[1]):
# #     ax.bar(x, down_layers[:, i], bottom=bottom_down, label=f'负层{i+1}' if i == 0 else "")
# #     bottom_down += down_layers[:, i]
# #
# # # 绘制折线
# ax.plot(x, fd_ud, marker='o', color='#990000', label='向上灵活性需求', markersize=5)  # 深红色
# # plt.plot(x, fd_dd, marker='o', color='#006699', label='折线3')  # 蓝绿色
# #
# # 设置图形属性
# ax.set_xlabel('时间尺度/h', fontproperties=font_prop)
# ax.set_ylabel('功率/KW', fontproperties=font_prop)
# ax.set_title('电力子系统向上灵活性供需关系', fontproperties=font_prop)
# ax.set_xticks([0, 6, 12, 18, 24])  # 设置x轴刻度为1到24
# ax.legend(prop=font_prop, loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=10)  # 添加图例
# ax.grid(False)
#
# # 调整图形的边距
# plt.subplots_adjust(top=0.9, bottom=0.4)   # 减少顶部边距，增加底部边距
#
# # 显示图形
# plt.tight_layout()
# plt.show()

"""
不同的不确定集
"""

"""
区间概率不确定集
"""
# # 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path, size=12.5)
#
# # 数据准备
# x = np.arange(1, 25)  # 24个柱体的x坐标
# path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx"
# # path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\pv.xlsx"
# dataset = pd.read_excel(path)
# min = dataset['min'].values
# max = dataset['max'].values
# mu = dataset['mu'].values
# real_value = dataset['real_value'].values
# min = min[0:24]
# max = max[0:24]
# mu = mu[0:24]
# real_value = real_value[0:24]
#
# predicted_min = min  # 随机生成预测最小值
# predicted_max = max  # 随机生成预测最大值
# predicted_values = mu  # 随机生成预测值
# actual_values = real_value  # 随机生成真实值
#
#
# fig, ax = plt.subplots(figsize=(6, 3))
#
# # 创建填充区域
# ax.fill_between(x, predicted_min, predicted_max, color='lightblue', alpha=0.5)
#
# # 绘制预测值最大值和最小值的折线
# ax.plot(x, predicted_max, color='#003366', label='区间上界')  # 深蓝色
# ax.plot(x, predicted_min, color='#990000', label='区间下界')  # 深红色
# ax.plot(x, predicted_values, color='#999999', label='预测值')  # 柔和橙色
#
# # 绘制预测值和真实值的点
# # plt.scatter(x, predicted_values, color='#BEB8DC', label='预测值', marker='o')  # 柔和蓝色
# ax.scatter(x, actual_values, color='#FFBE7A', label='真实值', marker='o', s=20)  # 柔和橙色
#
# # 设置图形属性
# ax.set_title('区间概率不确定集——光伏', fontsize=15, fontproperties=font_prop)
# ax.set_xlabel('时间尺度/h', fontsize=12.5, fontproperties=font_prop)
# ax.set_ylabel('功率/KW', fontsize=12.5, fontproperties=font_prop)
#
# ax.set_xticks([0, 6, 12, 18, 24])  # 设置x轴刻度为1到24
# ax.grid(False)
#
# # 调整刻度字体大小
# ax.tick_params(axis='both', labelsize=10)
#
# # 设置图例并调整字体大小
# ax.legend(fontsize=14)
#
# ax.legend(prop=font_prop)
#
# # 调整图形的边距
# plt.subplots_adjust(top=0.9, bottom=0.2)   # 减少顶部边距，增加底部边距
#
# # 显示图形
# plt.show()

"""
盒式不确定集
"""
# # 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path, size=12.5)
#
# # 数据准备
# x = np.arange(1, 25)  # 24个柱体的x坐标
# # path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx"
# path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\pv.xlsx"
# dataset = pd.read_excel(path)
# min = dataset['min'].values
# max = dataset['max'].values
# mu = dataset['mu'].values
# real_value = dataset['real_value'].values
# min = min[0:24]
# max = max[0:24]
# mu = mu[0:24]
# real_value = real_value[0:24]
# rate = mu * 0.2
# min = mu - rate
# max = mu + rate
#
# predicted_min = min  # 随机生成预测最小值
# predicted_max = max  # 随机生成预测最大值
# predicted_values = mu  # 随机生成预测值
# actual_values = real_value  # 随机生成真实值
#
# fig, ax = plt.subplots(figsize=(6, 3))
#
# # 创建填充区域
# ax.fill_between(x, predicted_min, predicted_max, color='lightblue', alpha=0.5)
#
# # 绘制预测值最大值和最小值的折线
# ax.plot(x, predicted_max, color='#003366', label='区间上界')  # 深蓝色
# ax.plot(x, predicted_min, color='#990000', label='区间下界')  # 深红色
# ax.plot(x, predicted_values, color='#999999', label='预测值')  # 柔和橙色
#
# # 绘制预测值和真实值的点
# # plt.scatter(x, predicted_values, color='#BEB8DC', label='预测值', marker='o')  # 柔和蓝色
# ax.scatter(x, actual_values, color='#FFBE7A', label='真实值', marker='o', s=20)  # 柔和橙色
#
# # 设置图形属性
# ax.set_title('传统盒式不确定集——光伏', fontsize=15, fontproperties=font_prop)
# ax.set_xlabel('时间尺度/h', fontsize=12.5, fontproperties=font_prop)
# ax.set_ylabel('功率/KW', fontsize=12.5, fontproperties=font_prop)
#
# ax.set_xticks([0, 6, 12, 18, 24])  # 设置x轴刻度为1到24
# ax.grid(False)
#
# # 调整刻度字体大小
# ax.tick_params(axis='both', labelsize=10)
#
# # 设置图例并调整字体大小
# ax.legend(fontsize=14)
#
# ax.legend(prop=font_prop)
#
# # 调整图形的边距
# plt.subplots_adjust(top=0.9, bottom=0.2)   # 减少顶部边距，增加底部边距
#
# # 显示图形
# plt.show()

"""
————————————实验2————————————
"""

"""
功率平衡图
"""
# 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path)
#
# # 处理数据
# path = r"C:\software\Github\DRLmicrogrid\Model_zzy\results_ro.xlsx"
# dataset = pd.read_excel(path)
#
# params = dataset.iloc[:, 0]
# results = dataset.iloc[:, 1]
#
# series_array = pd.Series(params)
# params = series_array[~series_array.isna() & (series_array != '')].values
#
# series_array0 = pd.Series(results)
# results = series_array0[~series_array0.isna() & (series_array0 != '')].values
#
# # 数据准备
# num_bars = 24  # 柱体数量
# num_layers = 5  # 每个柱体的叠层数量

"电力子系统"
# title = "电力子系统"
# load, storage_ch, eb, er, hp, storage_dis, flex_load, pv, wt, cchp, cpp = getEnergySystemData(type='e', params=params,
#                                                                                               results=results)
# positive_layers = np.concatenate((cpp, storage_dis, flex_load, pv, wt))  # 正半轴
# positive_layers = positive_layers.reshape(-1, 24)
# positive_layers = positive_layers.T
# negative_layers = np.concatenate((load, storage_ch, eb, er, hp))  # 负半轴
# negative_layers = negative_layers.reshape(-1, 24)
# negative_layers = negative_layers.T
#
# # positive_color = np.array(["#934B43", "#6f9fb7", "#c2d8de", "#e5e2b8", "#c6624b"])
# # negative_color = np.array(["#14517C", '#B0C4DE', '#c6624b', "#e3ae7b", '#D3D3D3'])
# positive_color = np.array(["#C74436", "#6BA3CB", "#9CC8E0", "#E9D898", "#FFA458"])
# negative_color = np.array(["#1C3C63", '#970529', '#F7E5B6', "#FF8C4A", '#2F5E8C'])
# positive_name = np.array(["外购电", "放能", "柔性负荷", "PV", "WT"])
# negative_name = np.array(["电负荷", "充能", "EB", "ER", "GSHP"])

#
# "天然气子系统"
# title = "天然气子系统"
# load, cchp, flex_load, gw = getEnergySystemData(type='g', params=params, results=results)
# positive_layers = np.concatenate((gw, flex_load))  # 正半轴
# positive_layers = positive_layers.reshape(-1, 24)
# positive_layers = positive_layers.T
# negative_layers = np.concatenate((load, cchp))  # 负半轴
# negative_layers = negative_layers.reshape(-1, 24)
# negative_layers = negative_layers.T
#
# positive_color = np.array(["#C74436", "#6BA3CB", "#9CC8E0", "#E9D898", "#FFA458"])
# negative_color = np.array(["#1C3C63", '#970529', '#F7E5B6', "#FF8C4A", '#2F5E8C'])
# positive_name = np.array(["外购气", "柔性负荷"])
# negative_name = np.array(["气负荷", "CCHP"])


"热能子系统"
# title = "热能子系统"
# load, storage_ch, storage_dis, flex_load, hp, eb = getEnergySystemData(type='th', params=params, results=results)
# positive_layers = np.concatenate((storage_dis, flex_load, hp, eb))  # 正半轴
# positive_layers = positive_layers.reshape(-1, 24)
# positive_layers = positive_layers.T
# negative_layers = np.concatenate((load, storage_ch))  # 负半轴
# negative_layers = negative_layers.reshape(-1, 24)
# negative_layers = negative_layers.T
#
# positive_color = np.array(["#C74436", "#6BA3CB", "#9CC8E0", "#E9D898", "#FFA458"])
# negative_color = np.array(["#1C3C63", '#970529', '#F7E5B6', "#FF8C4A", '#2F5E8C'])
# positive_name = np.array(["放能", "柔性负荷", "GSHP", "EB"])
# negative_name = np.array(["热负荷", "充能"])

#
# "冷能子系统"
# title = "冷能子系统"
# load, storage_ch, storage_dis, er = getEnergySystemData(type='c', params=params, results=results)
# positive_layers = np.concatenate((storage_dis, er))  # 正半轴
# positive_layers = positive_layers.reshape(-1, 24)
# positive_layers = positive_layers.T
# negative_layers = np.concatenate((load, storage_ch))  # 负半轴
# negative_layers = negative_layers.reshape(-1, 24)
# negative_layers = negative_layers.T
#
# positive_color = np.array(["#C74436", "#6BA3CB", "#9CC8E0", "#E9D898", "#FFA458"])
# negative_color = np.array(["#1C3C63", '#970529', '#F7E5B6', "#FF8C4A", '#2F5E8C'])
# positive_name = np.array(["放能", "ER"])
# negative_name = np.array(["冷负荷", "充能"])
#
#

# # 创建叠加柱体的正半轴
# x = np.arange(0, num_bars)  # x坐标（1到24）
# bottom = np.zeros(num_bars)  # 叠加的底部起始位置
#
# # 绘图
# fig, ax = plt.subplots(figsize=(6, 3))
#
# for i in range(positive_layers.shape[1]):
#     ax.bar(x, positive_layers[:, i], bottom=bottom, color=positive_color[i], alpha=0.8, label=positive_name[i])
#     bottom += positive_layers[:, i]  # 更新底部位置
#
# # 创建叠加柱体的负半轴
# bottom_neg = np.zeros(num_bars)  # 负半轴叠加的底部起始位置
#
# for i in range(negative_layers.shape[1]):
#     ax.bar(x, -negative_layers[:, i], bottom=-bottom_neg, color=negative_color[i], alpha=0.7, label=negative_name[i])
#     bottom_neg += negative_layers[:, i]  # 更新负半轴的底部位置
#
#
# # 设置图形属性
# ax.set_xlabel('时间尺度/h', fontproperties=font_prop, fontsize=12.5)
# ax.set_ylabel('功率/KW', fontproperties=font_prop, fontsize=12.5)
# ax.set_title(f'{title}功率平衡图', fontproperties=font_prop, fontsize=12.5)
# ax.set_xticks([0, 6, 12, 18, 24])  # 设置x轴刻度为1到24
# ax.axhline(0, color='black', linewidth=0.8)  # 添加水平基线
# ax.legend(prop=font_prop, loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=5, fontsize=11)  # 添加图例
# ax.grid(False)
#
# # 调整图形的边距
# plt.subplots_adjust(top=1, bottom=0.6)  # 减少顶部边距，增加底部边距
#
# # 显示图形
# plt.tight_layout()
# plt.show()


"""
————————————实验3——————————————
"""

"""
储能与外网供能对比
"""
# 设置字体
font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
font_prop = font_manager.FontProperties(fname=font_path)

# 处理数据
path = r"C:\software\Github\DRLmicrogrid\Model_zzy\results_ro.xlsx"
dataset = pd.read_excel(path)

params = dataset.iloc[:, 0]
results = dataset.iloc[:, 1]

series_array = pd.Series(params)
params = series_array[~series_array.isna() & (series_array != '')].values

series_array0 = pd.Series(results)
results = series_array0[~series_array0.isna() & (series_array0 != '')].values


# 时间数据
time = np.array([0, 6, 12, 18, 24])

"————储能————"

# 电能子系统
CP, DP, CP_US, CP_DS, DP_US, DP_DS, E = getStorageResult(type='e', params=params, results=results)
title = "储电装置"

# 热能子系统
# CP, DP, CP_US, CP_DS, DP_US, DP_DS, storage_power = getStorageResult(type='th', params=params, results=results)
# title = "储热装置"

# 冷能子系统
# CP, DP, CP_US, CP_DS, DP_US, DP_DS, storage_power = getStorageResult(type='c', params=params, results=results)
# title = "储冷装置"

"————外网供能————"
# 外网供能数据
CPP_name = "cpp_01P"
GW_name = "gw_01P"

CPP = getDecisionVariableResult(CPP_name, params, results)
GW = getDecisionVariableResult(GW_name, params, results)

fig, ax = plt.subplots(figsize=(6, 3))
x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
# 绘制设备运行区间
# ax.fill_between(time, equipment_operation, label='设备运行区间', alpha=0.3, color='lightblue')
# 绘制充电
ax.bar(x, CP, label='充电', color='#82B0D2')
# ax.plot(x, CP, label='充电', color='#82B0D2')
zero = np.zeros(24)
CP_L_US = CP - CP_DS
DP_L_DS = -DP + DP_DS

for i in range(24):
    if CP_L_US[i] <=0:
        CP_L_US[i] = zero[i]
    if DP_L_DS[i] >=0:
        DP_L_DS[i] = zero[i]

# 绘制充电灵活备用区间
ax.fill_between(x, CP_L_US, CP + CP_US, label='充能灵活备用区间', alpha=0.3, color='gray')

# 绘制放电
ax.bar(x, -DP, label='放电', color='#8ECFC9')
# 绘制放电灵活备用区间
ax.fill_between(x, DP_L_DS, -DP - DP_US, label='放能灵活备用区间', alpha=0.3, color='gray')
# 绘制SOC
# plt.plot(E, label='SOC', color='green')

ax.set_xlabel('时间尺度/h', fontproperties=font_prop, fontsize=12.5)
ax.set_ylabel('功率/kW', fontproperties=font_prop, fontsize=12.5)
ax.set_title(f"{title}", fontproperties=font_prop, fontsize=12.5)
ax.axhline(0, color='black', linewidth=0.8)

ax.set_xticks(time)

ax2 = ax.twinx()
ax2.plot(CPP, label='电网', color='#F27970')
ax2.plot(GW, label='气网', color='#BB9727')
# ax2.plot(E, label='储量', color='#F27970')

# 合并
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

all_lines = lines1 + lines2
all_labels = labels1 + labels2

ax.legend(all_lines, all_labels, prop=font_prop, loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=11)
# ax.legend(prop=font_prop, loc="upper center", bbox_to_anchor=(0.5, -0.27), ncol=4, fontsize=11)
plt.subplots_adjust(top=0.9, bottom=0.35)
plt.show()

# print(f"storage_e_01CP{CP}")
# print(f"storage_e_01DP{DP}")
# print(f"storage_e_01E{E}")
# print(f"storage_e_01ch_us{CP_US}")
# print(f"storage_e_01ch_ds{CP_DS}")
# print(f"storage_e_01ch_us{DP_US}")
# print(f"storage_e_01ch_ds{DP_DS}")