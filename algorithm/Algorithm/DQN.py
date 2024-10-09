import random
import tensorflow as tf
import numpy as np

from collections import namedtuple, deque
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense, Input

from tensorflow.python.keras.optimizers import adam_v2
from tensorflow.python.keras.losses import MSE

class DQN:
    def __init__(self, env):
        #Init
        self.SEED = 0
        self.MINBATCH_SIZE = 64
        self.TAU = 1e-3
        self.E_GREEDY_MAX = 0.995
        self.E_GREEDY_MIN = 0.01

        self.MEMORY_SIZE = 10000000
        self.GAMMA = 0.995
        self.ALPHA = 1e-3
        self.NUM_STEPS_FOR_UPDATE = 4

        self.state_size = env.observation_space
        self.num_actions = env.action_space.n

        self.q_network = Sequential([
            Input(shape=self.state_size),
            Dense(units=128, activation='relu'),
            Dense(units=128, activation='relu'),
            Dense(units=self.num_actions, activation='linear')
        ])

        self.target_q_network = Sequential([
            Input(shape=self.state_size),
            Dense(units=128, activation='relu'),
            Dense(units=128, activation='relu'),
            Dense(units=self.num_actions, activation='linear')
        ])

        self.target_q_network.set_weights(self.q_network.get_weights())

        self.optimizer = adam_v2.Adam(learning_rate=self.ALPHA)

        self.memory_buffer = deque(maxlen=self.MEMORY_SIZE)

        random.seed(self.SEED)



    def get_action(self, state, epsilon = 0.0, env = None):
        """

        :param state:
        :param epsilon:
        :param env:
        :return: action
        """
        state_q = np.expand_dims(state, axis = 0)
        q_values = self.q_network(state_q)
        if random.random() > epsilon:
            return np.argmax(q_values.numpy()[0])
        else:
            return random.choice(np.arange(env.action_space.n))

    def check_update_conditons(self, steps, env):

        if (steps + 1) % self.NUM_STEPS_FOR_UPDATE == 0 and len(self.memory_buffer) > self.MINBATCH_SIZE:
            experiences = self.__get_experiences()
            self.__agent_learn(experiences, env)

    def get_new_eps(self, epsilon):
        return max(self.E_GREEDY_MIN, self.E_GREEDY_MAX * epsilon)

    def __get_experiences(self):
        """

        :return:
        """
        experiences = random.sample(self.memory_buffer, k=self.MINBATCH_SIZE)

        states = tf.convert_to_tensor(
            np.array([e.state for e in experiences if e is not None]), dtype=tf.float32
        )
        actions = tf.convert_to_tensor(
            np.array([e.action for e in experiences if e is not None]), dtype=tf.float32
        )
        rewards = tf.convert_to_tensor(
            np.array([e.reward for e in experiences if e is not None]), dtype=tf.float32
        )
        next_states = tf.convert_to_tensor(
            np.array([e.next_state for e in experiences if e is not None]), dtype=tf.float32
        )
        done_vals = tf.convert_to_tensor(
            np.array([e.done for e in experiences if e is not None]).astype(np.uint8),
            dtype=tf.float32,
        )
        return (states, actions, rewards, next_states, done_vals)

    def __agent_learn(self, experiences, env):

        with tf.GradientTape() as tape:
            loss = self.__compute_loss(experiences, env)

        gradients = tape.gradient(loss, self.q_network.trainable_variables)

        self.optimizer.apply_gradients(zip(gradients, self.q_network.trainable_variables))

        self.__update_target_network()

    def __compute_loss(self, experiences, env):

        states, actions, rewards, next_states, done_vals = experiences

        max_qsa = tf.reduce_max(self.target_q_network(next_states), axis=1)

        y_targets = rewards + (self.GAMMA + max_qsa * (1 - done_vals))

        q_values = self.q_network(states)
        q_values = tf.gather_nd(q_values, tf.stack([tf.range(q_values.shape[0]), tf.cast(actions, tf.int32)], axis = 1))

        loss = MSE(y_targets, q_values)

        return loss

    def __update_target_network(self):

        for target_weights, q_network_wights in zip(self.target_q_network.weights, self.q_network.weights):
            target_weights.assign(self.TAU * q_network_wights + (1.0 - self.TAU) * target_weights)






