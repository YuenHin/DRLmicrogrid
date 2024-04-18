import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawRG import drawRG

class RT:
    def __init__(self, name, type ,id, production_price, production_total,time_num):
        self.name = name
        self.id = id

        self.way = 1

        self.production_price = production_price
        self.production_total = production_total

        self.type = type
        self.className = 'RT'
        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = np.zeros(time_num)
        self.p_max = np.zeros(time_num)

        self.p_rampingh_up = np.zeros(time_num)
        self.p_rampingh_down = np.zeros(time_num)

        self.params = np.array([""])

        self.day = int(self.time_num / 24)
        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
        ])
        "1"
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(self.time_num)

    def __set_C(self):
        self.c = np.zeros(self.time_num)
        "1"
        "产能成本"
        self.c = self.c + self.production_price

    def __getData(self):
        "导入可再生能源产能"
        if self.type == "WT":
            self.__getWTData()
        if self.type == "PV":
            self.__getPVData()
        "计算每小时最小值"
        "计算每个小时最大值"

        self.p = self.p.reshape((1, self.time_num))
        "获得一维数组，单位是kwh"
        self.p = self.p[0]
        self.p_max = self.p

        if self.type == "PV":
            self.p_rampingh_up = (self.p_max - self.p_min) * 0.5
            self.p_rampingh_down = (self.p_max - self.p_min) * 0.5
        if self.type == "WT":
            self.p_rampingh_up = (self.p_max - self.p_min) * 0.1
            self.p_rampingh_down = (self.p_max - self.p_min) * 0.1

    def __getWTData(self):
        self.p = getDataFromExcel("Data\WT.xlsx", self.id, self.id + self.day, 0, 24)
        temp = np.zeros(self.time_num)

        for i in range(self.day):
            for j in range(24):
                temp[i * 24 + j] = self.p[j][i]
        self.p = temp
        self.p = self.p.reshape((self.day, 24))

        production_total_day = self.production_total / self.day
        total = np.sum(self.p, axis=1)
        for i in range(self.day):
            self.p[i] = self.p[i] * (production_total_day / total[i])

    def __getPVData(self):
        self.p = getDataFromExcel("Data\Solar_home_electricity.xls", 5, 53, self.id + 1, self.id + 1 + self.day)
        self.p = self.p.reshape((self.day, 48))
        "转化为数字"
        for i in range(len(self.p)):
            for j in range(len(self.p[i])):
                self.p[i][j] = float(self.p[i][j])
        "半小时至转化为小时制"
        for i in range(len(self.p)):
            for j in range(int(len(self.p[i]) / 2)):
                self.p[i][j] = (self.p[i][2 * j] + self.p[i][2 * j + 1]) / 2
        "控制发电总量"
        temp = np.zeros(self.time_num)
        for i in range(self.day):
            for j in range(24):
                temp[i * 24 + j] = self.p[i][j]
        temp = temp.reshape((self.day, 24))
        self.p = temp

        production_total_day = self.production_total / self.day
        total = np.sum(self.p, axis=1)
        for i in range(self.day):
            self.p[i] = self.p[i] * (production_total_day / total[i])

    def constraints(self, num):
        "production limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "P" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.p_min[i], self.p_max[i], num)

        "Ramping limits:"
        B = np.array([
            [self.name + "P1", 1]
        ])
        CreatConstraintsByText(1, B, 0, 0, num)
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "P" + str(i + 1), -1],
                [self.name + "P" + str(i + 2), 1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[i], num)
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "P" + str(i + 1), 1],
                [self.name + "P" + str(i + 2), -1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_down[i], num)

    def draw(self):
        drawRG(self.x, self.p_max, self.p_min, self.p_rampingh_up, self.p_rampingh_down, None, title=self.name + "RG")









