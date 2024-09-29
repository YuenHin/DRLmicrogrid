import time

import gym
from alg.DDPG import DDPG
from alg.alTools.rl_starting import *
import matplotlib.pyplot as plt
from env.microgrid_env import microgrid_env
import torch
from tools.maybeExcel import writeDatatoExcel
from tools.Logic import save_data, draw

# from CPP_DG_D_RE_S import MMGs
from test_CPP_D import CPP_D_MMGs
from test_CPP_D_RE import CPP_D_PV_MMGs
from test_CPP_D_PV_S import CPP_D_PV_S_MMGs

start_time = time.time()
actor_lr = 3e-4
critic_lr = 3e-3
num_episodes = 1000
hidden_dim = 128
gamma = 0.98
tau = 0.005  # 软更新参数
buffer_size = 10000
minimal_size = 64
batch_size = 32
# sigma = 0.01  # 高斯噪声标准差
sigma = 0.8
#device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
device = torch.device("cpu")
#env = microgrid_env(MMGs, 24)
#env = microgrid_env(CPP_D_MMGs, 24)
#env = microgrid_env(CPP_D_PV_MMGs, 24)
env = microgrid_env(CPP_D_PV_S_MMGs, 24)
# random.seed(0)
# np.random.seed(0)
# env.seed(0)
# torch.manual_seed(0)
replay_buffer = ReplayBuffer(buffer_size)
return_buffer = ReturnBuffer()
state_dim = env.observation_space.shape[0]
action_dim = env.action_space.shape[0]
action_bound = 1  # 动作最大值
agent = DDPG(state_dim, hidden_dim, action_dim, action_bound, sigma, actor_lr, critic_lr, tau, gamma, device)


for parameters in agent.actor.parameters():
    print(parameters)

print("################################################")
for name, parameters in agent.actor.named_parameters():
    print(name, ':', parameters.size())
