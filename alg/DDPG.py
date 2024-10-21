import numpy as np
import torch
import torch.nn.functional as F
from random import random

class PolicyNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim, action_bound):
        super(PolicyNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, action_dim)
        self.action_bound = action_bound  # action_bound是环境可以接受的动作最大值

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return torch.tanh(self.fc2(x)) * self.action_bound

class PolicyNet2(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim, action_bound):
        super(PolicyNet2, self).__init__()
        # 第一个隐藏层
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        # 第二个隐藏层
        self.fc2 = torch.nn.Linear(hidden_dim, 8)
        # 第三个隐藏层，将第一个和第二个隐藏层的输出拼接
        self.fc3 = torch.nn.Linear(hidden_dim + 8, hidden_dim)
        # 输出层
        self.output_layer = torch.nn.Linear(hidden_dim, 1)  # 输出一个一维值
        self.action_bound = action_bound  # 动作边界

        self.locked = False  # 条件锁，用于决定是否锁定层和停止随机化

    def randomize_fc2_params(self):
        """随机化第二个隐藏层的权重和偏置"""
        if not self.locked:  # 如果未锁定，则随机化
            with torch.no_grad():
                self.fc2.weight = torch.nn.Parameter(torch.randn_like(self.fc2.weight))  # 随机化权重
                self.fc2.bias = torch.nn.Parameter(torch.randn_like(self.fc2.bias))  # 随机化偏置

    def lock_fc1_and_fc3(self):
        """锁定第一层和第三层的参数，不允许更新"""
        for param in self.fc1.parameters():
            param.requires_grad = False  # 锁定第一层
        for param in self.fc3.parameters():
            param.requires_grad = False  # 锁定第三层
        for param in self.output_layer.parameters():
            param.requires_grad = False  # 锁定输出层

    def unlock_fc2(self):
        """停止对第二个隐藏层的随机化，但允许继续训练和更新"""
        self.locked = True  # 一旦锁定，停止随机化

    def forward(self, x):
        # 如果未锁定，继续随机化第二层的参数
        self.randomize_fc2_params()

        # 第一个隐藏层
        x1 = F.relu(self.fc1(x))  # 第一个隐藏层的输出

        # 第二个隐藏层，接收第一个隐藏层的输出
        x2 = F.relu(self.fc2(x1))  # 第二个隐藏层的输出

        # 第三个隐藏层，接收第一个隐藏层和第二个隐藏层的输出，并将它们拼接
        x3 = torch.cat([x1, x2], dim=1)  # 按特征维度拼接
        x3 = F.relu(self.fc3(x3))  # 第三个隐藏层的输出

        # 输出层，生成一维的输出
        output = self.output_layer(x3)
        return torch.tanh(output) * self.action_bound

class QValueNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super(QValueNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.fc_out = torch.nn.Linear(hidden_dim, 1)

    def forward(self, x, a):
        cat = torch.cat([x, a], dim=1) # 拼接状态和动作
        x = F.relu(self.fc1(cat))
        x = F.relu(self.fc2(x))
        return self.fc_out(x)

class DDPG:
    ''' DDPG算法 '''
    def __init__(self, state_dim, hidden_dim, action_dim, action_bound, sigma, actor_lr, critic_lr, tau, gamma, device):
        self.actor = PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(device)
        self.critic = QValueNet(state_dim, hidden_dim, action_dim).to(device)
        self.target_actor = PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(device)
        self.target_critic = QValueNet(state_dim, hidden_dim, action_dim).to(device)

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

        self.start_sigma = self.sigma * 50  # 高斯噪声的标准差, 增加一个初始探索领域

    def take_action(self, state, cur_episode, time = 1000, i_episode = 1000):
        # state = torch.tensor([state], dtype=torch.float).to(self.device)
        # action = self.actor(state).item()
        # if time < 90:
        #     a = (random() * 2 - 1)
        #     b = action + self.actor(state).item()
        #     action = np.minimum(np.maximum(b, -self.action_bound), self.action_bound)
        # else:
        #     # 给动作添加噪声，增加探索
        #     if i_episode >= 5:
        #         self.start_sigma = np.maximum(self.start_sigma * 0.95, self.sigma)
        #     action = np.minimum(np.maximum(action + (self.sigma * (random() * 2 - 1)), -self.action_bound), self.action_bound)
        # if i_episode < 5:
        #     action = random() * 2 - 1
        # return action
        # test_array = np.zeros_like(state)
        # test_tensor = test_array + np.random.random()
        # test_tensor = torch.tensor([test_tensor], dtype=torch.float).to(self.device)
        # action_test = self.actor(test_tensor).item()

        state = torch.tensor([state], dtype=torch.float).to(self.device)
        action = self.actor(state).item()
        #给动作添加噪声，增加探索
        # action = action + self.start_sigma * np.random.randn(self.action_dim) #这里后续需要修改sigma
        action = action + self.sigma * np.random.randn(self.action_dim)
        # if cur_episode <= 1000:
        #     action = action + 0.8 * np.random.randn(self.action_dim)
        # elif cur_episode >1000 and cur_episode <=2000:
        #     action = action + 0.6 * np.random.randn(self.action_dim)
        # elif cur_episode >2000 and cur_episode <=3000:
        #     action = action + 0.4 * np.random.randn(self.action_dim)
        # elif cur_episode >3000 and cur_episode <=4000:
        #     action = action + 0.2 * np.random.randn(self.action_dim)
        # elif cur_episode >4000 and cur_episode <=5000:
        #     action = action + 0.1 * np.random.randn(self.action_dim)
        # else:
        #     action = action + 0.01 * np.random.randn(self.action_dim)
        if action > 1:
            action = action - 2
        if action < -1:
            action = action + 2
        return action

    def take_action_RO(self, state):

        state = torch.tensor([state], dtype=torch.float).to(self.device)
        action = self.actor(state)
        action = action.detach().squeeze().numpy()
        # action = self.actor(state).item()
        #给动作添加噪声，增加探索
        action = action + self.sigma * np.random.randn(self.action_dim)

        if action[0] > 1:
            action[0] = action[0] -1
        if action[0] < 0:
            action[0] = action[0] + 1
        if action[1] > 1:
            action[1] = action[1] - 1
        if action[1] < 0:
            action[1] = action[1] + 1
        for i in range(2,5):
            if action[i] > 1:
                action[i] = action[i] - 2
            if action[i] < -1:
                action[i] = action[i] + 2

        return action


    def soft_update(self, net, target_net):
        for param_target, param in zip(target_net.parameters(), net.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - self.tau) + param.data * self.tau)

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions'], dtype=torch.float).view(-1, 1).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'], dtype=torch.float).view(-1, 1).to(self.device)

        next_q_values = self.target_critic(next_states, self.target_actor(next_states))
        q_targets = rewards + self.gamma * next_q_values * (1 - dones)
        critic_loss = torch.mean(F.mse_loss(self.critic(states, actions), q_targets))
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        actor_loss = -torch.mean(self.critic(states, self.actor(states)))
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        self.soft_update(self.actor, self.target_actor)  # 软更新策略网络
        self.soft_update(self.critic, self.target_critic)  # 软更新价值网络

    def update_ro(self, transition_dict):
        states = torch.tensor(transition_dict['states'], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions'], dtype=torch.float).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'], dtype=torch.float).view(-1, 1).to(self.device)

        next_q_values = self.target_critic(next_states, self.target_actor(next_states))
        q_targets = rewards + self.gamma * next_q_values * (1 - dones)
        critic_loss = torch.mean(F.mse_loss(self.critic(states, actions), q_targets))
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        actor_loss = -torch.mean(self.critic(states, self.actor(states)))
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        self.soft_update(self.actor, self.target_actor)  # 软更新策略网络
        self.soft_update(self.critic, self.target_critic)  # 软更新价值网络