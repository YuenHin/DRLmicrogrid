import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawCPP import drawCPP

class DG:
    def __init__(self, name, id, total_production, production_price,time_num):
        self.name = name
        self.id = id
        self.total_production = total_production
        self.className = 'DG'

        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = (self.total_production / self.time_num) * 0.2 * (self.time_num // 24)
        self.p_max = 0
        self.p_ramping_up = (self.total_production / self.time_num) * 0.2 * (self.time_num // 24)
        self.p_ramping_down = (self.total_production / self.time_num) * 0.15 * (self.time_num // 24)
        self.p_startUp = (self.total_production / self.time_num) * 0.4 * (self.time_num // 24)
        self.p_shutDown = (self.total_production / self.time_num) * 0.2 * (self.time_num // 24)

        self.state = np.zeros(time_num)
        self.upAction = np.zeros(time_num)
        self.downAction = np.zeros(time_num)

        self.params = np.array([""])
        "4"

        #美元/kwh 0.027
        self.production_price = production_price

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
            self.c[i] = -self.production_price - 0.239 * 0.001 * 390.885
        # for i in range(self.time_num):
        #     self.c[i +self.time_num] = -self.production_price * 0.01

        # "停机成本"
        # for i in range(self.time_num):
        #     self.c[-i-1] = self.total_production * self.production_price * 0.1
        #
        # "开机成本"
        # for i in range(self.time_num):
        #     self.c[-i-1-self.time_num] = self.total_production * self.production_price * 0.2


    def __getData(self):
        self.p_max = self.p_max + self.total_production / self.time_num * (self.time_num // 24)

    def constraints(self, num):
        """
        Logic expressions:
        """
        # B = np.array([
        #     [self.name + "S1", 1],
        #     [self.name + "DA1", 1],
        #     [self.name + "UA1", -1]
        # ])
        # CreatConstraintsByText(1, B, 0, 0, num)
        #
        # B = np.array([
        #     [self.name + "S2", 1],
        #     [self.name + "S1", -1],
        #     [self.name + "DA2", 1],
        #     [self.name + "UA2", -1]
        # ])
        # CreatConstraintsByText(self.time_num - 1, B, 0, 0, num)
        #
        # B = np.array([
        #     [self.name + "DA1", 1],
        #     [self.name + "UA1", 1]
        # ])
        # CreatConstraintsByText(self.time_num , B, -np.inf, 1, num)

        """
        Power output limits
        """

        B = np.array([
            [self.name + "P1", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)
        self.contraint_num += self.time_num

        B = np.array([
            [self.name + "P"+ str(self.time_num), 1],
        ])
        CreatConstraintsByText(1, B, 0, 0, num)
        self.contraint_num += 1
        # B = np.array([
        #     [self.name + "P1", 1],
        #     [self.name + "S1", -self.p_max]
        # ])
        # CreatConstraintsByText(self.time_num, B, -np.inf, 0, num)

        """
        Ramping-up limits
        """
        B = np.array([
            [self.name + "P1", 1],
            # [self.name + "S1", -self.p_ramping_up],
            # [self.name + "UA1", -self.p_startUp]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.p_ramping_up, num)
        B = np.array([
            [self.name + "P2", 1],
            [self.name + "P1", -1],
            # [self.name + "S2", -self.p_ramping_up],
            # [self.name + "UA2", -self.p_startUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.p_ramping_up, num)
        self.contraint_num += self.time_num
        """
        Ramping-down limits
        """
        B = np.array([
            [self.name + "P1", -1],
            # [self.name + "S1", -self.p_ramping_down],
            # [self.name + "UA1", -self.p_shutDown]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.p_ramping_down, num)
        B = np.array([
            [self.name + "P2", -1],
            [self.name + "P1", 1],
            # [self.name + "S2", -self.p_ramping_down],
            # [self.name + "UA2", -self.p_shutDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.p_ramping_down, num)
        self.contraint_num += self.time_num
        """
        S、UA、DA归属于（0,1）
        """

        # B = np.array([
        #     [self.name + "S1", 1],
        # ])
        # CreatConstraintsByText(self.time_num, B, 0, 1, num)
        #
        # B = np.array([
        #     [self.name + "UA1", 1],
        # ])
        # CreatConstraintsByText(self.time_num, B, 0, 1, num)
        # B = np.array([
        #     [self.name + "DA1", 1],
        # ])
        # CreatConstraintsByText(self.time_num, B, 0, 1, num)

    def draw(self):
        p = self.x[0:self.time_num]
        s = self.x[self.time_num:self.time_num*2]
        drawCPP(p, self.p_max, 0, self.p_ramping_up, self.p_ramping_down, s, title= self.name + "Produciton")

    def remenber_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

    def get_action(self, step, num, action):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        done = False
        if step == 1:
            self.real_x[step - 1] = 0 + action * self.p_ramping_up
        else:
            self.real_x[step - 1] = self.real_x[step - 2] + action * self.p_ramping_up
        if self.real_x[step - 1] > self.p_max[step - 1] or self.real_x[step - 1] < self.p_min[step - 1]:
            done = True
            return done

        # 我需要控制不确定变化后不会跳出范围
        self.real_x[self.time_num + step - 1] = self.x[self.time_num + step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)
        return done

    def fix(self, num):

        for i in range(self.time_num):
            B = np.array([
                [self.name + "P" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.x[i], self.x[i], num)
