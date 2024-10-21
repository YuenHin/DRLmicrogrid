import time

import gym
import numpy as np

from alg.DDPG import DDPG
from alg.alTools.rl_starting import *
import matplotlib.pyplot as plt
from env.microgrid_env import microgrid_env
from env.microgrid_RO_env import microgrid_RO_env
import torch
from tools.maybeExcel import writeDatatoExcel
from tools.Logic import save_data, draw

# from CPP_DG_D_RE_S import MMGs
from test_CPP_D import CPP_D_MMGs
from test_CPP_D_RE import CPP_D_PV_MMGs
from test_CPP_D_PV_S import CPP_D_PV_S_MMGs
from zzy_RO_10_13 import UIES
class test_DDPG():
    def func(self, train_time, sigma):
        start_time = time.time()
        actor_lr = 3e-4
        critic_lr = 3e-3
        num_episodes = 50
        hidden_dim = 128
        gamma = 0.98
        tau = 0.005  # 软更新参数
        buffer_size = 10000
        minimal_size = 64
        batch_size = 32
        sigma = sigma[4]
        # sigma = sigma[train_time]
        #device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        device = torch.device("cpu")

        env = microgrid_RO_env(UIES, 24)

        # random.seed(0)
        # np.random.seed(0)
        # env.seed(0)
        # torch.manual_seed(0)
        replay_buffer = ReplayBuffer(buffer_size)
        return_buffer = ReturnBuffer()
        # state_dim = env.observation_space.shape[0]
        state_dim = len(env.observation_space)
        action_dim = env.action_space.shape[0]
        action_bound = 1  # 动作最大值
        agent = DDPG(state_dim, hidden_dim, action_dim, action_bound, sigma, actor_lr, critic_lr, tau, gamma, device)
        '''
        if train_time != 0:
            agent.actor.load_state_dict(torch.load('.\Data\save_RL_model\DDPG_actor_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.target_actor.load_state_dict(torch.load('.\Data\save_RL_model\DDPG_actor_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.critic.load_state_dict(torch.load('.\Data\save_RL_model\DDPG_critic_network'+ '_' + str(train_time-1) + '.pkl'))
            agent.target_critic.load_state_dict(torch.load('.\Data\save_RL_model\DDPG_critic_network'+ '_' + str(train_time-1) + '.pkl'))
        '''
        # agent.actor.load_state_dict(
        #     torch.load('.\Data\save_RL_model\DDPG_actor_network_5000v6.0.pkl'))
        # agent.target_actor.load_state_dict(
        #     torch.load('.\Data\save_RL_model\DDPG_actor_network_5000v6.0.pkl'))
        # agent.critic.load_state_dict(
        #     torch.load('.\Data\save_RL_model\DDPG_critic_network_5000v6.0.pkl'))
        # agent.target_critic.load_state_dict(
        #     torch.load('.\Data\save_RL_model\DDPG_critic_network_5000v6.0.pkl'))

        storage_punishment_buffer = StoragePunishmentBuffer()

        train_off_policy_agent_MG_RO(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer, storage_punishment_buffer)

        episodes_list = list(range(len(return_buffer.operation_cost)))
        return_list = np.array([return_buffer.operation_cost, return_buffer.carbon_emission, return_buffer.carbon_emission_cost, return_buffer.profit, return_buffer.total_cost])
        punishment_list = storage_punishment_buffer.sum_punishment
        title = np.array(["operation_cost", "es_punishment", "gap_punishment", "profit", "total_cost"])
        # writeDatatoExcel(".\Data\Result\DDPG_actor.xlsx", 0, 0, np.array([episodes_list]))

        print("训练用时：", time.time() - start_time)

        plt.plot(episodes_list, return_list[4])
        plt.xlabel('Episodes')
        plt.ylabel('Returns')
        plt.title('DDPG on UIES return')
        # plt.show()
        # plt.savefig('.\Data\RL_RO\DDPG on {}'.format(title[0])+ str(train_time) +'0.png')

        a = np.squeeze(return_list[4])
        mv_return = moving_average(a, 9)
        # mv_return = moving_average(np.array([return_list[i]]), 9)
        plt.plot(episodes_list, mv_return)
        plt.xlabel('Episodes')
        plt.ylabel('Returns')
        plt.title('DDPG on UIES return')
        plt.savefig('.\Data\RL_RO\DDPG on UIES return' + '_50.png')
        # plt.show()
        # plt.savefig('.\Data\save_RL_model\DDPG on {}'.format(title[0])+ str(train_time) +'1.png')

        plt.clf()
        ###############################################################################
        plt.plot(episodes_list, punishment_list)
        plt.xlabel('Episodes')
        plt.ylabel('total Punishment')
        # plt.title('DDPG on {}'.format(title[0]))
        plt.title('DDPG on UIES Punishment')
        plt.savefig('.\Data\RL_RO\DDPG on UIES Punishment' + '_50.png')
        # plt.show()
        ###############################################################################
        # 保存到excel
        writeDatatoExcel(".\Data\RL_RO\Result\DDPG_actor_RO_50.xlsx", 1, 0, return_list[0])
        writeDatatoExcel(".\Data\RL_RO\Result\DDPG_actor_RO_50.xlsx", 2, 0, return_list[1])
        writeDatatoExcel(".\Data\RL_RO\Result\DDPG_actor_RO_50.xlsx", 3, 0, return_list[2])
        writeDatatoExcel(".\Data\RL_RO\Result\DDPG_actor_RO_50.xlsx", 4, 0, return_list[4])
        writeDatatoExcel(".\Data\RL_RO\Result\DDPG_actor_RO_50.xlsx", 5, 0, punishment_list)

        # 保存模型参数
        torch.save(agent.actor.state_dict(), '.\Data\RL_RO\model\DDPG_actor_network' + '_50.pkl')
        torch.save(agent.critic.state_dict(), '.\Data\RL_RO\model\DDPG_critic_network' + '_50.pkl')
        # save_data(env.save_name+str(train_time), env.x, 2)
        #draw(env.env.MG)


# a =test_DDPG()
# a.func()

sigma = [0.8, 0.6, 0.4, 0.2, 0.4]
# sigma = [0.4]
start_time = time.time()
for i in range(len(sigma)-4):
    a = test_DDPG()
    a.func(i+4, sigma)
print("训练用时：", time.time() - start_time)
