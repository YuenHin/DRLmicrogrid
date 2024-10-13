import numpy as np
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawRG import drawRG
from tools.aDataSetting import smooth

import random

class RT:
    def __init__(self, name, type ,id, production_price, production_total, time_num, stochastic_value = 10):
        self.name = name
        self.id = id

        self.way = 1

        self.production_price = production_price
        self.production_total = production_total

        self.type =type
        self.className = 'RT'
        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = np.zeros(time_num)
        self.p_max = np.zeros(time_num)

        self.p_rampingh_up = np.zeros(time_num)
        self.p_rampingh_down = np.zeros(time_num)


        self.params = np.array([""])

        #self.day = int(self.time_num / 24)
        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.stochastic_value = stochastic_value
        #用来记录每一个
        self.contraint_num = 0

        self.stochas_P = np.zeros(self.time_num)  # 记录每一步增加随机性后的功率（除了第一步）

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "P",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(self.time_num)

    def __set_C(self):
        self.c = np.zeros(self.time_num)
        "1"
        "产能成本"
        self.c = self.c - self.production_price - 0.09 * 0.001 * 390.885
        # self.c = self.c
    def __getData(self):
        "导入可再生能源产能"
        if self.type == "WT":
            self.__getWTData()
        if self.type == "PV":
            self.__getPVData()
        "计算每小时最小值"
        "计算每个小时最大值"


        # self.p = self.p.reshape((1, self.time_num))
        "获得一维数组，单位是kwh"
        # self.p = self.p[0]
        for i in range(len(self.p)):
            if self.p[i] < 0 :
                self.p[i] = 0
        self.p_max = self.p

        if self.type == "PV":
            # self.p_rampingh_up = (self.p_max ) * 0.5
            # self.p_rampingh_down = (self.p_max ) * 0.5
            self.p_rampingh_up[0] = self.p_max[0]
            for i in range(self.time_num-1):
                self.p_rampingh_up[i+1] = abs(self.p_max[i+1] - self.p_max[i])
                self.p_rampingh_down[i+1] = self.p_rampingh_up[i+1]
        if self.type == "WT":
            self.p_rampingh_up = (self.p_max ) * 0.1
            self.p_rampingh_down = (self.p_max ) * 0.1

    def __getWTData(self):
        self.p = self.__24to96("./Data/RE/WT.xlsx", 2)

    def __getPVData(self):
        self.p = self.__24to96("./Data/RE/PV.xlsx", 2)



    def constraints(self, num):
        "production limits:"
        for i in range(self.time_num):
            B = np.array([
                [self.name + "P" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.p_min[i], self.p_max[i], num)

        "可再生能源不设置爬坡约束"
        "Ramping limits:"
        # B = np.array([
        #     [self.name + "P1", 1]
        # ])
        # CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[0], num)
        # for i in range(self.time_num - 1):
        #     B = np.array([
        #         [self.name + "P" + str(i + 1), -1],
        #         [self.name + "P"+ str(i + 2), 1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[i+1], num)
        #
        # B = np.array([
        #     [self.name + "P1", 1]
        # ])
        # CreatConstraintsByText(1, B, 0, np.inf, num)
        # for i in range(self.time_num - 1):
        #     B = np.array([
        #         [self.name + "P" + str(i + 1), 1],
        #         [self.name + "P"+ str(i + 2), -1]
        #     ])
        #     CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_down[i+1], num)

    def draw(self):
        drawRG(self.x, self.p_max, self.p_min, self.p_rampingh_up, self.p_rampingh_down, None, title=self.name + "RG")

    def __24to96(self, path, y_index):
        p = self.__downLoad_load(path, y_index)
        p = self.__creatY_96(p)
        return p * self.production_total

        # 顺滑Y轴24->96

    def __creatY_96(self, p):
        x = np.arange(1, len(p) + 1 , 1)
        x, p = smooth(x, p, self.time_num)
        return p

        # 加载Y轴数据

    def __downLoad_load(self, path, y_index):
        p = getDataFromExcel(path, y_index, y_index + 1, 1, 25)
        return p

    #依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
    def stochastic(self, step, num, mpc_num):

        # 我需要控制不确定变化后不会跳出范围
        #self.real_x[step - 1] = self.x[step - 1] * (1 + (random.random() * self.stochastic_value * 0.01))
        ran = random.choice([1, -1])
        # ran=1，真实出力值向上波动
        if ran == 1:
            self.real_x[step - 1] = self.x[step - 1] * (1 + (random.random() * self.stochastic_value * 0.01))
        # ran=-1，真实出力值向下波动
        if ran == -1:
            self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * self.stochastic_value * 0.01))

        # self.real_x[step - 1] = self.x[step - 1]

        if self.real_x[step - 1] > self.p_max[step - 1]:
            #num.bu[self.contraint_num + step - 1] = self.real_x[step - 1]
            # self.p_max[step - 1] = self.real_x[step - 1]
            self.real_x[step - 1] = self.p_max[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            #num.bl[self.contraint_num + step - 1] = self.real_x[step - 1]
            # self.p_min[step - 1] = self.real_x[step - 1]
            self.real_x[step - 1] = self.p_min[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], mpc_num)

        self.stochas_P[step - 1] = self.real_x[step - 1]  # 记录这一步增加随机性后的功率
        '''
        if step > 1 :
            if (self.real_x[step - 1] - self.real_x[step - 2]) > self.p_rampingh_up[step - 1]:
                a = self.real_x[step - 1]
                b = self.real_x[step - 2]
                c = self.p_rampingh_up[step - 1]
                self.real_x[step - 1] = self.real_x[step - 2] + self.p_rampingh_up[step - 1]
                # num.bu[self.contraint_num + self.time_num + step - 1] = np.inf
            if (self.real_x[step - 2] - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                d = self.real_x[step - 2]
                e = self.real_x[step - 1]
                f = self.p_rampingh_down[step - 1]
                self.real_x[step - 1] = self.real_x[step - 2] - self.p_rampingh_down[step - 1]
                # num.bu[self.contraint_num + self.time_num * 2 + step - 1 ] = np.inf
        if step == 1 :
            if (self.real_x[step - 1]) > self.p_rampingh_up[step - 1]:
                self.real_x[step - 1] = self.p_rampingh_up[step - 1]
                # num.bu[self.contraint_num + self.time_num + step - 1] = np.inf
            if ( - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                self.real_x[step - 1] = self.p_rampingh_down[step - 1]
                # num.bu[self.contraint_num + self.time_num * 2 + step - 1] = np.inf
        '''

    def retrain(self, step, num):
        num.bu[self.contraint_num + self.time_num + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step - 1] = np.inf
        num.bu[self.contraint_num + self.time_num + step] = np.inf
        num.bu[self.contraint_num + self.time_num * 2 + step] = np.inf