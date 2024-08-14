import numpy as np
from tools.maybeExcel import getDataFromExcel
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText

class TP:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line1, line2):
        self.name = name
        "TP、EL"
        self.className = 'TP'
        self.time_num = time_num
        self.line1 = line1
        self.line2 = line2

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.contraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "PI",
            self.name + "PO",
            self.name + "S"
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
            self.c[i] = - 0.120 * 0.001 * 390.885

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.2
        self.p_rampingDown = self.p_max * 0.15

    def constraints(self, num):
        """
        max/min limits
        """
        B = np.array([
            [self.name + "PI1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)

        """
        ramping Limits
        """
        # Up
        B = np.array([
            [self.name + "PI2", 1],
            [self.name + "PI1", -1],
            [self.name + "S2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        # Down
        B = np.array([
            [self.name + "PI2", -1],
            [self.name + "PI1", 1],
            [self.name + "S2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        """
        State
        """
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)
        """
        Balance
        """
        B = np.array([
            [self.name + "PI1", -self.conversion_rate],
            [self.name + "PO1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        """
        line1
        """
        B = np.array([
            [self.name + "PI1", 1],
            [self.line1.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
        """
        line2
        """
        B = np.array([
            [self.name + "PO1", 1],
            [self.line2.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
    def draw(self):
        print("draw_TP")

    def remenber_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "PI" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

class EL:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line1, line2):
        self.name = name

        self.className = 'EL'
        self.time_num = time_num
        self.line1 = line1
        self.line2 = line2

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        self.params = np.array([""])

        self.conversion_rate = conversion_rate

        self.day = int(self.time_num / 24)

        self.__init()


        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.contraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "PI",
            self.name + "PO",
            self.name + "S"
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
            self.c[i] = - 0 * 0.001 * 390.885

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.2
        self.p_rampingDown = self.p_max * 0.15

    def constraints(self, num):
        """
        max/min limits
        """
        B = np.array([
            [self.name + "PI1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)

        """
        ramping Limits
        """
        # # Up
        # B = np.array([
        #     [self.name + "PI2", 1],
        #     [self.name + "PI1", -1],
        #     # [self.name + "S2", -self.p_rampingUp]
        # ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        # # Down
        # B = np.array([
        #     [self.name + "PI2", -1],
        #     [self.name + "PI1", 1],
        #     # [self.name + "S2", -self.p_rampingDown]
        # ])
        # CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        """
        State
        """
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)
        """
        Balance
        """
        B = np.array([
            [self.name + "PI1", -self.conversion_rate],
            [self.name + "PO1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
        """
        line1
        """
        B = np.array([
            [self.name + "PI1", 1],
            [self.line1.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
        """
        line2
        """
        B = np.array([
            [self.name + "PO1", 1],
            [self.line2.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
    def draw(self):
        print("draw_EL")

    def remenber_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]
        if step != 94:
            B = np.array([
                [self.name + "PI" + str(step), 1],
            ])
            CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)




class CTP:
    def __init__(self, name, conversion_rate1, conversion_rate2, conversion_limits, time_num, line1, line2, line3):
        self.name = name
        self.className = 'CTP'
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3

        self.time_num = time_num

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        self.params = np.array([""])

        self.conversion_rate1 = conversion_rate1
        self.conversion_rate2 = conversion_rate2
        #self.day = int(self.time_num / 24)

        self.__init()

        self.length = len(self.params)

        self.x  = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        self.contraint_num = 0

    def __init(self):
        self.__params_named()
        self.__set_C()
        self.__set_intergrality()
        self.__getData()

    def __params_named(self):
        temp = np.array([
            self.name + "PI",
            self.name + "PO1",
            self.name + "PO2",
            self.name + "S"
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
            self.c[i] = - 0.181 * 0.001 * 390.885

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.2
        self.p_rampingDown = self.p_max * 0.15

    def constraints(self, num):
        """
        max/min limits
        """
        B = np.array([
            [self.name + "PI1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, self.p_max, num)

        """
        ramping Limits
        """
        # Up
        B = np.array([
            [self.name + "PI2", 1],
            [self.name + "PI1", -1],
            [self.name + "S2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        # Down
        B = np.array([
            [self.name + "PI2", -1],
            [self.name + "PI1", 1],
            [self.name + "S2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, num)
        """
        State
        """
        B = np.array([
            [self.name + "S1", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 1, num)
        """
        Balance
        """
        B = np.array([
            [self.name + "PI1", - self.conversion_rate1],
            [self.name + "PO11", 1],
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        B = np.array([
            [self.name + "PI1", - self.conversion_rate2],
            [self.name + "PO21", 1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        B = np.array([
            [self.name + "PO11", - self.conversion_rate2],
            [self.name + "PO21", self.conversion_rate1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

        """
        line1
        """
        B = np.array([
            [self.name + "PI1", 1],
            [self.line1.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
        """
        line2
        """
        B = np.array([
            [self.name + "PO11", 1],
            [self.line2.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)
        """
        line3
        """
        B = np.array([
            [self.name + "PO21", 1],
            [self.line3.name + "P1", -1]
        ])
        CreatConstraintsByText(self.time_num, B, 0, 0, num)

    def draw(self):
        print("draw_CTP")

    def remenber_realValue(self, step, num):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "PI" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)


"冷热电联产"
class CCHP:
    def __init__(self, name, conversion_rate_e, conversion_rate_h, conversion_rate_c, conversion_limit, time_num,
                 line_g, line_e, line_h):
        self.className = "cchp"
        # 设备名
        self.name = name

        # 气转电热冷的转化效率
        self.conversion_rate_e = conversion_rate_e
        self.conversion_rate_h = conversion_rate_h
        self.conversion_rate_c = conversion_rate_c

        # 最大最小功率
        self.max_input_g = 1000
        self.min_input_g = 300
        self.max_output_e = 800
        self.min_output_e = 200
        self.max_output_h = 500
        self.min_output_h = 50
        self.max_output_c = 400
        self.min_output_c = 20

        # 冷热电联产设备连接的线路
        self.line_g = line_g
        self.line_e = line_e
        self.line_h = line_h
        # self.line_c = line_c

        # 最大转化约束
        self.conversion_limit = conversion_limit

        # 爬坡功率与滑坡功率
        self.ramping_up = 84
        self.ramping_down = 84

        # 时间尺度
        self.time_num = time_num

        # 保存冷热电联产设备中的参数变量名
        self.params = np.array([""])
        # 获取冷热电联产设备中的参数长度
        self.length = len(self.params)

        # 强化学习中保存每一步计算的值
        self.value = np.zeros(self.length)
        self.real_value = np.array(self.length)

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
            self.name + "output_c",
            self.name + "state",
            self.name + "g_us",
            self.name + "g_ds",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "h_us",
            self.name + "h_ds",
            self.name + "c_us",
            self.name + "c_ds",
            self.name + "state_control_h",
            self.name + "state_control_c"
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
            self.intergrality[i + self.time_num * 4] = 1

    # 设备的运行成本
    def __operational_cost(self):
        self.c = np.zeros(len(self.params))
        for i in range(self.time_num):
            self.c[i] = -0.01

    # 约束条件
    def constraints(self, constraint_information_class):
        """*****"""
        """能量转化约束"""
        # 气转电、气转热、气转冷的转化效率约束
        transfer_constraint = np.array([
            [self.name + "input_g1", 1],
            [self.name + "output_e1", -1/self.conversion_rate_e],
            [self.name + "output_h1", -1/self.conversion_rate_h],
            [self.name + "output_c1", -1/self.conversion_rate_c]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint, 0, 0, constraint_information_class)

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
        CreatConstraintsByText(self.time_num, g_bound_ds, self.min_input_g, self.max_input_g,
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
        CreatConstraintsByText(self.time_num, e_bound_ds, self.min_output_e, self.max_output_e,
                               constraint_information_class)
        # 热能
        # 最大值约束——向上灵活性
        h_bound_max_us = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_us1", 1],
            [self.name + "state_control_h1", -self.max_output_h]
        ])
        CreatConstraintsByText(self.time_num, h_bound_max_us, -np.inf, 0,
                               constraint_information_class)
        # 最小值约束——向上灵活性
        h_bound_min_us = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_us1", 1],
            [self.name + "state_control_h1", -self.min_output_h]
        ])
        CreatConstraintsByText(self.time_num, h_bound_min_us, 0, np.inf,
                               constraint_information_class)
        # 最大值约束——向下灵活性
        h_bound_max_ds = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_ds1", -1],
            [self.name + "state_control_h1", -self.max_output_h]
        ])
        CreatConstraintsByText(self.time_num, h_bound_max_ds, -np.inf, 0,
                               constraint_information_class)
        # 最小值约束——向下灵活性
        h_bound_min_ds = np.array([
            [self.name + "output_h1", 1],
            [self.name + "h_ds1", 1],
            [self.name + "state_control_h1", -self.min_output_h]
        ])
        CreatConstraintsByText(self.time_num, h_bound_min_ds, 0, np.inf,
                               constraint_information_class)

        # 冷能
        # 最大值约束——向上灵活性
        c_bound_max_us = np.array([
            [self.name + "output_c1", 1],
            [self.name + "c_us1", 1],
            [self.name + "state_control_c1", -self.max_output_c]
        ])
        CreatConstraintsByText(self.time_num, c_bound_max_us, -np.inf, 0,
                               constraint_information_class)
        # 最小值约束——向上灵活性
        c_bound_min_us = np.array([
            [self.name + "output_c1", 1],
            [self.name + "c_us1", 1],
            [self.name + "state_control_c1", -self.min_output_c]
        ])
        CreatConstraintsByText(self.time_num, c_bound_min_us, 0, np.inf,
                               constraint_information_class)
        # 最大值约束——向下灵活性
        c_bound_max_ds = np.array([
            [self.name + "output_c1", 1],
            [self.name + "c_ds1", -1],
            [self.name + "state_control_c1", -self.max_output_c]
        ])
        CreatConstraintsByText(self.time_num, c_bound_max_ds, -np.inf, 0,
                               constraint_information_class)
        # 最小值约束——向下灵活性
        c_bound_min_ds = np.array([
            [self.name + "output_c1", 1],
            [self.name + "c_ds1", 1],
            [self.name + "state_control_c1", -self.min_output_c]
        ])
        CreatConstraintsByText(self.time_num, c_bound_min_ds, 0, np.inf,
                               constraint_information_class)

        """爬坡和滑坡约束"""
        # 爬坡功率约束
        ramping_up_constraint = np.array([
            [self.name + "input_g2", 1],
            [self.name + "input_g1", -1],
            [self.name + "state2", -self.ramping_up]
        ])
        print(ramping_up_constraint)
        print(self.params)
        CreatConstraintsByText(self.time_num-1, ramping_up_constraint, -np.inf, 0, constraint_information_class)
        # 滑坡功率约束
        ramping_down_constraint = np.array([
            [self.name + "input_g2", -1],
            [self.name + "input_g1", 1],
            [self.name + "state2", -self.ramping_down]
        ])
        print(ramping_down_constraint)
        print(self.params)
        CreatConstraintsByText(self.time_num-1, ramping_down_constraint, -np.inf, 0, constraint_information_class)

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


        """时间尺度约束"""
        operation_state = np.array([
            [self.name + "state1", 1]
        ])
        CreatConstraintsByText(self.time_num, operation_state, 0, 1, constraint_information_class)

    # 用来记录强化学习中每一步的值
    def remember_one_step_real_value(self, step, constraint_information_class):
        # 保存计算得到的真实值
        self.real_value[step - 1] = self.value[step - 1]
        remember_real_value = np.array([
            [self.name + "input_g" + str(step), 1]
        ])
        CreatConstraintsByText(1, remember_real_value,  self.real_value[step - 1],  self.real_value[step - 1],
                               constraint_information_class)

    def draw(self):
        print("draw_CCHP")


class EB:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_h):

        self.name = name
        self.className = 'eb'
        self.time_num = time_num
        self.line_e = line_e
        self.line_h = line_h

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.35
        self.ramping_down = 0.35

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = 320
        self.min_input_e = 150
        self.max_output_h = 300
        self.min_output_h = 80

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
            self.name + "state_change",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "h_us",
            self.name + "h_ds"
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
            self.c[i] = - 0.01

    def __getData(self):
        self.p_rampingUp = self.p_max * 0.35
        self.p_rampingDown = self.p_max * 0.35

    def constraints(self, constraint_information_class):
        # 能量转化约束
        transfer_constraint = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_h1", -self.conversion_rate]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint, 0, 0, constraint_information_class)

        # 爬坡功率与滑坡功率约束
        # 固定
        ramping_up_constraint = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "state_change2", -self.ramping_up]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_up_constraint, -np.inf, 0, constraint_information_class)
        ramping_down_constraint = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "state_change2", -self.ramping_down]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_down_constraint, -np.inf, 0, constraint_information_class)
        # 变动
        B = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "state_change2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        # Down
        B = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "state_change2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        """
        State
        """
        state_constraint = np.array([
            [self.name + "state_change1", 1]
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

        # 上下限约束
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
        CreatConstraintsByText(self.time_num, e_bound_ds, self.min_input_e, self.max_input_e,
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
        CreatConstraintsByText(self.time_num, h_bound_ds, self.min_output_h, self.max_output_h,
                               constraint_information_class)


    def draw(self):
        print("draw_EB")

    def remenber_realValue(self, step, constraint_information_class):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "input_e" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], constraint_information_class)


class ER:
    def __init__(self, name, conversion_rate, conversion_limits, time_num, line_e, line_c):

        self.name = name
        self.className = 'er'
        self.time_num = time_num
        self.line_e = line_e
        self.line_c = line_c

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.25
        self.ramping_down = 0.25

        self.p_max = conversion_limits
        self.p_rampingUp = None
        self.p_rampingDown = None

        # 最大最小功率
        self.max_input_e = 300
        self.min_input_e = 150
        self.max_output_c = 200
        self.min_output_c = 100

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
            self.name + "state_change",
            self.name + "e_us",
            self.name + "e_ds",
            self.name + "c_us",
            self.name + "c_ds"
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
            self.c[i] = - 0.01

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

        # 爬坡功率与滑坡功率约束
        # 固定
        ramping_up_constraint = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "state_change2", -self.ramping_up]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_up_constraint, -np.inf, 0, constraint_information_class)
        ramping_down_constraint = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "state_change2", -self.ramping_down]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_down_constraint, -np.inf, 0, constraint_information_class)
        # 变动
        B = np.array([
            [self.name + "input_e2", 1],
            [self.name + "input_e1", -1],
            [self.name + "state_change2", -self.p_rampingUp]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        # Down
        B = np.array([
            [self.name + "input_e2", -1],
            [self.name + "input_e1", 1],
            [self.name + "state_change2", -self.p_rampingDown]
        ])
        CreatConstraintsByText(self.time_num - 1, B, -np.inf, 0, constraint_information_class)
        """
        State
        """
        state_constraint = np.array([
            [self.name + "state_change1", 1]
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

        # 上下限约束
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
        CreatConstraintsByText(self.time_num, e_bound_ds, self.min_input_e, self.max_input_e,
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
        CreatConstraintsByText(self.time_num, h_bound_ds, self.min_output_c, self.max_output_c,
                               constraint_information_class)


    def draw(self):
        print("draw_ER")

    def remenber_realValue(self, step, constraint_information_class):
        #这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        B = np.array([
            [self.name + "input_e" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], constraint_information_class)

