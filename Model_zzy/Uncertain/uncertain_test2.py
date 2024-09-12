import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
import sklearn.gaussian_process.kernels as k
import pandas as pd
from scipy.stats import t
from sklearn.metrics.pairwise import rbf_kernel

"""
用的是这个
"""

"""
电负荷
"""
# training_days = 15
# testing_days = 15
# total_time_num = 96
# time_period = 15
# confidence_level = 0.9
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\load_e.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "load_e"

"""
气负荷
"""
# training_days = 15
# testing_days = 15
# total_time_num = 96
# time_period = 15
# confidence_level = 0.95
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\load_g.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "load_g"

"""
热负荷
"""
# training_days = 7
# testing_days = 7
# total_time_num = 96
# time_period = 15
# confidence_level = 0.95
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\load_h.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "load_h"

"""
冷负荷
"""
# training_days = 7
# testing_days = 7
# total_time_num = 96
# time_period = 15
# confidence_level = 0.95
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\load_c.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "load_c"

"""
光伏
"""
training_days = 15
testing_days = 15
total_time_num = 96
time_period = 15
confidence_level = 0.95
file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\pv.xlsx'
training_column_name = 'training_power'
testing_column_name = 'testing_power'
column_name = "testing_power"
n_samples = training_days * total_time_num
name = "pv"

"""
风电
"""
# training_days = 3
# testing_days = 3
# total_time_num = 96
# time_period = 15
# confidence_level = 0.9
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\wt.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "wt"

"""
地缘热泵
"""
# training_days = 7
# testing_days = 7
# total_time_num = 96
# time_period = 15
# confidence_level = 0.9
# file_path = 'C:\software\Github\DRLmicrogrid\Data\Predict\hp.xlsx'
# training_column_name = 'training_power'
# testing_column_name = 'testing_power'
# column_name = "testing_power"
# n_samples = training_days * total_time_num
# name = "hp"


def get_excel_data(file_path):
    df = pd.read_excel(file_path)
    return df

def get_X(column_name, days, total_time_num, time_period):
    data = df[column_name].values
    data = data[:days * total_time_num]
    return data

def get_y(column_name, days, total_time_num, time_period):
    data = df[column_name].values
    data = data[days * total_time_num:(days + 1) * total_time_num]
    return data


def data_dealing(data, days, total_time_num, time_period):
    x_data = np.zeros((total_time_num, days))
    for i in range(total_time_num):
        for j in range(days):
            x_data[i][j] = data[i + total_time_num * j]
    return x_data

# def get_y_test(total_time_num):
#     y_test = np.zeros(total_time_num)
#     return y_test
#
# def get_X_test(total_time_num, time_period):
#     X_test = np.zeros(total_time_num)
#     for i in range(total_time_num):
#         X_test[i] = i * time_period
#     return X_test


def gaussian_kernel(x1, x2, l=1.0, sigma_f=1.0):
    """Easy to understand but inefficient."""
    m, n = x1.shape[0], x2.shape[0]
    dist_matrix = np.zeros((m, n), dtype=float)
    for i in range(m):
        for j in range(n):
            dist_matrix[i][j] = np.sum((x1[i] - x2[j]) ** 2)
    return sigma_f ** 2 * np.exp(- 0.5 / l ** 2 * dist_matrix)

def gaussian_kernel_vectorization(x1, x2, l=1.0, gamma=1.0):
    """More efficient approach."""
    # dist_matrix = np.sum(x1**2, 1).reshape(-1, 1) + np.sum(x2**2, 1) - 2 * np.dot(x1, x2.T)
    # return gamma ** 2 * np.exp(-0.5 / l ** 2 * dist_matrix)
    kernel_value = rbf_kernel(x1, x2, gamma=gamma)
    return kernel_value


