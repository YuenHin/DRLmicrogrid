import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawLine import drawLine

class Line:
    def __init__(self, name, maxTransValue, line_price, Single = False, MG_point = False, from_MG = None, to_MG = None, time_num = 24, type = 'e', Convertion = False):
        self.name = name
        self.time_num = time_num
        self.className = 'Line'
        self.line_price = line_price
        self.Single = Single #True表示能量单向流动
        self.MG_point = MG_point
        self.from_MG = from_MG
        self.to_MG = to_MG
        self.type = type
        self.Conversion = Convertion

        self.maxTransValue = maxTransValue

        self.ramping = maxTransValue / 2

        self.params = np.array([""])

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)

        self.contraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
            self.name + "E"
        ])
        self.params  = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.c[i + self.time_num * 1] = self.c[i + self.time_num * 1] - self.line_price

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))

    def constraints(self, num):
        """
        Limits on power flows through lines
        """
        if self.Single or self.Conversion:
            B = np.array([
                [self.name + "P1", 1]
            ])
            CreatConstraintsByText(self.time_num, B, 0, self.maxTransValue, num)
        else:
            B = np.array([
                [self.name + "P1", 1]
            ])
            CreatConstraintsByText(self.time_num, B, -self.maxTransValue, self.maxTransValue, num)
        """
        LineMin
        """
        B = np.array([
            [self.name + "P1", -1],
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, -np.inf, 0, num)
        """
        LineMAX
        """
        B = np.array([
            [self.name + "P1", -1],
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, np.inf, num)

        """
        Ramping_Up
        """
        B = np.array([
            [self.name + "P2", 1],
            [self.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -self.ramping, self.ramping, num)
        """
        Ramping_Down  漏了？
        """

    def draw(self):
        x = self.x[:self.time_num]
        x_max = np.zeros(self.time_num)
        x_min = np.zeros(self.time_num)
        x_ramping = np.zeros(self.time_num)
        for i in range(len(x)):
            if x[i] > 0:
                x_max[i] = x[i] * 1.2
                x_min[i] = x[i] * 0.8
                x_ramping[i] = x[i] * 0.05
            else:
                x_max[i] = x[i] * 0.8
                x_min[i] = x[i] * 1.2
                x_ramping[i] = - x[i] * 0.05
        drawLine(x, x_max, x_min, x_ramping, None, title=self.name + "transform")






