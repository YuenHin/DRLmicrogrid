import torch
import torch.nn as nn


# 正向扩散过程，正向扩散过程负责在输入数据上逐步添加噪声：
def forward_diffusion_experience(experience, t, beta_t):
    """
    对输入的经验数据进行扩散过程中的噪声添加。
    """
    noise = torch.randn_like(experience)
    sqrt_alpha_t = torch.sqrt(1.0 - beta_t).to(experience.device).unsqueeze(1)
    sqrt_one_minus_alpha_t = torch.sqrt(beta_t).to(experience.device).unsqueeze(1)
    return sqrt_alpha_t * experience + sqrt_one_minus_alpha_t * noise


# Beta 调度函数，定义扩散过程中的 Beta 值，用于控制每一步中添加噪声的量
def linear_beta_schedule(timesteps):
    """
    生成线性 beta 调度，用于扩散过程。
    """
    beta_start = 0.0001
    beta_end = 0.02
    return torch.linspace(beta_start, beta_end, timesteps)


# 扩散模型中的去噪网络 (UNet)，一个简单的 U-Net 实现，用于去噪扩散模型中的输入
class ExperienceUNet(nn.Module):
    def __init__(self, c_in, c_out):
        super(ExperienceUNet, self).__init__()
        self.encoder = nn.Sequential(
            # nn.Conv2d(c_in, 64, kernel_size=3, padding=1),
            # nn.Linear(c_in, 128),  # 全连接层
            nn.Conv1d(1, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            # nn.Conv2d(64, 128, kernel_size=3, padding=1),
            # nn.Linear(128, 256),  # 全连接层
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            # nn.MaxPool2d(2)
            nn.MaxPool1d(2)
        )
        self.middle = nn.Sequential(
            # nn.Conv2d(128, 128, kernel_size=3, padding=1),
            # nn.Linear(256, 256),
            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            # nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            # nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),
            # nn.Linear(256, 128),  # 全连接层
            nn.ConvTranspose1d(128, 64, kernel_size=2, stride=2),
            nn.ReLU(),
            # nn.Conv2d(64, c_out, kernel_size=3, padding=1),
            # nn.Linear(128, c_out)
            nn.Conv1d(64, 1, kernel_size=3, padding=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x1 = self.encoder(x)
        x2 = self.middle(x1)
        x3 = self.decoder(x2)
        return x3


def sample_new_experience(unet, shape, timesteps):
    """
    从扩散模型中采样生成新的经验。
    """
    x = torch.randn(shape)
    beta_schedule = linear_beta_schedule(timesteps)

    for t in reversed(range(timesteps)):
        noise_pred = unet(x)
        x = x - beta_schedule[t] * noise_pred  # 逐步去噪

    return x  # 返回生成的新经验
