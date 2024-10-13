import numpy as np
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import torch

# 不再继承 nn.Module，因为 ARIMA-GARCH 不是一个神经网络模型
class ARIMAGARCH:
    def __init__(self, arima_order=(1, 1, 1), garch_order=(1, 1), prediction_length=24):
        self.arima_order = arima_order
        self.garch_order = garch_order
        self.prediction_length = prediction_length

    def fit_and_forecast(self, series):
        # 1. ARIMA 模型拟合
        arima_model = ARIMA(series, order=self.arima_order)
        arima_result = arima_model.fit()

        # 2. 获取 ARIMA 模型的残差
        residuals = arima_result.resid

        # 3. 使用 GARCH 模型对残差进行拟合
        garch_model = arch_model(residuals, vol='Garch', p=self.garch_order[0], q=self.garch_order[1])
        garch_result = garch_model.fit(disp="off")

        # 4. 进行预测
        arima_forecast = arima_result.forecast(steps=self.prediction_length).values
        garch_forecast = garch_result.forecast(horizon=self.prediction_length)
        sigma = np.sqrt(garch_forecast.variance.values[-1, :])

        return arima_forecast, sigma


def arima_garch_train_test(model, dataloader, context_length, prediction_length, testloader=None, model_path='arima_garch.pth'):
    all_mu = []
    all_sigma = []
    all_target = []

    # 遍历数据集
    for context, target in dataloader:
        context = context.cpu().numpy()
        target = target.cpu().numpy()

        batch_size = context.shape[0]

        for i in range(batch_size):
            series = context[i, :, 0]
            true_values = target[i, :]

            # 使用 ARIMA-GARCH 模型进行预测
            mu, sigma = model.fit_and_forecast(series)

            # 存储预测结果
            all_mu.append(mu)
            all_sigma.append(sigma)
            all_target.append(true_values)

    all_mu = np.array(all_mu).flatten()
    all_sigma = np.array(all_sigma).flatten()
    all_target = np.array(all_target).flatten()

    # 如果有测试集，则在测试集上进行同样的预测并绘图
    if testloader is not None:
        all_test_mu = []
        all_test_sigma = []
        all_test_target = []

        for context, target in testloader:
            context = context.cpu().numpy()
            target = target.cpu().numpy()

            batch_size = context.shape[0]

            for i in range(batch_size):
                series = context[i, :, 0]
                true_values = target[i, :]

                # 使用 ARIMA-GARCH 模型进行预测
                mu, sigma = model.fit_and_forecast(series)

                all_test_mu.append(mu)
                all_test_sigma.append(sigma)
                all_test_target.append(true_values)

        all_test_mu = np.array(all_test_mu).flatten()
        all_test_sigma = np.array(all_test_sigma).flatten()
        all_test_target = np.array(all_test_target).flatten()

        # 绘制预测结果和真实值
        time_steps = np.arange(len(all_test_target.flatten()))

        plt.figure(figsize=(12, 6))
        plt.plot(time_steps, all_test_target.flatten(), label='Measured Wind Power', color='blue')
        plt.plot(time_steps, all_test_mu.flatten(), label='ARIMA-GARCH Forecasts (mu)', color='orange')

        # 绘制置信区间
        plt.fill_between(time_steps, all_test_mu - 2 * all_test_sigma, all_test_mu + 2 * all_test_sigma,
                         color='orange', alpha=0.3, label='Confidence Interval (2 * sigma)')

        plt.title('Training Loss ' + "(" + model_path + ")")
        plt.legend(loc='upper left')
        plt.show()

    return all_mu, all_sigma, all_target


