import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from aDataSetting import smooth

class FD:
    def __init__(self, name, type, fluctuation_rate, time_num):
        self.className = "FD"
        self.name = name

        # type "e,g,th,c"
        self.type = type
        self.fluctuation_rate = fluctuation_rate

        self.time_num = time_num

        # 净负荷预测值
        if self.type == "e":
            self.predict_load = self.__24to96("C:\software\Github\DRLmicrogrid\Data\Load\predict_e.xlsx", 1)
            self.predict_pv = self.__24to96("C:\software\Github\DRLmicrogrid\Data\RE\PV.xlsx", 1)
            self.predict_wt = self.__24to96("C:\software\Github\DRLmicrogrid\Data\RE\WT.xlsx", 1)
            self.net_load = self.predict_load - self.predict_pv - self.predict_wt
        if self.type == "g":
            self.net_load = self.__24to96("Data/Load/predict_g.xlsx", 1)
        if self.type == "th":
            self.predict_load = self.__24to96("Data/Load/predict_th.xlsx", 1)
            self.predict_hp = self.__24to96("Data/RE/WT.xlsx", 1)
            self.net_load = self.predict_load - self.predict_hp
        if self.type == "c":
            self.net_load = self.__24to96("Data/Load/predict_c.xlsx", 1)

        # 净负荷波动上限
        self.net_load_max = self.net_load * (1 + fluctuation_rate)
        # 净负荷波动下限
        self.net_load_min = self.net_load * (1 - fluctuation_rate)

        # 向上灵活性需求
        self.ud_set = np.zeros(self.time_num)
        # 向下灵活性需求
        self.dd_set = np.zeros(self.time_num)

        self.__init()

    def __init(self):
        self.__getData()

    # 计算向上灵活性需求及向下灵活性需求
    def __getData(self):
        for i in range(self.time_num-1):
            # 向上灵活性需求计算
            self.ud_set[i] = max(0, self.net_load_min[i+1]-self.net_load[i], self.net_load_max[i+1]-self.net_load[i])
            if self.net_load_min[i+1]-self.net_load[i] > 0 and self.net_load_max[i+1]-self.net_load[i] > 0:
                self.ud_set[i] = self.net_load_min[i+1]-self.net_load[i] + self.net_load_max[i+1]-self.net_load[i]
            # 向下灵活性需求计算
            self.dd_set[i] = max(0, self.net_load[i]-self.net_load_min[i+1], self.net_load[i]-self.net_load_max[i+1])
            if self.net_load[i]-self.net_load_min[i+1] > 0 and self.net_load[i]-self.net_load_max[i+1] > 0:
                self.dd_set[i] = self.net_load[i]-self.net_load_min[i+1] + self.net_load[i]-self.net_load_max[i+1]

    def __24to96(self, path, y_index):
        p = self.__downLoad_load(path, y_index)
        p = self.__creatY_96(p)
        return p

        # 顺滑Y轴24->96

    def __creatY_96(self, p):
        x = np.arange(1, len(p) + 1, 1)
        x, p = smooth(x, p, self.time_num)
        return p

        # 加载Y轴数据

    def __downLoad_load(self, path, y_index):
        p = getDataFromExcel(path, y_index, y_index + 1, 1, 25)
        return p


# fd_e = FD("fd_e", "e", 0.1, 24)
# print(fd_e.predict_load)
# print(fd_e.predict_pv)
# print(fd_e.predict_wt)
# print(fd_e.net_load)
# print(fd_e.ud_set)
# print(fd_e.dd_set)


