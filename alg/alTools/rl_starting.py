from tqdm import tqdm
import numpy as np
import torch
import collections
import random
import pandas as pd
import sys

from tools.maybeExcel import writeDatatoExcel


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        transitions = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*transitions)
        return np.array(state), action, reward, np.array(next_state), done

    def size(self):
        return len(self.buffer)


class ReturnBuffer:
    def __init__(self):
        self.operation_cost = np.array([])
        self.carbon_emission = np.array([])
        self.carbon_emission_cost = np.array([])
        self.profit = np.array([])
        self.total_cost = np.array([])

    def add(self, operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost):
        self.operation_cost = np.append(self.operation_cost, operation_cost)
        self.carbon_emission = np.append(self.carbon_emission, carbon_emission)
        self.carbon_emission_cost = np.append(self.carbon_emission_cost, carbon_emission_cost)
        self.profit = np.append(self.profit, profit)
        self.total_cost = np.append(self.total_cost, total_cost)

    def size(self):
        return len(self.operation_cost)

    def save(self, path, id):
        writeDatatoExcel(path, id, 0, self.operation_cost)
        writeDatatoExcel(path, id + 1, 0, self.carbon_emission)
        writeDatatoExcel(path, id + 2, 0, self.carbon_emission_cost)
        writeDatatoExcel(path, id + 3, 0, self.profit)
        writeDatatoExcel(path, id + 4, 0, self.total_cost)

    def save_3d(self, path, index):
        writeDatatoExcel(path, index, 0, self.carbon_emission)
        writeDatatoExcel(path, index, 100, self.total_cost)


class StoragePunishmentBuffer():
    def __init__(self):
        self.ramping_punishment = np.array([])
        self.punishment2 = np.array([])
        self.punishment3 = np.array([])
        self.sum_punishment = np.array([])

    def add(self, ramping_punishment, punishment2, punishment3):
        self.ramping_punishment = np.append(self.ramping_punishment, ramping_punishment)
        self.punishment2 = np.append(self.punishment2, punishment2)
        self.punishment3 = np.append(self.punishment3, punishment3)
        self.sum_punishment = np.append(self.sum_punishment, ramping_punishment+punishment2+punishment3)

    def size(self):
        return len(self.ramping_punishment)


