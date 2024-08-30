import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText

class FA:
    def __init__(self, name, node, time_num):
        self.className = "FA"

        self.name = name

        self.node = node
        self.time_num = time_num

        # 向上向下灵活性供给
        self.us_set = 0
        self.ds_set = 0

        # 向上向下灵活性需求
        self.ud_set = 0
        self.dd_set = 0

        self.params = np.array([""])

        self.__init()

    def __init(self):
        self.__params_named()
        self.__get_analysis()
        self.__set_C()

    def __params_named(self):
        temp = np.array([
            # 恒为1的数
            # 向上灵活性缺额
            self.name + "S_U",
            # 向下灵活性缺额
            self.name + "S_D"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __get_analysis(self):
        for node in self.node:
            for device in node.devices:
                if device.className == "cchp":
                    self.us_set += device.x[self.time_num * 5: self.time_num * 7]
                    self.us_set += device.x[self.time_num * 8: self. time_num * 9]
                    self.ds_set += device.x[self.time_num * 4: self.time_num * 5]
                    self.ds_set += device.x[self.time_num * 7: self.time_num * 8]
                    self.ds_set += device.x[self.time_num * 9:]

                if device.className == "eb":
                    self.us_set += device.x[self.time_num * 4: self.time_num * 6]
                    self.ds_set += device.x[self.time_num * 3: self.time_num * 4]
                    self.ds_set += device.x[self.time_num * 6:]

                if device.className == "er":
                    self.us_set += device.x[self.time_num * 4: self.time_num * 6]
                    self.ds_set += device.x[self.time_num * 3: self.time_num * 4]
                    self.ds_set += device.x[self.time_num * 6: self.time_num * 7]

                if device.className == "S":
                    self.us_set += device.x[self.time_num * 5: self.time_num * 6]
                    self.ds_set += device.x[self.time_num * 6: self.time_num * 7]

                if device.className == "FL":
                    self.us_set += device.x[self.time_num * 2: self.time_num * 3]
                    self.ds_set += device.x[self.time_num * 3: self.time_num * 4]

    def __set_C(self):
        self.c = np.zeros(len(self.params))


    def constraints(self, num):
        # 恒为1约束
        B = np.array([
            [self.name + "S_U1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 1, 1, num)
        B = np.array([
            [self.name + "S_D1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 1, 1, num)







