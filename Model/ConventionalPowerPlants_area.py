import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawCPP import drawCPP

class CPP:
    def __init__(self, name, id, total_production, production_price, time_num):
        self.name = name
        self.id = id
        self.total_production = total_production
        self.className = 'CPP'

        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = (self.total_production / self.time_num) * 0.2
        self.p_max = 0
        self.p_ramping_up = (self.total_production / self.time_num) * 0.2
        self.p_ramping_down = (self.total_production / self.time_num) * 0.15
        self.p_startUp = (self.total_production / self.time_num) * 0.4
        self.p_shutDown = (self.total_production / self.time_num) * 0.2

        self.state = np.zeros(time_num)
        self.upAction = np.zeros(time_num)
        self.downAction = np.zeros(time_num)

        self.params = np.array([""])
        "4"

        # 美元/kwh 0.027
        self.production_price = production_price

        self.way = 1
        "表示能源从该设备流出"

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)

    def __init(self):
        self.__params_named()
        self.__getData()
        self.__set_intergrality()
        self.__set_C()

    def __params_named(self):
        temp = np.array([
            self.name + "P",

        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.ones(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i] = 0

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        "产能成本"
        for i in range(self.time_num):
            self.c[i] = self.production_price

    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num

    def constraints(self, num):
        """
        Power output limits
        """

        B = np.array([
            [self.name + "P1", 1],

        ])
        CreatConstraintsByText(self.time_num, B, -self.p_max, self.p_max, num)


    def draw(self):
        p = self.x[0:self.time_num]
        drawCPP(p, self.p_max, 0, self.p_ramping_up, self.p_ramping_down, None, title= self.name + "Produciton")








