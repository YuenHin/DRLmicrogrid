import numpy as np

from RE.Plot_RE import plot_wind_power2, draw_solar_nature, plot_solar_wind_power
from maybeExcel import getDataFromExcel

import matplotlib.pyplot as plt

########----------------------------Basic_data-getting------------------------------------##################
def get_re_narure_data(day):
    file = "D:\project\diffusion\data\RE\\2024_re_nature_"+ str(day) + ".xlsx"
    data = getDataFromExcel(file, 0, 14, 0, 96)
    #0：全球辐射
    #1：直接辐射
    #2：散射辐射
    #3:6英尺风速    7：6英尺风向    11：压力（kpa）
    #4：19英尺风速  8：19英尺风向   12:温度（摄氏度）
    #5：22英尺风速  9：22英尺风向   13：空气密度（kg/m^3）
    #6：33英尺风速  10：33英尺风向
    return data

########----------------------------风力发电出力数据------------------------------------##################
def get_draw_wind_generation_power(day, power_coefficient, area, draw = False):
    """
    Calculate wind power output.

    Parameters:
    density (float): Air density (kg/m^3)
    area (float): Swept area of wind turbine blades (m^2)
    wind_speed (list or array-like): Wind speed at different times (m/s)
    power_coefficient (float): Power coefficient (Cp)

    Returns:
    list: Power output at different times (W)
    """
    data = get_re_narure_data(day)
    density = np.array([row[13] for row in data])
    area = np.zeros(len(density)) + area
    power_coefficient = np.zeros(len(density)) + power_coefficient

    wind_speed_6 = np.array([row[0 + 3] for row in data])
    wind_speed_19 = np.array([row[1 + 3] for row in data])
    wind_speed_33 = np.array([row[3 + 3] for row in data])

    wind_power_6 = density * area * power_coefficient * (wind_speed_6 ** 3) / 2  / 1000
    wind_power_19 = density * area * power_coefficient * (wind_speed_19 ** 3) / 2 / 1000
    wind_power_33 = density * area * power_coefficient * (wind_speed_33 ** 3) / 2 / 1000

    if draw:
        plot_wind_power2(wind_power_6, wind_power_19, wind_power_33)
    return wind_power_6, wind_power_19, wind_power_33

########----------------------------太阳能发电出力数据------------------------------------##################
def get_draw_solar_nature_ending(day, draw = False):
    file = "D:\project\diffusion\data\RE\\2024_re_nature_" + str(day) + ".xlsx"
    global_radiation = getDataFromExcel(file, 0, 1, 0, 96).flatten()
    direct_radiation = getDataFromExcel(file, 1, 2, 0, 96).flatten()
    diffusion_radiation = getDataFromExcel(file, 2, 3, 0, 96).flatten()
    if draw:
        draw_solar_nature(global_radiation, direct_radiation, diffusion_radiation, day)
    return global_radiation, direct_radiation, diffusion_radiation

########----------------------------太阳能发电出力数据------------------------------------##################
def get_solar_generation_power(day, power_coefficient, area):
    global_radiation, direct_radiation, diffusion_radiation = get_draw_solar_nature_ending(day)
    area = np.zeros(len(global_radiation)) + area
    power_coefficient = np.zeros(len(global_radiation)) + power_coefficient

    solar_power = (global_radiation + direct_radiation + diffusion_radiation) * area * power_coefficient / 1000

    return solar_power
########----------------------------太阳能+风力发电出力数据------------------------------------##################
def get_draw_solar_wind_generation_power(day, wind_power_coefficient, wind_area, solar_power_coefficient, solar_area, draw = False):
    wind_power_6, wind_power_19, wind_power_33 = get_draw_wind_generation_power(day, wind_power_coefficient, wind_area)
    solar_power = get_solar_generation_power(day, solar_power_coefficient, solar_area)

    if draw:
        plot_solar_wind_power(wind_power_6, wind_power_19, wind_power_33, solar_power, day)
    return wind_power_6, wind_power_19, wind_power_33, solar_power

#get_draw_solar_wind_generation_power(4, 0.45, 10000, 0.339, 1000, True)


# for i in range(10):
#     get_draw_solar_wind_generation_power(i+141, 0.45, 10000, 0.339, 1000, True)


#读取若干天的数据
def get_total_day_re_narure_data(day):
    combined_data = np.empty((0, 14))
    for i in range(day):
        data = get_re_narure_data(i + 1)
        combined_data = np.concatenate((combined_data, data), axis=0)
    return combined_data

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset


#循环用的主函数

from Generation.DeepAR.algorithm import GRUDeepAR, LSTMDeepAR, TransformerDeepAR
from Generation.DeepAR.DeepAR import train_deepar_nll, test_deepar, calculate_metrics

#最终计算风力出力的概率分布函数
def count_GS_windPower(wind_speed_mean, wind_speed_std, density_mean, density_std, area, power_coefficient, wind_power_True):
    # 生成样本数量
    num_samples = 10000
    # 预测3天的数据
    time_steps = 96 * 3
    # 从高斯分布中生成样本
    wind_speed_samples = np.random.normal(wind_speed_mean, wind_speed_std, num_samples)
    density_samples = np.random.normal(density_mean, density_std, num_samples)

    # 从高斯分布中生成样本
    wind_speed_samples = np.random.normal(wind_speed_mean, wind_speed_std, (num_samples, time_steps))
    density_samples = np.random.normal(density_mean, density_std, (num_samples, time_steps))

    # 计算风力出力
    wind_power_samples = density_samples * area * power_coefficient * (wind_speed_samples ** 3) / 2 / 1000  # 转换为千瓦

    # 计算均值和真实值
    mean_wind_power = np.mean(wind_power_samples, axis=0)
    true_wind_power = wind_power_True  # 假设第一组样本作为真实值


    # 绘制风力出力的概率分布
    plt.figure(figsize=(12, 6))
    time = np.arange(time_steps)

    # 绘制所有样本
    for i in range(num_samples):
        plt.plot(time, wind_power_samples[i], color='gray', alpha=0.01, label='Wind Power Scenario')

    # 绘制均值
    plt.plot(time, mean_wind_power, color='orange', label='Deterministic Forecasts')

    # 绘制真实值
    plt.plot(time, true_wind_power, color='blue', label='Measured Wind Power')

    plt.title('Probability Distribution of Wind Power Output')
    plt.xlabel('Time Step')
    plt.ylabel('Wind Power Output (kW)')
    plt.legend()
    plt.show()

