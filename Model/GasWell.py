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

        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_max = (self.total_production / self.time_num) * 0.2
        self.p_min = 0

        self.c_emission = np.zeros(time_num)

        self.params = np.array([""])
        "4"

        #美元/kwh 0.027
        self.production_price = 0.254

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
        for i in range(self.time_num):
            self.c[i] = -self.production_price - 0.368 * 0.001 * 390.885

    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num * ( self.time_num / 24)

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
        drawCPP(p, self.p_max, 0, np.zeros(len(self.p)) + max(self.p), np.zeros(len(self.p)), None, title= self.name + "Produciton")

    def remenber_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

