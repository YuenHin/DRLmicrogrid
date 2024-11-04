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
        self.begin_location = None
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

        self.stochas_P = np.zeros(self.time_num)  # 记录每一步增加随机性后的功率

        if self.type == 'e':
            for i in range(self.time_num):
                self.stochas_P[i] = min(self.p_mu[i] * (1 + 0.01 * self.randoms_e[i]), self.p_max[i])
        elif self.type == 'g':
            for i in range(self.time_num):
                self.stochas_P[i] = min(self.p_mu[i] * (1 + 0.01 * self.randoms_g[i]), self.p_max[i])
        elif self.type == 'th':
            for i in range(self.time_num):
                self.stochas_P[i] = min(self.p_mu[i] * (1 + 0.01 * self.randoms_h[i]), self.p_max[i])
        elif self.type == 'c':
            for i in range(self.time_num):
                self.stochas_P[i] = min(self.p_mu[i] * (1 + 0.01 * self.randoms_c[i]), self.p_max[i])

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
        # for i in range(len(self.params)):
        #     self.c[i] = - (0.0001)
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

    #负荷数据修改
    def __getData2(self):
        if self.type == "e":
            # kw
            dataset = pd.read_excel(r"./Data\uncertainty\load_e.xlsx")
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
            dataset = pd.read_excel(r"./Data\uncertainty\load_g.xlsx")
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
            dataset = pd.read_excel(r"./Data\uncertainty\load_h.xlsx")
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
            dataset = pd.read_excel(r"./Data\uncertainty\load_c.xlsx")
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
        # 起始位置
        self.begin_location = len(num.A)

        """
        负荷的上下限约束
        """
        # for i in range(self.time_num):
        #     B = np.array([
        #         [self.params[i], 1]
        #     ])
        #     CreatConstraintsByText(1, B, self.p_min[i], self.p_max[i], num)

        if self.type == "e":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_mu[i] * (1 + 0.01 * self.randoms_e[i]), self.p_max[i]),
                                       self.p_max[i], num)
                # CreatConstraintsByText(1, B, min(self.p_mu[i], self.p_max[i]), self.p_max[i], num)

        if self.type == "g":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_mu[i] * (1 + 0.01 * self.randoms_g[i]), self.p_max[i]),
                                       self.p_max[i], num)
                # CreatConstraintsByText(1, B, min(self.p_mu[i], self.p_max[i]), self.p_max[i], num)

        if self.type == "th":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_mu[i] * (1 + 0.01 * self.randoms_h[i]), self.p_max[i]),
                                       self.p_max[i], num)
                # CreatConstraintsByText(1, B, min(self.p_mu[i], self.p_max[i]), self.p_max[i], num)

        if self.type == "c":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, min(self.p_mu[i] * (1 + 0.01 * self.randoms_c[i]), self.p_max[i]),
                                       self.p_max[i], num)
                # CreatConstraintsByText(1, B, min(self.p_mu[i], self.p_max[i]), self.p_max[i], num)
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


        return num.A, num.bl, num.bu

    def draw(self):
        drawDemands(self.x, self.p_max, self.p_min, self.ramping, self.type, self.name+"_Load")

    def getdata(self, path, y_index):
        self.p = self.__24to96(path, y_index)
        self.p_limit_max = self.p * (1 + self.ramping_rate)
        self.p_limit_min = self.p * (1 - self.ramping_rate)

        # using 24 step points to caculate 96 step points
        # limit the type of demand data

    def __24to96(self, path, y_index):
        p = self.__downLoad_load(path, y_index)
        p = self.__creatY_96(p)
        return p

        #顺滑Y轴24->96

    def __creatY_96(self, p):
        x = np.arange(1, len(p) + 1, 1)
        x, p = smooth(x, p, self.time_num)
        return p

        #加载Y轴数据

    def __downLoad_load(self, path, y_index):
        p = getDataFromExcel(path, y_index, y_index + 1, 1, 25)
        return p

    def stochastic(self, step, num):

        #依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
        #需要控制不确定变化后不会跳出范围
        '''
        ran = random.choice([1, -1])
        # ran=1，真实值向上波动
        if ran == 1:
            self.real_x[step - 1] = self.x[step - 1] * (1 + (random.random() * self.stochastic_value * 0.01))
        # ran=-1，真实值向下波动
        if ran == -1:
            # self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (0.5) * 0.01))
            self.real_x[step - 1] = self.x[step - 1]
        if self.real_x[step - 1] > self.p_max[step - 1]:
            self.real_x[step - 1] = self.p_max[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            self.real_x[step - 1] = self.p_min[step - 1]

        if step > 1:
            if self.real_x[step - 1] - self.real_x[step - 2] >= 0:
                if self.real_x[step - 1] - self.real_x[step - 2] > self.ramping[step - 1]:
                    self.real_x[step - 1] = self.real_x[step - 2] + self.ramping[step - 1]
            else:
                if self.real_x[step - 2] - self.real_x[step - 1] > self.ramping[step - 1]:
                    self.real_x[step - 1] = self.real_x[step - 2] - self.ramping[step - 1]
        '''
        # self.real_x[step - 1] = random.uniform(self.p_min[step - 1], self.p_max[step - 1])
        # self.real_x[step - 1] = self.p_min[step - 1]
        self.real_x[step - 1] = self.stochas_P[step - 1]
        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

        # self.stochas_P[step - 1] = self.real_x[step - 1]  # 记录当前时间步增加随机性后的功率


    def re_train(self, step, num):
        num.bu[self.contraint_num + self.time_num + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num + step] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step] = np.inf

    def remember_realVaule(self, step, num):
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)






















