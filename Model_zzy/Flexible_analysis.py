import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText

class FA:
    def __init__(self, name, nodes, max_limit_rate, min_limit_rate, fm_rate, fm_max, sets, time_num):
        self.className = "FA"

        self.name = name

        self.nodes = nodes
        self.time_num = time_num

        self.sets = sets

        self.fm_rate = fm_rate
        self.fm_max = fm_max

        self.way = 999

        # 灵活裕度控制范围
        self.max_limit_rate = max_limit_rate
        self.min_limit_rate = min_limit_rate

        # 电力系统的灵活供给能力
        self.us_e = np.zeros(self.time_num)
        self.ds_e = np.zeros(self.time_num)

        # 电力系统的灵活性需求
        self.ud_e = np.zeros(self.time_num)
        self.dd_e = np.zeros(self.time_num)

        # 天然气系统的灵活供给能力
        self.us_g = np.zeros(self.time_num)
        self.ds_g = np.zeros(self.time_num)

        # 天然气系统的灵活性需求
        self.ud_g = np.zeros(self.time_num)
        self.dd_g = np.zeros(self.time_num)

        # 热能系统的灵活供给能力
        self.us_h = np.zeros(self.time_num)
        self.ds_h = np.zeros(self.time_num)

        # 热能系统的灵活性需求
        self.ud_h = np.zeros(self.time_num)
        self.dd_h = np.zeros(self.time_num)

        # 冷能系统的灵活供给能力
        self.us_c = np.zeros(self.time_num)
        self.ds_c = np.zeros(self.time_num)

        # 冷能系统的灵活性需求
        self.ud_c = np.zeros(self.time_num)
        self.dd_c = np.zeros(self.time_num)

        self.params = np.array([""])

        self.__init()

    def __init(self):
        self.__params_named()
        self.__set_intergrality()
        self.__set_C()

    def __params_named(self):
        temp = np.array([
            self.name + "fm_u_e",  # 电力子系统向上灵活裕度
            self.name + "fm_d_e",  # 电力子系统向下灵活裕度
            self.name + "fm_u_g",  # 天然气子系统向上灵活裕度
            self.name + "fm_d_g",  # 天然气子系统向下灵活裕度
            self.name + "fm_u_h",  # 热能子系统向上灵活裕度
            self.name + "fm_d_h",  # 热能子系统向下灵活裕度
            self.name + "fm_u_c",  # 冷能子系统向上灵活裕度
            self.name + "fm_d_c",  # 冷能子系统向下灵活裕度
            self.name + "Z_e_ud",  # 辅助变量
            self.name + "Z_e_dd",  # 辅助变量
            self.name + "Z_g_ud",  # 辅助变量
            self.name + "Z_g_dd",  # 辅助变量
            self.name + "Z_h_ud",  # 辅助变量
            self.name + "Z_h_dd",  # 辅助变量
            self.name + "Z_c_ud",  # 辅助变量
            self.name + "Z_c_dd",  # 辅助变量
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]


    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        # 电力子系统
        for i in range(0, 6):  # 0点至6点
            self.c[i] = -0.8 * 0.5 * 0.7
        for i in range(6, 13):  # 7点至13点
            self.c[i] = -0.8 * 1.8 * 0.7
        for i in range(13, 16):  # 14点至16点
            self.c[i] = -0.8 * 0.7
        for i in range(16, 22):  # 17点至22点
            self.c[i] = -0.8 * 1.8 * 0.7
        for i in range(22, 24):  # 22点至24点
            self.c[i] = -0.8 * 0.5 * 0.7
        # for i in range(self.time_num):
        #     self.c[i] = -0.028
        #     self.c[i + self.time_num] = -0.028
        # 天然气子系统
        for i in range(0, 6):
            self.c[i] = -0.7 * 0.9 * 0.8
        for i in range(6, 13):
            self.c[i] = -0.7 * 1.1 * 0.8
        for i in range(13, 16):
            self.c[i] = -0.7 * 0.8
        for i in range(16, 22):
            self.c[i] = -0.7 * 1.1 * 0.8
        for i in range(22, 24):
            self.c[i] = -0.7 * 0.9 * 0.8
        # for i in range(self.time_num):
        #     self.c[i + self.time_num * 2] = -0.02
        #     self.c[i + self.time_num * 3] = -0.02
        # 热能子系统
        for i in range(0, 6):
            self.c[i] = -0.7 * 0.9 * 0.7
        for i in range(6, 13):
            self.c[i] = -0.7 * 1.1 * 0.7
        for i in range(13, 16):
            self.c[i] = -0.7 * 0.8
        for i in range(16, 22):
            self.c[i] = -0.7 * 1.1 * 0.7
        for i in range(22, 24):
            self.c[i] = -0.7 * 0.9 * 0.7
        # for i in range(self.time_num):
        #     self.c[i + self.time_num * 4] = -0.023
        #     self.c[i + self.time_num * 5] = -0.023
        # 冷能子系统
        for i in range(0, 6):
            self.c[i] = -0.7 * 0.9 * 0.7
        for i in range(6, 13):
            self.c[i] = -0.7 * 1.1 * 0.7
        for i in range(13, 16):
            self.c[i] = -0.7 * 0.8
        for i in range(16, 22):
            self.c[i] = -0.7 * 1.1 * 0.7
        for i in range(22, 24):
            self.c[i] = -0.7 * 0.9 * 0.7
        # for i in range(self.time_num):
        #     self.c[i + self.time_num * 6] = -0.021
        #     self.c[i + self.time_num * 7] = -0.021
        # 辅助变量
        for i in range(self.time_num):
            self.c[i + self.time_num * 8] = 0.1
            self.c[i + self.time_num * 9] = 0.1
            self.c[i + self.time_num * 10] = 0.1
            self.c[i + self.time_num * 11] = 0.1
            self.c[i + self.time_num * 12] = 0.1
            self.c[i + self.time_num * 13] = 0.1
            self.c[i + self.time_num * 14] = 0.1
            self.c[i + self.time_num * 15] = 0.1

    def constraints(self, num):
        # 电力子系统向上灵活裕度约束
        B = np.array([
            [self.name + "fm_u_e1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    # print(f"nodes.devices.name:{self.nodes[i].devices[j].name}")
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "eb":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "er":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "pg":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "e":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_ds1", -1],
                        [self.nodes[i].devices[j].name + "dis_us1", -1],
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "e":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "UD1", 1],
                    ]))

                "可再生能源出力"
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "PV":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "P1", 1]
                #     ]))
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "WT":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "P1", 1]
                #     ]))

                if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "e":
                    B = np.append(B, np.array([
                       [self.nodes[i].devices[j].name + "RP1", -1],
                    ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 电力子系统向下灵活裕度约束
        B = np.array([
            [self.name + "fm_d_e1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "eb":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "er":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "pg":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "e_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "e":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_us1", -1],
                        [self.nodes[i].devices[j].name + "dis_ds1", -1],
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "e":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "DD1", 1],
                    ]))

                "可再生能源出力"
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "PV":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "P1", -1]
                #     ]))
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "WT":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "P1", -1]
                #     ]))

                # if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "e":
                #     B = np.append(B, np.array([
                #        [self.nodes[i].devices[j].name + "ds1", -1],
                #     ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 天然气子系统向上灵活裕度约束
        B = np.array([
            [self.name + "fm_u_g1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "g_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "pg":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "g_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "g":
                    for k in range(self.time_num):
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "UD1", 1],
                        ]))

                if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "g":
                    B = np.append(B, np.array([
                       [self.nodes[i].devices[j].name + "RP1", -1],
                    ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 天然气子系统向下灵活裕度
        B = np.array([
            [self.name + "fm_d_g1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "g_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "pg":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "g_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "g":
                    for k in range(self.time_num):
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "DD1", 1],
                        ]))
                # if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "g":
                #     B = np.append(B, np.array([
                #        [self.nodes[i].devices[j].name + "ds1", -1],
                #     ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 热能子系统向上灵活裕度
        B = np.array([
            [self.name + "fm_u_h1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "h_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "eb":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "h_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "th":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_ds1", -1],
                        [self.nodes[i].devices[j].name + "dis_us1", -1],
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "th":
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "UD1", 1],
                        ]))
                "可再生能源出力"
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "HP":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "output_h1", 1]
                #     ]))

                if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "th":
                    B = np.append(B, np.array([
                       [self.nodes[i].devices[j].name + "RP1", -1],
                    ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)


        # 热能子系统向下灵活裕度
        B = np.array([
            [self.name + "fm_d_h1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "cchp":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "h_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "eb":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "h_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "th":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_us1", -1],
                        [self.nodes[i].devices[j].name + "dis_ds1", -1],
                    ]))
                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "th":
                    for k in range(self.time_num):
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "DD1", 1],
                        ]))

                "可再生能源出力"
                # if self.nodes[i].devices[j].className == "RT" and self.nodes[i].devices[j].type == "HP":
                #     B = np.append(B, np.array([
                #         [self.nodes[i].devices[j].name + "output_h1", -1]
                #     ]))

                # if self.nodes[i].devices[j].className == "FL" and self.nodes[i].devices[j].type == "th":
                #     B = np.append(B, np.array([
                #        [self.nodes[i].devices[j].name + "ds1", -1],
                #     ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 冷能子系统向上灵活裕度约束
        B = np.array([
            [self.name + "fm_u_c1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "er":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "c_us1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "c":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_ds1", -1],
                        [self.nodes[i].devices[j].name + "dis_us1", -1],
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "c":
                    for k in range(self.time_num):
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "UD1", 1],
                        ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        # 冷能子系统向下灵活裕度约束
        B = np.array([
            [self.name + "fm_d_c1", 1]
        ])
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i].devices)):
                if self.nodes[i].devices[j].className == "er":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "c_ds1", -1]
                    ]))

                if self.nodes[i].devices[j].className == "S" and self.nodes[i].devices[j].type == "c":
                    B = np.append(B, np.array([
                        [self.nodes[i].devices[j].name + "ch_us1", -1],
                        [self.nodes[i].devices[j].name + "dis_ds1", -1],
                    ]))

                if self.nodes[i].devices[j].className == "FD" and self.nodes[i].devices[j].type == "c":
                    for k in range(self.time_num):
                        B = np.append(B, np.array([
                            [self.nodes[i].devices[j].name + "DD1", 1],
                        ]))
        B = B.reshape(int(len(B) / 2), 2)
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        """灵活裕度上下限约束——辅助变量"""
        for i in range(len(self.sets)):
            for k in range(len(self.sets[i].devices)):
                if self.sets[i].devices[k].type == "e":
                    for j in range(self.time_num):
                        B = np.array([
                            [self.name + "Z_e_ud" + str(j + 1), 1],
                            [self.sets[i].devices[k].name + "UD" + str(j + 1), -self.fm_rate],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)
                        # B = np.array([
                        #     [self.name + "Z_e_ud" + str(j + 1), 1],
                        # ])
                        # CreatConstraintsByText(1, B, 150, np.inf, num)
                        B = np.array([
                            [self.name + "Z_e_dd" + str(j + 1), 1],
                            [self.sets[i].devices[k].name + "DD" + str(j + 1), -self.fm_rate],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)
                        # B = np.array([
                        #     [self.name + "Z_e_dd" + str(j + 1), 1],
                        # ])
                        # CreatConstraintsByText(1, B, 150, np.inf, num)

                if self.sets[i].devices[k].type == "g":
                    for h in range(self.time_num):
                        B = np.array([
                            [self.name + "Z_g_ud" + str(h + 1), 1],
                            [self.sets[i].devices[k].name + "UD" + str(h + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)
                        # B = np.array([
                        #     [self.name + "Z_g_ud" + str(h + 1), 1],
                        # ])
                        # CreatConstraintsByText(1, B, 150, np.inf, num)

                        B = np.array([
                            [self.name + "Z_g_dd" + str(h + 1), 1],
                            [self.sets[i].devices[k].name + "DD" + str(h + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)
                        # B = np.array([
                        #     [self.name + "Z_g_dd" + str(h + 1), 1],
                        # ])
                        # CreatConstraintsByText(1, B, 150, np.inf, num)

                if self.sets[i].devices[k].type == "th":
                    for p in range(self.time_num):
                        B = np.array([
                            [self.name + "Z_h_ud" + str(p + 1), 1],
                            [self.sets[i].devices[k].name + "UD" + str(p + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                        B = np.array([
                            [self.name + "Z_h_dd" + str(p + 1), 1],
                            [self.sets[i].devices[k].name + "DD" + str(p + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                if self.sets[i].devices[k].type == "c":
                    for n in range(self.time_num):
                        B = np.array([
                            [self.name + "Z_c_ud" + str(n + 1), 1],
                            [self.sets[i].devices[k].name + "UD" + str(n + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)
                        B = np.array([
                            [self.name + "Z_c_dd" + str(n + 1), 1],
                            [self.sets[i].devices[k].name + "DD" + str(n + 1), -self.fm_rate]
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)


        """灵活裕度上下限约束"""
        for i in range(len(self.sets)):
            for k in range(len(self.sets[i].devices)):
                if self.sets[i].devices[k].type == "e":
                    for j in range(self.time_num):
                        B = np.array([
                            [self.name + "fm_u_e" + str(j + 1), 1],
                            [self.name + "Z_e_ud" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_u_e" + str(j + 1), 1],
                            [self.name + "Z_e_ud" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                        B = np.array([
                            [self.name + "fm_d_e" + str(j + 1), 1],
                            [self.name + "Z_e_dd" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_d_e" + str(j + 1), 1],
                            [self.name + "Z_e_dd" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)


                if self.sets[i].devices[k].type == "g":
                    for j in range(self.time_num):
                        B = np.array([
                            [self.name + "fm_u_g" + str(j + 1), 1],
                            [self.name + "Z_g_ud" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_u_g" + str(j + 1), 1],
                            [self.name + "Z_g_ud" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                        B = np.array([
                            [self.name + "fm_d_g" + str(j + 1), 1],
                            [self.name + "Z_g_dd" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_d_g" + str(j + 1), 1],
                            [self.name + "Z_g_dd" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)


                if self.sets[i].devices[k].type == "th":
                    for j in range(self.time_num):
                        B = np.array([
                            [self.name + "fm_u_h" + str(j + 1), 1],
                            [self.name + "Z_h_ud" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_u_h" + str(j + 1), 1],
                            [self.name + "Z_h_ud" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                        B = np.array([
                            [self.name + "fm_d_h" + str(j + 1), 1],
                            [self.name + "Z_h_dd" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_d_h" + str(j + 1), 1],
                            [self.name + "Z_h_dd" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)


                if self.sets[i].devices[k].type == "c":
                    for j in range(self.time_num):
                        B = np.array([
                            [self.name + "fm_u_c" + str(j + 1), 1],
                            [self.name + "Z_c_ud" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_u_c" + str(j + 1), 1],
                            [self.name + "Z_c_ud" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)

                        B = np.array([
                            [self.name + "fm_d_c" + str(j + 1), 1],
                            [self.name + "Z_c_dd" + str(j + 1), -1],
                        ])
                        CreatConstraintsByText(1, B, -np.inf, 0, num)

                        B = np.array([
                            [self.name + "fm_d_c" + str(j + 1), 1],
                            [self.name + "Z_c_dd" + str(j + 1), 1],
                        ])
                        CreatConstraintsByText(1, B, 0, np.inf, num)















