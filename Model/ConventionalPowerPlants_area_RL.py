import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawCPP import drawCPP

from tools.maybeExcel import getDataFromExcel
from tools.aDataSetting import smooth

class CPP:
    def __init__(self, name, id, total_production, time_num, sell = False):
        self.name = name
        self.id = id
        self.total_production = total_production
        self.className = 'CPP'

        self.time_num = time_num
        self.p = np.zeros(time_num)
        #self.p_max = (self.total_production / self.time_num) * 0.2
        self.p_max = 10000
        self.p_min = 0

        self.c_emission = np.zeros(time_num)

        self.params = np.array([""])
        "4"
        #美元/kwh 0.027
        self.production_price = self.__24to96(".\Data\PRICE\price_e.xlsx", 13)
        self.sell_price = 0.315

        self.way = 1


        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.contraint_num = 0

    def __init(self):
        self.__params_named()
        self.__getData()
        self.__set_intergrality()
        self.__set_C()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
            self.name + "buy" + "P",
            self.name + "sell" + "P",
            self.name + "S",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.ones(len(self.params))
        for i in range(len(self.params) - self.time_num):
            self.intergrality[i] = 0

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        "产能成本"
        for i in range(self.time_num):
                # self.c[i + self.time_num * 1] = - self.production_price[i] - 0.839 * 0.001 * 390.885
                self.c[i] = - self.production_price[i] - 0.839 * 0.001 * 390.885

                # self.c[i + self.time_num * 2] = self.sell_price


    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num

    def constraints(self, num):
        """
        Power output limits
        """
        B = np.array([
            [self.name + "S1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)

        B = np.array([
            [self.name+ "P1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, -self.p_max, self.p_max, num)
        # CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)

        B = np.array([
            [self.name + "buy" + "P1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)
        B = np.array([
            [self.name + "buy" + "P1", 1],
            [self.name + "S1", -self.p_max],
        ])
        CreatConstraintsByText(self.time_num, B, -np.inf, 0, num)

        B = np.array([
            [self.name + "sell" + "P1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)
        B = np.array([
            [self.name + "sell" + "P1", 1],
            [self.name + "S1", self.p_max],
        ])
        CreatConstraintsByText(self.time_num, B, -np.inf, self.p_max, num)

        B = np.array([
            [self.name + "sell" + "P1", -1],
            [self.name + "buy" + "P1", 1],
            [self.name + "P1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)




    def draw(self):
        p = self.x[0:self.time_num]
        drawCPP(p, self.p_max, 0, np.zeros(len(self.p)) + max(self.p), np.zeros(len(self.p)), None, title= self.name + "Produciton")

    def __24to96(self, path, y_index):
        p = self.__downLoad_load(path, y_index)
        p = self.__creatY_96(p)
        return p

        # 顺滑Y轴24->96

    def __creatY_96(self, p):
        x = np.arange(1, len(p) + 1, 1)
        x, p = smooth(x, p, self.time_num)
        return p

        # 加载Y轴数据

    def __downLoad_load(self, path, y_index):
        p = getDataFromExcel(path, y_index, y_index + 1, 1, 25)
        return p

    def remember_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)