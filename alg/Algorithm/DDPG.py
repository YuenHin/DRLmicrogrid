from random import random

import torch
import torch.nn.functional as F
import copy
import numpy as np

# from algorithm.Tool.network import DDPG_PolicyNet, QValueNet
from DRLmicrogrid

class DDPG:
    ''' DDPG算法 '''
    def __init__(self, state_dim, hidden_dim, action_dim, action_bound, sigma, actor_lr, critic_lr, tau, gamma, device, loading = False, actor_network = None, critic_network = None):
        self.actor = DDPG_PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(device)
        self.critic = QValueNet(state_dim, hidden_dim, action_dim).to(device)
        self.target_actor = DDPG_PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(device)
        self.target_critic = QValueNet(state_dim, hidden_dim, action_dim).to(device)

        if loading :
            self.actor = torch.load(actor_network)
            self.critic = torch.load(critic_network)

        self.action_bound = action_bound
        # 初始化目标价值网络并设置和价值网络相同的参数
        self.target_critic.load_state_dict(self.critic.state_dict())
        # 初始化目标策略网络并设置和策略相同的参数
        self.target_actor.load_state_dict(self.actor.state_dict())

        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=critic_lr)
        self.gamma = gamma
        self.sigma = sigma  # 高斯噪声的标准差,均值直接设为0
        self.tau = tau  # 目标网络软更新参数
        self.action_dim = action_dim
        self.device = device

        self.start_sigma = self.sigma * 95# 高斯噪声的标准差, 增加一个初始探索领域

    def take_action(self, state, time = 1000, i_episode = 1000):
        state = torch.tensor(np.array([state]), dtype=torch.float).to(self.device)
        action = self.actor(state).item()
        if time < 90:
            a = (random() * 2 - 1)
            b = action + self.start_sigma * a
            action = np.minimum(np.maximum(b, -self.action_bound),
                                self.action_bound)
        else:
            # 给动作添加噪声，增加探索
            if i_episode >= 5:
                self.start_sigma = np.maximum(self.start_sigma * 0.99, self.sigma)
            a = (random() * 2 - 1)
            b = action + self.start_sigma * a
            action = np.minimum(np.maximum(b, -self.action_bound),
                                self.action_bound)
        # if i_episode < 5:
        #     action = random() * 2 - 1

        return action

    def soft_update(self, net, target_net):
        #更新神经网络的W和B，按照self.tau的百分比进行修改
        for param_target, param in zip(target_net.parameters(), net.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - self.tau) + param.data * self.tau)

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions'], dtype=torch.float).view(-1, 1).to(self.device)
        rewards = torch.tensor(np.array([transition_dict['rewards']]), dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'], dtype=torch.float).view(-1, 1).to(self.device)

        #探索后的Qt+1的价值函数----target_critic + target_actor
        next_q_values = self.target_critic(next_states, self.target_actor(next_states))

        #Qt的价值函数----reward + gamma * Qt+1
        q_targets = rewards + self.gamma * next_q_values * (1 - dones)

        #critic的loss----critic() / q_target
        critic_loss = torch.mean(F.mse_loss(self.critic(states, actions), q_targets))

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        #action的loss----梯度下降后的critic() / actor()
        actor_loss = -torch.mean(self.critic(states, self.actor(states)))

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        self.soft_update(self.actor, self.target_actor)  # 软更新策略网络
        self.soft_update(self.critic, self.target_critic)  # 软更新价值网络

