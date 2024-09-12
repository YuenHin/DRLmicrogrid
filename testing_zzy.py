import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

# 1. 生成示例数据
# 假设我们有30天的电力负荷数据，每天24小时
np.random.seed(1)
days = 30
hours_per_day = 24
X = np.array([[day, hour] for day in range(days) for hour in range(hours_per_day)])
y = np.sin(X[:, 1] / 24 * 2 * np.pi) * 10 + 50 + np.random.normal(0, 2, X.shape[0])

# 2. 定义核函数和高斯过程模型
# 核函数: 常数核 + RBF核
# kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))
kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (0.5, 2))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)

# 3. 训练模型
gp.fit(X, y)

# 4. 进行预测
# 假设我们要预测第31天的电力负荷数据
X_pred = np.array([[30, hour] for hour in range(hours_per_day)])
y_pred, sigma = gp.predict(X_pred, return_std=True)

# 5. 可视化结果
plt.figure(figsize=(14, 7))

# 训练数据可视化
plt.plot(X[:, 1], y, 'r.', markersize=5, label='Training data')

# 预测结果可视化
plt.plot(X_pred[:, 1], y_pred, 'b-', label='Prediction')
plt.fill_between(X_pred[:, 1], y_pred - 1.96 * sigma, y_pred + 1.96 * sigma, alpha=0.2, color='k', label='95% confidence interval')

plt.xlabel('Hour of the day')
plt.ylabel('Load (kW)')
plt.title('Electric Load Prediction for Day 31 using Gaussian Process Regression')
plt.legend(loc='upper left')

plt.show()