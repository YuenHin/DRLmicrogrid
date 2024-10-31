import numpy as np
import pandas as pd

from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from aDataSetting import smooth

class FD:
    def __init__(self, name, type, net_load_sets, fluctuation_rate, time_num):
        self.className = "FD"
        self.name = name

        self.stage = 2
        self.way = 10

        # type "e,g,th,c"
        self.type = type
        self.fluctuation_rate = fluctuation_rate

        # 计算净负荷所需的决策变量
        self.net_load_sets = net_load_sets

        self.time_num = time_num

        self.params = np.array([''])

        self.predict_load = np.zeros(self.time_num)
        self.net_load_max = np.zeros(self.time_num)
        self.net_load_min = np.zeros(self.time_num)


        # 向上灵活性需求
        self.ud_set = np.zeros(self.time_num)
        # 向下灵活性需求
        self.dd_set = np.zeros(self.time_num)

        self.x = np.zeros(len(self.params))
        self.real_x = np.zeros(len(self.params))

        self.__init()

    def __init(self):
        self.__getData()
        self.__set_params()
        self.__set_integrality()
        self.__set_c()

    # 计算向上灵活性需求及向下灵活性需求
    def __getData(self):
        # 净负荷预测值
        if self.type == "e":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx")
            self.predict_load = dataset['mu'].values
            self.predict_load = self.predict_load[:self.time_num]

        if self.type == "g":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_g.xlsx")
            self.predict_load = dataset['mu'].values
            self.predict_load = self.predict_load[:self.time_num]

        if self.type == "th":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_h.xlsx")
            self.predict_load = dataset['mu'].values
            self.predict_load = self.predict_load[:self.time_num]

        if self.type == "c":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_c.xlsx")
            self.predict_load = dataset['mu'].values
            self.predict_load = self.predict_load[:self.time_num]

        # 净负荷波动上下限
        if self.type == "e":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx")
            self.net_load_max = dataset['max'].values
            self.net_load_min = dataset['min'].values
            self.net_load_max = self.net_load_max[:self.time_num]
            self.net_load_min = self.net_load_min[:self.time_num]
        if self.type == "g":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_g.xlsx")
            self.net_load_max = dataset['max'].values
            self.net_load_min = dataset['min'].values
            self.net_load_max = self.net_load_max[:self.time_num]
            self.net_load_min = self.net_load_min[:self.time_num]
        if self.type == "th":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_h.xlsx")
            self.net_load_max = dataset['max'].values
            self.net_load_min = dataset['min'].values
            self.net_load_max = self.net_load_max[:self.time_num]
            self.net_load_min = self.net_load_min[:self.time_num]
        if self.type == "c":
            dataset = pd.read_excel(r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_c.xlsx")
            self.net_load_max = dataset['max'].values
            self.net_load_min = dataset['min'].values
            self.net_load_max = self.net_load_max[:self.time_num]
            self.net_load_min = self.net_load_min[:self.time_num]

    def __set_params(self):
        temp = np.array([
            # self.name + "Z_UD",  # 向上灵活性需求辅助变量
            # self.name + "Z_DD",  # 向下灵活性需求辅助变量
            self.name + "UD",  # 向上灵活性需求
            self.name + "DD",   # 向下灵活性需求
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_integrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_c(self):
        self.c = np.zeros(len(self.params))

        # for i in range(self.time_num):
        #     self.c[i] = 0.1
        #     self.c[i + self.time_num * 1] = 0.1

        if self.type == "e":
            for i in range(self.time_num):
                self.c[i] = 0.01
                self.c[i + self.time_num * 1] = 0.01
                # self.c[i + self.time_num * 2] = 0.1
                # self.c[i + self.time_num * 3] = 0.1

        if self.type == "g":
            for i in range(self.time_num):
                self.c[i] = 0.01
                self.c[i + self.time_num * 1] = 0.01
                # self.c[i + self.time_num * 2] = 0.1
                # self.c[i + self.time_num * 3] = 0.1

        if self.type == "th":
            for i in range(self.time_num):
                # self.c[i + self.time_num * 2] = 0.1        # -0.043
                # self.c[i + self.time_num * 3] = 0.1
                self.c[i] = 0.01
                self.c[i + self.time_num * 1] = 0.01

        if self.type == "c":
            for i in range(self.time_num):
                # self.c[i + self.time_num * 2] = 0.1            # -0.036
                # self.c[i + self.time_num * 3] = 0.1
                self.c[i] = 0.01
                self.c[i + self.time_num * 1] = 0.01

    def constraints(self, num):

        """ 约束条件 """
        # for i in range(self.time_num):
        #     B = np.array([
        #         [self.name + "UD" + str(i + 1), 1],
        #     ])
        #     CreatConstraintsByText(1, B, self.ud_set[i], self.ud_set[i], num)
        #
        # for i in range(self.time_num):
        #     B = np.array([
        #         [self.name + "DD" + str(i + 1), 1],
        #     ])
        #     CreatConstraintsByText(1, B, self.dd_set[i], self.dd_set[i], num)

        "电力子系统向上灵活性需求"
        if self.type == "e":
            B = np.array([
                [self.name + "UD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        # if self.type == "e":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, max(0, self.net_load_min[k+1] - self.predict_load[k],
        #                                          self.net_load_max[k + 1] - self.predict_load[k],
        #                                          self.net_load_max[k + 1] + self.net_load_min[k + 1]
        #                                          - 2 * self.predict_load[k]),
        #                                max(0, self.net_load_min[k + 1] - self.predict_load[k],
        #                                    self.net_load_max[k + 1] - self.predict_load[k],
        #                                    self.net_load_max[k + 1] + self.net_load_min[k + 1]
        #                                    - 2 * self.predict_load[k]), num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), -1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_min[k+1] - self.predict_load[k], np.inf, num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), -1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_max[k + 1] - self.predict_load[k], np.inf, num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), -2],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_max[k + 1] + self.net_load_min[k + 1] - 2 * self.predict_load[k], np.inf, num)


        "电力子系统向下灵活性需求"
        if self.type == "e":
            B = np.array([
                [self.name + "DD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        # if self.type == "e":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, max(0, self.predict_load[k] - self.net_load_min[k + 1],
        #                                          self.predict_load[k] - self.net_load_max[k + 1],
        #                                          2 * self.predict_load[k] - self.net_load_max[k + 1]
        #                                          - self.net_load_min[k + 1]),
        #                                max(0, self.predict_load[k] - self.net_load_min[k + 1],
        #                                    self.predict_load[k] - self.net_load_max[k + 1],
        #                                    2 * self.predict_load[k] - self.net_load_max[k + 1]
        #                                    - self.net_load_min[k + 1]), num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), 1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_min[k + 1], np.inf, num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), 1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_max[k + 1], np.inf, num)

        if self.type == "e":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "WT" or self.net_load_sets[i].devices[j].type == "PV":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "P" + str(k + 1), 2],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, 2 * self.predict_load[k] - self.net_load_max[k + 1] - self.net_load_min[k + 1], np.inf, num)

        if self.type == "e":
            B = np.array([
                [self.name + "UD24", 1],
            ])
            CreatConstraintsByText(1, B, 0, 0, num)
            B = np.array([
                [self.name + "DD24", 1],
            ])
            CreatConstraintsByText(1, B, 498.2124343, 498.2124343, num)

        # if self.type == "e":
        #     B = np.array([
        #         [self.name + "Z_UD1", 1],
        #         [self.name + "UD1", -1]
        #     ])
        #     CreatConstraintsByText(self.time_num, B, 0, 0, num)
        #     B = np.array([
        #         [self.name + "Z_DD1", 1],
        #         [self.name + "DD1", -1]
        #     ])
        #     CreatConstraintsByText(self.time_num, B, 0, 0, num)

        "热能子系统向上灵活性需求"
        if self.type == "th":
            B = np.array([
                [self.name + "UD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        # if self.type == "th":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, max(0, self.net_load_min[k+1] - self.predict_load[k],
        #                                          self.net_load_max[k + 1] - self.predict_load[k],
        #                                          self.net_load_max[k + 1] + self.net_load_min[k + 1]
        #                                          - 2 * self.predict_load[k]),
        #                                max(0, self.net_load_min[k + 1] - self.predict_load[k],
        #                                    self.net_load_max[k + 1] - self.predict_load[k],
        #                                    self.net_load_max[k + 1] + self.net_load_min[k + 1]
        #                                    - 2 * self.predict_load[k]), num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), -1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_min[k+1] - self.predict_load[k], np.inf, num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), -1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_max[k + 1] - self.predict_load[k], np.inf, num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), -2],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.net_load_max[k + 1] + self.net_load_min[k + 1] - 2 * self.predict_load[k], np.inf, num)

        "热能子系统向下灵活性需求"
        if self.type == "th":
            B = np.array([
                [self.name + "DD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        # if self.type == "th":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, max(0, self.predict_load[k] - self.net_load_min[k + 1],
        #                                          self.predict_load[k] - self.net_load_max[k + 1],
        #                                          2 * self.predict_load[k] - self.net_load_max[k + 1]
        #                                          - self.net_load_min[k + 1]),
        #                                max(0, self.predict_load[k] - self.net_load_min[k + 1],
        #                                    self.predict_load[k] - self.net_load_max[k + 1],
        #                                    2 * self.predict_load[k] - self.net_load_max[k + 1]
        #                                    - self.net_load_min[k + 1]), num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), 1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_min[k + 1], np.inf, num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), 1],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_max[k + 1], np.inf, num)

        if self.type == "th":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                for i in range(len(self.net_load_sets)):
                    for j in range(len(self.net_load_sets[i].devices)):
                        if self.net_load_sets[i].devices[j].type == "HP":
                            B = np.append(B, np.array([
                                [self.net_load_sets[i].devices[j].name + "output_h" + str(k + 1), 2],
                            ]))
                B = B.reshape(int(len(B) / 2), 2)
                CreatConstraintsByText(1, B, 2 * self.predict_load[k] - self.net_load_max[k + 1] - self.net_load_min[k + 1], np.inf, num)
        #
        if self.type == "th":
            B = np.array([
                [self.name + "UD24", 1],
            ])
            CreatConstraintsByText(1, B, 432.453534265, 432.453534265, num)
            B = np.array([
                [self.name + "DD24", 1],
            ])
            CreatConstraintsByText(1, B, 0, 0, num)

        # if self.type == "th":
        #     B = np.array([
        #         [self.name + "Z_UD1", 1],
        #         [self.name + "UD1", -1]
        #     ])
        #     CreatConstraintsByText(self.time_num, B, 0, 0, num)
        #     B = np.array([
        #         [self.name + "Z_DD1", 1],
        #         [self.name + "DD1", -1]
        #     ])
        #     CreatConstraintsByText(self.time_num, B, 0, 0, num)

        "气能子系统向上灵活性需求"
        if self.type == "g":
            B = np.array([
                [self.name + "UD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        if self.type == "g":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                CreatConstraintsByText(1, B, max(0, self.net_load_min[k+1] - self.predict_load[k],
                                                 self.net_load_max[k + 1] - self.predict_load[k],
                                                 self.net_load_max[k + 1] + self.net_load_min[k + 1]
                                                 - 2 * self.predict_load[k]),
                                       max(0, self.net_load_min[k + 1] - self.predict_load[k],
                                           self.net_load_max[k + 1] - self.predict_load[k],
                                           self.net_load_max[k + 1] + self.net_load_min[k + 1]
                                           - 2 * self.predict_load[k]), num)

        # if self.type == "g":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.net_load_min[k+1] - self.predict_load[k], np.inf, num)
        #
        # if self.type == "g":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.net_load_max[k + 1] - self.predict_load[k], np.inf, num)

        "气能子系统向下灵活性需求"
        if self.type == "g":
            B = np.array([
                [self.name + "DD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        if self.type == "g":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                CreatConstraintsByText(1, B, max(0, self.predict_load[k] - self.net_load_min[k + 1],
                                                 self.predict_load[k] - self.net_load_max[k + 1],
                                                 2 * self.predict_load[k] - self.net_load_max[k + 1]
                                                 - self.net_load_min[k + 1]),
                                       max(0, self.predict_load[k] - self.net_load_min[k + 1],
                                           self.predict_load[k] - self.net_load_max[k + 1],
                                           2 * self.predict_load[k] - self.net_load_max[k + 1]
                                           - self.net_load_min[k + 1]), num)

        # if self.type == "g":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_min[k+1], np.inf, num)
        #
        # if self.type == "g":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_max[k + 1], np.inf, num)

        if self.type == "g":
            B = np.array([
                [self.name + "UD24", 1],
            ])
            CreatConstraintsByText(1, B, 0, 0, num)
            B = np.array([
                [self.name + "DD24", 1],
            ])
            CreatConstraintsByText(1, B, 153.432564376, 153.432564376, num)

        "冷能子系统向上灵活性需求"
        if self.type == "c":
            B = np.array([
                [self.name + "UD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        if self.type == "c":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "UD" + str(k + 1), 1],
                ])
                CreatConstraintsByText(1, B, max(0, self.net_load_min[k+1] - self.predict_load[k],
                                                 self.net_load_max[k + 1] - self.predict_load[k],
                                                 self.net_load_max[k + 1] + self.net_load_min[k + 1]
                                                 - 2 * self.predict_load[k]),
                                       max(0, self.net_load_min[k + 1] - self.predict_load[k],
                                           self.net_load_max[k + 1] - self.predict_load[k],
                                           self.net_load_max[k + 1] + self.net_load_min[k + 1]
                                           - 2 * self.predict_load[k]), num)

        # if self.type == "c":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.net_load_min[k+1] - self.predict_load[k], np.inf, num)
        #
        # if self.type == "c":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "UD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.net_load_max[k + 1] - self.predict_load[k], np.inf, num)

        "冷能子系统向下灵活性需求"
        if self.type == "c":
            B = np.array([
                [self.name + "DD1", 1],
            ])
            CreatConstraintsByText(self.time_num - 1, B, 0, np.inf, num)

        if self.type == "c":
            for k in range(self.time_num - 1):
                B = np.array([
                    [self.name + "DD" + str(k + 1), 1],
                ])
                CreatConstraintsByText(1, B, max(0, self.predict_load[k] - self.net_load_min[k + 1],
                                                 self.predict_load[k] - self.net_load_max[k + 1],
                                                 2 * self.predict_load[k] - self.net_load_max[k + 1]
                                                 - self.net_load_min[k + 1]),
                                       max(0, self.predict_load[k] - self.net_load_min[k + 1],
                                           self.predict_load[k] - self.net_load_max[k + 1],
                                           2 * self.predict_load[k] - self.net_load_max[k + 1]
                                           - self.net_load_min[k + 1]), num)

        # if self.type == "c":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_min[k+1], np.inf, num)
        #
        # if self.type == "c":
        #     for k in range(self.time_num - 1):
        #         B = np.array([
        #             [self.name + "DD" + str(k + 1), 1],
        #         ])
        #         CreatConstraintsByText(1, B, self.predict_load[k] - self.net_load_max[k + 1], np.inf, num)

        if self.type == "c":
            B = np.array([
                [self.name + "UD24", 1],
            ])
            CreatConstraintsByText(1, B, 0, 0, num)
            B = np.array([
                [self.name + "DD24", 1],
            ])
            CreatConstraintsByText(1, B, 4.3146341432, 4.3146341432, num)
