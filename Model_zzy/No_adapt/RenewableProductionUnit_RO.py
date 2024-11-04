import numpy as np

from aDataSetting import smooth
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawRG import drawRG
import random
import pandas as pd

class RT:
    def __init__(self, name, type, id, production_price, production_total, time_num, stochastic_value=25):

        self.name = name
        self.id = id

        self.stage = 2
        self.way = 1

        # 生产成本
        self.production_price = production_price
        # 希望总产量
        self.production_total = production_total

        self.type = type
        self.className = 'RT'
        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = np.zeros(time_num)
        self.p_max = np.zeros(time_num)
        self.p_mu = np.zeros(time_num)

        self.p_rampingh_up = np.zeros(time_num)
        self.p_rampingh_down = np.zeros(time_num)

        self.randoms_pv = np.array([0.17585667, 0.11310877, 0.13890614, 0.04171659, 0.15476271, 0.06063636,
                                    0.21186455, 0.24243415, 0.23833435, 0.26983087, 0.07053308, 0.01336584,
                                    0.02009157, 0.20643886, 0.09236406, 0.04600884, 0.2080278,  0.21979565,
                                    0.23064161, 0.08826133, 0.11075521, 0.10486894, 0.16470218, 0.26452832])
        self.randoms_wt = np.array([0.16749573, 0.2123105,  0.25994513, 0.10613856, 0.16723538, 0.24197309,
                                    0.19656779, 0.22821717, 0.24671185, 0.24990843, 0.02937662, 0.0436565,
                                    0.21153729, 0.20440689, 0.09889093, 0.24154307, 0.07688684, 0.06677246,
                                    0.28295787, 0.16837925, 0.22980433, 0.03781076, 0.06734404, 0.10276821])

        self.params = np.array([""])

        # self.day = int(self.time_num / 24)
        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        # 随机波动
        self.stochastic_value = stochastic_value
        # 约束所在位置
        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(self.time_num)

    def __set_C(self):
        if self.type == "WT":
            self.c = np.zeros(len(self.params))
            for i in range(len(self.c)):
                self.c[i] = 0.0896 - 0.05

        if self.type == "PV":
            self.c = np.zeros(len(self.params))
            for i in range(len(self.c)):
                self.c[i] = 0.0896 - 0.05

    def __getData(self):
        "导入可再生能源产能"
        if self.type == "WT":
            self.__getWTData()
        if self.type == "PV":
            self.__getPVData()
        if self.type == "HP":
            self.__getHPData()
        "计算每小时最小值"
        "计算每个小时最大值"

        # self.p = self.p.reshape((1, self.time_num))
        "获得一维数组，单位是kwh"
        # self.p = self.p[0]
        # 数据清洗
        for i in range(len(self.p)):
            if self.p[i] < 0:
                self.p[i] = 0
        # 将处理过后的p数组赋值给p_max
        print(f"可再生能源出力值：{self.p}")
        # self.p_max = self.p
        # self.p_min = np.zeros_like(self.p_max)

        if self.type == "PV":
            # 光伏的爬坡功率与滑坡功率是最大功率的一半
            self.p_rampingh_up = (self.p_max - self.p_min) * 0.3
            self.p_rampingh_down = (self.p_max - self.p_min) * 0.3
        if self.type == "WT":
            # 风机的爬坡功率与滑坡功率是最大功率的十分之一
            self.p_rampingh_up = (self.p_max - self.p_min) * 0.3
            self.p_rampingh_down = (self.p_max - self.p_min) * 0.3
        if self.type == "HP":
            self.p_rampingh_up = self.p_max * 0.1
            self.p_rampingh_down = self.p_max * 0.1

    def __getWTData(self):
        # 平滑处理后的纵坐标值×production_total
        dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\wt.xlsx")
        self.p = dataset['real_value'].values
        self.p = self.p[:self.time_num]
        self.p_min = dataset['min'].values
        self.p_min = self.p_min[:self.time_num]
        self.p_max = dataset['max'].values
        self.p_max = self.p_max[:self.time_num]
        self.p_mu = dataset['mu'].values
        self.p_mu = self.p_mu[:self.time_num]

    def __getPVData(self):
        dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\pv.xlsx")
        self.p = dataset['real_value'].values
        self.p = self.p[:self.time_num]
        self.p_min = dataset['min'].values
        self.p_min = self.p_min[:self.time_num]
        self.p_max = dataset['max'].values
        self.p_max = self.p_max[:self.time_num]
        self.p_mu = dataset['mu'].values
        self.p_mu = self.p_mu[:self.time_num]

    def __getHPData(self):
        dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\hp.xlsx")
        self.p = dataset['real_value'].values
        self.p = self.p[:self.time_num]
        self.p_min = dataset['min'].values
        self.p_min = self.p_min[:self.time_num]
        self.p_max = dataset['max'].values
        self.p_max = self.p_max[:self.time_num]
        self.p_mu = dataset['mu'].values
        self.p_mu = self.p_mu[:self.time_num]

    def constraints(self, num):

        "Production limits:"
        if self.type == "PV":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, self.p_min[i], max(self.p_min[i] * (1 + 0.01 * self.randoms_pv[i]), self.p_min[i]),
                                       num)

        if self.type == "WT":
            for i in range(self.time_num):
                B = np.array([
                    [self.name + "P" + str(i + 1), 1]
                ])
                CreatConstraintsByText(1, B, self.p_min[i], max(self.p_min[i] * (1 + 0.01 * self.randoms_wt[i]), self.p_min[i]),
                                       num)

        "Ramping limits:"
        # B = np.array([
        #     [self.name + "P1", 1]
        # ])
        # CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[0], num)
        # for i in range(self.time_num - 1):
        #     B = np.array([
        #         [self.name + "P" + str(i + 1), -1],
        #         [self.name + "P" + str(i + 2), 1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[i+1], num)
        #
        # B = np.array([
        #     [self.name + "P1", 1]
        # ])
        # CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_down[0], num)
        # for i in range(self.time_num - 1):
        #     B = np.array([
        #         [self.name + "P" + str(i + 1), 1],
        #         [self.name + "P" + str(i + 2), -1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_down[i+1], num)

