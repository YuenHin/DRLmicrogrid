import numpy as np
import pandas as pd
import pylab as p

from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText


class FL:
    def __init__(self, name, type, limit, time_num):
        self.className = "FL"

        self.way = 5

        self.name = name
        self.type = type
        self.time_num = time_num

        self.limit = limit

        # 最大响应功率
        self.fl_max = np.zeros(self.time_num)
        # 最小响应功率
        self.fl_min = np.zeros(self.time_num)

        # 灵活性需求
        self.p_max = p.zeros(self.time_num)
        self.p_rampingUp = np.zeros(self.time_num)
        self.p_rampingDown = np.zeros(self.time_num)

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
            # self.name + "S",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    # 01变量
    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        # for i in range(self.time_num):
        #     self.intergrality[i + self.time_num] = 1

    # 目标函数
    def __set_C(self):
        self.c = np.zeros(len(self.params))

        if self.type == "e":
            # 响应功率
            for i in range(self.time_num):
                # 柔性负荷作为灵活性供给的成本 自愿减碳收入
                self.c[i] = 0.03 - 0.035

        if self.type == "g":
            for i in range(self.time_num):
                # 柔性负荷作为灵活性供给的成本
                self.c[i] = 0.04 - 0.027

        if self.type == "th":
            for i in range(self.time_num):
                # 柔性负荷作为灵活性供给的成本
                self.c[i] = 0.035 - 0.029

    # 数据获取
    def __getData(self):

        if self.type == "e":
            dataset = pd.read_excel(r"./Data\uncertainty\load_e.xlsx")
            self.p = dataset['mu'].values
            series_array = pd.Series(self.p)
            self.p = series_array[~series_array.isna() & (series_array != '')].values

            self.p_rampingUp = self.p * 0.15
            self.p_rampingDown = self.p * 0.15

            self.fl_max = self.p * 0.1
            self.fl_min = self.p * 0.03

        if self.type == "g":
            dataset = pd.read_excel(r"./Data\uncertainty\load_g.xlsx")
            self.p = dataset['mu'].values
            series_array = pd.Series(self.p)
            self.p = series_array[~series_array.isna() & (series_array != '')].values

            self.p_rampingUp = self.p * 0.15
            self.p_rampingDown = self.p * 0.15

            self.fl_max = self.p * 0.1
            self.fl_min = self.p * 0.03

        if self.type == "th":
            dataset = pd.read_excel(r"./Data\uncertainty\load_h.xlsx")
            self.p = dataset['mu'].values
            series_array = pd.Series(self.p)
            self.p = series_array[~series_array.isna() & (series_array != '')].values

            self.p_rampingUp = self.p * 0.15
            self.p_rampingDown = self.p * 0.15

            self.fl_max = self.p * 0.1
            self.fl_min = self.p * 0.03

        for i in range(self.time_num):
            if self.type == "e" and self.fl_max[i] == 0:
                self.fl_max[i] = self.p_rampingUp[i]
            if self.type == "g" and self.fl_max[i] == 0:
                self.fl_max[i] = self.p_rampingUp[i]
            if self.type == "th" and self.fl_max[i] == 0:
                self.fl_max[i] = self.p_rampingUp[i]


    def constraints(self, num):

        """响应功率上下限约束"""
        for i in range(self.time_num):
            B = np.array([
                [self.name + "RP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.fl_min[i], self.fl_max[i], num)

        # """爬坡滑坡功率约束"""
        # for i in range(self.time_num - 1):
        #     B = np.array([
        #         [self.name + "RP" + str(i + 2), 1],
        #         [self.name + "RP" + str(i + 1), -1],
        #         [self.name + "S" + str(i + 2), -self.p_rampingUp[i]]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, 0, num)
        #     B = np.array([
        #         [self.name + "RP" + str(i + 2), -1],
        #         [self.name + "RP" + str(i + 1), 1],
        #         [self.name + "S" + str(i + 2), -self.p_rampingDown[i]]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, 0, num)

        # """状态约束"""
        # B = np.array([
        #     [self.name + "S1", 1]
        # ])
        # CreatConstraintsByText(self.time_num, B, 1, 1, num)

    def remember_realValue(self, step, num):
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "RP" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)