import math
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

#time的位置编码
class SinusoidalPosEmb(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        device = x.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device = device) * -emb)
        emb = x[:, None] * emb[None, :]
        emb = torch.cat((emb.sin(), emb.cos()), dim = -1)
        return emb

class MLP(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim, device, t_dim = 16):
        super().__init__()

        self.t_dim = t_dim
        self.action_dim = action_dim
        self.d_model = hidden_dim
        self.device = device

        #时间编码的神经网络
        self.time_mlp = nn.Sequential(
            SinusoidalPosEmb(t_dim),
            nn.Linear(t_dim, t_dim*2),
            nn.Mish(),
            nn.Linear(t_dim*2, t_dim)
        ).to(self.device)

        input_dim = state_dim + action_dim + t_dim
        self.mid_layer = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Mish(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Mish(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Mish(),
        ).to(self.device)
        self.final_layer = nn.Linear(hidden_dim, action_dim).to(self.device)

        self.init_weights()

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x, time, state):
        t_emb = self.time_mlp.forward(time).to(self.device)
        x = torch.cat([x, state, t_emb], dim = 1).to(self.device)
        x = self.mid_layer(x)
        x = self.final_layer(x)
        return x

