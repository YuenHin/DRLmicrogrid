import torch
import torch.nn as nn

import torch
import torch.nn as nn


class GRUDeepAR(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length):
        super(GRUDeepAR, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.prediction_length = prediction_length
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.mu = nn.Linear(hidden_size, prediction_length)
        self.sigma = nn.Linear(hidden_size, prediction_length)

    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h_0)
        out = self.layer_norm(out)
        mu = self.mu(out[:, -1, :])
        sigma = torch.exp(self.sigma(out[:, -1, :])) + 1e-6  # 确保sigma为正值并避免log(0)情况
        return mu, sigma


import torch
import torch.nn as nn


class TransformerDeepAR(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length, nhead=1):
        super(TransformerDeepAR, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.prediction_length = prediction_length

        self.embedding = nn.Linear(input_size, hidden_size)
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_size, nhead=nhead)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.mu = nn.Linear(hidden_size, prediction_length)
        self.sigma = nn.Linear(hidden_size, prediction_length)

    def forward(self, x):
        x = self.embedding(x)
        x = x.permute(1, 0, 2)  # (batch_size, seq_len, hidden_size) -> (seq_len, batch_size, hidden_size)
        out = self.transformer(x)
        out = out.permute(1, 0, 2)  # (seq_len, batch_size, hidden_size) -> (batch_size, seq_len, hidden_size)
        out = self.layer_norm(out)
        mu = self.mu(out[:, -1, :])
        sigma = torch.exp(self.sigma(out[:, -1, :])) + 1e-6  # 确保sigma为正值并避免log(0)情况
        return mu, sigma

import torch
import torch.nn as nn

class LSTMDeepAR(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length):
        super(LSTMDeepAR, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.prediction_length = prediction_length
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.mu = nn.Linear(hidden_size, prediction_length)
        self.sigma = nn.Linear(hidden_size, prediction_length)

    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h_0, c_0))
        out = self.layer_norm(out)
        mu = self.mu(out[:, -1, :])
        sigma = torch.exp(self.sigma(out[:, -1, :])) + 1e-6  # 确保sigma为正值并避免log(0)情况
        return mu, sigma

class GRUDeterministic(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length):
        super(GRUDeterministic, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.prediction_length = prediction_length
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.output_layer = nn.Linear(hidden_size, prediction_length)  # 直接输出预测值

    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h_0)
        out = self.layer_norm(out)
        predictions = self.output_layer(out[:, -1, :])  # 仅返回预测值
        return predictions

class DeepAR(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length):
        super(DeepAR, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.prediction_length = prediction_length

        # 使用 LSTM 作为递归神经网络
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)

        # 全连接层，分别生成 mu 和 sigma
        self.mu = nn.Linear(hidden_size, prediction_length)
        self.sigma = nn.Linear(hidden_size, prediction_length)

        # 确保 sigma 输出为正值
        self.softplus = nn.Softplus()

    def forward(self, x):
        # 初始化 LSTM 的初始隐藏状态和记忆细胞
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        # LSTM 前向传播
        out, _ = self.lstm(x, (h_0, c_0))

        # 只使用最后一个时间步的输出
        out = out[:, -1, :]

        # 输出 mu 和 sigma，sigma 经过 softplus 以确保正值
        mu = self.mu(out)
        sigma = self.softplus(self.sigma(out)) + 1e-6  # 防止 sigma 为 0 或负值

        return mu, sigma

