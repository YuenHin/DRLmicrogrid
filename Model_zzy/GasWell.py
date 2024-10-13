import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from ConventionalPowerPlants import drawCPP

class GW:
    def __init__(self, name, id, total_production, production_price, time_num):

        self.name = name
        self.id = id
        self.total_production = total_production
        self.className = 'GW'
        self.type = "gw"

        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_max = self.total_production / self.time_num
        self.p_min = 0

        self.c_emission = np.zeros(time_num)

        self.params = np.array([""])
        "4"

        #美元/kwh 0.027
        self.production_price = 0.254

        self.stage = 1
        self.way = 1
        "表示能源从该设备流出"

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
        for i in range(0, 7):  # 0点至7点
            self.c[i] = 0.7 * 0.9
        for i in range(7, 14):  # 8点至14点
            self.c[i] = 0.7 * 1.1
        for i in range(14, 17):  # 13点至17点
            self.c[i] = 0.7
        for i in range(17, 23):  # 18点至23点
            self.c[i] = 0.7 * 1.1
        self.c[23] = 0.7 * 0.9

    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num

    def constraints(self, num):

        """
        Power output limits
        """

        B = np.array([
            [self.name + "P1", 1],

        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)


class GWSecond:
    def __init__(self, name, id, total_production, production_price, time_num, values, p1):

        self.name = name
        self.id = id
        self.total_production = total_production
        self.className = 'GW'

        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_max = self.total_production / self.time_num
        self.p_min = 0

        self.c_emission = np.zeros(time_num)

        self.params = np.array([""])
        "4"

        # 美元/kwh 0.027
        self.production_price = 0.254

        self.stage = 2
        self.way = 1
        "表示能源从该设备流出"

        self.values = values
        self.p1 = p1

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
        for i in range(0, 7):  # 0点至7点
            self.c[i] = 0.7 * 0.9
        for i in range(7, 14):  # 8点至14点
            self.c[i] = 0.7 * 1.1
        for i in range(14, 17):  # 13点至17点
            self.c[i] = 0.7
        for i in range(17, 23):  # 18点至23点
            self.c[i] = 0.7 * 1.1
        self.c[23] = 0.7 * 0.9

    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num

    def constraints(self, num):
        """
        Power output limits
        """

        B = np.array([
            [self.name + "P1", 1],

        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)

