import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawStorage import drawStorage
"""
1.充电折损
2.存电折损
3.放电折损
4.运维成本
5.存储成本
"""
class S:
    def __init__(self, name, type, id, storage_price, storage_limit, lifetimes, self_discharging, charging_rate, discharging_date, time_num, begin = None):
        self.name = name
        "string"
        self.id = id
        "int"
        self.type = type
        "e、h、g"
        self.className = 'S'
        self.time_num = time_num
        "hours"

        self.way = -1

        self.storage_price = storage_price
        "美元/kwh"
        self.storagr_limit = storage_limit
        if begin == None:
            self.begin = self.storagr_limit / 2
        else:
            self.begin = begin
        self.lifetimes = lifetimes
        "year"

        self.self_discharging = self_discharging
        "%/hours"

        self.e = 0
        self.charging_max = None
        self.discharging_max = None

        self.charging_rate = charging_rate
        self.discharging_rate = discharging_date

        self.params = np.array([""])

        "4"
        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraints_num = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
            self.name + "E", #储能单元当前的储量
            self.name + "CP", #充电功率
            self.name + "DP", #放电功率
            self.name + "S", #充放电状态，等于0或1
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.ones(len(self.params))
        for i in range( self.time_num * 4):
            self.intergrality[i] = 0

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        for i in range(self.time_num):
            # self.c[i + self.time_num * 4] = -self.storage_price / (self.lifetimes * 365 * 24)
            self.c[i + self.time_num * 4] = 0
            self.c[i + self.time_num * 1] = -self.storage_price / (self.lifetimes * 365 * 24) * 0.2
            self.c[i + self.time_num * 2] = - 0.083 * 0.001 * 390.885
            self.c[i + self.time_num * 3] = - 0.083 * 0.001 * 390.885

    def __getData(self):
        self.e = self.e + self.storagr_limit
        self.charging_max = self.e * 0.025
        self.discharging_max = self.e * 0.025
        self.ramping_limit = self.e * 0.025

    def constraints(self, num):
        "Energy storaed limited"
        B = np.array([
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.e, num)

        "Charging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1],
                [self.name + "S" + str(i + 1), -self.charging_max]
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
                [self.name + "S" + str(i + 1), self.discharging_max]
            ])
            CreatConstraintsByText(1, B, 0, self.discharging_max, num)

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
        CreatConstraintsByText(1, B, self.begin, self.begin, num)

        B = np.array([
            [self.name + "E1", -1],
            [self.name + "E2", 1],
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)

        B = np.array([
            [self.name + "E1", 1],
            [self.name + "E2", -1],
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)

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
        # B = np.array([
        #     [self.name + "DP1", 1],
        # ])
        # CreatConstraintsByText(1, B, 200, np.inf, num)

    def draw(self):
        x = self.x[self.time_num:self.time_num*2]
        p = self.x[:self.time_num]
        drawStorage(x, p, self.name + "SE")

    def get_action(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        #self.real_x[step - 1] = np.maximum(np.minimum(self.x[self.time_num + step - 1], self.e), 0)
        # 我需要控制不确定变化后不会跳出范围
        self.real_x[self.time_num + step - 1] = self.x[self.time_num + step - 1]
        if self.type != 'h' and step != 92:
            B = np.array([
                [self.name + "E" + str(step), 1],
            ])
            CreatConstraintsByText(1, B, self.real_x[self.time_num +step - 1], self.real_x[self.time_num +step - 1], num)













