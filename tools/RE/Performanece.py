import numpy as np
from tools.RE.Logic_RE import getDataFromExcel, get_re_narure_data

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

########----------------------------MAE------------------------------------##################
def MAE_count(predictions, observations):
    mae_data = np.sum(np.abs(predictions - observations)) / np.sum(observations)
    return mae_data

def MAE_count_test(day):
    observations = get_re_narure_data(1)
    predictions = get_re_narure_data(day)
    mea = MAE_count(predictions, observations)
    print(mea)

########----------------------------RMSE------------------------------------##################
def RMSE_count(predictions, observations):
    RMSE_data = np.sqrt(np.sum((predictions - observations)  ** 2) / (len(predictions[0]) * np.sum(observations) ** 2))
    return RMSE_data

def RMSE_count_test(day):
    observations = get_re_narure_data(1)
    predictions = get_re_narure_data(day)
    rmse = RMSE_count(predictions, observations)
    print(rmse)

########----------------------------PS------------------------------------##################
def PS_count(predictions, observations, tau):
    predictions = predictions.flatten()
    observations = observations.flatten()
    PS_data= np.array([])
    for i in range(len(observations)):
        temp = 0
        if observations[i] >= predictions[i]:
            temp = tau * (observations[i] - predictions[i])
        else:
            temp = (tau - 1) * (observations[i] - predictions[i])
        if observations[i] != 0:
            temp = temp / observations[i]
        PS_data = np.append(PS_data, temp)
    PS_data = np.sum(PS_data) / len(observations)
    return PS_data

def PS_count_test(day, tau):
    observations = get_re_narure_data(1)
    predictions = get_re_narure_data(day)
    ps = PS_count(predictions, observations, tau)
    #print(ps)
    return ps

def plot_3d_data(data, tau_start=0.05, tau_end=1.00, tau_step=0.05):
    """
    绘制三维数据图

    参数:
    data: 二维 numpy 数组，形状为 (n_tau, data_length)，表示不同 τ 值和每组数据的长度
    tau_start: float, τ 的起始值
    tau_end: float, τ 的结束值（不包括在内）
    tau_step: float, τ 的步长

    返回:
    None
    """
    # 生成 τ 的取值范围
    tau_values = np.arange(tau_start, tau_end, tau_step)

    # 检查数据形状是否与 τ 值的数量匹配
    if data.shape[0] != len(tau_values):
        raise ValueError("数据的行数应与 τ 值的数量匹配")

    # 创建网格
    X, Y = np.meshgrid(np.arange(data.shape[1]), tau_values)

    # 创建图形
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 绘制三维表面图
    surf = ax.plot_surface(X, Y, data, cmap='viridis')

    # 添加颜色条
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    # 添加标签
    ax.set_xlabel('Data Index')
    ax.set_ylabel('τ Value')
    ax.set_zlabel('Pinball Score')

    # 显示图形
    plt.show()

def test_PS():
    temp =np.array([])
    for j in range(19):
        num_temp = np.array([])
        for i in range(146):
            #print(i+2, ":", end=" ")
            a = PS_count_test(i+2, 0.05 + j * 0.05)
            num_temp = np.append(num_temp, a)
        temp = np.append(temp, num_temp)
    temp = temp.reshape(int(len(temp)/146), 146)
    plot_3d_data(temp)

########----------------------------CRPS------------------------------------##################
def CRPS_count(predictions, observations):
    CRPS_value = np.array([])
    for i in range(len(observations)):
        y = observations[i]
        ensemble = predictions[:, i]
        ensemble = np.sort(ensemble)
        n = len(ensemble)
        indicator = (ensemble >= y).astype(int)
        crps = np.mean((indicator - (np.arange(n) + 1) / n) ** 2)
        CRPS_value = np.append(CRPS_value, crps)
    return np.mean(CRPS_value)

def CRPS_count_test():
    observations = get_re_narure_data(1).flatten()
    predictions = np.array([])
    for i in range(146):
        predictions = np.append(predictions, get_re_narure_data(i + 2).flatten())
    predictions = predictions.reshape(146, len(observations))
    crps = CRPS_count(predictions, observations)
    return crps
########----------------------------ACE------------------------------------##################
# def ACE_count():

########----------------------------TEST------------------------------------##################
# print(CRPS_count_test())
# from scipy.stats import norm
# # 示例数据
# n_samples = 1000  # 每个预测的样本数
# n_predictions = 147  # 预测值和实际观测值的长度
#
# # 生成随机预测值（每个预测是一个概率分布的样本集合）
# predictions = norm.rvs(loc=0.5, scale=0.1, size=(n_samples, n_predictions))
#
# # 生成实际观测值
# observations = norm.rvs(loc=0.5, scale=0.1, size=n_predictions)