import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.drawCPP import drawCPP


"冷热电联产"
class CCHPFirst:
    def __init__(self, name, type, conversion_rate_e, conversion_rate_h, conversion_limit, time_num,
                 line_g, line_e, line_h):

        self.className = "cchp"
        # 设备名
        self.name = name
        self.type = type

        self.stage = 1

        # 气转电热冷的转化效率
        self.conversion_rate_e = conversion_rate_e
        self.conversion_rate_h = conversion_rate_h

        # 最大最小功率
        self.max_input_g = conversion_limit
        self.min_input_g = 0
        self.max_output_e = conversion_limit * conversion_rate_e
        self.min_output_e = 0
        self.max_output_h = conversion_limit * conversion_rate_h
        self.min_output_h = 0

        # 冷热电联产设备连接的线路
        self.line_g = line_g
        self.line_e = line_e
        self.line_h = line_h
        # self.line_c = line_c

        # 最大转化约束
        self.conversion_limit = conversion_limit

        # 爬坡功率与滑坡功率
        self.ramping_up = conversion_limit * 0.15
        self.ramping_down = conversion_limit * 0.15

        # 时间尺度
        self.time_num = time_num

        # 保存冷热电联产设备中的参数变量名
        self.params = np.array([""])
        # 获取冷热电联产设备中的参数长度
        self.length = len(self.params)

        # 强化学习中保存每一步计算的值
        self.x = np.zeros(self.length)
        self.real_x = np.array(self.length)

        # 初始化
        self.__init()

    def __init(self):
        self.__params_name()
        self.__integrality()
        self.__operational_cost()


    # 参数变量名数组（为了方便获取数据，而不混淆）
    def __params_name(self):
        temp = np.array([
            self.name + "input_g",
            self.name + "output_e",
            self.name + "output_h",
            self.name + "S",
        ])
        # 生成这个设备有关的全时间尺度所需数据的变量名
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]
        # print(self.params)

    # 定义整型变量
    def __integrality(self):
        self.intergrality = np.zeros(len(self.params))
       # 将所有的状态变量都设置为1
        for i in range(self.time_num):
            self.intergrality[i + self.time_num * 3] = 1

    # 设备的运行成本
    def __operational_cost(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 运维成本
            self.c[i] = 0.084
            # 调节成本
            self.c[i + self.time_num] = 0.018
            self.c[i + self.time_num * 2] = 0.015

    # 约束条件
    def constraints(self, constraint_information_class):
        """*****"""
        """能量转化约束"""
        # 气转电、气转热、气转冷的转化效率约束
        transfer_constraint = np.array([
            [self.name + "input_g1", 1],
            [self.name + "output_e1", -1/self.conversion_rate_e],
            [self.name + "output_h1", -1/self.conversion_rate_h]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint, 0, 0, constraint_information_class)

        """爬坡和滑坡约束"""
        # 爬坡功率约束
        ramping_up_constraint = np.array([
            [self.name + "input_g2", 1],
            [self.name + "input_g1", -1],
            [self.name + "S2", -self.ramping_up]
        ])
        # print(ramping_up_constraint)
        # print(self.params)
        CreatConstraintsByText(self.time_num - 1, ramping_up_constraint, -np.inf, 0, constraint_information_class)
        # 滑坡功率约束
        ramping_down_constraint = np.array([
            [self.name + "input_g2", -1],
            [self.name + "input_g1", 1],
            [self.name + "S2", -self.ramping_down]
        ])
        # print(ramping_down_constraint)
        # print(self.params)
        CreatConstraintsByText(self.time_num - 1, ramping_down_constraint, -np.inf, 0, constraint_information_class)

        """线路约束"""
        # line_g
        # 其中P表示线路的传输功率
        line_g_constraint = np.array([
            [self.name + "input_g1", 1],
            [self.line_g.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, line_g_constraint, 0, 0, constraint_information_class)
        # line_e
        line_e_constraint = np.array([
            [self.name + "output_e1", 1],
            [self.line_e.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, line_e_constraint, 0, 0, constraint_information_class)
        # line_h
        line_h_constraint = np.array([
            [self.name + "output_h1", 1],
            [self.line_h.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, line_h_constraint, 0, 0, constraint_information_class)

        """运行状态约束"""
        operation_state = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, operation_state, 0, 1, constraint_information_class)

        """上下限约束（无灵活性供给）"""
        # 天然气
        g_bound_us = np.array([
            [self.name + "input_g1", 1]
        ])
        CreatConstraintsByText(self.time_num, g_bound_us, self.min_input_g, self.max_input_g,
                               constraint_information_class)

        # 电力
        e_bound_us = np.array([
            [self.name + "output_e1", 1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_output_e, self.max_output_e,
                               constraint_information_class)
        h_bound_us = np.array([
            [self.name + "output_h1", 1]
        ])
        CreatConstraintsByText(self.time_num, h_bound_us, self.min_output_h, self.max_output_h,
                               constraint_information_class)



class CCHPSecond:
    def __init__(self, name, type, conversion_rate_e, conversion_rate_h, conversion_limit, time_num,
                 line_g, line_e, line_h, values, p1):

        self.className = "cchp"
        # 设备名
        self.name = name
        self.type = type

        # 传入第一阶段计算出的固定y值，有input_g, output_e, output_h
        self.values = values
        self.p1 = p1

        self.stage = 2

        # 气转电热冷的转化效率
        self.conversion_rate_e = conversion_rate_e
        self.conversion_rate_h = conversion_rate_h

        # 最大最小功率
        self.max_input_g = conversion_limit
        self.min_input_g = 0
        self.max_output_e = conversion_limit * conversion_rate_e
        self.min_output_e = 0
        self.max_output_h = conversion_limit * conversion_rate_h
        self.min_output_h = 0

        # 冷热电联产设备连接的线路
        self.line_g = line_g
        self.line_e = line_e
        self.line_h = line_h

        # 最大转化约束
        self.conversion_limit = conversion_limit

        # 爬坡功率与滑坡功率
        self.ramping_up = conversion_limit * 0.15
        self.ramping_down = conversion_limit * 0.15

        # 时间尺度
        self.time_num = time_num

        # 保存冷热电联产设备中的参数变量名
        self.params = np.array([""])
        # 获取冷热电联产设备中的参数长度
        self.length = len(self.params)

        # 强化学习中保存每一步计算的值
        self.x = np.zeros(self.length)
        self.real_x = np.array(self.length)

        """第二阶段接收第一阶段求解"""
        self.input_g = np.zeros(self.time_num)
        self.output_e = np.zeros(self.time_num)
        self.output_h = np.zeros(self.time_num)

        # 初始化
        self.__init()

    def __init(self):
        self.__params_name()
        self.__integrality()
        self.__operational_cost()
        self.__getData()


    # 参数变量名数组（为了方便获取数据，而不混淆）
    def __params_name(self):
        temp = np.array([
            self.name + "input_g",
            self.name + "output_e",
            self.name + "output_h",
            self.name + "g_us",
            self.name + "g_ds",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "h_us",
            self.name + "h_ds",
        ])
        # 生成这个设备有关的全时间尺度所需数据的变量名
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]
        # print(self.params)

    # 定义整型变量
    def __integrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __getData(self):
        for i in range(len(self.p1)):
            for j in range(self.time_num):
                if self.p1[i] == self.name + "input_g" + str(j + 1):
                    self.input_g[j] = self.values[i]
                if self.p1[i] == self.name + "output_e" + str(j + 1):
                    self.output_e[j] = self.values[i]
                if self.p1[i] == self.name + "output_h" + str(j + 1):
                    self.output_h[j] = self.values[i]

    # 设备的运行成本
    def __operational_cost(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 灵活性供给成本
            self.c[i + self.time_num * 3] = 0.019
            self.c[i + self.time_num * 4] = 0.019
            self.c[i + self.time_num * 5] = 0.001
            self.c[i + self.time_num * 6] = 0.001
            self.c[i + self.time_num * 7] = 0.001
            self.c[i + self.time_num * 8] = 0.001

    # 约束条件
    def constraints(self, constraint_information_class):
        """约束运行功率"""
        for i in range(self.time_num):
            B = np.array([
                [self.name + "input_g" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.input_g[i], self.input_g[i], constraint_information_class)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "output_e" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.output_e[i], self.output_e[i], constraint_information_class)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "output_h" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.output_h[i], self.output_h[i], constraint_information_class)

        """上下限约束"""
        # 天然气
        g_bound_us = np.array([
            [self.name + "input_g1", 1],
            [self.name + "g_us1", 1]
        ])
        g_bound_ds = np.array([
            [self.name + "input_g1", 1],
            [self.name + "g_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, g_bound_us, self.min_input_g, self.max_input_g,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, g_bound_ds, -np.inf, self.max_input_g,
                               constraint_information_class)
        # 电力
        e_bound_us = np.array([
            [self.name + "output_e1", 1],
            [self.name + "e_us1", 1]
        ])
        e_bound_ds = np.array([
            [self.name + "output_e1", 1],
            [self.name + "e_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_output_e, self.max_output_e,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, e_bound_ds, -np.inf, self.max_output_e,
                               constraint_information_class)
        # 热能
        # 最大值约束——向上灵活性
        # 最小值约束——向上灵活性
        h_bound_us = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_us1", 1]
        ])
        CreatConstraintsByText(self.time_num, h_bound_us, self.min_output_h, self.max_output_h,
                               constraint_information_class)
        # 最大值约束——向下灵活性
        # 最小值约束——向下灵活性
        h_bound_max_ds = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_ds1", -1],
        ])
        CreatConstraintsByText(self.time_num, h_bound_max_ds, -np.inf, self.max_output_h,
                               constraint_information_class)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "g_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_up, constraint_information_class)
            B = np.array([
                [self.name + "g_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_down, constraint_information_class)
            B = np.array([
                [self.name + "h_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_up, constraint_information_class)
            B = np.array([
                [self.name + "h_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_down, constraint_information_class)
            B = np.array([
                [self.name + "e_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_up, constraint_information_class)
            B = np.array([
                [self.name + "e_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_down, constraint_information_class)

            B = np.array([
                [self.name + "g_us1", 1],
                [self.name + "e_us1", -1/self.conversion_rate_e],
                [self.name + "h_us1", -1/self.conversion_rate_h]
            ])
            CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)

            B = np.array([
                [self.name + "g_ds1", 1],
                [self.name + "e_ds1", -1 / self.conversion_rate_e],
                [self.name + "h_ds1", -1 / self.conversion_rate_h]
            ])
            CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)


class EBFirst:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_h):
        self.name = name
        self.className = 'eb'
        self.time_num = time_num
        self.line_e = line_e
        self.line_h = line_h

        self.stage = 1
        self.way = 1

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.35
        self.ramping_down = 0.35

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = conversion_limits
        self.min_input_e = 0
        self.max_output_h = conversion_limits * conversion_rate
        self.min_output_h = 0

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_h",
            self.name + "S",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i + self.time_num * 2] = 1

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 运维成本
            self.c[i] = 0.056
            # 调节成本
            self.c[i + self.time_num] = 0.015

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.35
        self.p_rampingDown = self.p_max * 0.35

    def constraints(self, constraint_information_class):

        # 能量转化约束
        transfer_constraint = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_h1", -1 / self.conversion_rate]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint, 0, 0, constraint_information_class)

        # 爬坡功率与滑坡功率约束
        # 固定
        ramping_up_constraint = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "S2", -self.ramping_up]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_up_constraint, -np.inf, 0, constraint_information_class)
        ramping_down_constraint = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "S2", -self.ramping_down]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_down_constraint, -np.inf, 0, constraint_information_class)
        # 变动
        B = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "S2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        # Down
        B = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "S2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        """
        State
        """
        state_constraint = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, state_constraint, 0, 1, constraint_information_class)

        # 线路约束
        """
        line_e
        """
        B = np.array([
            [self.name + "input_e1", 1],
            [self.line_e.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)
        """
        line_h
        """
        B = np.array([
            [self.name + "output_h1", 1],
            [self.line_h.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)

        """
        上下限约束(无灵活性供给)
        """
        e_bound_us = np.array([
            [self.name + "input_e1", 1]
        ])
        e_bound_ds = np.array([
            [self.name + "input_e1", 1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, e_bound_ds, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        h_bound_us = np.array([
            [self.name + "output_h1", 1]
        ])
        h_bound_ds = np.array([
            [self.name + "output_h1", 1]
        ])
        CreatConstraintsByText(self.time_num, h_bound_us, self.min_output_h, self.max_output_h,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, h_bound_ds, self.min_output_h, self.max_output_h,
                               constraint_information_class)


class EBSecond:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_h, values, p1):

        self.name = name
        self.className = 'eb'
        self.time_num = time_num
        self.line_e = line_e
        self.line_h = line_h

        self.values = values
        self.p1 = p1

        self.stage = 2
        self.way = 1

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.35
        self.ramping_down = 0.35

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = conversion_limits
        self.min_input_e = 0
        self.max_output_h = conversion_limits * conversion_rate
        self.min_output_h = 0

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        """第二阶段接收第一阶段求解"""
        self.input_e = np.zeros(self.time_num)
        self.output_h = np.zeros(self.time_num)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_h",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "h_us",
            self.name + "h_ds",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 灵活性供给成本
            self.c[i + self.time_num * 2] = 0.015
            self.c[i + self.time_num * 3] = 0.015
            self.c[i + self.time_num * 4] = 0.001
            self.c[i + self.time_num * 5] = 0.001

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.35
        self.p_rampingDown = self.p_max * 0.35

        for i in range(len(self.p1)):
            for j in range(self.time_num):
                if self.p1[i] == self.name + "input_e" + str(i + 1):
                    self.input_e[j] = self.values[i]
                if self.p1[i] == self.name + "output_h" + str(i + 1):
                    self.output_h[j] = self.values[i]

    def constraints(self, constraint_information_class):
        for i in range(self.time_num):
            B = np.array([
                [self.name + "input_e" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.input_e[i], self.input_e[i], constraint_information_class)

            B = np.array([
                [self.name + "output_h" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.output_h[i], self.output_h[i], constraint_information_class)

        """
        上下限约束
        """
        e_bound_us = np.array([
            [self.name + "input_e1", 1],
            [self.name + "e_us1", 1]
        ])
        e_bound_ds = np.array([
            [self.name + "input_e1", 1],
            [self.name + "e_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, e_bound_ds, -np.inf, self.max_input_e,
                               constraint_information_class)
        h_bound_us = np.array([
             [self.name + "output_h1", 1],
             [self.name + "h_us1", 1]
         ])
        h_bound_ds = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, h_bound_us, self.min_output_h, self.max_output_h,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, h_bound_ds, -np.inf, self.max_output_h,
                               constraint_information_class)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "e_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.p_rampingUp, constraint_information_class)
            B = np.array([
                [self.name + "e_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.p_rampingDown, constraint_information_class)
            B = np.array([
                [self.name + "h_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.p_rampingUp, constraint_information_class)
            B = np.array([
                [self.name + "h_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.p_rampingDown, constraint_information_class)

            B = np.array([
                [self.name + "e_us1", 1],
                [self.name + "h_us1", -1 / self.conversion_rate],
            ])
            CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)

            B = np.array([
                [self.name + "e_ds1", 1],
                [self.name + "h_ds1", -1 / self.conversion_rate],
            ])
            CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)


class ERFirst:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_c):

        self.name = name
        self.className = 'er'
        self.time_num = time_num
        self.line_e = line_e
        self.line_c = line_c

        self.stage = 1
        self.way = 1

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.25
        self.ramping_down = 0.25

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = conversion_limits
        self.min_input_e = 0
        self.max_output_c = conversion_limits * conversion_rate
        self.min_output_c = 0

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_c",
            self.name + "S",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.intergrality[i + self.time_num * 2] = 1

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 运维成本
            self.c[i] = 0.07
            # 调节成本
            self.c[i + self.time_num] = 0.013


    def __getData(self):
        self.p_rampingUp = self.p_max * 0.25
        self.p_rampingDown = self.p_max * 0.25

    def constraints(self, constraint_information_class):

        # 能量转化约束
        transfer_constraint = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_c1", -self.conversion_rate]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint, 0, 0, constraint_information_class)

        # 变动
        B = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "S2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        # Down
        B = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "S2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        """
        State
        """
        state_constraint = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, state_constraint, 0, 1, constraint_information_class)

        # 线路约束
        """
        line_e
        """
        B = np.array([
            [self.name + "input_e1", 1],
            [self.line_e.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)
        """
        line_h
        """
        B = np.array([
            [self.name + "output_c1", 1],
            [self.line_c.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)


        """
        上下限约束(无灵活性供给)
        """
        e_bound_us = np.array([
            [self.name + "input_e1", 1]
        ])
        e_bound_ds = np.array([
            [self.name + "input_e1", 1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, e_bound_ds, self.min_input_e, self.max_input_e,
                               constraint_information_class)



class ERSecond:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_c, values, p1):

        self.name = name
        self.className = 'er'
        self.time_num = time_num
        self.line_e = line_e
        self.line_c = line_c

        self.values = values
        self.p1 = p1

        self.stage = 2
        self.way = 1

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.25
        self.ramping_down = 0.25

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = conversion_limits
        self.min_input_e = 0
        self.max_output_c = conversion_limits * conversion_rate
        self.min_output_c = 0

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        """第二阶段接收第一阶段求解"""
        self.input_e = np.zeros(self.time_num)
        self.output_c = np.zeros(self.time_num)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.constraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_c",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "c_us",
            self.name + "c_ds",
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __set_intergrality(self):
        self.intergrality = np.zeros(len(self.params))

    def __set_C(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            # 灵活性供给成本
            self.c[i] = 0.015
            self.c[i + self.time_num] = 0.015
            self.c[i + self.time_num * 2] = 0.002
            self.c[i + self.time_num * 3] = 0.002


    def __getData(self):
        self.p_rampingUp = self.p_max * 0.25
        self.p_rampingDown = self.p_max * 0.25

        for i in range(len(self.p1)):
            for j in range(self.time_num):
                if self.p1[i] == self.name + "input_e" + str(j + 1):
                    self.input_e[j] = self.values[i]
                if self.p1[i] == self.name + "output_c" + str(j + 1):
                    self.output_c[j] = self.values[i]

    def constraints(self, constraint_information_class):
        for i in range(self.time_num):
            B = np.array([
                [self.name + "input_e" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.input_e[i], self.input_e[i], constraint_information_class)
            B = np.array([
                [self.name + "output_c" + str(i + 1), 1],
            ])
            CreatConstraintsByText(1, B, self.output_c[i], self.output_c[i], constraint_information_class)

        """
        上下限约束
        """
        e_bound_us = np.array([
            [self.name + "input_e1", 1],
            [self.name + "e_us1", 1]
        ])
        e_bound_ds = np.array([
            [self.name + "input_e1", 1],
            [self.name + "e_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, e_bound_us, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, e_bound_ds, -np.inf, self.max_input_e,
                               constraint_information_class)
        h_bound_us = np.array([
             [self.name + "output_c1", 1],
             [self.name + "c_us1", 1]
         ])
        h_bound_ds = np.array([
            [self.name + "output_c1", 1],
            [self.name + "c_ds1", -1]
        ])
        CreatConstraintsByText(self.time_num, h_bound_us, self.min_output_c, self.max_output_c,
                               constraint_information_class)
        CreatConstraintsByText(self.time_num, h_bound_ds, -np.inf, self.max_output_c,
                               constraint_information_class)

        for i in range(self.time_num):
            B = np.array([
                [self.name + "e_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_up, constraint_information_class)
            B = np.array([
                [self.name + "e_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_down, constraint_information_class)
            B = np.array([
                [self.name + "c_us" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_up, constraint_information_class)
            B = np.array([
                [self.name + "c_ds" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, 0, self.ramping_down, constraint_information_class)

        B = np.array([
            [self.name + "e_us1", 1],
            [self.name + "c_us1", -1 / self.conversion_rate],
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)

        B = np.array([
            [self.name + "e_ds1", 1],
            [self.name + "c_ds1", -1 / self.conversion_rate],
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, constraint_information_class)