def moving_average(a, window_size):
    cumulative_sum = np.cumsum(np.insert(a, 0, 0))
    middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
    r = np.arange(1, window_size - 1, 2)
    begin = np.cumsum(a[:window_size - 1])[::2] / r
    end = (np.cumsum(a[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((begin, middle, end))


def train_on_policy_agent(env, agent, num_episodes):
    return_list = []
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):

                episode_return = 0
                transition_dict = {'states': [], 'actions': [], 'next_states': [], 'rewards': [], 'dones': []}
                state = env.reset()
                done = False
                while not done:
                    # 渲染环境
                    env.render()

                    action = agent.take_action(state)
                    next_state, reward, done, _ = env.step(action)
                    transition_dict['states'].append(state)
                    transition_dict['actions'].append(action)
                    transition_dict['next_states'].append(next_state)
                    transition_dict['rewards'].append(reward)
                    transition_dict['dones'].append(done)
                    state = next_state
                    episode_return += reward
                return_list.append(episode_return)
                agent.update(transition_dict)
                if (i_episode + 1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes / 10 * i + i_episode + 1),
                                      'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    return return_list


def train_off_policy_agent(env, agent, num_episodes, replay_buffer, minimal_size, batch_size):
    return_list = []

    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                state = env.reset()
                done = False
                while not done:
                    action = agent.take_action(state)
                    next_state, reward, done, _ = env.step(action)
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward

                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                           'dones': b_d}
                        agent.update(transition_dict)
                env.env.countCost()
                return_list.append(episode_return)
                if (i_episode + 1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes / 10 * i + i_episode + 1),
                                      'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    return return_list


def train_off_policy_agent_MG(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer, storage_punishment_buffer):
    action_list = []
    ave_num = int(num_episodes // 20)
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                epsidoe_action_list = []
                # state = env.reset()
                # for MG in env.env.MG:
                #     for node in MG.node:
                #         for device in node.devices:
                #             print(device.name)
                state = env.reset2()
                done = False
                j = 1
                going = False
                actionSuccess = False
                cur_episode = i_episode + (i * num_episodes / 10)
                while not done:
                    # for k in range(500):
                    #     action = agent.take_action(state, time = env.step_time, i_episode = i_episode)
                    #     print(action)
                    while not going:
                        if actionSuccess == False:
                            # state = env.reset()
                            state = env.reset2()
                            epsidoe_action_list = []
                            # 对Demand和RT在t=1的功率添加随机性
                            # state = env.first_stochastic_factor_setting_RED()
                            state_1 = state
                        action = agent.take_action(state)
                        # next_state, reward, done, going = env.step2(action)
                        next_state, reward, done, going, action_ = env.step3(action, cur_episode, storage_punishment_buffer)
                        if next_state == None:
                            next_state = state_1
                        action = action_
                        if going == True:
                            actionSuccess = True
                        else:
                            actionSuccess = False
                    going = False
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward
                    epsidoe_action_list.append(action)
                    j += 1
                    print('\r', {'action': '%.3f' % np.mean(epsidoe_action_list[-1]),
                                 'step': '%d' % env.step_time,
                                 'time': '%d' % j}, end='', flush=False)

                    # 测试时不更新
                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                           'dones': b_d}
                        agent.update(transition_dict)

                operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost = env.env.countCost()
                print('operation_cost:', operation_cost)
                return_buffer.add(operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost)
                if (i_episode + 1) % ave_num == 0:
                    pbar.set_postfix({'episode': '%.3f' % (num_episodes / 10 * i + i_episode + 1),
                                      'operation_cost': '%.3f' % np.mean(return_buffer.operation_cost[-ave_num:]),
                                      'carbon_emission': '%.3f' % np.mean(return_buffer.carbon_emission[-ave_num:]),
                                      'carbon_emission_cost': '%.3f' % np.mean(
                                          return_buffer.carbon_emission_cost[-ave_num:]),
                                      'profit': '%.3f' % np.mean(return_buffer.profit[-ave_num:]),
                                      'total_cost': '%.3f' % np.mean(return_buffer.total_cost[-ave_num:])})
                    # 动作方差为0说明动作选择出错了
                    if np.var(epsidoe_action_list[-ave_num:]) == 0:
                        break
                pbar.update(1)

def train_off_policy_agent_MG_SAC(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer, storage_punishment_buffer):
    action_list = []
    ave_num = int(num_episodes // 20)
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                epsidoe_action_list = []
                # state = env.reset()
                # for MG in env.env.MG:
                #     for node in MG.node:
                #         for device in node.devices:
                #             print(device.name)
                state = env.reset2()
                done = False
                j = 1
                going = False
                actionSuccess = False
                cur_episode = i_episode + (i * num_episodes / 10)
                while not done:
                    while not going:
                        if actionSuccess == False:
                            # state = env.reset()
                            state = env.reset2()
                            epsidoe_action_list = []
                            # 对Demand和RT在t=1的功率添加随机性
                            state = env.first_stochastic_factor_setting_RED()
                            state_1 = state
                        action = agent.take_action(state)
                        action = action[0]
                        # next_state, reward, done, going = env.step2(action)
                        next_state, reward, done, going, action_ = env.step_SAC(action, cur_episode, storage_punishment_buffer)
                        if next_state == None:
                            next_state = state_1
                        action = action_
                        if going == True:
                            actionSuccess = True
                        else:
                            actionSuccess = False
                    going = False
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward
                    epsidoe_action_list.append(action)
                    j += 1
                    print('\r', {'action': '%.3f' % np.mean(epsidoe_action_list[-1]),
                                 'step': '%d' % env.step_time,
                                 'time': '%d' % j}, end='', flush=False)

                    # 测试时不更新
                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r, 'dones': b_d}
                        agent.update(transition_dict)

                operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost = env.env.countCost()
                print('operation_cost:', operation_cost)
                print('total_cost:', total_cost)
                return_buffer.add(operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost)
                if (i_episode + 1) % ave_num == 0:
                    pbar.set_postfix({'episode': '%.3f' % (num_episodes / 10 * i + i_episode + 1),
                                      'operation_cost': '%.3f' % np.mean(return_buffer.operation_cost[-ave_num:]),
                                      'carbon_emission': '%.3f' % np.mean(return_buffer.carbon_emission[-ave_num:]),
                                      'carbon_emission_cost': '%.3f' % np.mean(
                                          return_buffer.carbon_emission_cost[-ave_num:]),
                                      'profit': '%.3f' % np.mean(return_buffer.profit[-ave_num:]),
                                      'total_cost': '%.3f' % np.mean(return_buffer.total_cost[-ave_num:])})
                    # 动作方差为0说明动作选择出错了
                    if np.var(epsidoe_action_list[-ave_num:]) == 0:
                        break
                pbar.update(1)

def train_off_policy_agent_MG_RO(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer, storage_punishment_buffer):
    action_list = []
    ave_num = int(num_episodes // 20)
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                epsidoe_action_list = []
                # state = env.reset()
                # for MG in env.env.MG:
                #     for node in MG.node:
                #         for device in node.devices:
                #             print(device.name)
                state = env.reset()
                done = False
                j = 1
                going = False
                actionSuccess = False
                cur_episode = i_episode + (i * num_episodes / 10)
                while not done:
                    while not going:
                        if actionSuccess == False:
                            state = env.reset()
                            epsidoe_action_list = []
                            # 对Demand和RT(PV,WT)在t=1的功率添加随机性
                            state = env.first_stochastic_factor_setting_RED()
                            state_1 = state
                        action = agent.take_action_RO(state)
                        next_state, reward, done, going, action_ = env.step3(action, cur_episode, storage_punishment_buffer)
                        if next_state == None:
                            next_state = state_1
                        action = action_
                        if going == True:
                            actionSuccess = True
                        else:
                            actionSuccess = False
                    going = False
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward
                    epsidoe_action_list.append(action)
                    j += 1
                    print('\r', {'action_e': '%.3f' % action[0],
                                 'action_th': '%.3f' % action[1],
                                 'step': '%d' % env.step_time,
                                 'time': '%d' % j}, end='', flush=False)

                    # 测试时不更新，要注释这段代码
                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                           'dones': b_d}
                        agent.update_ro(transition_dict)

                # operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost = env.env.countCost()
                operation_cost, es_punishment, gap_punishment, profit, total_cost = env.env.countCost_RO(env.res)
                return_buffer.add(operation_cost, es_punishment, gap_punishment, profit, total_cost)

                # if env.rl_res is not None and es_punishment == 0 and operation_cost < env.min_operation:
                if True:
                    env.min_operation = operation_cost
                    df = pd.DataFrame({
                        'params': env.flash_num.params,
                        'value': env.rl_res.x
                    })
                    path = "D:\HeYuanxing\BaiduSyncdisk\DRLmicrogrid\Data\RL_RO\Result\\results_ddpg_ro.xlsx"
                    df.to_excel(path, index=False)
                    # sys.exit(0)
                if (i_episode + 1) % ave_num == 0:
                    pbar.set_postfix({'episode': '%.3f' % (num_episodes / 10 * i + i_episode + 1),
                                      'operation_cost': '%.3f' % np.mean(return_buffer.operation_cost[-ave_num:]),
                                      'carbon_emission': '%.3f' % np.mean(return_buffer.carbon_emission[-ave_num:]),
                                      'carbon_emission_cost': '%.3f' % np.mean(
                                          return_buffer.carbon_emission_cost[-ave_num:]),
                                      'profit': '%.3f' % np.mean(return_buffer.profit[-ave_num:]),
                                      'total_cost': '%.3f' % np.mean(return_buffer.total_cost[-ave_num:])})
                    # 动作方差为0说明动作选择出错了
                    if np.var(epsidoe_action_list[-ave_num:]) == 0:
                        break
                pbar.update(1)

def train_off_policy_agent_MG_ROtest(env, agent, num_episodes, replay_buffer, minimal_size, batch_size, return_buffer, storage_punishment_buffer):
    action_list = []
    ave_num = int(num_episodes // 20)
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                epsidoe_action_list = []
                # state = env.reset()
                # for MG in env.env.MG:
                #     for node in MG.node:
                #         for device in node.devices:
                #             print(device.name)
                state = env.reset()
                done = False
                j = 1
                going = False
                actionSuccess = False
                cur_episode = i_episode + (i * num_episodes / 10)
                while not done:
                    while not going:
                        if actionSuccess == False:
                            state = env.reset()
                            epsidoe_action_list = []
                            # 对Demand和RT(PV,WT)在t=1的功率添加随机性
                            state = env.first_stochastic_factor_setting_RED()
                            state_1 = state
                        action = agent.take_action_RO(state)
                        next_state, reward, done, going, action_ = env.step3(action, cur_episode, storage_punishment_buffer)
                        if next_state == None:
                            next_state = state_1
                        action = action_
                        if going == True:
                            actionSuccess = True
                        else:
                            actionSuccess = False
                    going = False
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward
                    epsidoe_action_list.append(action)
                    j += 1
                    print('\r', {'action': '%.3f' % np.mean(epsidoe_action_list[-1]),
                                 'step': '%d' % env.step_time,
                                 'time': '%d' % j}, end='', flush=False)
                    '''
                    # 测试时不更新，要注释这段代码
                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                           'dones': b_d}
                        agent.update_ro(transition_dict)
                    '''
                # operation_cost, carbon_emission, carbon_emission_cost, profit, total_cost = env.env.countCost()


                operation_cost, es_punishment, gap_punishment, profit, total_cost = env.env.countCost_RO(env.res)
                return_buffer.add(operation_cost, es_punishment, gap_punishment, profit, total_cost)

                if env.rl_res is not None and es_punishment == 0 and operation_cost < env.min_operation:
                    env.min_operation = operation_cost
                    df = pd.DataFrame({
                        'params': env.flash_num.params,
                        'value': env.rl_res.x
                    })
                    path = "D:\HeYuanxing\BaiduSyncdisk\DRLmicrogrid\Data\RL_RO\Result\\results_ddpg_ro.xlsx"
                    df.to_excel(path, index=False)
                    sys.exit(0)
                if (i_episode + 1) % ave_num == 0:
                    pbar.set_postfix({'episode': '%.3f' % (num_episodes / 10 * i + i_episode + 1),
                                      'operation_cost': '%.3f' % np.mean(return_buffer.operation_cost[-ave_num:]),
                                      'carbon_emission': '%.3f' % np.mean(return_buffer.carbon_emission[-ave_num:]),
                                      'carbon_emission_cost': '%.3f' % np.mean(
                                          return_buffer.carbon_emission_cost[-ave_num:]),
                                      'profit': '%.3f' % np.mean(return_buffer.profit[-ave_num:]),
                                      'total_cost': '%.3f' % np.mean(return_buffer.total_cost[-ave_num:])})
                    # 动作方差为0说明动作选择出错了
                    if np.var(epsidoe_action_list[-ave_num:]) == 0:
                        break
                pbar.update(1)

def compute_advantage(gamma, lmbda, td_delta):
    td_delta = td_delta.detach().numpy()
    advantage_list = []
    advantage = 0.0
    for delta in td_delta[::-1]:
        advantage = gamma * lmbda * advantage + delta
        advantage_list.append(advantage)
    advantage_list.reverse()
    return torch.tensor(advantage_list, dtype=torch.float)
