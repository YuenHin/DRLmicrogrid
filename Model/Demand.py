import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawDemands import drawDemands
from tools.aDataSetting import smooth
import random

class D:
    def __init__(self, name, type, p_total, id = 1, MG_id = 1, ramping_rate = 0.25, time_num = 96, stochastic_value = 10):
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
        self.p_max = np.zeros(self.time_num)

        self.params = np.array([""])
        "1"

        self.c = np.zeros(self.time_num)
        "1"
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

    def __set_C(self):
        self.c = np.zeros(self.length)
        Day_price = None
        if self.type == "e":
            "获取电力售电价格："
            # GBP / MWh
            Day_price = getDataFromExcel("Data\power_price.xls", 1 + self.MG_id, 2 + self.MG_id, 2, 2 + 24)
        if self.type == "g":
            "获取天然气出售价格："
            # GBP / MWh
            Day_price = getDataFromExcel("Data\gas_price.xlsx", 1 + self.MG_id, 2 + self.MG_id, 2, 2 + 24)
        if self.type == "th":
            "获取天然气出售价格："
            # GBP / MWh
            Day_price = getDataFromExcel("Data\gas_price.xlsx", 1 + self.MG_id, 2 + self.MG_id, 2, 2 + 24)
        if self.type == "h":
            "获取天然气出售价格："
            # GBP / MWh
            Day_price = getDataFromExcel("Data\gas_price.xlsx", 1 + self.MG_id, 2 + self.MG_id, 2, 2 + 24)
        tempArray = np.zeros(24)

        for i in range(len(Day_price)):
            tempNum = 10
            temp = 0
            for j in range(len(Day_price[i][0])):
                if Day_price[i][0][j] != ',':
                    temp = temp + float(Day_price[i][0][j]) * tempNum
                    tempNum = tempNum / 10
            tempArray[i] = temp
        Day_price = tempArray
        # USD/KWH
        Day_price = Day_price / 1000 * 1.1125
        self.c = np.zeros(len(Day_price))

    def __set_C2(self):
        self.c = np.zeros(self.time_num)

    def __getData(self):
        if self.type == "e":
            # kw
            self.p = getDataFromExcel("Data\Data_demands.xlsx", 1, 25, self.id, self.id + self.research_day) * 365  * (self.p_total / self.research_day)
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "g":
            self.p = getDataFromExcel("Data\Data_demands.xlsx", 1, 25, self.id +50, self.id + 50 + self.research_day) * 365 * (
                        self.p_total / self.research_day)
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "th":
            self.p = getDataFromExcel("Data\Data_demands.xlsx", 1, 25, self.id +100, self.id + 100 + self.research_day) * 365 * (
                        self.p_total / self.research_day)
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "h":
            self.p = getDataFromExcel("Data\Data_demands.xlsx", 1, 25, self.id +150, self.id + 150 + self.research_day) * 365 * (
                        self.p_total / self.research_day)
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        self.total_Demand = np.sum(self.p)

    def __getData2(self):
        if self.type == "e":
            # kw
            self.p = self.__24to96("./Data/Load/electricity_H.xlsx", 0) * self.p_total
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "g":
            self.p = self.__24to96("./Data/Load/gas_H.xlsx", 3) * self.p_total
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "th":
            self.p = self.__24to96("./Data/Load/thermal_H.xlsx", 7) * self.p_total
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)

        if self.type == "h":
            self.p = self.__24to96("./Data/Load/hydrogen_H.xlsx", 2) * self.p_total
            self.p = self.p.flatten()
            self.p_min = self.p * (1 - self.ramping_rate)
            self.p_max = self.p * (1 + self.ramping_rate)
        self.ramping = (self.p_max - self.p_min) / 8

    def constraints(self, num):
        """
        负荷的上下限约束
        """
        for i in range(self.time_num):
            B = np.array([
                [self.params[i], 1]
            ])
            CreatConstraintsByText(1, B, self.p_min[i], self.p_max[i], num)
        """
        ramping limits
        """

        if self.type != 'h':

            """
            Up ramping limits
            """
            B = np.array([
                [self.params[0], 1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.p[0] + self.ramping[0], num)

            for i in range(self.time_num - 1):
                B = np.array([
                    [self.params[i+1], 1],
                    [self.params[i], -1]
                ])
                CreatConstraintsByText(1, B, -np.inf, self.ramping[i+1], num)

            """
            Down ramping limits
            """
            B = np.array([
                [self.params[0], -1]
            ])
            CreatConstraintsByText(1, B, -np.inf, -self.p[0] + self.ramping[0], num)
            for i in range(self.time_num - 1):
                B = np.array([
                    [self.params[i+1], -1],
                    [self.params[i], 1]
                ])
                CreatConstraintsByText(1, B, -np.inf, self.ramping[i+1], num)

        """
        total
        """
        B = np.array([
            ["s", 1]
        ])
        for i in range(self.time_num):
            B = np.append(B, np.array([
                [self.name + 'P' + str(i+1), 1]
            ]))
        B = B[2:]
        B = B.reshape((int(len(B) / 2), 2))
        CreatConstraintsByText(1, B, self.p_total * (self.time_num / 24), np.inf, num)
        return num.A, num.bl, num.bu

    def draw(self):
        drawDemands(self.x, self.p_max, self.p_min, self.ramping, self.type  ,self.name+"_Load")

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
        self.real_x[step - 1] * (1 + (random.random() * (self.stochastic_value) * 0.01))
        # if (step != 93 and self.type != 'g') and (step != 96 and self.type != 'h'):
        #     self.real_x[step - 1] = self.x[step - 1] * (1 + (random.random() * (self.stochastic_value ) * 0.01))
        # else:
        #     self.real_x[step - 1] = self.x[step - 1]

        if self.real_x[step - 1] > self.p_max[step - 1]:
            num.bu[self.contraint_num + step - 1] = self.real_x[step - 1]
            self.p_max[step - 1] = self.real_x[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            num.bl[self.contraint_num + step - 1] = self.real_x[step - 1]
            self.p_min[step - 1] = self.real_x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1] * (1 - self.flexible_value),
                                        self.real_x[step - 1] * (1 + self.flexible_value), num)

    def re_train(self, step, num):
        num.bu[self.contraint_num + self.time_num + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num + step] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step] = np.inf
