class CustomDataset(Dataset):
    def __init__(self, data, target, context_length, prediction_length):
        self.data = data
        self.target = target
        self.context_length = context_length
        self.prediction_length = prediction_length

    #用于定义当对一个数据集对象调用 len() 函数时应该返回的值。
    def __len__(self):
        return len(self.data) - self.context_length - self.prediction_length + 1

    def __getitem__(self, idx):
        context = self.data[idx:idx + self.context_length]
        target = self.target[idx + self.context_length:idx + self.context_length + self.prediction_length]
        return torch.tensor(context, dtype=torch.float32), torch.tensor(target, dtype=torch.float32)

# 自定义数据集类
class TimeSeriesDataset(Dataset):
    def __init__(self, data, target, context_length, prediction_length):
        self.data = data
        self.target = target
        self.context_length = context_length
        self.prediction_length = prediction_length

    def __len__(self):
        return len(self.data) - self.context_length - self.prediction_length + 1

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            raise TypeError("Expected idx to be an integer, got slice.")

        context = self.data[idx:idx + self.context_length]
        target = self.target[idx + self.context_length:idx + self.context_length + self.prediction_length]
        return torch.tensor(context, dtype=torch.float32), torch.tensor(target, dtype=torch.float32), idx

# 准备数据
def prepare_data(data, feature_indices, target_feature_index):
    selected_features = data[:, feature_indices]
    target = data[:, target_feature_index]
    return selected_features, target

def create_dataloaders(data, target, context_length, prediction_length, batch_size):
    # 确定训练集和测试集的大小
    train_data = data[:96 * 27]
    train_target = target[:96 * 27]
    # 确保测试数据足够大，以满足后续处理需求
    test_data = data[96 * 27 - context_length:]
    test_target = target[96 * 27:]

    # 创建数据集
    train_dataset = CustomDataset(train_data, train_target, context_length, prediction_length)
    test_dataset = CustomDataset(test_data, test_target, context_length, prediction_length)

    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader


def extract_targets(dataloader):
    targets = []
    for _, target in dataloader:
        targets.append(target.numpy())
    return np.concatenate(targets, axis=0)

# 主函数
def main(data,features ,feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, only_test = False):
    input_size = len(feature_indices)
    #input:data:(96*30, 14)
    #output:data:(96*30, feature_indices)
    #       target:(96*30, target_feature_index)
    data, target = prepare_data(data, feature_indices, target_feature_index)

    #Context shape: torch.Size([32, 96, 14]), Target shape: torch.Size([32, 24])
    train_loader, test_loader = create_dataloaders(data, target, context_length, prediction_length, batch_size)

    if model_type == 'DeepAR_GRU':
        model = GRUDeepAR(input_size, hidden_size, num_layers, prediction_length)
    elif model_type == 'DeepAR_LSTM':
        model = LSTMDeepAR(input_size, hidden_size, num_layers, prediction_length)
    elif model_type == 'DeepAR_Transformer':
        model = TransformerDeepAR(input_size, hidden_size, num_layers, prediction_length)
    else:
        raise ValueError("Invalid model type")

    model_path = f'{model_type.lower()}_'+features[target_feature_index]+'.pth'
    if only_test is False:
        train_deepar_nll(model, train_loader, model_path=model_path)

    pred_mu, pred_sigma, target = test_deepar(model, test_loader, context_length, prediction_length, model_path=model_path)
    metrics = calculate_metrics(pred_mu, target, pred_sigma)

    print(metrics)

# 示例调用
if __name__ == '__main__':
    data = get_total_day_re_narure_data(30)
    features = ["global radiation", "direct radiation", "diffusion radiation", "6ft-wind-speed", "19ft-wind-speed", "22ft-wind-speed", "33ft-wind-speed", "6ft-wind-direction", "19ft-wind-direction", "22ft-wind-direction", "33ft-wind-direction", "Station Pressure", "Temperature", "Air Density"]
    feature_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]  # 选择特定特征的索引作为输入
    target_feature_index = 6  # 例如，选择第 4 列特征作为目标
    context_length = 24
    prediction_length = 12
    batch_size = 32
    hidden_size = 128
    num_layers = 2

    model_type = 'DeepAR_GRU'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, only_test=False)
    # model_type = 'DeepAR_LSTM'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    # main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
    #      hidden_size, num_layers, model_type, only_test=True)
    # model_type = 'DeepAR_Transformer'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    # main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
    #      hidden_size, num_layers, model_type, only_test=True)
    #
    # target_feature_index = 13  # 例如，选择第 4 列特征作为目标
    # model_type = 'DeepAR_GRU'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    # main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
    #      hidden_size, num_layers, model_type, only_test=True)
    # model_type = 'DeepAR_LSTM'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    # main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
    #      hidden_size, num_layers, model_type, only_test=True)
    # model_type = 'DeepAR_Transformer'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
    # main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
    #      hidden_size, num_layers, model_type, only_test=True)






