import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision import datasets
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt


# 定义正向过程（Forward Diffusion Process）
def forward_diffusion_sample(x_0, t, beta_t):
    """
    Args:
        x_0: 原始图像张量 (batch_size, num_channels, height, width)
        t: 当前的时间步 (int)
        beta_t: 不同时间步的噪声方差（调度表）

    Returns:
        添加噪声后的图像样本
    """
    # 生成与 x_0 形状相同的随机噪声
    noise = torch.randn_like(x_0)
    # 计算方差的平方根
    sqrt_alpha_t = torch.sqrt(1.0 - beta_t).to(x_0.device)
    sqrt_one_minus_alpha_t = torch.sqrt(beta_t).to(x_0.device)
    return sqrt_alpha_t * x_0 + sqrt_one_minus_alpha_t * noise


# 反向过程网络定义（Unet 结构）
# 在扩散模型中，UNet 网络常被用于学习从噪声中恢复数据。这里我们定义一个简单的 UNet 网络。
class UNet(nn.Module):
    def __init__(self, c_in=1, c_out=1):
        super(UNet, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(c_in, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.middle = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, c_out, kernel_size=3, padding=1),
            nn.Sigmoid()  # 输出介于 0-1 之间
        )

    def forward(self, x):
        x1 = self.encoder(x)
        x2 = self.middle(x1)
        x3 = self.decoder(x2)
        return x3


# 定义噪声调度表
# 噪声调度表决定了每个时间步的噪声大小。我们可以使用线性调度来简单地定义它。
def linear_beta_schedule(timesteps, start=1e-4, end=0.02):
    """
    定义时间步上的线性beta调度
    """
    return torch.linspace(start, end, timesteps)


# 训练过程定义
# 训练时，我们从经验池中取出样本，添加噪声并通过去噪网络恢复原始样本。
def train_diffusion_model(unet, dataloader, timesteps, epochs, lr=1e-3):
    optimizer = optim.Adam(unet.parameters(), lr=lr)
    mse_loss = nn.MSELoss()  # 使用均方误差损失
    beta_schedule = linear_beta_schedule(timesteps)

    for epoch in range(epochs):
        for step, (x, _) in enumerate(dataloader):
            optimizer.zero_grad()
            t = torch.randint(0, timesteps, (x.size(0),)).long()  # 随机选择时间步
            x_noisy = forward_diffusion_sample(x, t, beta_schedule[t])

            noise_pred = unet(x_noisy)
            loss = mse_loss(noise_pred, x)  # 学习预测去噪
            loss.backward()
            optimizer.step()

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {loss.item()}')


# 采样生成
# 经过训练后，可以通过逐步反向去噪生成新样本
def sample(unet, shape, timesteps):
    x = torch.randn(shape)  # 从纯噪声开始
    beta_schedule = linear_beta_schedule(timesteps)

    for t in reversed(range(timesteps)):
        noise_pred = unet(x)
        x = x - beta_schedule[t] * noise_pred  # 去噪步

    return x



