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
