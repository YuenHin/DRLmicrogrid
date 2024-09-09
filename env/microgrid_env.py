from tools.Logic import MMGs_logic, x_callBack, draw, save_data
from tools.MILP import EndCount, PrintBounds
import numpy as np
import time
import os
from copy import deepcopy
class microgrid_env:
    def __init__(self, MMGs, step_all):
        self.start_time = time.time()
        self.step_all = step_all
        #初始化
        self.con_add_num = 12 #这是？
        self.env = MMGs
        self.save_name = "microgrid"
        self.C, self.intergrality, self.start_num = MMGs_logic(self.env, self.save_name)
        self.flash_num = deepcopy(self.start_num)
        # self.start_num_ =self.start_num
        # self.flash_num = self.start_num_
        # for i in range(len(self.flash_num.params)):
        #     print(self.flash_num.params[i], "   :", np.round(self.C[i], 5))
        # print(self.flash_num.params)
        # PrintBounds(self.flash_num)
        self.observation_space = self.start_num.params
        self.action_space = np.array([1])

        #第一次执行全流程Perfect_MILP程序
        res = EndCount(-self.C, self.intergrality, self.flash_num)
        # PrintBounds(self.flash_num)
        # self.flash_num.bu[0] = 170
        # self.flash_num.bl[0] = 165
        # res = EndCount(-self.C, self.intergrality, self.flash_num)
        PrintBounds(self.flash_num)
        os.system("pause")
        self.res = res
        self.x = res.x
        # 第一次数据记录
        self.step_time = 1
        x_callBack(res, self.env, self.save_name, flag=False)
        # 初始化结束之后，每一个设备在预测值下的运行数据都已经获得了；下面需要对数据进行第一轮处理
        print("初始化用时：", time.time() - self.start_time)
        self.last_time = time.time()

    def reset(self):
        self.flash_num = deepcopy(self.start_num) #深拷贝
        self.step_time = 1
        self.x = self.res.x
        return self.x

    # 一级设备：不确定性数据载入一级设备（RE、D）
    def __stochastic_factor_setting_RED(self):
        # 1.先找到每一个RE、D
        # 2.执行每一个(RE、D)的随机函数，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "RT" or (device.className == "D" and (
                            device.type == "e" or device.type == "g" or device.type == "th" or device.type == "h")):
                        device.stochastic(self.step_time, self.flash_num)

    # 二级设备：储能+DG
    def __get_action_SE(self, action):
        # 1.先找到每一个SE
        # 2.执行每一个SE的执行动作，并附加约束
        done = False
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S" and device.type == "e":
                        done = device.get_action(self.step_time, self.flash_num, action)
                        return done
        return done

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

    # 测试用，储能S不通过智能体选择动作，而是直接拿MILP的求解结果
    def __remember_S(self):
        # 1.先找到每一个储能设备
        # 2.记录储能设备的动作，并附加约束
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "S" and device.type == "e":
                        device.remenber_realValue(self.step_time, self.flash_num)

    #调试设备
    def __re_train(self):
        # 1.先找到每一个RE、D
        # 2.执行每一个RE、D的调试备用函数
        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    if device.className == "RT" or (device.className == "D" and (device.type == "e" or device.type == "g" or device.type == "th" or device.type == "h")):
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

        for MG in self.env.MG:
            for node in MG.node:
                for device in node.devices:
                    # pp生产成本 pp是什么
                    if device.className == "CPP":
                        operation_cost += device.x[self.step_time - 1] * device.production_price[self.step_time - 1] * (24 / device.time_num)
                        carbon_emission += device.x[device.time_num + self.step_time - 1] * 0.839 * (24 / device.time_num)
                        profit += device.x[device.time_num * 2 + self.step_time - 1] * 0.315 * (24 / device.time_num)

                    # gw生产成本
                    if device.className == "GW":
                        operation_cost += device.x[self.step_time - 1] * device.production_price * (
                                    24 / device.time_num)
                        carbon_emission += device.x[self.step_time - 1] * 0.368 * (24 / device.time_num)
                    # pv生产成本
                    # wt生产成本
                    if device.className == "RT":
                        operation_cost += device.x[self.step_time - 1] * device.production_price * (
                                    24 / device.time_num)
                        carbon_emission += device.x[self.step_time - 1] * 0.09 * (24 / device.time_num)
                    # dg生产成本
                    if device.className == "DG":
                        operation_cost += device.x[self.step_time - 1] * device.production_price * (
                                    24 / device.time_num)
                        carbon_emission += device.x[self.step_time - 1] * 0.839 * (24 / device.time_num)
                    # 储能碳排放
                    if device.className == "S":
                        carbon_emission += device.x[device.time_num * 2 + self.step_time - 1] * 0.083 * (
                                    24 / device.time_num)
                        carbon_emission += device.x[device.time_num * 3 + self.step_time - 1] * 0.083 * (
                                    24 / device.time_num)
                    # tp碳排放
                    if device.className == "TP":
                        carbon_emission += device.x[self.step_time - 1] * 0.12 * (24 / device.time_num)
                    # ctp碳排放
                    if device.className == "CTP":
                        carbon_emission += device.x[self.step_time - 1] * 0.181 * (24 / device.time_num)

        carbon_emission = carbon_emission * 0.001
        carbom_emission_cost = carbon_emission * 390.885
        reward = -(operation_cost + carbom_emission_cost - profit)

        return reward

    # 三级设备：DG、CPP、GW、EC 我这里的动作、名称和状态应该是一个数组（多个智能体）
    # 先使用单智能体控制SE_e试试
    def step(self, action):
        # 增加随机变量
        self.__stochastic_factor_setting_RED()
        # 获得动作
        # done = self.__get_action_SE(action)
        # if done == True:
        #     return self.x, np.array([0]), True, None
        # self.__get_action_SE_nocontrol()

        # PrintBounds(self.flash_num)
        # for i in range(len(self.flash_num.params)):
        #     print(self.flash_num.params[i], "   :", np.round(self.C[i], 5))
        # print(self.flash_num.params)
        # PrintBounds(self.flash_num)
        # 计算该环境下的真实控制值
        res = EndCount(-self.C, self.intergrality, self.flash_num)
        flag = 0
        done = False
        while res.success == False:
            PrintBounds(self.flash_num)
            print("无解！！！！！！flag=",flag)
            done = True
            os.system("pause")
            self.__de_constrains()
            res = EndCount(-self.C, self.intergrality, self.flash_num)
            flag = flag + 1
            print("删一个")
            if res.success == True:
                 print("有解了，flag=",flag)
                 os.system("pause")


        # if res.success == True:
        #     print("flag=",flag)
        #     print("step=",self.step_time)
        #     os.system("pause")
        # else:

        # if self.step_time == 10:
        #     PrintBounds(self.flash_num)
        #     os.system("pause")

        done = False
        self.__remember_S()
        self.__get_action_SE_nocontrol()


        """
            flag = 0
                while res.success == False:
            # os.system("pause")
            print("第", self.step_time, "步出错了，调试中....")
            self.__re_train()
            res = EndCount(-self.C, self.intergrality, self.flash_num)
            # PrintBounds(self.flash_num)
            if flag > 1:
                # 删除一个约束
                # print("嘿嘿嘿，删一个")
                self.__de_constrains()
                if flag > 1 + self.con_add_num:
                    for i in range(len(self.flash_num.params)):
                        print(self.flash_num.params[i], "   :", np.round(self.C[i], 5))
                    print(self.flash_num.params)
                    # PrintBounds(self.flash_num)
                    break
            flag += 1
            # os.system("pause")
        """

        # while res.success == False:
        #     print("第", self.step_time, "步无解，重新选动作中....(第", flag+1, "次重选....")
        #     #首先需要删除这个step中选择储能动作后所添加的储能的约束
        #
        #     #获得储能的动作并添加相应约束
        #     done = self.__get_action_SE(action)

        x_callBack(res, self.env, self.save_name, flag=False)
        self.x = res.x
        # 记录三级设备的真实控制状态
        self.__remenber_CPPGWECDG()

        if self.step_time == 24:
            PrintBounds(self.flash_num)
            os.system("pause")

        # 计算奖励
        reward = 20 + self.__count_reward()
        if self.step_time == self.step_all:
            a, b, c, d, total_cost = self.env.countCost()
            reward += 2000 - total_cost
            done = True
        # 更新步长
        self.step_time += 1

        return res.x, np.array([reward[0]]), done, None


























