import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawStorage import drawStorage

"""储能装置"""
class ESFirst:
    def __init__(self, name, type, id, storage_price, storage_limit, storage_limit_min, lifetimes, self_discharging,
                 charging_rate, discharging_rate, time_num, begin=None):

        self.className = 'S'
        self.name = name
        "string"
        self.id = id
        "int"
        self.time_num = time_num
        "hours"

        # 能源类型
        self.type = type
        "e, h, c"

        self.stage = 1
        self.way = 4

        self.storage_price = storage_price
        "美元/kwh"
        self.storage_limit = storage_limit
        self.storage_limit_min = storage_limit_min
        if begin == None:
            self.begin = self.storage_limit / 2
        else:
            self.begin = begin
        self.lifetimes = lifetimes
        "year"

        # 自损率
        self.self_discharging = self_discharging
        "%/hours"

        self.e = 0
        self.charging_max = None
        self.discharging_max = None

        # 充电效率
        self.charging_rate = charging_rate
        # 放电效率
        self.discharging_rate = discharging_rate

        self.params = np.array([""])

        "4"
        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraints_num = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",  # 当前功率
            self.name + "E",  # 储能单元当前的储量
            self.name + "CP",  # 充电功率
            self.name + "DP",  # 放电功率
            self.name + "S",  # 充电状态，等于0或1
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i + self.time_num * 4] = 1

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        if self.type == "e":
            for i in range(self.time_num):
                # 运维成本和调节成本
                self.c[i + self.time_num * 2] = 0.043 + 0.008 - 0.0035
                self.c[i + self.time_num * 3] = 0.043 + 0.008 - 0.0035

        if self.type == "th":
            for i in range(self.time_num):
                # 运维成本和调节成本
                self.c[i + self.time_num * 2] = 0.056 + 0.015 - 0.0025
                self.c[i + self.time_num * 3] = 0.056 + 0.015 - 0.0025

        if self.type == "c":
            for i in range(self.time_num):
                # 运行功率
                self.c[i + self.time_num * 2] = 0.06 + 0.012 - 0.0025
                self.c[i + self.time_num * 3] = 0.06 + 0.012 - 0.0025

    def __getData(self):
        self.e = self.e + self.storage_limit
        self.charging_max = self.e * 0.065
        self.discharging_max = self.e * 0.065
        self.ramping_limit = self.e * 0.055

    def constraints(self, num):

        "Energy storaed limited"
        B = np.array([
            [self.name + "E1", 1]
        ])
        CreatConstraintsByText(1, B, 0, self.e, num)

        "Charging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1],
                [self.name + "S" + str(i + 1), -self.charging_max]
            ])
            CreatConstraintsByText(1, B, -np.inf, 0, num)

        "Discharging power limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, np.inf, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i + 1), 1],
                [self.name + "S" + str(i + 1), self.discharging_max]
            ])
            CreatConstraintsByText(1, B, 0, self.discharging_max, num)


        "Energy balance in the storage unit"
        B = np.array([
            [self.name + "E1", 1],
            [self.name + "CP1", -self.charging_rate],
            [self.name + "DP1", 1 / self.charging_rate]
        ])
        CreatConstraintsByText(1, B, self.begin, self.begin, num)
        B = np.array([
            [self.name + "E2", 1],
            [self.name + "E1", -(1 - self.self_discharging)],
            [self.name + "CP2", -self.charging_rate],
            [self.name + "DP2", 1 / self.charging_rate]
        ])
        CreatConstraintsByText(self.time_num - 1, B, 0, 0, num)
        B = np.array([
            [self.name + "E" + str(self.time_num), 1]
        ])
        CreatConstraintsByText(1, B, self.begin, self.begin, num)

        B = np.array([
            [self.name + "E1", -1],
            [self.name + "E2", 1],
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)

        B = np.array([
            [self.name + "E1", 1],
            [self.name + "E2", -1],
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, self.ramping_limit, num)

        "State"
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)

        "P = cP + dp"
        B = np.array([
            [self.name + "P1", 1],
            [self.name + "CP1", -1],
            [self.name + "DP1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)



class ESSecond:
    def __init__(self, name, type, id, storage_price, storage_limit, storage_limit_min, lifetimes, self_discharging,
                 charging_rate, discharging_rate, time_num, values, p1, begin=None):

        self.className = 'S'
        self.name = name
        "string"
        self.id = id
        "int"
        self.time_num = time_num
        "hours"

        self.values = values
        self.p1 = p1

        # 能源类型
        self.type = type
        "e, h, c"

        self.stage = 2
        self.way = 4

        self.storage_price = storage_price
        "美元/kwh"
        self.storage_limit = storage_limit
        self.storage_limit_min = storage_limit_min
        if begin == None:
            self.begin = self.storage_limit / 2
        else:
            self.begin = begin
        self.lifetimes = lifetimes
        "year"

        # 自损率
        self.self_discharging = self_discharging
        "%/hours"

        self.e = 0
        self.charging_max = None
        self.discharging_max = None

        # 充电效率
        self.charging_rate = charging_rate
        # 放电效率
        self.discharging_rate = discharging_rate

        self.params = np.array([""])

        "4"
        self.day = int(self.time_num / 24)

        "第二阶段接收第一阶段求解"
        self.CP = np.zeros(self.time_num)
        self.DP = np.zeros(self.time_num)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraints_num = 0

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "CP",
            self.name + "DP",
            self.name + "ch_us",
            self.name + "ch_ds",
            self.name + "dis_us",  # 储电装置放电的向上灵活性供给能力
            self.name + "dis_ds",  # 储电装置放电的向下灵活性供给能力
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        "4"
        if self.type == "e":
            for i in range(self.time_num):
                # 灵活供给&缺额惩罚
                self.c[i] = 0.009
                self.c[i + self.time_num] = 0.009
                self.c[i + self.time_num * 2] = 0.009
                self.c[i + self.time_num * 3] = 0.009

        if self.type == "th":
            for i in range(self.time_num):
                # 灵活供给
                self.c[i] = 0.013
                self.c[i + self.time_num] = 0.013
                self.c[i + self.time_num * 2] = 0.013
                self.c[i + self.time_num * 3] = 0.013


        if self.type == "c":
            for i in range(self.time_num):
                # 灵活供给
                self.c[i] = 0.015
                self.c[i + self.time_num] = 0.015
                self.c[i + self.time_num * 2] = 0.015
                self.c[i + self.time_num * 3] = 0.015

    def __getData(self):
        self.e = self.e + self.storage_limit
        self.charging_max = self.e * 0.065
        self.discharging_max = self.e * 0.065
        self.ramping_limit = self.e * 0.055

        for i in range(len(self.p1)):
            for j in range(self.time_num):
                if self.p1[i] == self.name + "CP" + str(j + 1):
                    self.CP[j] = self.values[i]
                if self.p1[i] == self.name + "DP" + str(j + 1):
                    self.DP[j] = self.values[i]

    def constraints(self, num):
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.CP[i], self.CP[i], num)
            B = np.array([
                [self.name + "DP" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.DP[i], self.DP[i], num)


        "Charging Flexible Analysis"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_us" + str(i+1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.charging_max, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "CP" + str(i+1), 1],
                [self.name + "ch_ds" + str(i+1), -1]
            ])
            CreatConstraintsByText(1, B, -self.charging_max, self.charging_max, num)

        """Discharging Flexible Analysis"""
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_us" + str(i+1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.discharging_max, num)
        for i in range(self.time_num):
            B = np.array([
                [self.name + "DP" + str(i+1), 1],
                [self.name + "dis_ds" + str(i+1), -1]
            ])
            CreatConstraintsByText(1, B, -self.discharging_max, self.discharging_max, num)

        """Flexible Constraints"""
        for i in range(self.time_num):
            B = np.array([
                [self.name + "ch_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_limit, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "ch_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_limit, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "dis_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_limit, num)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "dis_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_limit, num)