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
                 line_g, line_e, line_h, line_c):
        # 设备名
        self.name = name + "_"

        # 气转电热冷的转化效率
        self.conversion_rate_e = conversion_rate_e
        self.conversion_rate_h = conversion_rate_h
        self.conversion_rate_c = conversion_rate_c

        # 冷热电联产设备连接的线路
        self.line_g = line_g
        self.line_e = line_e
        self.line_h = line_h
        self.line_c = line_c

        # 最大转化约束
        self.conversion_limit = conversion_limit

        # 爬坡功率与滑坡功率
        self.ramping_up = 0.2
        self.ramping_down = 0.2

        # 时间尺度
        self.time_num = time_num

        # 保存冷热电联产设备中的参数变量名
        self.params = np.array([""])
        # 获取冷热电联产设备中的参数长度
        self.length = len(self.params)

        # 初始化
        self.init()

    def init(self):
        pass

    # 参数变量名数组（为了方便获取数据，而不混淆）
    def params_name(self):
        temp = np.array([
            self.name + "input",
            self.name + "output_e",
            self.name + "output_h",
            self.name + "output_c",
            self.name + "operation_state"
        ])
        # 生成这个设备有关的全时间尺度所需数据的变量名
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    # 定义整型变量
    def integrality(self):
        integrality = np.zeros(len(self.params))
       # 将所有的状态变量都设置为1
        for i in range(self.time_num):
            integrality[i + self.time_num * 4] = 1

    # 设备的运行成本
    def operational_cost(self):
        operational_cost = np.zeros(len(self.params))
        for i in range(self.time_num):
            operational_cost[i] = -0.01

    # 最大运行功率与最小运行功率
    def set_ramping_data(self):
        operation_power_max = self.conversion_limit
        operation_power_min = 0

    # 约束条件
    def constraints(self, param_matrix):
        """*****"""
        """能量转化约束"""
        # 气转电的转化效率约束
        transfer_constraint_e = np.array([
            [self.name + "input", -self.conversion_rate_e],
            [self.name + "output_e", 1]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint_e, 0, 0, param_matrix)
        # 气转热的转化效率约束
        transfer_constraint_h = np.array([
            [self.name + "input", -self.conversion_rate_h],
            [self.name + "output_h", 1]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint_h, 0, 0, param_matrix)
        # 气转冷的转化效率约束
        transfer_constraint_c = np.array([
            [self.name + "input", -self.conversion_rate_c],
            [self.name + "output_c", 1]
        ])
        CreatConstraintsByText(self.time_num, transfer_constraint_c, 0, 0, param_matrix)

        """爬坡和滑坡约束"""
        # 爬坡功率约束
        ramping_up_constraint = np.array([
            [self.name + ""]
        ])