import torch.optim as optim
import torch.nn as nn
from DDPM_exp import *
from ReplayBuffer import *
from preprocess_exp import *


# 初始化参数
timesteps = 1000
beta_schedule = linear_beta_schedule(timesteps)
epochs = 10
learning_rate = 1e-3
training_steps = 1000  # 每个epoch中的训练步数

# 初始化 ReplayBuffer
replay_buffer = ReplayBuffer(10000)
# batch_size = replay_buffer.size()
batch_size = 1000

# 获取状态和动作维度
states, actions, rewards, next_states, dones = replay_buffer.sample(batch_size)
state_dim = states.shape[1]  # 状态的特征数量
action_dim = actions.shape[1]  # 动作的特征数量（假设动作是一个向量）

# 初始化 UNet 模型
unet = ExperienceUNet(c_in=state_dim + action_dim + state_dim, c_out=state_dim + action_dim + state_dim)
optimizer = optim.Adam(unet.parameters(), lr=learning_rate)
mse_loss = nn.MSELoss()

# 训练循环
for epoch in range(epochs):
    for step in range(training_steps):
        # 从经验池中随机采样
        states, actions, rewards, next_states, dones = replay_buffer.sample(batch_size)

        # 预处理经验数据
        experience_tensor = preprocess_experience_np(states, actions, rewards, next_states)

        # 随机选择时间步
        t = torch.randint(0, timesteps, (experience_tensor.size(0),)).long()

        # 扩散过程中的噪声添加
        noisy_experience = forward_diffusion_experience(experience_tensor, t, beta_schedule[t])

        # 通过 U-Net 去噪
        predicted_noise = unet(noisy_experience)

        # 计算损失
        loss = mse_loss(predicted_noise, experience_tensor)

        # 反向传播并更新模型参数
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item()}")
