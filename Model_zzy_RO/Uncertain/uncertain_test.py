import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
import sklearn.gaussian_process.kernels as k
import pandas as pd
from scipy.stats import t


training_days = 15
testing_days = 15
total_time_num = 96
time_period = 15
confidence_level = 0.05
file_path = '/Predict/load_e.xlsx'
training_column_name = 'training_power'
testing_column_name = 'testing_power'
n_samples = training_days * total_time_num


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

def gpr_regressor(X_train, y_train, X_test, y_test,
                  kernel=k.ConstantKernel(constant_value=0.2, constant_value_bounds=(1e-4, 1e4)) * RBF(length_scale=0.5, length_scale_bounds=(1e-4, 1e4))):
    """
    gpr model for regression
    :param X_train: (n_samples, n_features)
    :param y_train: (n_samples,)
    :param X_test: (n_samples, n_features)
    :param y_test: (n_samples,)
    :param kernel: kernel of gpr
    :return:
        y_pred: mean predictions
        y_pred_std: std predictions
        r2: r2 score of gpr
    """
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2)
    gp.fit(X_train, y_train)  # Instantiated Gaussian regression model
    r2_train = gp.score(X_train, y_train)
    print('r2 coefficient is {:.2f}'.format(r2_train))
    print("the learned kernel parameters:\t {}".format(gp.kernel))  # the learned kernel parameters
    # 得到预测值与标准差
    y_pred, y_pred_std = gp.predict(X_test, return_std=True)
    r2_test = gp.score(X_test, y_test)
    print('r2 coefficient is {:.2f}'.format(r2_test))
    return y_pred, y_pred_std, r2_test


def plot_errorbar_gpr(y_pred, y_pred_std, r2, y_test):
    """
    plot errorbar for gpr predictions
    :param y_pred:
    :param y_pred_std:
    :param r2:
    :param y_test: one-dimension
    :return:
    """

    plt.errorbar(x=y_test, y=y_pred, yerr=y_pred_std, fmt="o", label="Samples", markersize=5, color='#2698eb')
    # x, y define the data locations, xerr, yerr define the errorbar sizes
    plt.xlabel("ground true")
    plt.ylabel("predicted ")
    plt.title("Gaussian process regression, R2=%.2f" % (r2))
    print("finished!")


def plot_intervel_gpr(y_pred, y_pred_std, r2, X_draw, y_pred_min, y_pred_max, y_train, days, total_time_num):
    """
    plot confidence interval for gpr predictions
    :param y_pred:
    :param y_pred_std:
    :param r2:
     :param X_test: should be one-dimension shape
    :return:
    """
    # for i in range(days):
    #     y_draw = y_train[i*total_time_num:(i+1)*total_time_num]
    #     plt.scatter(x=X_draw, y=y_draw, label="observation")
    # plt.plot(X_draw, y_pred, label="GPR", ls="-")

    plt.plot(X_draw, y_pred_max, label="GPR", ls="-", color='black')
    plt.fill_between(X_draw,
                     y_pred_max,
                     y_pred_min,
                     y_pred_max>y_pred_min,
                     label="95% confidence",
                     color="#2698eb")
    plt.legend(ncol=4, fontsize=12)
    plt.title("Gaussian process regression, R2=%.2f" % (r2))
    plt.show()
    print("finished!")

def data_dealing(data, days, total_time_num, time_period):
    x_data = np.zeros((total_time_num, days))
    for i in range(total_time_num):
        for j in range(days):
            x_data[i][j] = data[i + total_time_num * j]
    return x_data

def get_y_test(total_time_num):
    y_test = np.zeros(total_time_num)
    return y_test

def get_X_test(total_time_num, time_period):
    X_test = np.zeros(total_time_num)
    for i in range(total_time_num):
        X_test[i] = i * time_period
    return X_test



df = get_excel_data(file_path)
# 得到训练数据
# training_data = get_X(training_column_name, training_days, total_time_num, time_period)
# X_train = data_dealing(training_data, training_days, total_time_num, time_period)
# y_train = get_y(training_column_name, training_days, total_time_num, time_period)
np.random.seed(0)
X = np.random.rand(total_time_num, 1)
X_train = np.random.rand(n_samples, 1).reshape(total_time_num, training_days)
y_train = np.sin(10*X) + np.cos(5*X) + np.random.normal(scale=0.1, size=total_time_num)
# print(X_train)
# print(X_train.shape)
# print(y_train)
# print(y_train.shape)

# # 得到测试数据
testing_data = get_X(testing_column_name, testing_days, total_time_num, time_period)
X_test = data_dealing(testing_data, testing_days, total_time_num, time_period)
y_test = get_y(testing_column_name, testing_days, total_time_num, time_period)
# print(X_test.shape)
# print(X_test)
# print(y_test.shape)
# print(y_test)

# 高斯回归
# y_pred是预测值 y_pred_std是标准差
y_pred, y_pred_std, r2 = gpr_regressor(X_train, y_train, X_test, y_test)
print(y_pred.shape)
print(y_pred)
print(y_pred_std)
# # 计算置信区间
# t_value = t.ppf(confidence_level, days-1)
# print(t_value)
# length = len(y_pred)
# y_pred_min = np.zeros(length)
# y_pred_max = np.zeros(length)
#
# for i in range(length):
#     y_pred_min[i] = y_pred[i] - t_value * y_pred_std[i] / math.sqrt(days)
#     y_pred_max[i] = y_pred[i] + t_value * y_pred_std[i] / math.sqrt(days)
#
# print(y_pred_std)
# print(y_pred_min)
# print(y_pred_max)
# print(y_pred)








