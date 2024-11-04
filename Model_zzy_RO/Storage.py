import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawStorage import drawStorage

"""储能装置"""
class ES:
    def __init__(self, name, type, id, storage_price, storage_limit, storage_limit_min, lifetimes, self_discharging,
                 charging_rate, discharging_rate, time_num, begin=None):

        self.className = 'S'
        self.name = name
        "string"
        self.id = id
        "int"
        self.time_num = time_num
        "hours"

        # 能源类型
        self.type = type
        "e, h, c"

        self.way = 4

        self.storage_price = storage_price
        "美元/kwh"
        self.storage_limit = storage_limit
        self.storage_limit_min = storage_limit_min
        if begin == None:
            self.begin = self.storage_limit / 2
        else:
            self.begin = begin
        self.lifetimes = lifetimes
        "year"

        # 自损率
        self.self_discharging = self_discharging
        "%/hours"

        self.e = self.storage_limit
        self.charging_max = None
        self.discharging_max = None

        # 充电效率
        self.charging_rate = charging_rate
        # 放电效率
        self.discharging_rate = discharging_rate

        # 葱一样的柱子搞成一个ramping
        # 需要一个人random
        self.randoms_ch_us = np.array([0.24851727, 0.03739422, -0.09191158, 0.00893554, -0.29600178, 0.0596546,
                                       -0.22886036, 0.01212567, 0.128045, 0.11692753, -0.04133845, -0.11306276,
                                       0.28413274, -0.12880762, -0.26353677, 0.27066543, 0.15701774, 0.18188486,
                                       0.09516315, 0.01044985, -0.13600274, 0.22347429, 0.00928955, -0.13478322])
        self.randoms_ch_ds = np.array([-0.2316746,  -0.171143,   -0.13346602,  0.09881519, -0.07429107, -0.27868075,
                                       -0.10334106,  0.22687573, -0.23047181,  0.15514376,  0.11487653,  0.15455269,
                                       0.06842947, -0.12176454,  0.27524408,  0.25005093, -0.06035696, -0.27607277,
                                       -0.0027325,  -0.12132561,  0.0417038,   0.17613344, -0.02879777, -0.10891241])
        self.randoms_dis_us = np.array([0.13106457, -0.22243633, -0.18905384,  0.10561013,  0.01943447, -0.2621602,
                                        -0.08631154,  0.00847533,  0.23719053,  0.21944282,  0.06451267,  0.1198098,
                                        0.21208015, -0.27660178, -0.01655773, 0.20274194, -0.09415135,  0.24744209,
                                        0.11152833, -0.08412433,  0.10216065, -0.05073274,  0.28595126, -0.18825898])
        self.randoms_dis_ds = np.array([0.05828629,  0.23471519, -0.25958544, -0.1079146,  -0.0048018,  -0.23394671,
                                        0.02820027, -0.10859014,  0.14840945,  0.01650291,  0.22561462,  0.24100637,
                                        0.15958893, -0.07053523,  0.26013171,  0.27469844, -0.20316884,  0.22391081,
                                        0.28548823, -0.29475551,  0.1447116,  -0.06451897, -0.20676269, -0.10050451])

        self.params = np.array([""])

        "4"
        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraints_num = 0

        self.real_E = np.zeros(self.time_num)  # 记录执行每一步动作后的储能容量

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",  # 当前功率
            self.name + "E",  # 储能单元当前的储量
            self.name + "CP",  # 充电功率
            self.name + "DP",  # 放电功率
            self.name + "S",  # 充电状态，等于0或1
            self.name + "ch_us",
            self.name + "ch_ds",
            self.name + "dis_us",  # 储电装置放电的向上灵活性供给能力
            self.name + "dis_ds",  # 储电装置放电的向下灵活性供给能力
            self.name + "state"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i + self.time_num * 4] = 1
            self.intergrality[i + self.time_num * 9] = 1

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        if self.type == "e":
            for i in range(self.time_num):
                # 运维成本和调节成本
                self.c[i + self.time_num * 2] = 0.023 - 0.0035
                self.c[i + self.time_num * 3] = 0.023 - 0.0035
                # 灵活供给&缺额惩罚
                self.c[i + self.time_num * 5] = 0.009
                self.c[i + self.time_num * 6] = 0.009
                self.c[i + self.time_num * 7] = 0.009
                self.c[i + self.time_num * 8] = 0.009
                # self.c[i + self.time_num * 5] = 0.029
                # self.c[i + self.time_num * 6] = 0.029
                # self.c[i + self.time_num * 7] = 0.029
                # self.c[i + self.time_num * 8] = 0.029
                # 运行损耗
                self.c[i + self.time_num * 9] = self.storage_limit * 0.005

        if self.type == "th":
            for i in range(self.time_num):
                # 运维成本和调节成本
                self.c[i + self.time_num * 2] = 0.036 - 0.0025
                self.c[i + self.time_num * 3] = 0.036 - 0.0025
                # 灵活供给
                self.c[i + self.time_num * 5] = 0.013
                self.c[i + self.time_num * 6] = 0.013
                self.c[i + self.time_num * 7] = 0.013
                self.c[i + self.time_num * 8] = 0.013
                # self.c[i + self.time_num * 5] = 0.024
                # self.c[i + self.time_num * 6] = 0.024
                # self.c[i + self.time_num * 7] = 0.024
                # self.c[i + self.time_num * 8] = 0.024
                # 运维损耗
                self.c[i + self.time_num * 9] = self.storage_limit * 0.007

        if self.type == "c":
            for i in range(self.time_num):
                # 运行功率
                self.c[i + self.time_num * 2] = 0.04 - 0.0025
                self.c[i + self.time_num * 3] = 0.04 - 0.0025
                # 灵活供给
                self.c[i + self.time_num * 5] = 0.015
                self.c[i + self.time_num * 6] = 0.015
                self.c[i + self.time_num * 7] = 0.015
                self.c[i + self.time_num * 8] = 0.015
                # self.c[i + self.time_num * 5] = 0.022
                # self.c[i + self.time_num * 6] = 0.022
                # self.c[i + self.time_num * 7] = 0.022
                # self.c[i + self.time_num * 8] = 0.022
                # 运维损耗
                self.c[i + self.time_num * 9] = self.storage_limit * 0.008

    def __getData(self):
        # self.e = self.e + self.storage_limit
        self.charging_max = self.e * 0.0623345
        self.discharging_max = self.e * 0.0634637
        self.ramping_limit = self.e * 0.06234

        self.max = self.e * 0.3931231

    def constraints(self, num):

        "Energy storaed limited"
        B = np.array([
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.e, num)
        '''
        "初始约束"
        B = np.array([
            [self.name + "P1", 1]
        ])
        CreatConstraintsByText(1, B, -self.ramping_limit, self.ramping_limit, num)
        '''
        "充放电最大约束"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "P" + str(i + 1), 1]
            ])
            # CreatConstraintsByText(1, B, -self.max, self.max, num)
            CreatConstraintsByText(1, B, -self.e, self.e, num)

        #########################################################

        "Charging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1],
                [self.name + "S" + str(i + 1), -self.e]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        "Discharging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i + 1), 1],
                [self.name + "S" + str(i + 1), self.e]
            ])
            CreatConstraintsByText(1, B, 0, self.e, num)

        #################################################################

        "ramping limits"
        for i in range(self.time_num-1):
            B = np.array([
                [self.name + "CP" + str(i + 1), -1],
                [self.name + "CP" + str(i + 2), 1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.charging_max, num)

        for i in range(self.time_num-1):
            B = np.array([
                [self.name + "DP" + str(i + 1), -1],
                [self.name + "DP" + str(i + 2), 1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.discharging_max, num)

        #############################################################################

        "Charging Flexible Analysis"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_us" + str(i+1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.e, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_ds" + str(i+1), -1]
            ])
            CreatConstraintsByText(1, B, -self.e, self.e, num)

        "Discharging Flexible Analysis"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_us" + str(i+1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.e, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_ds" + str(i+1), -1]
            ])
            CreatConstraintsByText(1, B, -self.e, self.e, num)

