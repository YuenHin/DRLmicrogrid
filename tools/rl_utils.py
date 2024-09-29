from tqdm import tqdm
import numpy as np
import torch
import collections
import random
import pandas as pd


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

    def save_to_excel(self, file_name):
        # 创建一个空的列表来存储每个 transition 的数据
        data = []

        for state, action, reward, next_state, done in self.buffer:
            # 将state和next_state展开成列表，action是一个list，reward和done是单个值
            row = list(state) + action + [reward] + list(next_state) + [done]
            data.append(row)

        # 定义列名（根据state和next_state的形状为3，action为1，reward为1，done为1）
        columns = ['state1', 'state2', 'state3', 'action', 'reward', 'next_state1', 'next_state2', 'next_state3',
                   'done']

        # 使用 pandas 将数据保存为 DataFrame
        df = pd.DataFrame(data, columns=columns)

        # 将 DataFrame 写入 Excel
        df.to_excel('..\hyx_experiment\save_buffer\exp_' + file_name + '.xlsx', index=False)

    def load_from_excel(self, file_name):
        """从 Excel 文件加载数据到 ReplayBuffer"""
        # 读取 Excel 文件
        df = pd.read_excel('..\hyx_experiment\save_buffer\exp_' + file_name + '.xlsx')

        # 遍历每一行，将数据加入 ReplayBuffer
        for _, row in df.iterrows():
            # 提取 state、action、reward、next_state 和 done
            state = np.array([row['state1'], row['state2'], row['state3']])
            action = [row['action']]  # action 是一个列表
            reward = row['reward']
            next_state = np.array([row['next_state1'], row['next_state2'], row['next_state3']])
            done = row['done']

            # 添加到 ReplayBuffer 中
            self.add(state, action, reward, next_state, done)


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
                state = state[0] # Pendulum-v1环境用
                done = False
                while not done:
                    action = agent.take_action(state)
                    # next_state, reward, done, _ = env.step(action)
                    next_state, reward, truncated, done, _ = env.step(action)
                    replay_buffer.add(state, action, reward, next_state, done)
                    state = next_state
                    episode_return += reward
                    if replay_buffer.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                           'dones': b_d}
                        agent.update(transition_dict)
                return_list.append(episode_return)
                if (i_episode + 1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes / 10 * i + i_episode + 1),
                                      'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    return return_list

def my_train_off_policy_agent(env, agent, num_episodes, replay_buffer, minimal_size, batch_size):
    return_list = []
    for i in range(int(num_episodes)):
        with tqdm(total=int(num_episodes), desc='Iteration %d' % i) as pbar:
            episode_return = 0
            state = env.reset()
            state = state[0]  # Pendulum-v1环境用
            done = False
            while not done:
                action = agent.take_action(state)
                next_state, reward, truncated, done, _ = env.step(action)
                replay_buffer.add(state, action, reward, next_state, done)
                state = next_state
                episode_return += reward
                if replay_buffer.size() > minimal_size:
                    b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                    transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r,
                                       'dones': b_d}
                    agent.update(transition_dict)
            return_list.append(episode_return)
            pbar.update(1)
    return return_list

def compute_advantage(gamma, lmbda, td_delta):
    td_delta = td_delta.detach().numpy()
    advantage_list = []
    advantage = 0.0
    for delta in td_delta[::-1]:
        advantage = gamma * lmbda * advantage + delta
        advantage_list.append(advantage)
    advantage_list.reverse()
    return torch.tensor(advantage_list, dtype=torch.float)
