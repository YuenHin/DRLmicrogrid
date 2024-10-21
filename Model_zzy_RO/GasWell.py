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
        # self.production_price = 0.254

        self.stage = 1
        self.way = 1
        "表示能源从该设备流出"

        self.__init()

        self.length = len(self.params)

        self.production_price = self.c

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)
        self.rl_p = np.zeros(self.length)

        self.contraint_num = 0

        self.p_gap = np.zeros(self.length)  # 记录强化学习的动作和最优动作之间的差距，用于计算reward

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
        # CreatConstraintsByText(self.time_num, B, -self.p_max, self.p_max, num)

    def get_action(self, step, num, action, cur_episode):
        # 记录智能体所给的动作功率
        self.rl_p[step - 1] = self.p_max * action * 0.1
        self.p_gap[step - 1] = abs(self.x[step - 1] - self.rl_p[step - 1])
        self.real_x[step - 1] = self.x[step - 1]
        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        # CreatConstraintsByText(1, B, self.rl_p[step - 1], np.inf, num)
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)
        return False, action

    def remember_realValue(self, step, num):
        # 这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

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

