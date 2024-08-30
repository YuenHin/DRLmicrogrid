import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText


class FL:
    def __init__(self, name, type, fl_min, fl_max, time_num):
        self.className = "FL"

        self.way = 5

        self.name = name
        self.type = type
        self.time_num = time_num

        # 最大响应功率
        self.fl_max = fl_max
        # 最小响应功率
        self.fl_min = fl_min

        self.p_max = fl_max
        self.p_rampingUp = None
        self.p_rampingDown = None

        self.params = np.array([""])

        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    # 决策变量
    def __params_named(self):
        temp = np.array([
            # 响应功率
            self.name + "RP",
            # 响应状态
            self.name + "S",
            # 向上灵活性供给
            self.name + "US",
            # 向下灵活性供给
            self.name + "DS"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    # 01变量
    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i + self.time_num] = 1

    # 目标函数
    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.c[i] = -0.02 + 0.303
        for i in range(self.time_num*2, self.time_num*4):
            self.c[i] = -0.00385

    # 数据获取
    def __getData(self):
        self.p_rampingUp = self.p_max * 0.15
        self.p_rampingDown = self.p_max * 0.15

    def constraints(self, num):
        # 最大最小约束
        B = np.array([
            [self.name + "RP1", 1],
            [self.name + "US1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, self.fl_min, self.fl_max, num)
        B = np.array([
            [self.name + "RP1", 1],
            [self.name + "DS1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, self.fl_min, self.fl_max, num)

        # 爬坡滑坡功率
        B = np.array([
            [self.name + "RP2", 1],
            [self.name + "RP1", -1],
            [self.name + "S2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num-1, B, -np.inf, 0, num)
        B = np.array([
            [self.name + "RP2", -1],
            [self.name + "RP1", 1],
            [self.name + "S2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num-1, B, -np.inf, 0, num)
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 1, 1, num)

    def draw(self):
        x = self.x[:self.time_num]
        p = self.x[:self.time_num]
