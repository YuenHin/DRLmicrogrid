import math

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
                    # cpp生产成本
                    if devices.className == "CPP":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.c[i] * (24 / devices.time_num)
                            carbom_emission += devices.x[i] * 0.839 * (24 / devices.time_num)
                            # profit += devices.x[devices.time_num * 2 + i] * 0.315 * (24 / devices.time_num)
                    # gw生产成本
                    if devices.className == "GW":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.c[i] * (24 / devices.time_num)
                            carbom_emission += devices.x[i] * 0.368 * (24 / devices.time_num)
                    # pv生产成本
                    # wt生产成本
                    if devices.className == "RT":
                        for i in range(devices.time_num):
                            operation_cost += devices.x[i] * devices.c[i] * (24 / devices.time_num)
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

    def countCost_RO(self, res):
        operation_cost = 0
        carbom_emission = 0
        gap_punishment = 0
        ramping_punishment = 0
        punishment2 = 0
        punishment3 = 0
        punishment4 = 0
        ramping_p = 0
        for MG in self.MG:
            for node in MG.node:
                for device in node.devices:
                    # cpp生产成本
                    if device.className == "CPP":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (24 / device.time_num)
                            # CPP的惩罚项
                            gap_punishment += device.p_gap[step_time] * 1

                    # gw生产成本
                    if device.className == "GW":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (24 / device.time_num)
                            # GW的惩罚项
                            gap_punishment += device.p_gap[step_time] * 1

                    # pv生产成本
                    # wt生产成本
                    if device.className == "RT" and (device.type == "PV" or device.type == "WT"):
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (24 / device.time_num)

                    if device.className == "RT" and device.type == "HP":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[device.time_num * 1 +step_time] * (24 / device.time_num)

                    # 储能成本
                    if device.className == "S":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                        24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 2 + step_time] * device.c[
                                device.time_num * 2 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 3 + step_time] * device.c[
                                device.time_num * 3 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 4 + step_time] * device.c[
                                device.time_num * 4 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 5 + step_time] * device.c[
                                device.time_num * 5 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 6 + step_time] * device.c[
                                device.time_num * 6 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 7 + step_time] * device.c[
                                device.time_num * 7 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 8 + step_time] * device.c[
                                device.time_num * 8 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 9 + step_time] * device.c[
                                device.time_num * 9 + step_time] * (24 / device.time_num)
                            # 是否超出ramping_limit的约束，超出的部分乘一个系数
                            # 当前容量等于0时，扣大分
                            # t=24时容量如果小于最大容量的一半，扣大分
                            if device.type != 'c':
                                if step_time == 0:
                                    ramping_p = abs(device.real_E[step_time] - (device.e / 2)) - device.ramping_limit
                                else:
                                    ramping_p = abs(device.real_E[step_time] - device.real_E[step_time - 1]) - device.ramping_limit
                                if ramping_p > 0:
                                    ramping_punishment += ramping_p * 50
                                # punishment4 += (device.real_E[step_time] >= device.e) * 300
                                punishment2 += (device.real_E[step_time] <= 0) * 200
                                punishment3 += (step_time+1 == device.time_num and device.real_E[step_time] < device.e / 2) * 400

                                a = device.time_num - math.ceil(device.e / 2 / device.ramping_limit)
                                if step_time+1 - a > 0 and step_time < 23:
                                    b = step_time+1 - a
                                    if device.real_E[step_time] < device.ramping_limit * b:
                                        punishment3 += 300

                    # 能量转化设备成本
                    if device.className == "er":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                    24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 2 + step_time] * device.c[
                                device.time_num * 2 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 3 + step_time] * device.c[
                                device.time_num * 3 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 4 + step_time] * device.c[
                                device.time_num * 4 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 5 + step_time] * device.c[
                                device.time_num * 5 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 6 + step_time] * device.c[
                                device.time_num * 6 + step_time] * (24 / device.time_num)

                    if device.className == "eb":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                    24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 2 + step_time] * device.c[
                                device.time_num * 2 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 3 + step_time] * device.c[
                                device.time_num * 3 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 4 + step_time] * device.c[
                                device.time_num * 4 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 5 + step_time] * device.c[
                                device.time_num * 5 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 6 + step_time] * device.c[
                                device.time_num * 6 + step_time] * (24 / device.time_num)

                    if device.className == "cchp":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                    24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 2 + step_time] * device.c[
                                device.time_num * 2 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 3 + step_time] * device.c[
                                device.time_num * 3 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 4 + step_time] * device.c[
                                device.time_num * 4 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 5 + step_time] * device.c[
                                device.time_num * 5 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 6 + step_time] * device.c[
                                device.time_num * 6 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 7 + step_time] * device.c[
                                device.time_num * 7 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 8 + step_time] * device.c[
                                device.time_num * 8 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 9 + step_time] * device.c[
                                device.time_num * 9 + step_time] * (24 / device.time_num)

                    # 负荷
                    if device.className == "D":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                        24 / device.time_num)

                    # 柔性负荷
                    if device.className == "FL":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                        24 / device.time_num)

                    # 灵活性需求
                    if device.className == "FD":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                        24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)

                    # 灵活性分析
                    if device.className == "FA":
                        for step_time in range(device.time_num):
                            operation_cost += device.x[step_time] * device.c[step_time] * (
                                    24 / device.time_num)
                            operation_cost += device.x[device.time_num * 1 + step_time] * device.c[
                                device.time_num * 1 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 2 + step_time] * device.c[
                                device.time_num * 2 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 3 + step_time] * device.c[
                                device.time_num * 3 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 4 + step_time] * device.c[
                                device.time_num * 4 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 5 + step_time] * device.c[
                                device.time_num * 5 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 6 + step_time] * device.c[
                                device.time_num * 6 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 7 + step_time] * device.c[
                                device.time_num * 7 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 8 + step_time] * device.c[
                                device.time_num * 8 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 9 + step_time] * device.c[
                                device.time_num * 9 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 10 + step_time] * device.c[
                                device.time_num * 10 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 11 + step_time] * device.c[
                                device.time_num * 11 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 12 + step_time] * device.c[
                                device.time_num * 12 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 13 + step_time] * device.c[
                                device.time_num * 13 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 14 + step_time] * device.c[
                                device.time_num * 14 + step_time] * (24 / device.time_num)
                            operation_cost += device.x[device.time_num * 15 + step_time] * device.c[
                                device.time_num * 15 + step_time] * (24 / device.time_num)


        es_punishment = ramping_punishment + punishment2 + punishment3 + punishment4
        milp_operation_cost = res.fun
        total_cost = operation_cost + es_punishment + gap_punishment
        print("operation cost:", operation_cost)
        print("total cost:", total_cost)
        print("milp operation cost:", 89160.7224)
        print("total es_punishment:", es_punishment)
        print("total gap_punishment:", gap_punishment)
        return operation_cost, es_punishment, gap_punishment, 0, total_cost

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