class HP:
    def __init__(self, name, type, id, production_price, production_total, time_num, line_e, line_h, stochastic_value=10):

        self.className = "RT"
        self.type = "HP"

        self.name = name
        self.id = id

        self.stage = 2
        self.way = 3

        self.production_price = production_price
        self.production_total = production_total

        self.production_cost = 0

        # 时间尺度
        self.time_num = time_num

        self.day = int(self.time_num / 24)

        self.type = type

        self.line_e = line_e
        self.line_h = line_h

        # 最大/最小功率
        self.max_input_e = 3000
        self.min_input_e = 0
        self.max_output_h = 2500
        self.min_output_h = 0

        # 供能性能系数
        self.coefficient_h = 4.5
        # self.coefficient_c = 4

        # 保存数据的数组
        # 输出功率的最大最小值
        self.p = np.zeros(self.time_num)
        self.p_max = np.zeros(self.time_num)
        self.p_min = np.zeros(self.time_num)

        # 输入功率的最大最小值
        self.min = np.zeros(len(self.p_min))
        self.max = np.zeros(len(self.p_max))

        # 爬坡与滑坡功率
        self.p_rampingh_up = np.zeros(self.time_num)
        self.p_rampingh_down = np.zeros(self.time_num)

        self.randoms_hp = np.array([0.17585667, 0.11310877, 0.13890614, 0.04171659, 0.15476271, 0.06063636,
                                    0.19656779, 0.22821717, 0.24671185, 0.24990843, 0.02937662, 0.0436565,
                                    0.21153729, 0.20440689, 0.09889093, 0.24154307, 0.07688684, 0.06677246,
                                    0.23064161, 0.08826133, 0.11075521, 0.10486894, 0.16470218, 0.26452832])

        self.ramping_up = 300
        self.ramping_down = 300

        self.params = np.array([""])
        self.length = len(self.params)

        # 初始化
        self.__init()

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        # 用于强化学习
        self.stochastic_value = stochastic_value

        # 约束所在位置
        self.constraint_num = 0

    def __init(self):
        self.__params_name()
        self.__getdata()
        self.__integrality()
        self.__set_c()

    def __params_name(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_h"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __integrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_c(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num, self.time_num * 2):
            self.c[i] = 0.0673 - 0.025

    # 拿到可再生能源数据
    def __getdata(self):
        # 得到处理后的数据
        dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\hp.xlsx")
        self.p = dataset['real_value'].values
        self.p = self.p[:self.time_num]
        self.p_min = dataset['min'].values
        self.p_min = self.p_min[:self.time_num]
        self.p_max = dataset['max'].values
        self.p_max = self.p_max[:self.time_num]

        self.p = self.p * (1 - 0.07)

        # 数据清洗
        for i in range(len(self.p)):
            if self.p[i] < 0:
                self.p[i] = 0
        # 将处理后的p数组赋值给p_max
        # self.p_max = self.p
        self.p_rampingh_up = (self.p_max - self.p_min) * 0.8
        self.p_rampingh_down = (self.p_max - self.p_min) * 0.8

        for i in range(len(self.p_min)):
            self.min[i] = self.p_min[i] / self.coefficient_h
            self.max[i] = self.p_max[i] / self.coefficient_h


    def constraints(self, constraint_information_class):

        # 性能系数约束
        coefficient_constraint_h = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_h1", -1/self.coefficient_h]
        ])
        CreatConstraintsByText(self.time_num, coefficient_constraint_h, 0, 0, constraint_information_class)

        # 最大/最小功率约束
        for i in range(self.time_num):
            # power_constraint_e = np.array([
            #     [self.name + "input_e" + str(i + 1), 1]
            # ])
            # CreatConstraintsByText(1, power_constraint_e, self.min[i], self.max[i], constraint_information_class)
            power_constraint_h = np.array([
                [self.name + "output_h" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, power_constraint_h, self.p_min[i], max(self.p_min[i] * (1 + 0.01 * self.randoms_hp[i]), self.p_min[i]),
                                   constraint_information_class)


        # 线路约束
        # line_e
        B = np.array([
            [self.name + "input_e1", 1],
            [self.line_e.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)
        # line_h
        B = np.array([
            [self.name + "output_h1", 1],
            [self.line_h.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)









