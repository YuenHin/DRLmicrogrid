import numpy as np


class MMGs:
    def __init__(self, MG):
        self.MG = MG

        self.contraint_num = np.array([])





    """
    每一个区域能源售价不一样
    """
    def price(self):
        for MG in self.MG:
            MG.price_e()
            MG.price_g()
            MG.price_th()
            MG.price_h()
    """
    绘制数据表格
    """
    def draw(self):
        for MG in self.MG:
            MG.draw()

    #计算step下的操作成本


    """
    计算操作成本
    """
    def countCost(self):
        target = 0
        operation_cost = 0
        profit = 0
        carbom_emission = 0

        for MG in self.MG:
            for node in MG.node:
                for devices in node.devices:
                    # pp生产成本
                    if devices.className == "CPP":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[devices.time_num + i] * devices.production_price[i] * (24 / devices.time_num)
                            carbom_emission += devices.x[devices.time_num + i] * 0.839 * (24 / devices.time_num)
                            profit += devices.x[devices.time_num * 2 + i] * 0.315 * (24 / devices.time_num)
                    # gw生产成本
                    if devices.className == "GW":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.production_price * (24 / devices.time_num)
                            carbom_emission += devices.x[i] * 0.368 * (24 / devices.time_num)
                    # pv生产成本
                    # wt生产成本
                    if devices.className == "RT":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.production_price * (24 / devices.time_num)
                            carbom_emission += devices.x[i] * 0.09 * (24 / devices.time_num)
                    # dg生产成本
                    if devices.className == "DG":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.production_price * (24 / devices.time_num)
                            carbom_emission += devices.x[i] * 0.839 * (24 / devices.time_num)
                    # 储能碳排放
                    if devices.className == "S":
                        for i in range(devices.time_num):
                            carbom_emission += devices.x[devices.time_num * 2 + i] * 0.083 * (24 / devices.time_num)
                            carbom_emission += devices.x[devices.time_num * 3 + i] * 0.083 * (24 / devices.time_num)
                    # tp碳排放
                    if devices.className == "TP":
                        for i in range(devices.time_num):
                            carbom_emission += devices.x[i] * 0.12 * (24 / devices.time_num)
                    # ctp碳排放
                    if devices.className == "CTP":
                        for i in range(devices.time_num):
                            carbom_emission += devices.x[i] * 0.181 * (24 / devices.time_num)

        carbom_emission = carbom_emission * 0.001
        carbom_emission_cost = carbom_emission * 390.885

        print("opeation cost:", operation_cost)
        print("carom emission:", carbom_emission)
        print("carom emission cost:", carbom_emission_cost)
        print("profit:", profit)
        print("total cost:", operation_cost + carbom_emission_cost - profit)
        return operation_cost, carbom_emission, carbom_emission_cost, profit, operation_cost + carbom_emission_cost - profit

    def fix_SE_DG(self, num):
        for MG in self.MG:
            for node in MG.node:
                for devices in node.devices:
                    if  devices.className == "S" :
                        devices.fix(num)

    def count_contrainst_num(self):
        for MG in self.MG:
            self.contraint_num = np.append(self.contraint_num, MG.contraint_num)
        #print(self.contrainst_num)
    def getting_contrainst_num(self):
        return self.contraint_num
    def save_contrainst_num(self, num):
        np.save(num.path + "contrainst_num", self.contraint_num)
    def Load_contrainst_num(self, num):

        self.contraint_num = np.load(num.path + "contrainst_num.npy")
        self.__pull_contrainst_num()

    #下放的过程
    def __pull_contrainst_num(self):
        i = 0
        for MG in self.MG:
            for node in MG.node:
                for device in node.devices:
                    device.contraint_num = int(self.contraint_num[i])
                    i += 1
                for sline in node.sLine:
                    sline.constraint_num = int(self.contraint_num[i])
                    i += 1
                for rline in node.rLine:
                    rline.constraint_num = int(self.contraint_num[i])
                    i += 1
                node.constraint_num = int(self.contraint_num[i])
                i += 1




