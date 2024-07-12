import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import matplotlib.pyplot as plt

from algorithm import GRUDeepAR, TransformerDeepAR, LSTMDeepAR

# 解决 OMP 问题
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# 设置单线程
torch.set_num_threads(1)

# 自定义数据集
class TimeSeriesDataset(Dataset):
    def __init__(self, data, target, context_length, prediction_length):
        self.data = data
        self.target = target
        self.context_length = context_length
        self.prediction_length = prediction_length

    def __len__(self):
        return len(self.data) - self.context_length - self.prediction_length + 1

    def __getitem__(self, idx):
        context = self.data[idx:idx + self.context_length]
        target = self.target[idx + self.context_length:idx + self.context_length + self.prediction_length]
        return torch.tensor(context, dtype=torch.float32), torch.tensor(target, dtype=torch.float32)


# DeepAR 模型
# class DeepAR(nn.Module):
#     def __init__(self, input_size, hidden_size, num_layers, prediction_length):
#         super(DeepAR, self).__init__()
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
#         self.prediction_length = prediction_length
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
#         self.layer_norm = nn.LayerNorm(hidden_size)
#         self.mu = nn.Linear(hidden_size, prediction_length)
#         self.sigma = nn.Linear(hidden_size, prediction_length)
#
#     def forward(self, x):
#         h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
#         c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
#         out, _ = self.lstm(x, (h_0, c_0))
#         out = self.layer_norm(out)
#         mu = self.mu(out[:, -1, :])
#         sigma = torch.exp(self.sigma(out[:, -1, :])) + 1e-6  # 确保sigma为正值并避免log(0)情况
#         return mu, sigma


# 生成示例数据
def generate_synthetic_data(seq_len=1000):
    np.random.seed(42)
    data = np.sin(np.linspace(0, 100, seq_len))
    data = (data - np.mean(data)) / np.std(data)
    target = np.roll(data, -1)
    return data, target

import sys

def print_progress(message):
    sys.stdout.write('\r' + message)
    sys.stdout.flush()

