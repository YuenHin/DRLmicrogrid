import numpy as np
import torch
import torch.nn as nn

class VAEDeepAR(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, prediction_length, latent_dim = 128):
        super(VAEDeepAR, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.latent_dim = latent_dim
        self.prediction_length = prediction_length

        # 编码器：输入 -> 隐藏层
        self.encoder = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)

        # 编码器：隐藏层 -> 均值和方差（潜在空间的参数）
        self.fc_mu = nn.Linear(hidden_size, latent_dim)
        self.fc_logvar = nn.Linear(hidden_size, latent_dim)

        # 解码器：潜在变量 -> 隐藏层
        self.decoder = nn.GRU(latent_dim, hidden_size, num_layers, batch_first=True)

        # 输出层：隐藏层 -> 预测的mu和sigma
        self.mu = nn.Linear(hidden_size, prediction_length)
        self.sigma = nn.Linear(hidden_size, prediction_length)
        self.softplus = nn.Softplus()  # 确保 sigma 为正值

    def reparameterize(self, mu, logvar):
        """使用 reparameterization trick 生成潜在变量 z"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        # 初始化编码器的初始隐藏状态
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        # 编码器前向传播
        _, h = self.encoder(x, h_0)  # 只保留最后一层的输出 h

        # 计算潜在空间的均值和对数方差
        h = h[-1, :, :]  # 取最后一层的输出
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)

        # 重参数化技巧采样 z
        z = self.reparameterize(mu, logvar)

        # 初始化解码器的初始隐藏状态
        z = z.unsqueeze(1).repeat(1, self.prediction_length, 1)  # 扩展维度适应解码器输入
        h_0_decoder = torch.zeros(self.num_layers, z.size(0), self.hidden_size).to(x.device)

        # 解码器前向传播
        out, _ = self.decoder(z, h_0_decoder)

        # 生成 mu 和 sigma
        mu_out = self.mu(out[:, -1, :])
        sigma_out = self.softplus(self.sigma(out[:, -1, :])) + 1e-6  # 防止 sigma 为负值或 0

        return mu_out, sigma_out, mu, logvar  # 返回预测值以及潜在空间的 mu 和 logvar 用于损失计算


def create_loass_VAE():
    def loss_function_VAE(recon_mu, recon_sigma, target, mu, logvar):
        # 1. 重构损失使用负对数似然 (NLL)
        recon_loss = torch.mean(0.5 * torch.log(recon_sigma) + 0.5 * ((target - recon_mu) ** 2) / recon_sigma)

        # 2. KL 散度
        kl_divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

        # 总损失 = 重构损失 + KL 散度
        loss = recon_loss + kl_divergence

        return loss

    return loss_function_VAE