##############################################################################################

        "Flexible Constraints"
        "充电"
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "ch_us" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), -self.ramping_limit * (1 + self.randoms_ch_us[i])]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "ch_ds" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), -self.ramping_limit * (1 + self.randoms_ch_ds[i])]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        B = np.array([
            [self.name + "ch_us24", 1],
            [self.name + "S24", -self.ramping_limit * (1 + self.randoms_ch_us[23])]
        ])
        CreatConstraintsByText(1, B, -np.inf, 0, num)
        B = np.array([
            [self.name + "ch_ds24", 1],
            [self.name + "S24", -self.ramping_limit * (1 + self.randoms_ch_ds[23])]
        ])
        CreatConstraintsByText(1, B, -np.inf, 0, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "ch_us" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "ch_ds" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        "放电"
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "dis_us" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), self.ramping_limit * (1 + self.randoms_dis_us[i])]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.ramping_limit*(1 + self.randoms_dis_us[i]), num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "dis_ds" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), self.ramping_limit * (1 + self.randoms_dis_ds[i])]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.ramping_limit*(1 + self.randoms_dis_ds[i]), num)

        B = np.array([
            [self.name + "dis_us24", 1],
            [self.name + "S24", self.ramping_limit * (1 + self.randoms_dis_us[23])]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.ramping_limit*(1 + self.randoms_dis_us[23]), num)
        B = np.array([
            [self.name + "dis_ds24", 1],
            [self.name + "S24", self.ramping_limit * (1 + self.randoms_dis_ds[23])]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.ramping_limit*(1 + self.randoms_dis_ds[23]), num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "dis_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "dis_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

########################################################################################################

        "Energy balance in the storage unit"
        B = np.array([
            [self.name + "E1", 1],
            [self.name + "CP1", -self.charging_rate],
            [self.name + "DP1", 1 / self.charging_rate]
        ])
        CreatConstraintsByText(1, B, self.begin, self.begin, num)
        B = np.array([
            [self.name + "E2", 1],
            [self.name + "E1", -(1 - self.self_discharging)],
            [self.name + "CP2", -self.charging_rate],
            [self.name + "DP2", 1 / self.charging_rate]
        ])
        CreatConstraintsByText(self.time_num - 1, B, 0, 0, num)
        B = np.array([
            [self.name + "E" + str(self.time_num), 1]
        ])
        # CreatConstraintsByText(1, B, self.begin, self.begin, num)  # 强化学习，放开约束
        # CreatConstraintsByText(1, B, self.begin, np.inf, num)
        CreatConstraintsByText(1, B, 0, self.e, num)

        # B = np.array([
        #     [self.name + "E1", -1],
        #     [self.name + "E2", 1],
        # ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)
        #
        # B = np.array([
        #     [self.name + "E1", 1],
        #     [self.name + "E2", -1],
        # ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)

        "State"
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)

        "P = cP + dp"
        B = np.array([
            [self.name + "P1", 1],
            [self.name + "CP1", -1],
            [self.name + "DP1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        "储能充放能转换"
        B = np.array([
            [self.name + "state1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)

        B = np.array([
            [self.name + "state1", 1]
        ])
        CreatConstraintsByText(1, B, 0, 0, num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "state" + str(i + 2), 1],
                [self.name + "S" + str(i + 2), -1],
                [self.name + "S" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "state" + str(i + 2), 1],
                [self.name + "S" + str(i + 2), 1],
                [self.name + "S" + str(i + 1), -1],
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

    def draw(self):
        x = self.x[self.time_num:self.time_num * 2]
        p = self.x[:self.time_num]
        drawStorage(x, p, self.name + self.type)

    def get_action(self, step, num, action, cur_episode):
        action_ = action
        if step == 1:
            # self.real_x[self.time_num + step - 1] = self.begin + action * self.ramping_limit
            # self.real_x[self.time_num + step - 1] = self.begin + action * 90
            if action >= 0:
                self.real_x[self.time_num + step - 1] = self.begin + 1 * self.ramping_limit
            else:
                self.real_x[self.time_num + step - 1] = self.begin + 1 * self.ramping_limit
        else:
            # self.real_x[self.time_num + step - 1] = self.real_x[self.time_num + step - 2] + action * self.ramping_limit
            # self.real_x[self.time_num + step - 1] = self.real_x[self.time_num + step - 2] + action * 90
            if action >= 0:
                self.real_x[self.time_num + step - 1] = self.real_x[self.time_num + step - 2] + 1 * self.ramping_limit
            else:
                self.real_x[self.time_num + step - 1] = self.real_x[self.time_num + step - 2] + 1 * self.ramping_limit

        # if self.real_x[self.time_num + step - 1] > self.e or self.real_x[self.time_num + step - 1] < 0:
        #     return True, action_

        if self.real_x[self.time_num + step - 1] > self.e:
            self.real_x[self.time_num + step - 1] = self.e
        if self.real_x[self.time_num + step - 1] < 0:
            self.real_x[self.time_num + step - 1] = 0

        B = np.array([
            [self.name + "E" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[self.time_num + step - 1], self.real_x[self.time_num + step - 1], num)

        self.real_E[step - 1] = self.real_x[self.time_num + step - 1]  # 记录执行这一步的action后的储能容量，之后用于添加到state中

        return False, action_

        # self.real_x[self.time_num + step - 1] = self.x[self.time_num + step - 1]
        # if self.type != 'h' and step != 92:
        #     B = np.array([
        #         [self.name + "E" + str(step), 1],
        #     ])
        #     CreatConstraintsByText(1, B, self.real_x[self.time_num + step - 1], self.real_x[self.time_num + step - 1],
        #                            num)

    def remember_realValue(self, step, num):
        # 我需要控制不确定变化后不会跳出范围
        self.real_x[self.time_num + step - 1] = self.x[self.time_num + step - 1]
        self.real_E[step - 1] = self.real_x[self.time_num + step - 1]

        B = np.array([
            [self.name + "E" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[self.time_num + step - 1], self.real_x[self.time_num + step - 1], num)


"""蓄热罐"""

"""蓄冷罐"""

# """新能源汽车"""
# class EV:
#     def __init__(self, name, id, storage_price, storage_limit_max, storage_limit_min, lifetimes, self_discharging,
#                  charging_rate, discharging_rate, time_num, begin=None):
#         self.name = name
#         "string"
#         self.id = id
#         "int"
#         self.time_num = time_num
#         "hours"
#
#         self.way = -1
#
#         self.storage_price = storage_price
#         "美元/kwh"
#         self.storage_limit_max = storage_limit_max
#         self.storage_limit_min = storage_limit_min
#         if begin == None:
#             self.begin = self.storage_limit_max / 2
#         else:
#             self.begin = begin
#         self.lifetimes = lifetimes
#         "year"
#
#         # 自损率
#         self.self_discharging = self_discharging
#         "%/hours"
#
#         self.e = 0
#         self.charging_max = None
#         self.discharging_max = None
#
#         # 充电效率
#         self.charging_rate = charging_rate
#         # 放电效率
#         self.discharging_rate = discharging_rate
#
#         # 最低出行需求
#         self.travel_demand_min = 25
#
#         self.params = np.array([""])
#
#         "4"
#         self.day = int(self.time_num / 24)
#
#         self.__init()
#
#         self.length = len(self.params)
#
#         self.x = np.zeros(self.length)
#         self.real_x = np.zeros(self.length)
#
#         self.constraints_num = 0
#
#     def __init(self):
#         self.__params_named()
#         self.__set_intergrality()
#         self.__set_C()
#         self.__getData()
#
#     def __params_named(self):
#         temp = np.array([
#             self.name + "P",  # 充电-放电
#             self.name + "E",  # 新能源汽车当前的储量
#             self.name + "CP",  # 充电功率
#             self.name + "DP",  # 放电功率
#             self.name + "S",  # 充放电状态，等于0或1
#             #  self.name + "TS"  出行状态
#         ])
#         self.params = AddParams(self.params, self.time_num, temp)
#         self.params = self.params[1:]
#
#     def __set_intergrality(self):
#         self.intergrality = np.ones(len(self.params))
#         for i in range(self.time_num * 4):
#             self.intergrality[i] = 0
#
#     def __set_C(self):
#         self.c = np.zeros(len(self.params))
#         "4"
#         for i in range(self.time_num):
#             # self.c[i + self.time_num * 4] = -self.storage_price / (self.lifetimes * 365 * 24)
#             self.c[i + self.time_num * 4] = 0
#             self.c[i + self.time_num * 1] = -self.storage_price / (self.lifetimes * 365 * 24) * 0.2
#             self.c[i + self.time_num * 2] = - 0.083 * 0.001 * 390.885
#             self.c[i + self.time_num * 3] = - 0.083 * 0.001 * 390.885
#
#     def __getData(self):
#         self.e = self.e + self.storage_limit_max
#         self.charging_max = self.e * 0.025
#         self.discharging_max = self.e * 0.025
#         self.ramping_limit = self.e * 0.025
#
#     def constraints(self, num):
#         "Energy storaed limited"
#         B = np.array([
#             [self.name + "E1", 1]
#         ])
#         CreatConstraintsByText(self.time_num, B, 0, self.e, num)
#
#         # 额定功率最大最小约束
#         B = np.array([
#             [self.name + "E1", 1]
#         ])
#         CreatConstraintsByText(self.time_num, B, self.storage_limit_min, self.storage_limit_max, num)
#
#         "Charging power limits:"
#         for i in range(self.time_num):
#             B = np.array([
#                 [self.name + "CP" + str(i + 1), 1]
#             ])
#             CreatConstraintsByText(1, B, 0, np.inf, num)
#
#         for i in range(self.time_num):
#             B = np.array([
#                 [self.name + "CP" + str(i + 1), 1],
#                 [self.name + "S" + str(i + 1), -self.charging_max]
#             ])
#             CreatConstraintsByText(1, B, -np.inf, 0, num)
#
#         "Discharging power limits:"
#         for i in range(self.time_num):
#             B = np.array([
#                 [self.name + "DP" + str(i + 1), 1]
#             ])
#             CreatConstraintsByText(1, B, 0, np.inf, num)
#         for i in range(self.time_num):
#             B = np.array([
#                 [self.name + "DP" + str(i + 1), 1],
#                 [self.name + "S" + str(i + 1), self.discharging_max]
#             ])
#             CreatConstraintsByText(1, B, 0, self.discharging_max, num)
#
#
#         "Energy balance in the storage unit"
#         B = np.array([
#             [self.name + "E1", 1],
#             [self.name + "CP1", -self.charging_rate],
#             [self.name + "DP1", 1 / self.charging_rate]
#         ])
#         CreatConstraintsByText(1, B, self.begin, self.begin, num)
#         B = np.array([
#             [self.name + "E2", 1],
#             [self.name + "E1", -(1 - self.self_discharging)],
#             [self.name + "CP2", -self.charging_rate],
#             [self.name + "DP2", 1 / self.charging_rate]
#         ])
#         CreatConstraintsByText(self.time_num - 1, B, 0, 0, num)
#         B = np.array([
#             [self.name + "E" + str(self.time_num), 1]
#         ])
#         CreatConstraintsByText(1, B, self.begin, self.begin, num)
#
#         B = np.array([
#             [self.name + "E1", -1],
#             [self.name + "E2", 1],
#         ])
#         CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)
#
#         B = np.array([
#             [self.name + "E1", 1],
#             [self.name + "E2", -1],
#         ])
#         CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)
#
#         "State"
#         B = np.array([
#             [self.name + "S1", 1]
#         ])
#         CreatConstraintsByText(self.time_num, B, 0, 1, num)
#
#         "P = cP - dp"
#         B = np.array([
#             [self.name + "P1", 1],
#             [self.name + "CP1", -1],
#             [self.name + "DP1", 1]
#         ])
#         CreatConstraintsByText(self.time_num, B, 0, 0, num)
#
#         "出行状态约束"
#         B = np.array([
#             [self.name + "E1", 1]
#         ])
#         CreatConstraintsByText(self.time_num, B, self.travel_demand_min, self.storage_limit_max, num)
#
#     def draw(self):
#         x = self.x[self.time_num:self.time_num * 2]
#         p = self.x[:self.time_num]
#         drawStorage(x, p, self.name + "SE" + self.type)
#
#     def get_action(self, step, num):
#         # 这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
#         # self.real_x[step - 1] = np.maximum(np.minimum(self.x[self.time_num + step - 1], self.e), 0)
#         # 我需要控制不确定变化后不会跳出范围
#         self.real_x[self.time_num + step - 1] = self.x[self.time_num + step - 1]
#         if self.type != 'h' and step != 92:
#             B = np.array([
#                 [self.name + "E" + str(step), 1],
#             ])
#             CreatConstraintsByText(1, B, self.real_x[self.time_num + step - 1], self.real_x[self.time_num + step - 1],
#                                    num)











