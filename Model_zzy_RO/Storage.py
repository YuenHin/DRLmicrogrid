import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawStorage import drawStorage

"""储能装置"""
class ES:
    def __init__(self, name, type, id, storage_price, storage_limit, storage_limit_min, lifetimes, self_discharging,
                 charging_rate, discharging_rate, time_num, begin=None):
        self.end_location_bl = None
        self.begin_location_bl = None
        self.first_location_bl = None
        self.first_location = None
        self.begin_location = None
        self.end_location = None
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

        self.e = 0
        self.charging_max = None
        self.discharging_max = None

        # 充电效率
        self.charging_rate = charging_rate
        # 放电效率
        self.discharging_rate = discharging_rate

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
                self.c[i + self.time_num * 2] = 0.043 + 0.008 - 0.0035
                self.c[i + self.time_num * 3] = 0.043 + 0.008 - 0.0035
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
                self.c[i + self.time_num * 9] = self.storage_limit * 0.0005

        if self.type == "th":
            for i in range(self.time_num):
                # 运维成本和调节成本
                self.c[i + self.time_num * 2] = 0.056 + 0.015 - 0.0025
                self.c[i + self.time_num * 3] = 0.056 + 0.015 - 0.0025
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
                self.c[i + self.time_num * 9] = self.storage_limit * 0.0007

        if self.type == "c":
            for i in range(self.time_num):
                # 运行功率
                self.c[i + self.time_num * 2] = 0.06 + 0.012 - 0.0025
                self.c[i + self.time_num * 3] = 0.06 + 0.012 - 0.0025
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
                self.c[i + self.time_num * 9] = self.storage_limit * 0.0008

    def __getData(self):
        self.e = self.e + self.storage_limit
        self.charging_max = self.e * 0.065
        self.discharging_max = self.e * 0.065
        self.ramping_limit = self.e * 0.055

    def constraints(self, num):
        # 起始位置
        self.begin_location = len(num.A)
        self.begin_location_bl = len(num.bl)

        "Energy storaed limited"
        B = np.array([
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(1, B, 0, self.e, num)

        "Charging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1],
                # [self.name + "S" + str(i + 1), -self.charging_max]  # 强化学习，放开充放电约束
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
                # [self.name + "S" + str(i + 1), self.discharging_max]  # 强化学习，放开充放电约束
                [self.name + "S" + str(i + 1), self.e]
            ])
            # CreatConstraintsByText(1, B, 0, self.discharging_max, num)  # 强化学习，放开充放电约束
            CreatConstraintsByText(1, B, 0, self.e, num)

        self.first_location = len(num.A)
        self.first_location_bl = len(num.bl)

        "Charging Flexible Analysis"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_us" + str(i+1), 1]
            ])
            # CreatConstraintsByText(1, B, 0, self.charging_max, num)  # 强化学习，放开约束
            CreatConstraintsByText(1, B, 0, self.e, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_ds" + str(i+1), -1]
            ])
            # CreatConstraintsByText(1, B, -self.charging_max, self.charging_max, num)  # 强化学习，放开约束
            CreatConstraintsByText(1, B, -self.e, self.e, num)

        "Discharging Flexible Analysis"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_us" + str(i+1), 1]
            ])
            # CreatConstraintsByText(1, B, 0, self.discharging_max, num)  # 强化学习，放开约束
            CreatConstraintsByText(1, B, 0, self.e, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_ds" + str(i+1), -1]
            ])
            # CreatConstraintsByText(1, B, -self.discharging_max, self.discharging_max, num)  # 强化学习，放开约束
            CreatConstraintsByText(1, B, -self.e, self.e, num)

        "Flexible Constraints"
        "充电"
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "ch_us" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), -self.ramping_limit]  # 强化学习，放开约束
                # [self.name + "S" + str(i + 2), -self.e]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "ch_ds" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), -self.ramping_limit]  # 强化学习，放开约束
                # [self.name + "S" + str(i + 2), -self.e]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        B = np.array([
            [self.name + "ch_us24", 1],
            [self.name + "S24", -self.ramping_limit]  # 强化学习，放开约束
            # [self.name + "S24", -self.e]
        ])
        CreatConstraintsByText(1, B, -np.inf, 0, num)
        B = np.array([
            [self.name + "ch_ds24", 1],
            [self.name + "S24", -self.ramping_limit]  # 强化学习，放开约束
            # [self.name + "S24", -self.e]
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
                [self.name + "S" + str(i + 2), self.ramping_limit]  # 强化学习，放开约束
                # [self.name + "S" + str(i + 2), self.e]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
            # CreatConstraintsByText(1, B, -np.inf, self.e, num)

        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "dis_ds" + str(i + 1), 1],
                [self.name + "S" + str(i + 2), self.ramping_limit]  # 强化学习，放开约束
                # [self.name + "S" + str(i + 2), self.e]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
            # CreatConstraintsByText(1, B, -np.inf, self.e, num)

        B = np.array([
            [self.name + "dis_us24", 1],
            [self.name + "S24", self.ramping_limit]  # 强化学习，放开约束
            # [self.name + "S24", self.e]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
        # CreatConstraintsByText(1, B, -np.inf, self.e, num)
        B = np.array([
            [self.name + "dis_ds24", 1],
            [self.name + "S24", self.ramping_limit]  # 强化学习，放开约束
            # [self.name + "S24", self.e]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
        # CreatConstraintsByText(1, B, -np.inf, self.ramping_limit, num)

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
        CreatConstraintsByText(1, B, 0, np.inf, num)

        B = np.array([
            [self.name + "E1", -1],
            [self.name + "E2", 1],
        ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.e, num)

        B = np.array([
            [self.name + "E1", 1],
            [self.name + "E2", -1],
        ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)  # 强化学习，放开约束
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.e, num)

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


        # 起始位置
        self.end_location = len(num.A)
        self.end_location_bl = len(num.bl)

    def draw(self):
        x = self.x[self.time_num:self.time_num * 2]
        p = self.x[:self.time_num]
        drawStorage(x, p, self.name + self.type)

    def get_action(self, step, num, action, cur_episode):
        action_ = action
        if step == 1:
            self.real_x[self.time_num + step - 1] = self.begin + action * self.ramping_limit
        else:
            self.real_x[self.time_num + step - 1] = self.real_x[self.time_num + step - 2] + action * self.ramping_limit

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











