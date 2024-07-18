import numpy as np
from tools.maybeExcel import getDataFromExcel

from tools.drawMG import drawPrice, drawSource_Load_e, drawSource_Load_g, drawSource_Load_th, drawSource_Load_h, drawInteraction

from tools.drawDemands import drawDemands

class MG:
    def __init__(self, name, node, id, type, time_num):
        self.time_num = time_num
        self.id = id
        self.node = node
        self.name = name
        self.type = type

        self.CPP_e_price = None
        self.DG_e_price = None
        self.PV_e_price = None
        self.WT_e_price = None
        self.Day_sell_e_price = None

        self.contraint_num = np.array([])

    """
    区域内电价出售定价
    """
    def price_e(self):
        "获取电力售电价格"
        # GBP / MWh
        Day_price = getDataFromExcel("Data\power_price.xls", 1 + self.id, 2 + self.id, 2, 2 + 24)
        tempArray = np.zeros(24)

        for i in range(len(Day_price)):
            tempNum = 10
            temp = 0
            for j in range(len(Day_price)):
                if Day_price[i][0][j] != ',':
                    temp = temp + float(Day_price[i][0][j]) * tempNum
                    tempNum = tempNum / 10
            tempArray[i] = temp
        Day_price = tempArray
        #USD/KWH
        Day_price = Day_price / 1000 * 1.1125
        self.Day_sell_e_price = Day_price

        "计算实验各时间结点电价:"
        price_e = np.zeros(0)
        for i in range(int(self.time_num / 24)):
            price_e = np.append(price_e, Day_price)

        "通知给各个需求节点、获得区域售价"
        for node in self.node:
            for device in node.devices:
                if device.className == 'D' and device.type == 'e':
                    device.c = price_e
                if device.className == 'CPP':
                    self.CPP_e_price = device.production_price
                if device.className == 'DG':
                    self.DG_e_price = device.production_price
                if device.className == 'RT' and device.type == 'WT':
                    self.WT_e_price = device.production_price
                if device.className == 'RT' and device.type == 'PV':
                    self.PV_e_price = device.production_price

    """
        区域内天然气价格
        """

    def price_g(self):
        Day_price = getDataFromExcel("Data\gas_price.xlsx", 1 + self.id, 2 + self.id, 2, 2 + 24)
        tempArray = np.zeros(24)

        for i in range(len(Day_price)):
            tempNum = 10
            temp = 0
            for j in range(len(Day_price[i][0])):
                if Day_price[i][0][j] != ',':
                    temp = temp + float(Day_price[i][0][j]) * tempNum
                    tempNum = tempNum / 10
            tempArray[i] = temp
        Day_price = tempArray
        # USD/KWH
        Day_price = Day_price / 1000 * 1.1125
        self.Day_sell_g_price = Day_price

        "计算实验各时间结点电价:"
        price_g = np.zeros(0)
        for i in range(int(self.time_num / 24)):
            price_g = np.append(price_g, Day_price)

        "通知给各个需求节点、获得区域售价"
        for node in self.node:
            for device in node.devices:
                if device.className == 'D' and device.type == 'g':
                    device.c = price_g

    """
    区域内热能价格
    """

    def price_th(self):
        Day_price = getDataFromExcel("Data\\thermal_price.xlsx", 1 + self.id, 2 + self.id, 2, 2 + 24)
        tempArray = np.zeros(24)

        for i in range(len(Day_price)):
            tempNum = 10
            temp = 0
            for j in range(len(Day_price[i][0])):
                if Day_price[i][0][j] != ',':
                    temp = temp + float(Day_price[i][0][j]) * tempNum
                    tempNum = tempNum / 10
            tempArray[i] = temp
        Day_price = tempArray
        # USD/KWH
        Day_price = Day_price / 1000 * 1.1125
        self.Day_sell_th_price = Day_price

        "计算实验各时间结点电价:"
        price_th = np.zeros(0)
        for i in range(int(self.time_num / 24)):
            price_th = np.append(price_th, Day_price)

        "通知给各个需求节点、获得区域售价"
        for node in self.node:
            for device in node.devices:
                if device.className == 'D' and device.type == 'th':
                    device.c = price_th

    """
    区域内氢能价格
    """

    def price_h(self):
        Day_price = getDataFromExcel("Data\hygrogen_price.xlsx", 1 + self.id, 2 + self.id, 2, 2 + 24)
        tempArray = np.zeros(24)

        for i in range(len(Day_price)):
            tempNum = 10
            temp = 0
            for j in range(len(Day_price[i][0])):
                if Day_price[i][0][j] != ',':
                    temp = temp + float(Day_price[i][0][j]) * tempNum
                    tempNum = tempNum / 10
            tempArray[i] = temp
        Day_price = tempArray
        # USD/KWH
        Day_price = Day_price / 1000 * 1.1125
        self.Day_sell_h_price = Day_price

        "计算实验各时间结点电价:"
        price_h = np.zeros(0)
        for i in range(int(self.time_num / 24)):
            price_h = np.append(price_h, Day_price)

        "通知给各个需求节点、获得区域售价"
        for node in self.node:
            for device in node.devices:
                if device.className == 'D' and device.type == 'h':
                    device.c = price_h

    """
        1.数据采集：P 类型 累加在一起做成区域的
        用户需求（目前先做电的）、标志device.className = "D" and type == 'e'
        风力发电、标志device.className == "RT" and device.type == "WT"
        光伏发电、标志device.className = "RT" and device.type == "PV"
        电池、标志device.className = "S" 这个是充电为正噢！
        直流发电机：device.className == "DG"
        大电网:line.MG_point == "True" and type == 'e'

        来自天然气的：
        来自热能的：
        来自氢能的：
        """

    def P_e_collection(self):
        self.D_P_e = np.zeros(self.time_num)
        self.WT_P = np.zeros(self.time_num)
        self.PV_P = np.zeros(self.time_num)
        self.S_P_e = np.zeros(self.time_num)
        self.DG_P = np.zeros(self.time_num)
        self.MG_P_e = np.zeros(self.time_num)
        self.P_CTP_e = np.zeros(self.time_num)
        self.P_TP_e = np.zeros(self.time_num)
        self.P_EL_e = np.zeros(self.time_num)
        self.P_e_h = np.zeros(self.time_num)

        self.D_P_max_e = np.zeros(self.time_num)
        self.D_P_min_e = np.zeros(self.time_num)
        self.D_P_ramping_e = np.zeros(self.time_num)

        self.key_e = False

        for node in self.node:
            for device in node.devices:
                if device.className == "D" and device.type == "e":
                    self.D_P_e = self.D_P_e + device.x[:self.time_num]

                    self.D_P_max_e = self.D_P_max_e + device.p_max
                    self.D_P_min_e = self.D_P_min_e + device.p_min
                    self.D_P_ramping_e = self.D_P_ramping_e + device.ramping
                    self.key_e = True

                if device.className == "RT" and device.type == "WT":
                    self.WT_P = self.WT_P + device.x[:self.time_num]
                if device.className == "RT" and device.type == "PV":
                    self.PV_P = self.PV_P + device.x[:self.time_num]
                if device.className == "S" and device.type == 'e':
                    self.S_P_e = self.S_P_e - device.x[:self.time_num]
                if device.className == "DG":
                    self.DG_P = self.DG_P + device.x[:self.time_num]
                if device.className == "CTP":
                    self.P_CTP_e += device.x[self.time_num:self.time_num * 2]
                if device.className == "TP":
                    self.P_TP_e -= device.x[:self.time_num]
                if device.className == "EL":
                    self.P_EL_e -= device.x[:self.time_num]

            for rline in node.rLine:
                if rline.MG_point and rline.type == 'e':
                    self.MG_P_e = self.MG_P_e + rline.x[:self.time_num]
                if not rline.MG_point and rline.Single:
                    self.P_e_h += rline.x[:self.time_num]
            for sline in node.sLine:
                if sline.type == 'he':
                    self.MG_P_e = self.MG_P_e - sline.x[:self.time_num]

    """
    1.负荷：device.className == 'D' and device.type == 'g'
    2.微电网间交互: 
    3.储能
    4.电网
    """

    def P_g_collection(self):
        self.D_P_g = np.zeros(self.time_num)
        self.MG_P_g = np.zeros(self.time_num)
        self.S_P_g = np.zeros(self.time_num)
        self.P_CTP_g = np.zeros(self.time_num)

        self.D_P_max_g = np.zeros(self.time_num)
        self.D_P_min_g = np.zeros(self.time_num)
        self.D_P_ramping_g = np.zeros(self.time_num)

        self.key_g = False

        "付个值呗"
        for node in self.node:
            for device in node.devices:
                if device.className == 'D' and device.type == 'g':
                    self.D_P_g += device.x[:self.time_num]

                    self.D_P_max_g += device.p_max
                    self.D_P_min_g += device.p_min
                    self.D_P_ramping_g += device.ramping
                    self.key_g = True
                if device.className == "S" and device.type == 'g':
                    self.S_P_g -= device.x[:self.time_num]
                if device.className == "CTP":
                    self.P_CTP_g -= device.x[:self.time_num]

            for rline in node.rLine:
                if rline.MG_point and rline.type == 'g':
                    self.MG_P_g += rline.x[:self.time_num]
            for sline in node.sLine:
                if sline.MG_point and sline.type == 'g':
                    self.MG_P_g -= sline.x[:self.time_num]

    """
    1.负荷：device.className == 'D' and device.type == 'th'
    2.CTP
    """

    def P_th_collection(self):
        self.D_P_th = np.zeros(self.time_num)
        self.P_CTP_th = np.zeros(self.time_num)
        self.P_TP_th = np.zeros(self.time_num)

        self.D_P_max_th = np.zeros(self.time_num)
        self.D_P_min_th = np.zeros(self.time_num)
        self.D_P_ramping_th = np.zeros(self.time_num)

        self.key_th = False

        for node in self.node:
            for device in node.devices:
                if device.className == "D" and device.type == "th":
                    self.D_P_th += device.x[:self.time_num]

                    self.D_P_max_th += device.p_max
                    self.D_P_min_th += device.p_min
                    self.D_P_ramping_th += device.ramping
                    self.key_th = True
                if device.className == "CTP":
                    temp = device.x[self.time_num * 2: self.time_num * 3]
                    self.P_CTP_th += temp
                if device.className == "TP":
                    self.P_TP_th += device.x[self.time_num: self.time_num * 2]

    """
    1.负荷--H
    2.负荷--E
    3.S
    4.EL
    """

    def P_h_collection(self):
        self.P_D_h = np.zeros(self.time_num)
        self.P_EL_h = np.zeros(self.time_num)
        self.S_h = np.zeros(self.time_num)
        self.P_h_e = np.zeros(self.time_num)

        self.D_P_max_h = np.zeros(self.time_num)
        self.D_P_min_h = np.zeros(self.time_num)
        self.D_P_ramping_h = np.zeros(self.time_num)
        self.key_h = False

        for node in self.node:
            for device in node.devices:
                if device.className == "D" and device.type == "h":
                    self.P_D_h += device.x[:self.time_num]

                    self.D_P_max_h += device.p_max
                    self.D_P_min_h = device.p_min
                    self.D_P_ramping_h += device.ramping
                    self.key_h = True
                if device.className == "S" and device.type == "h":
                    self.S_h -= device.x[:self.time_num]
                if device.className == "EL":
                    self.P_EL_h += device.x[self.time_num:self.time_num * 2]

            for sline in node.sLine:
                if sline.type == 'he':
                    self.P_h_e -= sline.x[:self.time_num]

    """
        1.绘制各个设备、线路的数据表格（已完成）
        2.绘制区域总用电曲线（未完成-待数据采集完成）
        """

    def draw(self):
        "e"
        self.P_e_collection()
        if self.key_e:
            "电能-供需关系"
            drawSource_Load_e(np.array(
                [self.WT_P, self.PV_P, self.DG_P, self.S_P_e, self.MG_P_e, self.P_CTP_e, self.P_TP_e, self.P_EL_e,
                 self.P_e_h]), self.D_P_e, self.name + "_e_Balance")
            "电能总需求"
            drawDemands(self.D_P_e, self.D_P_max_e, self.D_P_min_e, self.D_P_ramping_e, 'e', self.name + "e_Demand")

        "g"
        self.P_g_collection()
        if self.key_g:
            "天然气-供需关系"
            drawSource_Load_g(np.array([self.MG_P_g, self.S_P_g, self.P_CTP_g]), self.D_P_g, self.name + "_g_Balance")
            "天然气总需求"
            drawDemands(self.D_P_g, self.D_P_max_g, self.D_P_min_g, self.D_P_ramping_g, 'g', self.name + "g_Demand")

        "th"
        self.P_th_collection()
        if self.key_th:
            "热能-供需关系"
            drawSource_Load_th(np.array([self.P_CTP_th, self.P_TP_th]), self.D_P_th, self.name + "_th_Balance")
            "热能总需求"
            drawDemands(self.D_P_th, self.D_P_max_th, self.D_P_min_th, self.D_P_ramping_th, 'th',
                        self.name + "th_Demand")

        "h"
        self.P_h_collection()

        if self.key_h:
            "氢能-供需关系"
            drawSource_Load_h(np.array([self.P_EL_h, self.S_h, self.P_h_e]), self.P_D_h, self.name + "_h_Balance")
            "氢能总需求"
            drawDemands(self.P_D_h, self.D_P_max_h, self.D_P_min_h, self.D_P_ramping_h, 'h', self.name + "h_Demand")

        "价格绘画参数准备，各个设备上的图标"
        # if self.key_e:
        #     sell_pirce_e = np.array([self.Day_sell_e_price])
        #     sell_label_e = np.array(['e'])
        #     production_price_e = np.array([-self.DG_e_price, -self.WT_e_price, -self.PV_e_price])
        #     production_label_e = np.array(['DG', 'WT', 'PV'])
        #     drawPrice(sell_pirce_e, sell_label_e, production_price_e, production_label_e, self.name + "e_Price")
        # if self.key_g:
        #     sell_pirce_g = np.array([self.Day_sell_g_price])
        #     sell_label_g = np.array(['g'])
        #     drawPrice(sell_pirce_g, sell_label = sell_label_g, production_price = np.array([]), production_label = np.array([]), title=self.name + "g_Price")
        # if self.key_th:
        #     sell_pirce_th = np.array([self.Day_sell_th_price])
        #     sell_label_th = np.array(['th'])
        #     drawPrice(sell_pirce_th, sell_label = sell_label_th, production_price = np.array([]), production_label = np.array([]), title=self.name + "th_Price")
        # if self.key_h:
        #     sell_pirce_h = np.array([self.Day_sell_h_price])
        #     sell_label_h = np.array(['h'])
        #     drawPrice(sell_pirce_h, sell_label = sell_label_h, production_price = np.array([]), production_label = np.array([]), title=self.name + "h_Price")

        "绘制这个微电网的能源与外部交互之间到底留着哪些位置？"
        "找数据-每一个微电网交换数据、大电网数据"
        self.MG_P_Array_e = np.zeros(0)
        self.MG_P_Array_Name_e = np.array([""])
        self.CPP = np.zeros(0)
        for node in self.node:
            for rLine in node.rLine:
                if rLine.MG_point and not rLine.Single and rLine.type == 'e':
                    self.MG_P_Array_e = np.append(self.MG_P_Array_e, rLine.x[:self.time_num])
                    self.MG_P_Array_Name_e = np.append(self.MG_P_Array_Name_e, rLine.from_MG + "to" + self.name)
                if rLine.MG_point and rLine.Single and rLine.type == 'e':
                    self.CPP = rLine.x[:self.time_num]

            for sLine in node.sLine:
                if sLine.MG_point and not sLine.Single and sLine.type == 'e':
                    self.MG_P_Array_e = np.append(self.MG_P_Array_e, -sLine.x[:self.time_num])
                    self.MG_P_Array_Name_e = np.append(self.MG_P_Array_Name_e, sLine.to_MG + "to" + self.name)

        self.MG_P_Array_Name_e = self.MG_P_Array_Name_e[1:]
        self.MG_P_Array_e = self.MG_P_Array_e.reshape((int(len(self.MG_P_Array_e) / self.time_num)), self.time_num)
        "微电网之间电能交互关系"
        if len(self.MG_P_Array_e) > 0 and len(self.CPP) > 0:
            drawInteraction(self.MG_P_Array_e, self.MG_P_Array_Name_e, self.CPP, self.name)

    def count_constraints_num(self):
        for node in self.node:
            self.contraint_num = np.append(self.contraint_num, node.contraint_num)
        # print(self.constraints_num)

    def getting_constraints_num(self):
        return self.contraint_num

