df = get_excel_data(file_path)
# 得到训练数据
# training_data = get_X(column_name, training_days, total_time_num, time_period)
# X_train = data_dealing(training_data, training_days, total_time_num, time_period)
# X_train = X_train.T
# y_train = get_y(column_name, training_days, total_time_num, time_period)
training_data = get_X(training_column_name, training_days, total_time_num, time_period)
X_train = data_dealing(training_data, training_days, total_time_num, time_period)
y_train = get_y(training_column_name, training_days, total_time_num, time_period)
print("X_train")
print(X_train)
print("X_train.shape")
print(X_train.shape)
print("y_train")
print(y_train)
print("y_train.shape")
print(y_train.shape)

# # 得到测试数据
# X_test = X_train
# y_test = y_train
testing_data = get_X(testing_column_name, testing_days, total_time_num, time_period)
X_test = data_dealing(testing_data, testing_days, total_time_num, time_period)
y_test = get_y(testing_column_name, testing_days, total_time_num, time_period)
# testing_data = get_X(column_name, testing_days, total_time_num, time_period)
# X_test = data_dealing(testing_data, testing_days, total_time_num, time_period)
# X_test = X_test.T
# y_test = get_y(column_name, testing_days, total_time_num, time_period)
print("X_test")
print(X_test)
print("X_test.shape")
print(X_test.shape)
print("y_test")
print(y_test)
print("y_test.shape")
print(y_test)

# print(X_test.T.shape)

K_XX = gaussian_kernel_vectorization(X_train, X_train, l=training_days, gamma=0.5)
K_X_X = gaussian_kernel_vectorization(X_test, X_train, l=training_days, gamma=0.5)
K_XX_ = gaussian_kernel_vectorization(X_train, X_test, l=training_days, gamma=0.5)
K_X_X_ = gaussian_kernel_vectorization(X_test, X_test, l=training_days, gamma=0.5)
# print("K_XX")
# print(K_XX.shape)
# print("K_X_X")
# print(K_X_X.shape)
# print("K_XX_")
# print(K_XX_.shape)
# print("K_X_X_")
# print(K_X_X_.shape)

# 计算训练数据均值
X_train_mean = np.mean(X_train, axis=1)
print("X_train_mean")
print(X_train_mean.shape)
X_test_mean = np.mean(X_test, axis=1)
var = 0.01 ** 2 * np.eye(X_train.shape[0])

# 计算训练数据方差
X_train_var = np.var(X_train, axis=1)
X_train_std = np.sqrt(X_train_var)

y_pred_mu = K_X_X.dot(np.linalg.inv(K_XX + np.diag(var))).dot(y_train - X_train_mean) + X_test_mean
print("预测值均值")
print(y_pred_mu)
y_pred_var = K_X_X_ - K_X_X.dot(np.linalg.inv(K_XX + np.diag(var))).dot(K_XX_)
print("预测值方差")
print(y_pred_var)
# 标准差
y_pred_std = np.sqrt(y_pred_var)

# 计算置信区间
t_value = t.ppf(confidence_level, testing_days-1)
print(t_value)
length = len(y_pred_mu)
print(y_pred_std.shape)
y_pred_min = np.zeros(length)
y_pred_max = np.zeros(length)

for i in range(length):
    y_pred_min[i] = y_pred_mu[i] - t_value * X_train_std[i] / math.sqrt(testing_days)
    y_pred_max[i] = y_pred_mu[i] + t_value * X_train_std[i] / math.sqrt(testing_days)

print("预测值下限")
print(y_pred_min)
print("预测值上限")
print(y_pred_max)

X_draw = np.zeros(total_time_num)
for i in range(total_time_num):
    X_draw[i] = i * time_period

plt.title(name)
plt.plot(X_draw, y_pred_mu, label="GPR", ls="-", color='purple')
plt.plot(X_draw, y_test, label="real", ls="-", color='red')
plt.fill_between(X_draw,
                y_pred_max,
                y_pred_min,
                label=f"{confidence_level}confidence",
                color="pink")
plt.legend(ncol=4, fontsize=12)
plt.show()
print("finished!")