def train_deepar_mse(model, dataloader, lr=0.00001, patience=100, delta=0.0001, model_path='deepar_mse.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_values = []
    best_loss = float('inf')
    epochs_no_improve = 0

    # 记录每个epoch的损失
    epoch_losses = []

    epoch_counter = 0

    while True:
        model.train()
        epoch_loss = 0
        for context, target in dataloader:
            context = context.to(device)
            target = target.to(device)

            mu, _ = model(context)
            mu = mu.view(-1, model.prediction_length)
            target = target.view(-1, model.prediction_length)

            # 使用 nn.MSELoss
            loss = criterion(mu, target)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        epoch_loss /= len(dataloader)
        loss_values.append(epoch_loss)
        epoch_losses.append(epoch_loss)
        epoch_counter += 1

        # Early stopping check
        if epoch_loss < best_loss - delta:
            best_loss = epoch_loss
            epochs_no_improve = 0
            # Save the best model
            torch.save(model.state_dict(), model_path)
        else:
            epochs_no_improve += 1

        # 打印损失并刷新终端显示
        print_progress(f"Epoch {len(loss_values)}, Loss: {epoch_loss:.4f}")

        # 仅在每 patience 次打印一次损失函数差值的均值
        if epoch_counter % patience == 0:
            if len(epoch_losses) >= patience:
                recent_losses = np.diff(epoch_losses[-patience:])
                mean_recent_loss_change = recent_losses.mean()
                print_progress(f"Epoch {len(loss_values)}, Loss: {epoch_loss:.4f}, Mean Change in Last {patience} Epochs: {mean_recent_loss_change:.4f}")

        if epochs_no_improve >= patience:
            print(f"\nEarly stopping after {len(loss_values)} epochs")
            break

    plt.plot(loss_values)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss ' + "(" + model_path + ")")
    plt.show()


# 训练函数 - 使用 nn.GaussianNLLLoss
def train_deepar_nll(model, dataloader, lr=0.00001, patience=100, delta=0.0001, model_path='deepar_nll.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = nn.GaussianNLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_values = []
    best_loss = float('inf')
    epochs_no_improve = 0

    # 记录每个epoch的损失
    epoch_losses = []

    epoch_counter = 0

    while True:
        model.train()
        epoch_loss = 0
        #context(32, context_length, 14)
        #target(32, prediction_length)
        # index = 0
        for context, target in dataloader:
            context = context.to(device)
            target = target.to(device)

            # mu(32, 24)
            # sigma(32, 24)
            mu, sigma = model.forward(context)
            mu = mu.view(-1, model.prediction_length)
            sigma = sigma.view(-1, model.prediction_length)
            target = target.view(-1, model.prediction_length)

            # 使用 nn.GaussianNLLLoss
            loss = criterion(mu, target, sigma)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

            # index += mu.size(0)
        # print(index)
        epoch_loss /= len(dataloader)
        loss_values.append(epoch_loss)
        epoch_losses.append(epoch_loss)
        epoch_counter += 1

        # Early stopping check
        if epoch_loss < best_loss - delta:
            best_loss = epoch_loss
            epochs_no_improve = 0
            # Save the best model
            torch.save(model.state_dict(), model_path)
        else:
            epochs_no_improve += 1

        # 仅在每 patience 次打印一次损失函数差值的均值
        if (epoch_counter) % 100 == 0:
            if len(epoch_losses) >= patience:
                recent_losses = np.diff(epoch_losses[-patience:])
                mean_recent_loss_change = recent_losses.mean()
                print(f"Epoch {len(loss_values)}, Loss: {epoch_loss:.4f}, Mean Change in Last {patience} Epochs: {mean_recent_loss_change:.8f}")

                # if np.abs(mean_recent_loss_change) <= delta:
                #     print(f"Early stopping after {len(loss_values)} epochs")
                #     #torch.save(model.state_dict(), model_path)
                #     break

        if epochs_no_improve >= patience:
            print(f"Early stopping after {len(loss_values)} epochs")
            break


    plt.plot(loss_values)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss ' + "(" + model_path + ")")
    plt.show()


import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt


# 测试函数
def test_deepar(model, dataloader, context_length, prediction_length, model_path, num_samples=100):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()

    all_mu = []
    all_sigma = []
    all_target = []
    all_samples = []

    with torch.no_grad():
        #Context shape: torch.Size([32, 96, 14]), Target shape: torch.Size([32, 24])
        for context, target in dataloader:
            context = context.to(device)
            target = target.to(device)

            mu, sigma = model(context)
            mu = mu.view(-1, prediction_length)
            sigma = sigma.view(-1, prediction_length)
            target = target.view(-1, prediction_length)

            # 蒙特卡洛采样
            samples = torch.randn(num_samples, *mu.shape).to(device) * sigma.unsqueeze(0) + mu.unsqueeze(0)
            samples_mean = samples.mean(dim=0)

            mu = samples_mean.cpu().numpy()
            sigma = sigma.cpu().numpy()
            target = target.cpu().numpy()
            samples = samples.cpu().numpy()

            all_mu.append(mu)
            all_sigma.append(sigma)
            all_target.append(target)
            all_samples.append(samples)

    all_mu = np.concatenate(all_mu, axis=0)
    all_sigma = np.concatenate(all_sigma, axis=0)
    all_target = np.concatenate(all_target, axis=0)
    all_samples = np.concatenate(all_samples, axis=1)

    # 可视化整个序列的预测结果
    plt.figure(figsize=(12, 6))
    time_steps = np.arange(len(all_target.flatten()))
    plt.plot(time_steps, all_target.flatten(), label='Measured Wind Power', color='blue')
    plt.plot(time_steps, all_mu.flatten(), label='Deterministic Forecasts', color='orange')
    for i in range(all_samples.shape[0]):
        if i == 0:
            plt.plot(time_steps, all_samples[i].flatten(), color='gray', alpha=0.1, label='Wind Power Scenario')
        else:
            plt.plot(time_steps, all_samples[i].flatten(), color='gray', alpha=0.1)

    # 设置X轴刻度和标签
    ticks = np.arange(0, len(all_target.flatten()), 24)  # 每24个点设置一个刻度（即每6小时一个点）
    labels = [f'Day {i // 4 + 1}\n{(i % 4) * 6}h' for i in range(len(ticks))]  # 标签显示为 Day X\nYh
    plt.xticks(ticks, labels, rotation=45)

    plt.title(model_path)
    plt.legend(loc='upper left')
    plt.show()

    return all_mu, all_sigma, all_target

# 示例调用
# Define model, dataloader and other parameters as required
# pred_mu, pred_sigma, target = test_deepar(model, dataloader, model_path=model_path)


# 计算指标
def calculate_metrics(predictions, targets, sigma, alpha=0.05):
    # 检查并调整形状
    if predictions.shape != targets.shape:
        targets = targets.reshape(predictions.shape)

    mae = np.abs(predictions - targets).mean()
    rmse = np.sqrt(((predictions - targets) ** 2).mean())

    z = np.percentile(sigma, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    coverage = np.mean((targets >= predictions + z[0]) & (targets <= predictions + z[1]))

    pinball_loss = np.mean(np.maximum(alpha * (targets - predictions), (alpha - 1) * (targets - predictions)))
    sharpness = sigma.mean()
    interval_width = z[1] - z[0]
    es = (predictions - targets).mean() / np.sqrt(sigma.var())
    vs = np.var(targets - predictions) / sigma.var()

    return {
        'MAE': mae,
        'RMSE': rmse,
        'Coverage': coverage,
        'Pinball Loss': pinball_loss,
        'Sharpness': sharpness,
        'Interval Width': interval_width,
        'ES': es,
        'VS': vs
    }

#
# # 生成示例数据
# data, target = generate_synthetic_data()
#
# # 数据集和数据加载器
# context_length = 50
# prediction_length = 10
# batch_size = 32
#
# train_dataset = TimeSeriesDataset(data, target, context_length, prediction_length)
# train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
# test_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)  # 测试时不打乱数据
#
# # 定义和训练模型
# input_size = 1
# hidden_size = 50
# num_layers = 2
# model_grl = GRUDeepAR(input_size, hidden_size, num_layers, prediction_length)
# model_lstm = LSTMDeepAR(input_size, hidden_size, num_layers, prediction_length)
# model_transformer = TransformerDeepAR(input_size, hidden_size, num_layers, prediction_length)
#
# # # 训练模型 - 使用蒙特卡洛采样的均方误差损失
# # train_deepar_mse(model_mse, train_loader)
#
# # 训练模型 - 使用 nn.GaussianNLLLoss
# # train_deepar_nll(model_grl, train_loader, model_path= "deepar_grl.pth")
# # train_deepar_nll(model_lstm, train_loader, model_path= "deepar_lstm.pth")
# # train_deepar_nll(model_transformer, train_loader, model_path= "deepar_transformer.pth")
#
#
# # 测试模型
# # pred_mu_mse, pred_sigma_mse, target_mse = test_deepar(model_mse, train_loader, 'deepar_mse.pth')
# pred_mu_gru, pred_sigma_gru, target_gru = test_deepar(model_grl, test_loader, 'deepar_grl.pth')
# pred_mu_lstm, pred_sigma_lstm, target_lstm = test_deepar(model_lstm, test_loader, 'deepar_lstm.pth')
# pred_mu_transformer, pred_sigma_transformer, target_transformer = test_deepar(model_transformer, test_loader, 'deepar_transformer.pth')
#
# # 计算并打印性能指标
# # metrics_mse = calculate_metrics(pred_mu_mse, target_mse, pred_sigma_mse)
# metrics_gru = calculate_metrics(pred_mu_gru, target_gru, pred_sigma_gru)
# metrics_lstm = calculate_metrics(pred_mu_lstm, target_lstm, pred_sigma_lstm)
# metrics_transformer = calculate_metrics(pred_mu_transformer, target_transformer, pred_sigma_transformer)
#
# # print("Metrics for MSE Loss:")
# # for key, value in metrics_mse.items():
# #     print(f"{key}: {value:.4f}")
#
# print("\nMetrics for GRU Loss:")
# for key, value in metrics_gru.items():
#     print(f"{key}: {value:.4f}")
#
# print("\nMetrics for LSTM Loss:")
# for key, value in metrics_lstm.items():
#     print(f"{key}: {value:.4f}")
#
# print("\nMetrics for Transformer Loss:")
# for key, value in metrics_transformer.items():
#     print(f"{key}: {value:.4f}")


# 绘制图形
# def plot_predictions_with_baseline(pred_mu_gru, pred_mu_lstm, pred_mu_transformer, target = test_loader):
#     # 计算相对差异
#     diff_gru = pred_mu_gru - target
#     diff_lstm = pred_mu_lstm - target
#     diff_transformer = pred_mu_transformer - target
#
#     # 计算平均差异
#     mean_diff_gru = diff_gru.mean(axis=0)
#     mean_diff_lstm = diff_lstm.mean(axis=0)
#     mean_diff_transformer = diff_transformer.mean(axis=0)
#     mean_target = target.mean(axis=0)
#
#     # 绘制真实值和相对差异
#     plt.figure(figsize=(15, 8))
#     plt.plot(mean_target, label='True', color='black')
#     plt.plot(mean_diff_gru, label='GRU', linestyle='dashed')
#     plt.plot(mean_diff_lstm, label='LSTM', linestyle='dotted')
#     plt.plot(mean_diff_transformer, label='Transformer')
#     plt.legend()
#     plt.xlabel('Time Step')
#     plt.ylabel('Value / Relative Prediction Difference')
#     plt.title('Prediction Differences')
#     plt.show()

# # 调用绘图函数
# plot_predictions_with_baseline(target_gru, pred_mu_gru, pred_mu_lstm, pred_mu_transformer)














