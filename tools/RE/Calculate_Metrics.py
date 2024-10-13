import numpy as np

def calculate_metrics(predictions, targets, sigma, alpha=0.05):
    # 检查并调整形状
    if predictions.shape != targets.shape:
        targets = targets.reshape(predictions.shape)

    ev = np.abs((predictions - targets) / targets).mean()
    mae = np.abs(predictions - targets).mean()
    rmse = np.sqrt(((predictions - targets) ** 2).mean())

    # 计算准确率，假设在误差小于某个阈值时，认为是准确的预测
    accuracy_threshold = 0.1  # 你可以根据实际需求调整阈值
    accuracy = np.mean(np.abs(predictions - targets) < accuracy_threshold) * 100  # 转为百分比

    z = np.percentile(sigma, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    coverage = np.mean((targets >= predictions + z[0]) & (targets <= predictions + z[1]))

    pinball_losses = []
    for u in np.arange(0.05, 1, 0.05):
        pinball_loss_u = np.mean(np.maximum(u * (targets - predictions), (u - 1) * (targets - predictions)))
        pinball_losses.append((u, pinball_loss_u))
        #print(f"Pinball Loss at u={u}: {pinball_loss_u}")

    sharpness = sigma.mean()
    interval_width = z[1] - z[0]
    es = (predictions - targets).mean() / np.sqrt(sigma.var())
    vs = np.var(targets - predictions) / sigma.var()

    # CRPS 计算
    M = 100  # 采样数量
    u_values = np.arange(0.05, 1, 0.05)  # 从 0.05 到 0.95 的 CDF 值，间隔 0.05
    crps_total = 0
    for i in range(len(predictions)):  # 遍历所有预测点
        crps_sum = 0
        for u in u_values:  # 对每个 u 值进行计算
            # 计算 phi 函数，表示不同区间内的损失值
            phi_u = np.where(targets[i] >= predictions[i], u * (targets[i] - predictions[i]),
                             (u - 1) * (targets[i] - predictions[i]))
            crps_sum += np.mean(phi_u)  # 累积所有 u 值的 CRPS
        crps_total += crps_sum
    crps = crps_total / len(predictions)  # 平均 CRPS

    return {
        'EV': ev,
        'MAE': mae,
        'RMSE': rmse,
        'Accuracy (%)': accuracy,
        'Coverage': coverage,
        'Pinball Losses': pinball_losses,  # 返回每个u的Pinball Loss
        'Sharpness': sharpness,
        'Interval Width': interval_width,
        'ES': es,
        'VS': vs,
        'CRPS': crps  # 返回 CRPS
    }

# 示例使用
# pred_mu = np.random.rand(100)
# targets = np.random.rand(100)
# pred_sigma = np.random.rand(100) * 0.1  # 假设 sigma 是方差的估计
#
# metrics = calculate_metrics(pred_mu, targets, pred_sigma)
# print(metrics)