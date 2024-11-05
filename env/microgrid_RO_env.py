import math

from tools.Logic import MMGs_logic, x_callBack, draw, save_data
from tools.MILP import EndCount, PrintBounds,EndCount_notPrint
import numpy as np
import time
import os
from copy import deepcopy

import gurobipy as gp
from gurobipy import GRB


class microgrid_RO_env:
    def __init__(self, MMGs, step_all):
        self.start_time = time.time()
        self.step_all = step_all
        # 初始化
        self.con_add_num = 12  # 这是？
        self.env = MMGs
        self.save_name = "zzy_RO"
        self.C, self.intergrality, self.start_num = MMGs_logic(self.env, self.save_name, flag=True)
        self.flash_num = deepcopy(self.start_num)
        # self.start_num_ =self.start_num
        # self.flash_num = self.start_num_
        # for i in range(len(self.flash_num.params)):
        #     print(self.flash_num.params[i], "   :", np.round(self.C[i], 5))
        # print(self.flash_num.params)
        # PrintBounds(self.flash_num)
        # self.observation_space = self.start_num.params
        self.observation_space = ['current_t', 'current_e_price', 'current_g_price', 'demand_e_total_t', 'demand_th_total_t', 'demand_c_total_t', 'demand_g_total_t', 'RT_P_total_t',
                                  'S_e_t', 'S_th_t', 'S_c_t']
        # self.action_space = np.array([len(self.observation_space)])
        # self.action_space = np.array(['CPP_P', 'GW_P', 'S_e', 'S_th', 'S_c'])
        self.action_space = np.array(['S_e', 'S_th'])
        # for MG in self.env.MG:
        #     for node in MG.node:
        #         for device in node.devices:
        #             print(device.className)

        # 第一次执行全流程Perfect_MILP程序
        res = EndCount_notPrint(self.C, self.intergrality, self.flash_num)
        # PrintBounds(self.flash_num)
        # res = EndCount(-self.C, self.intergrality, self.flash_num)
        # PrintBounds(self.flash_num)
        # os.system("pause")
        self.res = res
        self.x = res.x
        # 第一次数据记录
        self.step_time = 1
        x_callBack(res, self.env, self.save_name, flag=False)
        # 初始化结束之后，每一个设备在预测值下的运行数据都已经获得了；下面需要对数据进行第一轮处理
        print("初始化用时：", time.time() - self.start_time)

        # for MG in self.env.MG:
        #     for node in MG.node:
        #         for device in node.devices:
        #             print(device.className)

        self.last_time = time.time()

        self.afterReset = True

        self.rl_res = None  # 记录强化学习的求解结果
        self.min_operation = 80000

    def reset(self):
        demand_e_total_t = 0  # 所有Demand(e)设备在第t步的功率需求总和
        demand_th_total_t = 0  # 所有Demand(th)设备在第t步的功率需求总和
        demand_c_total_t = 0  # 所有Demand(c)设备在第t步的功率需求总和
        demand_g_total_t = 0  # 所有Demand(g)设备在第t步的功率需求总和
        RT_P_total_t = 0  # 所有可再生能源在第t步的出力功率总和
        S_e_t = 0  # 电储能设备在第t步的剩余容量
        S_th_t = 0  # 热储能设备在第t步的剩余容量
        S_c_t = 0  # 冷储能设备在第t步的剩余容量
        current_e_price = 0  # 第t步的电价
        current_g_price = 0  # 第t步的天然气价格
        self.flash_num = deepcopy(self.start_num)  # 深拷贝
        self.step_time = 1
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == 'D' and device.type == 'e':
                        D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_e_total_t = demand_e_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'th':
                        D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_th_total_t = demand_th_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'c':
                        D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_c_total_t = demand_c_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'g':
                        D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_g_total_t = demand_g_total_t + D_norma_P1
                    elif device.className == 'RT':
                        RT_P1 = device.p[0]
                        RT_P_min = device.p_min.min()
                        RT_P_max = device.p_max.max()
                        RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                        RT_P_total_t = RT_P_total_t + RT_norma_P1
                    elif device.className == 'S' and device.type == 'e':
                        E_e_0 = device.storage_limit / 2
                        norma_E_e_0 = E_e_0 / device.storage_limit  # 归一化
                        S_e_t = S_e_t + norma_E_e_0
                    elif device.className == 'S' and device.type == 'th':
                        E_th_0 = device.storage_limit / 2
                        norma_E_th_0 = E_th_0 / device.storage_limit  # 归一化
                        S_th_t = S_th_t + norma_E_th_0
                    elif device.className == 'S' and device.type == 'c':
                        E_c_0 = device.storage_limit / 2
                        norma_E_c_0 = E_c_0 / device.storage_limit  # 归一化
                        S_c_t = S_c_t + norma_E_c_0
                    elif device.className == 'CPP':
                        current_e_price = device.production_price[0]
                    elif device.className == 'GW':
                        current_g_price = device.production_price[0]
        current_t = 1
        current_t = current_t / self.step_all
        #状态：    当前时间t     电价               天然气价格       电能需求               热能需求            冷能需求         天然气需求      可再生能源总出力 电储容量 热储容量 冷储容量
        state = [current_t, current_e_price, current_g_price, demand_e_total_t, demand_th_total_t, demand_c_total_t, demand_g_total_t, RT_P_total_t, S_e_t, S_th_t, S_c_t]
        return state

    # 一级设备：不确定性数据载入一级设备（RE、D）
    def __stochastic_factor_setting_RED(self):
        # 1.先找到每一个RE、D
        # 2.执行每一个(RE、D)的随机函数，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if ((device.className == "RT" and (device.type == "PV" or device.type == "WT")) or
                            (device.className == "D" and (device.type == "e" or device.type == "g" or device.type == "th" or device.type == "c"))):
                        device.stochastic(self.step_time, self.flash_num)

    def first_stochastic_factor_setting_RED(self):
        #  只会在每次reset之后从外部调用一次
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if ((device.className == "RT" and( device.type == "PV" or device.type == "WT")) or
                            (device.className == "D" and (device.type == "e" or device.type == "g" or device.type == "th" or device.type == "c"))):
                        device.stochastic(self.step_time, self.flash_num)
        demand_e_total_t = 0  # 所有Demand(e)设备在第t步的功率需求总和
        demand_th_total_t = 0  # 所有Demand(th)设备在第t步的功率需求总和
        demand_c_total_t = 0  # 所有Demand(c)设备在第t步的功率需求总和
        demand_g_total_t = 0  # 所有Demand(g)设备在第t步的功率需求总和
        RT_P_total_t = 0  # 所有可再生能源在第t步的出力功率总和
        S_e_t = 0  # 电储能设备在第t步的剩余容量
        S_th_t = 0  # 热储能设备在第t步的剩余容量
        S_c_t = 0  # 冷储能设备在第t步的剩余容量
        current_e_price = 0  # 第t步的电价
        current_g_price = 0  # 第t步的天然气价格
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == 'D' and device.type == 'e' and device.name != 'load_e_ex':
                        # D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P1 = device.real_x[0]  # 获取该负荷设备在t=1时刻的功率需求
                        # D_P1 = device.x[0]
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_e_total_t = demand_e_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'th':
                        # D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P1 = device.real_x[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_th_total_t = demand_th_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'c':
                        # D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P1 = device.real_x[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_c_total_t = demand_c_total_t + D_norma_P1
                    elif device.className == 'D' and device.type == 'g':
                        # D_P1 = device.p[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P1 = device.real_x[0]  # 获取该负荷设备在t=1时刻的功率需求
                        D_P_min = device.p_min.min()
                        D_P_max = device.p_max.max()
                        D_norma_P1 = (D_P1 - D_P_min) / (D_P_max - D_P_min)  # 归一化
                        demand_g_total_t = demand_g_total_t + D_norma_P1
                    elif device.className == 'RT':
                        # RT_P1 = device.p[0]
                        # RT_P1 = device.real_x[0]  # 获取该可再生能源设备在t=1时刻的出力功率
                        RT_P1 = device.p_max[0]
                        RT_P_min = device.p_min.min()
                        if RT_P_min < 0:
                            RT_P_min = 0
                        RT_P_max = device.p_max.max()
                        RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                        RT_P_total_t = RT_P_total_t + RT_norma_P1
                    elif device.className == 'S' and device.type == 'e':
                        E_e_0 = device.storage_limit / 2
                        norma_E_e_0 = E_e_0 / device.storage_limit  # 归一化
                        S_e_t = S_e_t + norma_E_e_0
                    elif device.className == 'S' and device.type == 'th':
                        E_th_0 = device.storage_limit / 2
                        norma_E_th_0 = E_th_0 / device.storage_limit  # 归一化
                        S_th_t = S_th_t + norma_E_th_0
                    elif device.className == 'S' and device.type == 'c':
                        E_c_0 = device.storage_limit / 2
                        norma_E_c_0 = E_c_0 / device.storage_limit  # 归一化
                        S_c_t = S_c_t + norma_E_c_0
                    elif device.className == 'CPP':
                        current_e_price = device.production_price[0]
                    elif device.className == 'GW':
                        current_g_price = device.production_price[0]
        current_t = 1
        current_t = current_t / self.step_all
        # 状态：    当前时间t     电价               天然气价格       电能需求               热能需求            冷能需求         天然气需求      可再生能源总出力 电储容量 热储容量 冷储容量
        state = [current_t, current_e_price, current_g_price, demand_e_total_t, demand_th_total_t, demand_c_total_t,
                 demand_g_total_t, RT_P_total_t, S_e_t, S_th_t, S_c_t]
        return state

    # 二级设备：储能+DG
    def __get_action_SE(self, action, cur_episode):
        # 1.先找到每一个SE
        # 2.执行每一个SE的执行动作，并附加约束
        # action['CPP_P', 'GW_P', 'S_e', 'S_th', 'S_c']
        # action['S_e', 'S_th']
        action_ = action
        done = False
        '''
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S" and device.type == "e":
                        done, action_[2] = device.get_action(self.step_time, self.flash_num, action[2], cur_episode)
                    elif device.className == "S" and device.type == "th":
                        done, action_[3] = device.get_action(self.step_time, self.flash_num, action[3], cur_episode)
                    elif device.className == "S" and device.type == "c":
                        done, action_[4] = device.get_action(self.step_time, self.flash_num, action[4], cur_episode)
        '''
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S" and device.type == "e":
                        done, action_[0] = device.get_action(self.step_time, self.flash_num, action[0], cur_episode)
                    elif device.className == "S" and device.type == "th":
                        done, action_[1] = device.get_action(self.step_time, self.flash_num, action[1], cur_episode)
        return done, action_

    # 二级设备：储能+DG
    def __get_action_SE_nocontrol(self):
        # 1.先找到每一个设备
        # 2.执行每一个设备的执行动作，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S" and (device.type == "g" or device.type == "h"):
                        device.remember_realValue(self.step_time, self.flash_num)
                    if device.className == "DG":
                        device.remember_realValue(self.step_time, self.flash_num)

    # 三级设备记录
    def __remenber_CPPGWECDG(self):
        # 1.先找到每一个设备
        # 2.执行每一个设备的执行动作，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    # if device.className == "CPP" or device.className == "GW" or device.className == "TP" or device.className == "CTP" or device.className == "D":
                    if device.className == "CPP" or device.className == "GW" or device.className == "TP" or device.className == "CTP":
                        device.remember_realValue(self.step_time, self.flash_num)

    def __remember_CPPGW(self):
        # 1.先找到每一个设备(CPP、GW)
        # 2.附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "CPP" or device.className == "GW":
                        device.remember_realValue(self.step_time, self.flash_num)

    def __get_action_CPPGW(self, action, cur_episode):
        # 1.先找到每一个CPP、GW
        # 2.执行每一个CPP、GW的执行动作，并附加约束
        # action['CPP_P', 'GW_P', 'S_e', 'S_th', 'S_c']
        action_ = action
        done = False
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "CPP":
                        done, action_[0] = device.get_action(self.step_time, self.flash_num, action[0], cur_episode)
                    elif device.className == "GW":
                        done, action_[1] = device.get_action(self.step_time, self.flash_num, action[1], cur_episode)

        return done, action_

    # 测试用，储能S不通过智能体选择动作，而是直接拿MILP的求解结果
    def __remember_S(self):
        # 1.先找到每一个储能设备
        # 2.记录储能设备的动作，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S":
                        device.remember_realValue(self.step_time, self.flash_num)

    # 调试设备
    def __re_train(self):
        # 1.先找到每一个RE、D
        # 2.执行每一个RE、D的调试备用函数
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "RT" or (device.className == "D" and (
                            device.type == "e" or device.type == "g" or device.type == "th" or device.type == "h")):
                        device.retrain(self.step_time, self.flash_num)

    # 删除一个约束
    def __de_constrains(self):
        self.flash_num.A = self.flash_num.A[:-(self.flash_num.variableNum)]
        self.flash_num.bl = self.flash_num.bl[:-1]
        self.flash_num.bu = self.flash_num.bu[:-1]

    # 计算一个奖励
    def __count_reward(self):
        reward = 0
        operation_cost = 0
        profit = 0
        carbon_emission = 0
        ramping_punishment = 0
        punishment2 = 0
        punishment3 = 0
        punishment4 = 0
        gap_punishment = 0

        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    # cpp生产成本
                    if device.className == "CPP":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)
                        # CPP的惩罚项
                        gap_punishment += device.p_gap[self.step_time - 1] * 1.5

                    # gw生产成本
                    if device.className == "GW":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)
                        # GW的惩罚项
                        gap_punishment += device.p_gap[self.step_time - 1] * 1.5

                    # pv生产成本
                    # wt生产成本
                    if device.className == "RT":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)

                    # 储能成本
                    if device.className == "S":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 2 + self.step_time - 1] * device.c[device.time_num * 2 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 3 + self.step_time - 1] * device.c[device.time_num * 3 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 4 + self.step_time - 1] * device.c[device.time_num * 4 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 5 + self.step_time - 1] * device.c[device.time_num * 5 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 6 + self.step_time - 1] * device.c[device.time_num * 6 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 7 + self.step_time - 1] * device.c[device.time_num * 7 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 8 + self.step_time - 1] * device.c[device.time_num * 8 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 9 + self.step_time - 1] * device.c[device.time_num * 9 + self.step_time - 1] * (24 / device.time_num)
                        # 是否超出ramping_limit的约束，超出的部分乘一个系数
                        # 当前容量等于0时，扣大分
                        # t=24时容量如果小于最大容量的一半，扣大分
                        if device.type != 'c':
                            if self.step_time == 1:
                                ramping_p = abs(device.real_E[self.step_time - 1] - (device.e/2)) - device.ramping_limit
                            else:
                                ramping_p = abs(device.real_E[self.step_time - 1] - device.real_E[self.step_time - 2]) - device.ramping_limit
                            if ramping_p > 0:
                                ramping_punishment += ramping_p * 500
                            punishment2 += (device.real_E[self.step_time - 1] <= 0) * 1000
                            # punishment4 += (device.real_E[self.step_time - 1] >= device.e) * 1000
                            # if self.step_time == 24:
                            #     print("24")
                            punishment3 += (self.step_time == self.step_all and device.real_E[self.step_time-1] < device.e/2) * 10000
                            a = device.time_num - math.ceil(device.e/2 / device.ramping_limit)
                            if self.step_time - a > 0 and self.step_time < 24:
                                b = self.step_time - a
                                if device.real_E[self.step_time - 1] < device.ramping_limit * b:
                                    punishment3 += 1000

                    # 能量转化设备成本
                    if device.className == "er":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (
                                    24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[
                            device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 2 + self.step_time - 1] * device.c[
                            device.time_num * 2 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 3 + self.step_time - 1] * device.c[
                            device.time_num * 3 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 4 + self.step_time - 1] * device.c[
                            device.time_num * 4 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 5 + self.step_time - 1] * device.c[
                            device.time_num * 5 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 6 + self.step_time - 1] * device.c[
                            device.time_num * 6 + self.step_time - 1] * (24 / device.time_num)

                    if device.className == "eb":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (
                                    24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[
                            device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 2 + self.step_time - 1] * device.c[
                            device.time_num * 2 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 3 + self.step_time - 1] * device.c[
                            device.time_num * 3 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 4 + self.step_time - 1] * device.c[
                            device.time_num * 4 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 5 + self.step_time - 1] * device.c[
                            device.time_num * 5 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 6 + self.step_time - 1] * device.c[
                            device.time_num * 6 + self.step_time - 1] * (24 / device.time_num)

                    if device.className == "cchp":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (
                                    24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[
                            device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 2 + self.step_time - 1] * device.c[
                            device.time_num * 2 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 3 + self.step_time - 1] * device.c[
                            device.time_num * 3 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 4 + self.step_time - 1] * device.c[
                            device.time_num * 4 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 5 + self.step_time - 1] * device.c[
                            device.time_num * 5 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 6 + self.step_time - 1] * device.c[
                            device.time_num * 6 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 7 + self.step_time - 1] * device.c[
                            device.time_num * 7 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 8 + self.step_time - 1] * device.c[
                            device.time_num * 8 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 9 + self.step_time - 1] * device.c[
                            device.time_num * 9 + self.step_time - 1] * (24 / device.time_num)

                    # 负荷
                    if device.className == "D":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)

                    # 柔性负荷
                    if device.className == "FL":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)

                    # 灵活性需求
                    if device.className == "FD":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)

                    # 灵活性分析
                    if device.className == "FA":
                        operation_cost += device.x[self.step_time - 1] * device.c[self.step_time - 1] * (
                                24 / device.time_num)
                        operation_cost += device.x[device.time_num * 1 + self.step_time - 1] * device.c[
                            device.time_num * 1 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 2 + self.step_time - 1] * device.c[
                            device.time_num * 2 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 3 + self.step_time - 1] * device.c[
                            device.time_num * 3 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 4 + self.step_time - 1] * device.c[
                            device.time_num * 4 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 5 + self.step_time - 1] * device.c[
                            device.time_num * 5 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 6 + self.step_time - 1] * device.c[
                            device.time_num * 6 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 7 + self.step_time - 1] * device.c[
                            device.time_num * 7 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 8 + self.step_time - 1] * device.c[
                            device.time_num * 8 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 9 + self.step_time - 1] * device.c[
                            device.time_num * 9 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 10 + self.step_time - 1] * device.c[
                            device.time_num * 10 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 11 + self.step_time - 1] * device.c[
                            device.time_num * 11 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 12 + self.step_time - 1] * device.c[
                            device.time_num * 12 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 13 + self.step_time - 1] * device.c[
                            device.time_num * 13 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 14 + self.step_time - 1] * device.c[
                            device.time_num * 14 + self.step_time - 1] * (24 / device.time_num)
                        operation_cost += device.x[device.time_num * 15 + self.step_time - 1] * device.c[
                            device.time_num * 15 + self.step_time - 1] * (24 / device.time_num)

                    if device.name == "load_e_ex":
                        gap_punishment += device.x[self.step_time - 1] * 10 * (24 / device.time_num)

        reward = -(operation_cost + punishment2 + punishment3 + ramping_punishment + punishment4 + gap_punishment)
        # sp_max = 600
        # reward = -( 2*(punishment2 + punishment3 + ramping_punishment) +
        #             (operation_cost + carbom_emission_cost - profit) +
        #             (operation_cost + carbom_emission_cost - profit)*(punishment2 + punishment3 + ramping_punishment)/sp_max
        # )
        es_punishment = ramping_punishment + punishment2 + punishment3 + punishment4
        return reward, es_punishment, gap_punishment

    def step3(self, action, cur_episode, storage_punishment_buffer):
        done = False
        action_ = action
        # action = [0, 0]
        # res = EndCount(self.C, self.intergrality, self.flash_num)
        # 执行动作
        # 先执行储能的动作
        done, action_ = self.__get_action_SE(action, cur_episode)  # 控制电储和热储

        if done == True:
            return self.x, np.array([0]), True, None, action_
        res = EndCount_notPrint(self.C, self.intergrality, self.flash_num)  # 使用MILP验证执行动作后有无解
        done = False
        if res.success == False:
            # PrintBounds(self.flash_num)
            res_gurobi = self.__get_guribo_result(self.C, self.intergrality, self.flash_num)
            print("储能动作后无解了！！！！！！！！！")
            # for MG in self.env.MG:
            #     for node in MG.node:
            #         for device in node.devices:
            #             print(device.className)
            return None, np.array([0]), done, False, action_
        x_callBack(res, self.env, self.save_name, flag=False)
        self.x = res.x

        '''
        # 再执行CPP和GW的动作
        done, action_ = self.__get_action_CPPGW(action, cur_episode)
        if done == True:
            return self.x, np.array([0]), True, None, action_
        res = EndCount_notPrint(self.C, self.intergrality, self.flash_num)  # 使用MILP验证执行动作后有无解，并得到该环境下的其他设备的真实控制值
        done = False
        if res.success == False:
            # PrintBounds(self.flash_num)
            print("CPP和GW动作后无解了！！！！！！！！！")
            return None, np.array([0]), done, False, action_

        x_callBack(res, self.env, self.save_name, flag=False)
        self.x = res.x
        '''
        # 记录设备的真实控制状态
        self.__remember_CPPGW()  # CPP和GW
        # self.__remember_conversion_unit()  # CCHP,EB,ER
        # self.__remember_FaFlFd()  # FA,FL,FD
        # self.__remember_S()  # S_e,S_th,S_c


        # 接下来进行t+1时刻RT和Demand随机性的添加
        self.step_time += 1  ############################################################################
        if self.step_time < 25:
            self.__stochastic_factor_setting_RED()

            # 这里需要获取下一步的负荷的总需求功率和可再生能源的总出力功率
            demand_e_total_t = 0  # 所有Demand(e)设备在第t步的功率需求总和
            demand_th_total_t = 0  # 所有Demand(th)设备在第t步的功率需求总和
            demand_c_total_t = 0  # 所有Demand(c)设备在第t步的功率需求总和
            demand_g_total_t = 0  # 所有Demand(g)设备在第t步的功率需求总和
            RT_P_total_t = 0  # 所有可再生能源在第t步的出力功率总和
            S_e_t = 0  # 电储能设备在第t步的剩余容量
            S_th_t = 0  # 热储能设备在第t步的剩余容量
            S_c_t = 0  # 冷储能设备在第t步的剩余容量
            current_e_price = 0  # 第t步的电价
            current_g_price = 0  # 第t步的天然气价格
            current_t = self.step_time / self.step_all  # 处理后的值在0到1之间
            for MG in self.env.MG:
                for node in MG.node:
                    for device in node.devices:
                        if device.className == 'D' and device.type == 'e' and device.name != 'load_e_ex':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_e_total_t = demand_e_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'th':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_th_total_t = demand_th_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'c':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_c_total_t = demand_c_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'g':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_g_total_t = demand_g_total_t + D_norma_P1
                        elif device.className == 'RT' and device.type != 'HP':
                            # RT_P1 = device.stochas_P[self.step_time - 1]
                            # RT_P1 = device.p[self.step_time - 1]
                            # RT_P1 = device.real_x[self.step_time - 1]
                            RT_P1 = device.p_max[self.step_time - 1]
                            RT_P_min = device.p_min.min()
                            if RT_P_min < 0:
                                RT_P_min = 0
                            RT_P_max = device.p_max.max()
                            RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                            RT_P_total_t = RT_P_total_t + RT_norma_P1
                        elif device.className == 'RT' and device.type == 'HP':
                            # RT_P1 = device.p[self.step_time - 1]
                            RT_P1 = device.p_max[self.step_time - 1]
                            RT_P_min = device.p_min.min()
                            if RT_P_min < 0:
                                RT_P_min = 0
                            RT_P_max = device.p_max.max()
                            RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                            RT_P_total_t = RT_P_total_t + RT_norma_P1
                        elif device.className == 'S' and device.type == 'e':
                            E_e = device.real_E[self.step_time - 2]
                            norma_E_e = E_e / device.storage_limit  # 归一化，处理后的值在0到1之间
                            S_e_t = S_e_t + norma_E_e
                        elif device.className == 'S' and device.type == 'th':
                            E_th = device.real_E[self.step_time - 2]
                            norma_E_th = E_th / device.storage_limit  # 归一化
                            S_th_t = S_th_t + norma_E_th
                        elif device.className == 'S' and device.type == 'c':
                            E_c = device.real_E[self.step_time - 2]
                            norma_E_c = E_c / device.storage_limit  # 归一化
                            S_c_t = S_c_t + norma_E_c
                        elif device.className == 'CPP':
                            current_e_price = device.production_price[self.step_time - 1]
                        elif device.className == 'GW':
                            current_g_price = device.production_price[self.step_time - 1]
            # 状态：    当前时间t     电价               天然气价格       电能需求               热能需求            冷能需求         天然气需求      可再生能源总出力 电储容量 热储容量 冷储容量
            state = [current_t, current_e_price, current_g_price, demand_e_total_t, demand_th_total_t,
                     demand_c_total_t, demand_g_total_t, RT_P_total_t, S_e_t, S_th_t, S_c_t]

        if self.step_time == 25:
            # 将t=1的state作为t=25的state
            # t=1的state在上一级函数可以获取
            state = None
        self.step_time -= 1  #######################################################################################

        # 计算奖励
        reward, es_punishment, gap_punishment = self.__count_reward()
        if es_punishment == 0:
            reward += 100
        print("-------------es_punishment:", es_punishment)
        # reward += 20
        # es_punishment +=es_punishment
        if self.step_time == self.step_all:
            # a, b, c, d, total_cost = self.env.countCost()
            # reward += 2000 - total_cost
            # reward = res.fun + es_punishment + gap_punishment
            done = True
            storage_punishment_buffer.add(es_punishment, gap_punishment, 0)
            # print("-------------gap_punishment:", gap_punishment)
            self.rl_res = res
        # 更新步长
        self.step_time += 1

        return state, reward, done, True, action_

    def __remember_conversion_unit(self):
        # 1.先找到每一个设备(ER,EB,CCHP)
        # 2.附加约束(记录控制的真实功率)
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == 'cchp' or device.className == 'eb' or device.className == 'er':
                        device.remember_realValue(self.step_time, self.flash_num)

    def __remember_FaFlFd(self):
        # 1.先找到每一个设备(FA,FL,FD)
        # 2.附加约束(记录控制的真实功率)
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == 'FA' or device.className == 'FD' or device.className == 'FL':
                        device.remember_realValue(self.step_time, self.flash_num)



    def __get_guribo_result(self, C, integrality, num):

        "打印约束"
        # PrintBounds(num)

        A = num.A
        params = num.params
        A = A.reshape((int(len(A) / len(params)), len(params)))
        bl = num.bl
        bu = num.bu
        c = C

        model = gp.Model("RO")

        # 创建决策变量
        vars = model.addVars(range(len(params)), vtype=gp.GRB.CONTINUOUS)
        for i in range(len(params)):
            vars[i].varName = params[i]

        # 设置目标函数
        model.setObjective(gp.quicksum(c[i] * vars[i] for i in range(len(c))), gp.GRB.MINIMIZE)

        # 设置约束
        for j in range(A.shape[0]):
            model.addConstr(gp.quicksum(A[j, i] * vars[i] for i in range(len(params))) >= bl[j])
            model.addConstr(gp.quicksum(A[j, i] * vars[i] for i in range(len(params))) <= bu[j])

        "求解RO问题"
        model.optimize()

        if model.status != gp.GRB.OPTIMAL:
            model.computeIIS()
            model.write("model_ro_notorch.ilp")

        "保存问题的解"
        var_values = np.zeros(len(vars))
        for i in range(len(vars)):
            var_values[i] = vars[i].x

        return var_values


    def step3_notorch(self, action, cur_episode, storage_punishment_buffer):
        done = False
        action_ = action
        # action = [0, 0]
        # res = EndCount(self.C, self.intergrality, self.flash_num)
        # 执行动作
        # 先执行储能的动作
        done, action_ = self.__get_action_SE(action, cur_episode)  # 控制电储和热储

        if done == True:
            return self.x, np.array([0]), True, None, action_
        res = EndCount_notPrint(self.C, self.intergrality, self.flash_num)  # 使用MILP验证执行动作后有无解

        # res = self.__get_guribo_result(self.C, self.intergrality, self.flash_num)

        done = False
        # if res.success == False:
        #     PrintBounds(self.flash_num)
        #     print("储能动作后无解了！！！！！！！！！")
        #     for MG in self.env.MG:
        #         for node in MG.node:
        #             for device in node.devices:
        #                 print(device.className)
        #     return None, np.array([0]), done, False, action_
        # x_callBack(res, self.env, self.save_name, flag=False)
        # self.x = res

        '''
        # 再执行CPP和GW的动作
        done, action_ = self.__get_action_CPPGW(action, cur_episode)
        if done == True:
            return self.x, np.array([0]), True, None, action_
        res = EndCount_notPrint(self.C, self.intergrality, self.flash_num)  # 使用MILP验证执行动作后有无解，并得到该环境下的其他设备的真实控制值
        done = False
        if res.success == False:
            # PrintBounds(self.flash_num)
            print("CPP和GW动作后无解了！！！！！！！！！")
            return None, np.array([0]), done, False, action_

        x_callBack(res, self.env, self.save_name, flag=False)
        self.x = res.x
        '''
        # 记录设备的真实控制状态
        self.__remember_CPPGW()  # CPP和GW
        # self.__remember_conversion_unit()  # CCHP,EB,ER
        # self.__remember_FaFlFd()  # FA,FL,FD
        # self.__remember_S()  # S_e,S_th,S_c


        # 接下来进行t+1时刻RT和Demand随机性的添加
        self.step_time += 1  ############################################################################
        if self.step_time < 25:
            self.__stochastic_factor_setting_RED()

            # 这里需要获取下一步的负荷的总需求功率和可再生能源的总出力功率
            demand_e_total_t = 0  # 所有Demand(e)设备在第t步的功率需求总和
            demand_th_total_t = 0  # 所有Demand(th)设备在第t步的功率需求总和
            demand_c_total_t = 0  # 所有Demand(c)设备在第t步的功率需求总和
            demand_g_total_t = 0  # 所有Demand(g)设备在第t步的功率需求总和
            RT_P_total_t = 0  # 所有可再生能源在第t步的出力功率总和
            S_e_t = 0  # 电储能设备在第t步的剩余容量
            S_th_t = 0  # 热储能设备在第t步的剩余容量
            S_c_t = 0  # 冷储能设备在第t步的剩余容量
            current_e_price = 0  # 第t步的电价
            current_g_price = 0  # 第t步的天然气价格
            current_t = self.step_time / self.step_all  # 处理后的值在0到1之间
            for MG in self.env.MG:
                for node in MG.node:
                    for device in node.devices:
                        if device.className == 'D' and device.type == 'e' and device.name != 'load_e_ex':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_e_total_t = demand_e_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'th':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_th_total_t = demand_th_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'c':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_c_total_t = demand_c_total_t + D_norma_P1
                        elif device.className == 'D' and device.type == 'g':
                            # D_P = device.stochas_P[self.step_time - 1]  # 获取该负荷设备在t=1时刻的功率需求
                            # D_P = device.p[self.step_time - 1]
                            D_P = device.real_x[self.step_time - 1]
                            D_P_min = device.p_min.min()
                            D_P_max = device.p_max.max()
                            D_norma_P1 = (D_P - D_P_min) / (D_P_max - D_P_min)  # 归一化
                            demand_g_total_t = demand_g_total_t + D_norma_P1
                        elif device.className == 'RT' and device.type != 'HP':
                            # RT_P1 = device.stochas_P[self.step_time - 1]
                            # RT_P1 = device.p[self.step_time - 1]
                            # RT_P1 = device.real_x[self.step_time - 1]
                            RT_P1 = device.p_max[self.step_time - 1]
                            RT_P_min = device.p_min.min()
                            if RT_P_min < 0:
                                RT_P_min = 0
                            RT_P_max = device.p_max.max()
                            RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                            RT_P_total_t = RT_P_total_t + RT_norma_P1
                        elif device.className == 'RT' and device.type == 'HP':
                            # RT_P1 = device.p[self.step_time - 1]
                            RT_P1 = device.p_max[self.step_time - 1]
                            RT_P_min = device.p_min.min()
                            if RT_P_min < 0:
                                RT_P_min = 0
                            RT_P_max = device.p_max.max()
                            RT_norma_P1 = (RT_P1 - RT_P_min) / (RT_P_max - RT_P_min)  # 归一化
                            RT_P_total_t = RT_P_total_t + RT_norma_P1
                        elif device.className == 'S' and device.type == 'e':
                            E_e = device.real_E[self.step_time - 2]
                            norma_E_e = E_e / device.storage_limit  # 归一化，处理后的值在0到1之间
                            S_e_t = S_e_t + norma_E_e
                        elif device.className == 'S' and device.type == 'th':
                            E_th = device.real_E[self.step_time - 2]
                            norma_E_th = E_th / device.storage_limit  # 归一化
                            S_th_t = S_th_t + norma_E_th
                        elif device.className == 'S' and device.type == 'c':
                            E_c = device.real_E[self.step_time - 2]
                            norma_E_c = E_c / device.storage_limit  # 归一化
                            S_c_t = S_c_t + norma_E_c
                        elif device.className == 'CPP':
                            current_e_price = device.production_price[self.step_time - 1]
                        elif device.className == 'GW':
                            current_g_price = device.production_price[self.step_time - 1]
            # 状态：    当前时间t     电价               天然气价格       电能需求               热能需求            冷能需求         天然气需求      可再生能源总出力 电储容量 热储容量 冷储容量
            state = [current_t, current_e_price, current_g_price, demand_e_total_t, demand_th_total_t,
                     demand_c_total_t, demand_g_total_t, RT_P_total_t, S_e_t, S_th_t, S_c_t]

        if self.step_time == 25:
            # 将t=1的state作为t=25的state
            # t=1的state在上一级函数可以获取
            state = None
        self.step_time -= 1  #######################################################################################

        # 计算奖励
        reward, es_punishment, gap_punishment = self.__count_reward()
        if es_punishment == 0:
            reward += 100
        print("-------------es_punishment:", es_punishment)
        # reward += 20
        # es_punishment +=es_punishment
        if self.step_time == self.step_all:
            # a, b, c, d, total_cost = self.env.countCost()
            # reward += 2000 - total_cost
            # reward = res.fun + es_punishment + gap_punishment
            done = True
            storage_punishment_buffer.add(es_punishment, gap_punishment, 0)
            # print("-------------gap_punishment:", gap_punishment)
            self.rl_res = res
        # 更新步长
        self.step_time += 1

        return state, reward, done, True, action_
