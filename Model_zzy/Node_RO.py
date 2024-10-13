import numpy as np
from tools.MILP import CreatConstraintsByText

class Node:
    def __init__(self, name, devices, sLine, rLine, time_num, type):
        self.name = name
        self.time_num = time_num
        self.className = 'Node'
        self.devices = devices
        self.sLine = sLine
        self.rLine = rLine
        self.type = type

        self.__init()

        self.contraint_num = 0

    def __init(self):
        self.params = np.array([""])
        self.c = np.zeros(0)
        self.intergrality = np.zeros(0)
        self.__params_named()
        self.__set_C()
        self.__set_integrality()

    def __params_named(self):
        for i in range(len(self.devices)):
            self.params = np.append(self.params, self.devices[i].params)

        if len(self.sLine) != 0:
            for i in range(len(self.sLine)):
                self.params = np.append(self.params, self.sLine[i].params)

        self.params = self.params[1:]

    def __set_C(self):
        for i in range(len(self.devices)):
            self.c = np.append(self.c, self.devices[i].c)

        if len(self.sLine) != 0:
            for i in range(len(self.sLine)):
                self.c = np.append(self.c, self.sLine[i].c)

    def __set_integrality(self):
        for i in range(len(self.devices)):
            self.intergrality = np.append(self.intergrality, self.devices[i].intergrality)

        if len(self.sLine) != 0:
            for i in range(len(self.sLine)):
                self.intergrality = np.append(self.intergrality, self.sLine[i].intergrality)

    def constraints(self, num, start_num):
        self.contraint_num = np.array([start_num])
        "收集基本约束"
        for i in range(len(self.devices)):
            self.devices[i].constraints(num)
            length = len(num.bl) - start_num
            self.contraint_num = np.append(self.contraint_num, len(num.bl))
            self.devices[i].contraint_num = start_num
            start_num += length

        if len(self.sLine) != 0:
             for i in range(len(self.sLine)):
                 self.sLine[i].constraints(num)
                 length = len(num.bl) - start_num
                 self.contraint_num = np.append(self.contraint_num, len(num.bl))
                 self.sLine[i].contraint_num = start_num
                 start_num += length

        if len(self.rLine) != 0:
            for i in range(len(self.rLine)):
                self.rLine[i].constraints(num)
                length = len(num.bl) - start_num
                self.contraint_num = np.append(self.contraint_num, len(num.bl))
                self.rLine[i].contraint_num = start_num
                start_num += length

        B = np.array([
            ["Node", 1]
        ])
        "整合balance约束：流向Node的方向视为正方向"
        if self.type != "CCHP" and self.type != "EB" and self.type != "ER" and self.type != "HP":
            for i in range(len(self.devices)):
                if self.devices[i].way == 1 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "P1", 1]
                    ]))
                if self.devices[i].way == -1 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "P1", -1]
                    ]))
                if self.devices[i].way == 0 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "P1", 1]
                    ]))
                if self.devices[i].way == -2 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "buy" + "P1", 1]
                    ]))
                    B = np.append(B, np.array([
                        [self.devices[i].name + "sell" + "P1", 1]
                    ]))
                # 储能设备e
                if self.devices[i].way == 4 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "CP1", -1],
                        [self.devices[i].name + "DP1", 1]
                    ]))
                # 柔性负荷
                if self.devices[i]. way == 5 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "RP1", 1]
                    ]))
                if self.devices[i].way == 10 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "UD1", 0],
                        [self.devices[i].name + "DD1", 0]
                    ]))
                if self.devices[i].way == 999 and self.devices[i].stage == 2:
                    B = np.append(B, np.array([
                        [self.devices[i].name + "fm_u_e1", 0]
                    ]))

            if len(self.sLine) != 0:
                for i in range(len(self.sLine)):
                    B = np.append(B, np.array([
                        [self.sLine[i].name + "P1", -1]
                    ]))

            if len(self.rLine) != 0:
                for i in range(len(self.rLine)):
                    B = np.append(B, np.array([
                        [self.rLine[i].name + "P1", 1]
                    ]))
            B = B[2:]
            B = B.reshape(int(len(B) / 2), 2)
            CreatConstraintsByText(self.time_num, B, 0, 0, num)


        length = len(num.bl) - start_num
        self.contraint_num = np.append(self.contraint_num, len(num.bl))
        start_num += length

        return start_num

    def draw(self):
        for device in self.devices:
            device.draw()

    def get_constraint_num(self):
        return self.contraint_num












