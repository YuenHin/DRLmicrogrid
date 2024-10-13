import torch


def preprocess_experience_np(states, actions, rewards, next_states):
    """
    处理从 ReplayBuffer 采样得到的 NumPy 经验，并将其转换为 PyTorch 张量。
    拼接状态、动作和下一个状态为扩散模型输入。
    """
    # 转换 numpy 数组为 PyTorch 张量
    states_tensor = torch.tensor(states, dtype=torch.float32)
    actions_tensor = torch.tensor(actions, dtype=torch.float32)
    rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
    rewards_tensor = torch.unsqueeze(rewards_tensor, 1)
    next_states_tensor = torch.tensor(next_states, dtype=torch.float32)

    # 拼接状态、动作和下一个状态
    experience_tensor = torch.cat([states_tensor, actions_tensor, rewards_tensor, next_states_tensor], dim=1)  # 在维度上拼接
    return experience_tensor
