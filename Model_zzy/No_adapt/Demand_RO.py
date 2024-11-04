import numpy as np
import pandas as pd

from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawDemands import drawDemands
from tools.aDataSetting import smooth
import random

class D:
    def __init__(self, name, type, p_total, id, MG_id, ramping_rate, time_num, stochastic_value=10):
        self.name = name
        self.id = id
        self.MG_id = MG_id
        self.time_num = time_num

        self.type = type
        self.className = 'D'

        self.ramping_rate = ramping_rate
        self.reseach_day = 1

        self.p_total = p_total

        self.p = np.zeros(self.time_num)
        self.p_min = np.zeros(self.time_num)
        self.p_mu = np.zeros(self.time_num)
        self.p_max = np.zeros(self.time_num)

        self.randoms_e = np.array([0.11236204, 0.28521429, 0.21959818, 0.17959755, 0.04680559, 0.04679836,
                                    0.01742508, 0.25985284, 0.1803345,  0.21242177, 0.00617535, 0.29097296,
                                    0.24973279, 0.06370173, 0.05454749, 0.05502135, 0.09127267, 0.15742693,
                                    0.12958351, 0.08736874, 0.18355587, 0.04184816, 0.08764339, 0.10990855])
        self.randoms_g = np.array([0.21651324, 0.2913107,  0.12957349, 0.12455763, 0.00544368, 0.25198967,
                                    0.14901604, 0.04595882, 0.23330536, 0.094079,   0.06942008, 0.13112689,
                                    0.24014087, 0.14563949, 0.20326681, 0.06313587, 0.15087258, 0.27935159,
                                    0.22504639, 0.06087852, 0.01193102, 0.11714176, 0.04954388, 0.15724382])
        self.randoms_h = np.array([0.02782551, 0.09093528, 0.01193102, 0.06087852, 0.15724382, 0.04954388,
                                    0.11714176, 0.02782551, 0.09093528, 0.01193102, 0.06087852, 0.15724382,
                                    0.04954388, 0.11714176, 0.02782551, 0.09093528, 0.01193102, 0.06087852,
                                    0.15724382, 0.04954388, 0.11714176, 0.02782551, 0.09093528, 0.01193102])
        self.randoms_c = np.array([0.06087852, 0.15724382, 0.04954388, 0.11714176, 0.02782551, 0.09093528,
                                    0.01193102, 0.06087852, 0.15724382, 0.04954388, 0.11714176, 0.02782551,
                                    0.09093528, 0.01193102, 0.06087852, 0.15724382, 0.04954388, 0.11714176,
                                    0.02782551, 0.09093528, 0.01193102, 0.06087852, 0.15724382, 0.04954388])


        self.params = np.array([""])
        "1"

        "1"
        self.stage = 2
        self.way = -1
        "表示能源流向该设备"

        self.__init()

        self.x = np.zeros(self.length)

        self.real_x = np.zeros(self.length)

        self.stochastic_value = stochastic_value

        self.contraint_num = 0

        self.flexible_value = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C2()
        self.__getData2()

    def __params_named(self):
        temp = np.array([
            self.name + "P"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]
        self.length = len(self.params)

    def __set_intergrality(self):
        self.intergrality = np.zeros(self.time_num)



    def __set_C2(self):
        self.c = np.zeros(len(self.params))

        if self.type == "e":
            for i in range(self.time_num):
                self.c[i] = 0.01

        if self.type == "g":
            for i in range(self.time_num):
                self.c[i] = 0.02

        if self.type == "th":
            for i in range(self.time_num):
                self.c[i] = 0.01

        if self.type == "c":
            for i in range(self.time_num):
                self.c[i] = 0.01

        # if self.type == "e":
        #     for i in range(0, 7):  # 0点至7点
        #         self.c[i] = -0.5 * 0.5
        #     for i in range(7, 14):  # 8点至14点
        #         self.c[i] = -0.5 * 1.8
        #     for i in range(14, 17):  # 13点至17点
        #         self.c[i] = -0.5
        #     for i in range(17, 23):  # 18点至23点
        #         self.c[i] = -0.5 * 1.8
        #     self.c[23] = -0.5 * 0.5

        # if self.type == "g":
        #     for i in range(0, 7):  # 0点至7点
        #         self.c[i] = -0.5 * 0.9
        #     for i in range(7, 14):  # 8点至14点
        #         self.c[i] = -0.5 * 1.1
        #     for i in range(14, 17):  # 13点至17点
        #         self.c[i] = -0.5
        #     for i in range(17, 23):  # 18点至23点
        #         self.c[i] = -0.5 * 1.1
        #     self.c[23] = -0.5 * 0.9

        # if self.type == "th":
        #     for i in range(0, 7):  # 0点至7点
        #         self.c[i] = -0.5 * 0.9
        #     for i in range(7, 14):  # 8点至14点
        #         self.c[i] = -0.5 * 1.1
        #     for i in range(14, 17):  # 13点至17点
        #         self.c[i] = -0.5
        #     for i in range(17, 23):  # 18点至23点
        #         self.c[i] = -0.5 * 1.1
        #     self.c[23] = -0.5 * 0.9
        #
        # if self.type == "c":
        #     for i in range(0, 7):  # 0点至7点
        #         self.c[i] = -0.5 * 0.9
        #     for i in range(7, 14):  # 8点至14点
        #         self.c[i] = -0.5 * 1.1
        #     for i in range(14, 17):  # 13点至17点
        #         self.c[i] = -0.5
        #     for i in range(17, 23):  # 18点至23点
        #         self.c[i] = -0.5 * 1.1
        #     self.c[23] = -0.5 * 0.9


    #负荷数据修改
    def __getData2(self):
        if self.type == "e":
            # kw
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx")
            self.p = dataset['real_value'].values
            # 移除数组中的nan
            # 使用 pandas 将数组转换为 Series
            series_array = pd.Series(self.p)
            # 使用 isna() 方法检查 NaN，并通过布尔索引过滤掉 NaN 和空字符串
            self.p = series_array[~series_array.isna() & (series_array != '')].values
            print(f"电力负荷值:{self.p}")
            self.p = self.p[:self.time_num]
            self.p_min = dataset['min'].values
            self.p_max = dataset['max'].values
            self.p_mu = dataset['mu'].values
            self.p_mu = self.p_mu[:self.time_num]
            self.p_min = self.p_min[:self.time_num]
            self.p_max = self.p_max[:self.time_num]

        if self.type == "g":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_g.xlsx")
            self.p = dataset['real_value'].values
            # 移除数组中的nan
            # 使用 pandas 将数组转换为 Series
            series_array = pd.Series(self.p)
            # 使用 isna() 方法检查 NaN，并通过布尔索引过滤掉 NaN 和空字符串
            self.p = series_array[~series_array.isna() & (series_array != '')].values
            print(f"天然气负荷值:{self.p}")
            self.p = self.p[:self.time_num]
            self.p_min = dataset['min'].values
            self.p_max = dataset['max'].values
            self.p_mu = dataset['mu'].values
            self.p_mu = self.p_mu[:self.time_num]
            self.p_min = self.p_min[:self.time_num]
            self.p_max = self.p_max[:self.time_num]

        if self.type == "th":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_h.xlsx")
            self.p = dataset['real_value'].values
            # 移除数组中的nan
            # 使用 pandas 将数组转换为 Series
            series_array = pd.Series(self.p)
            # 使用 isna() 方法检查 NaN，并通过布尔索引过滤掉 NaN 和空字符串
            self.p = series_array[~series_array.isna() & (series_array != '')].values
            print(f"热能负荷值:{self.p}")
            self.p = self.p[:self.time_num]
            self.p_min = dataset['min'].values
            self.p_max = dataset['max'].values
            self.p_mu = dataset['mu'].values
            self.p_mu = self.p_mu[:self.time_num]
            self.p_min = self.p_min[:self.time_num]
            self.p_max = self.p_max[:self.time_num]

        if self.type == "c":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_c.xlsx")
            self.p = dataset['real_value'].values
            # 移除数组中的nan
            # 使用 pandas 将数组转换为 Series
            series_array = pd.Series(self.p)
            # 使用 isna() 方法检查 NaN，并通过布尔索引过滤掉 NaN 和空字符串
            self.p = series_array[~series_array.isna() & (series_array != '')].values
            print(f"冷能负荷值:{self.p}")
            self.p = self.p[:self.time_num]
            self.p_min = dataset['min'].values
            self.p_max = dataset['max'].values
            self.p_mu = dataset['mu'].values
            self.p_mu = self.p_mu[:self.time_num]
            self.p_min = self.p_min[:self.time_num]
            self.p_max = self.p_max[:self.time_num]

        self.ramping = (self.p_max - self.p_min) / 8

    def constraints(self, num):

        """
        负荷的上下限约束
        """
        if self.type == "e":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_max[i] * (1 - 0.01 * self.randoms_e[i]), self.p_max[i]),
                                       self.p_max[i], num)

        if self.type == "g":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_max[i] * (1 - 0.01 * self.randoms_g[i]), self.p_max[i]),
                                       self.p_max[i], num)

        if self.type == "th":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_max[i] * (1 - 0.01 * self.randoms_h[i]), self.p_max[i]),
                                       self.p_max[i], num)

        if self.type == "c":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_max[i] * (1 - 0.01 * self.randoms_c[i]), self.p_max[i]),
                                       self.p_max[i], num)
        """
        ramping limits
        """

        # if self.type != 'th' and self.type != 'c':
        #
        #     """
        #     Up ramping limits
        #     """
        #     B = np.array([
        #         [self.params[0], 1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, self.p[0] + self.ramping[0], num)
        #
        #     for i in range(self.time_num - 1):
        #         B = np.array([
        #             [self.params[i+1], 1],
        #             [self.params[i], -1]
        #         ])
        #         CreatConstraintsByText(1, B, -np.inf, self.ramping[i+1], num)
        #
        #     """
        #     Down ramping limits
        #     """
        #     B = np.array([
        #         [self.params[0], -1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, -self.p[0] + self.ramping[0], num)
        #     for i in range(self.time_num - 1):
        #         B = np.array([
        #             [self.params[i+1], -1],
        #             [self.params[i], 1]
        #         ])
        #         CreatConstraintsByText(1, B, -np.inf, self.ramping[i+1], num)

        """
        total
        """
        # B = np.array([
        #     ["s", 1]
        # ])
        # for i in range(self.time_num):
        #     B = np.append(B, np.array([
        #         [self.name + 'P' + str(i+1), 1]
        #     ]))
        # B = B[2:]
        # B = B.reshape((int(len(B) / 2), 2))
        # CreatConstraintsByText(1, B, self.p_total * (self.time_num / 24), np.inf, num)




























