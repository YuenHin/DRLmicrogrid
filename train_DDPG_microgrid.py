import time

import gym
from algorithm.DDPG import DDPG
from algorithm.alTools.rl_starting import *
import matplotlib.pyplot as plt
from env.microgrid_env import microgrid_env
import torch
from tools.maybeExcel import writeDatatoExcel
from tools.Logic import save_data, draw

from CPP_DG_D_RE_S import MMGs
from test_CPP_D import CPP_D_MMGs
from test_CPP_D_RE import CPP_D_PV_MMGs
from test_CPP_D_PV_S import CPP_D_PV_S_MMGs

class test_DDPG():
    def func(self, train_time, sigma):
        start_time = time.time()
        actor_lr = 3e-4
        critic_lr = 3e-3
        num_episodes = 1000
        hidden_dim = 128
        gamma = 0.98
        tau = 0.005  # 软更新参数
        buffer_size = 10000
        minimal_size = 32
        batch_size = 32
        # sigma = 0.01  # 高斯噪声标准差
        sigma = sigma[train_time]
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

        if train_time != 0:
            agent.actor.load_state_dict(torch.load('.\Data\Result\DDPG_actor_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.target_actor.load_state_dict(torch.load('.\Data\Result\DDPG_actor_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.critic.load_state_dict(torch.load('.\Data\Result\DDPG_critic_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.target_critic.load_state_dict(torch.load('.\Data\Result\DDPG_critic_network'+ '_' + str(train_time-1) + '.pkl'))


        train_off_policy_agent_MG(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer)

        episodes_list = list(range(len(return_buffer.operation_cost)))
        return_list = np.array([return_buffer.operation_cost, return_buffer.carbon_emission, return_buffer.carbon_emission_cost, return_buffer.profit, return_buffer.total_cost])
        title = np.array(["operation_cost", "carbon_emission", "carbon_emission_cost", "profit", "total_cost"])
        # writeDatatoExcel(".\Data\Result\DDPG_actor.xlsx", 0, 0, np.array([episodes_list]))

        print("训练用时：", time.time() - start_time)

        # for i in range(5):
        #     plt.plot(episodes_list, return_list[i])
        #     plt.xlabel('Episodes')
        #     plt.ylabel('Returns')
        #     plt.title('DDPG on {}'.format(title[i]))
        #     plt.show()
        #
        #     a = np.squeeze(return_list[i])
        #     mv_return = moving_average(a, 9)
        #     # mv_return = moving_average(np.array([return_list[i]]), 9)
        #     plt.plot(episodes_list, mv_return)
        #     plt.xlabel('Episodes')
        #     plt.ylabel('Returns')
        #     plt.title('DDPG on {}'.format(title[i]))
        #     plt.show()

        plt.plot(episodes_list, return_list[0])
        plt.xlabel('Episodes')
        plt.ylabel('Returns')
        plt.title('DDPG on {}'.format(title[0]))
        # plt.show()
        plt.savefig('.\Data\Result\DDPG on {}'.format(title[0])+ str(train_time) +'0.png')

        a = np.squeeze(return_list[i])
        mv_return = moving_average(a, 9)
        # mv_return = moving_average(np.array([return_list[i]]), 9)
        plt.plot(episodes_list, mv_return)
        plt.xlabel('Episodes')
        plt.ylabel('Returns')
        plt.title('DDPG on {}'.format(title[0]))
        # plt.show()
        plt.savefig('.\Data\Result\DDPG on {}'.format(title[0])+ str(train_time) +'1.png')

        plt.clf()

            # writeDatatoExcel(".\Data\Result\DDPG_actor.xlsx", 1 + i * 2, 0, return_list)
            # writeDatatoExcel(".\Data\Result\DDPG_actor.xlsx", 2 + i * 2 , 0, mv_return)


        torch.save(agent.actor.state_dict(), '.\Data\Result\DDPG_actor_network'+ '_' + str(train_time) + '.pkl')
        torch.save(agent.critic.state_dict(), '.\Data\Result\DDPG_critic_network'+ '_' + str(train_time) + '.pkl')
        save_data(env.save_name+str(train_time), env.x, 2)
        #draw(env.env.MG)


# a =test_DDPG()
# a.func()

sigma = [0.8, 0.6, 0.4, 0.2, 0.1]
start_time = time.time()
for i in range(5):
    a = test_DDPG()
    a.func(i, sigma)
print("训练用时：", time.time() - start_time)
