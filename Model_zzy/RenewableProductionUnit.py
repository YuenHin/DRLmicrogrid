import numpy as np

from aDataSetting import smooth
from tools.addParams import AddParams
from tools.MILP import CreatConstraintsByText
from tools.maybeExcel import getDataFromExcel
from tools.drawRG import drawRG
import random

class RT:
    def __init__(self, name, type, id, production_price, production_total, time_num, stochastic_value=25):
        self.name = name
        self.id = id

        self.way = 1

        # 生产成本
        self.production_price = production_price
        # 希望总产量
        self.production_total = production_total

        self.type = type
        self.className = 'RT'
        self.time_num = time_num
        self.p = np.zeros(time_num)
        self.p_min = np.zeros(time_num)
        self.p_max = np.zeros(time_num)

        self.p_rampingh_up = np.zeros(time_num)
        self.p_rampingh_down = np.zeros(time_num)

        self.params = np.array([""])

        # self.day = int(self.time_num / 24)
        self.__init()

        self.length = len(self.params)

        self.x = np.zeros(self.length)
        self.real_x = np.zeros(self.length)

        # 随机波动
        self.stochastic_value = stochastic_value
        # 约束所在位置
        self.constraint_num = 0

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
        # 数据清洗
        for i in range(len(self.p)):
            if self.p[i] < 0:
                self.p[i] = 0
        # 将处理过后的p数组赋值给p_max
        print(self.p)
        self.p_max = self.p
        self.p_min = np.zeros_like(self.p_max)

        if self.type == "PV":
            # 光伏的爬坡功率与滑坡功率是最大功率的一半
            self.p_rampingh_up = self.p_max * 0.5
            self.p_rampingh_down = self.p_max * 0.5
        if self.type == "WT":
            # 风机的爬坡功率与滑坡功率是最大功率的十分之一
            self.p_rampingh_up = self.p_max * 0.1
            self.p_rampingh_down = self.p_max * 0.1

    def __getWTData(self):
        # 平滑处理后的纵坐标值×production_total
        self.p = self.__24to96("C:\software\Github\DRLmicrogrid\Data\RE\WT.xlsx", 2)

    def __getPVData(self):
        self.p = self.__24to96("C:\software\Github\DRLmicrogrid\Data\RE\PV.xlsx", 2)

    def constraints(self, num):
        # production limits:
        for i in range(self.time_num):
            B = np.array([
                [self.name + "P" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, B, self.p_min[i], self.p_max[i], num)

        "Ramping limits:"
        B = np.array([
            [self.name + "P1", 1]
        ])
        CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[0], num)
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "P" + str(i + 1), -1],
                [self.name + "P" + str(i + 2), 1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_up[i+1], num)

        B = np.array([
            [self.name + "P1", 1]
        ])
        CreatConstraintsByText(1, B, 0, np.inf, num)
        for i in range(self.time_num - 1):
            B = np.array([
                [self.name + "P" + str(i + 1), 1],
                [self.name + "P" + str(i + 2), -1]
            ])
            CreatConstraintsByText(1, B, -np.inf, self.p_rampingh_down[i+1], num)

    def draw(self):
        drawRG(self.x, self.p_max, self.p_min, self.p_rampingh_up, self.p_rampingh_down, type="", title=self.name + "RG")

    def __24to96(self, path, y_index):
        # 得到y_idex列的数据
        p = self.__downLoad_load(path, y_index)
        # 将以上操作得到的出力数据进行平滑处理,得到平滑处理后的纵坐标
        p = self.__creatY_96(p)
        # 返回平滑处理后的纵坐标
        return p * self.production_total

        # 顺滑Y轴24->96

    def __creatY_96(self, p):
        # arange函数返回有起点，有终点，有固定步长的数组
        x = np.arange(1, len(p) + 1, 1)

        x, p = smooth(x, p, self.time_num)
        # smooth内部为利用np.linspace生成从1至24的24个数
        # make_interp_spline是一种插值法，是一种折线平滑处理的方法
        return p

        # 加载Y轴数据

    def __downLoad_load(self, path, y_index):
        # 得到第三列的数据，由第2行至24行
        p = getDataFromExcel(path, y_index, y_index + 1, 1, 25)
        return p

    #依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
    def stochastic(self, step, num):

        # 我需要控制不确定变化后不会跳出范围
        self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value ) * 0.01))

        if self.real_x[step - 1] > self.p_max[step - 1]:
            num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_max[step - 1] = self.real_x[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_min[step - 1] = self.real_x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

        if step > 1:
            if (self.real_x[step - 1] - self.real_x[step - 2]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (self.real_x[step - 2] - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1 ] = np.inf
        if step == 1:
            if (self.real_x[step - 1]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (-self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf

    def stochastic_perfect(self, step, num):
        # 我需要控制不确定变化后不会跳出范围
        self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value ) * 0.01))

        if self.real_x[step - 1] > self.p_max[step - 1]:
            num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_max[step - 1] = self.real_x[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_min[step - 1] = self.real_x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, 0, self.real_x[step - 1], num)

        if step > 1 :
            if (self.real_x[step - 1] - self.real_x[step - 2]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (self.real_x[step - 2] - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf
        if step == 1:
            if (self.real_x[step - 1]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (-self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf


    def re_train(self, step, num):
        num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
        num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf
        num.bu[self.constraint_num + self.time_num + step] = np.inf
        num.bu[self.constraint_num + self.time_num * 2 + step] = np.inf

    # 依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
    def stochastic_env(self, step, num):
        #self.PrintBounds(num)

        # 我需要控制不确定变化后不会跳出范围
        #self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value) * 0.01))

        temp = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value) * 0.01))

        #max-min
        if temp > self.p_max[step - 1]:
            temp = self.p_max[step - 1]
        if temp < self.p_min[step - 1]:
            temp = self.p_min[step - 1]

        #render:
        #pro
        if step != 1:
            if temp > self.x[step - 2] + self.p_rampingh_up[step - 2]:
                temp = self.x[step - 2] + self.p_rampingh_up[step - 2]
            if temp < self.x[step - 2] - self.p_rampingh_down[step - 2]:
                temp = self.x[step - 2] - self.p_rampingh_down[step - 2]
        else:
            if temp > self.p_rampingh_up[step - 1]:
                temp = self.p_rampingh_up[step - 1]
            if temp < -self.p_rampingh_down[step - 1]:
                temp = -self.p_rampingh_down[step - 1]
        #next
        #我当前的值 用我的down 如果不可以到达下一个位置 修改波动
        #我这里是不是可以不用管呀
        # if step != self.time_num:
        #     if temp - self.p_rampingh_down[step - 1] > self.x[step]:
        #         #temp = self.p_rampingh_down[step - 1] + self.x[step]
        #         num.bu[self.constraint_num + step - 1 + self.time_num * 2] = temp - self.x[step]
        #     if temp < self.x[step] - self.p_rampingh_up[step - 1]:
        #         temp = self.x[step] - self.p_rampingh_up[step - 1]

        self.real_x[step - 1] = self.x[step - 1]

        #这里不能够直接添加额外的约束，会与之前的约束产生冲突
        #我需要去修改之前约束的值
        # B = np.array([
        #     [self.name + "P" + str(step), 1],
        # ])
        # CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)
        num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
        num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]

        #print("------------------------------------------------------------------------------------")
        #self.PrintBounds(num)

    '''
    小工具:将系数矩阵转化为公式
    '''
    def PrintBounds(self, Number, step):
        A = Number.A
        A = A.reshape((int(len(A) / len(Number.params)), len(Number.params)))
        bl = Number.bl
        bu = Number.bu
        print("\t\t", "Min", "\t", "Max")
        num = step + 1
        for k in range(3):
            for i in range(num):
                i = i + self.constraint_num  + self.time_num * k
                print("第", i + 1, "个：", bl[i], "\t", bu[i], "\t", end=" ")
                for j in range(Number.Getting_variableNum()):
                    if A[i][j] != 0:
                        if A[i][j] > 0:
                            print("+", A[i][j], Number.params[j], " ", end="\t")
                        else:
                            print(A[i][j], Number.params[j], " ", end="\t")
                print("")

    def remenber_realValue(self, step, num):
        # 这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
        num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]

# rt = RT("RT", "PV", 1, 0.03, 700, 24, 25)


class HP:
    def __init__(self, name, energy_type, id, production_price, production_total, time_num, line_e, line_h):
        self.className = "HP"

        self.name = name
        self.id = id

        self.production_price = production_price
        self.production_total = production_total

        self.production_cost = 0

        # 时间尺度
        self.time_num = time_num

        self.day = int(self.time_num / 24)

        self.energy_type = energy_type

        # 线路
        self.line_e = line_e
        self.line_h = line_h
        # self.line_c = line_c

        # 最大/最小功率
        self.max_input_e = 300
        self.min_input_e = 150
        self.max_output_h = 500
        self.min_output_h = 300
        self.max_output_c = 450
        self.min_output_c = 280

        # 供能性能系数
        self.coefficient_h = 4.5
        self.coefficient_c = 4

        # 保存数据的数组
        self.p = np.zeros(self.time_num)
        self.p_max = np.zeros(self.time_num)
        self.p_min = np.zeros(self.time_num)

        # 爬坡与滑坡功率
        self.p_ramping_up = np.zeros(self.time_num)
        self.p_ramping_down = np.zeros(self.time_num)

        self.ramping_up = 300
        self.ramping_down = 300

        self.params = np.array([""])
        self.length = len(self.params)

        # 初始化
        self.__init()

        self.x = np.zeros(self.length)
        self.x_real = np.zeros(self.length)

        # 用于强化学习
        self.stochastic_value = 25

        # 约束所在位置
        self.constraint_num = 0

    def __init(self):
        self.__params_name()
        self.__integrality()
        self.__set_c()

    def __params_name(self):
        temp = np.array([
            self.name + "input_e",
            self.name + "output_h",
            self.name + "output_c",
            self.name + "state_control_h",
            self.name + "state_control_c"
        ])
        self.params = AddParams(self.params, self.time_num, temp)
        self.params = self.params[1:]

    def __integrality(self):
        self.intergrality = np.zeros(self.time_num)

    def __set_c(self):
        self.c = np.zeros(self.time_num)

        self.c = self.c - self.production_price - 0.01

    # 拿到可再生能源数据
    def __getdata(self):
        # 得到处理后的数据
        self.p = self.__data_after_handle("C:\software\Github\DRLmicrogrid\Data\RE\HP.xls", 2)

        # 数据清洗
        for i in range(len(self.p)):
            if self.p[i] < 0:
                self.p[i] = 0
        # 将处理后的p数组赋值给p_max
        self.p_max = self.p

        if self.energy_type == "h":
            self.p_ramping_up = (self.p_max - self.p_min) * 0.45
            self.p_ramping_down = (self.p_max - self.p_min) * 0.45
        if self.energy_type == "c":
            self.p_ramping_up = (self.p_max - self.p_min) * 0.4
            self.p_ramping_down = (self.p_max - self.p_min) * 0.4

    def constraints(self, constraint_information_class):
        # 性能系数约束
        coefficient_constraint_h = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_h1", -self.coefficient_h]
        ])
        CreatConstraintsByText(self.time_num, coefficient_constraint_h, 0, 0, constraint_information_class)
        coefficient_constraint_c = np.array([
            [self.name + "input_e1", 1],
            [self.name + "output_c1", -self.coefficient_c]
        ])
        CreatConstraintsByText(self.time_num, coefficient_constraint_c, 0, 0, constraint_information_class)

        # 最大/最小功率约束
        power_constraint_e = np.array([
            [self.name + "input_e1", 1]
        ])
        CreatConstraintsByText(self.time_num, power_constraint_e, self.min_input_e, self.max_input_e,
                               constraint_information_class)
        power_constraint_h_max = np.array([
            [self.name + "output_h1", 1],
            [self.name + "state_control_h1", -self.max_output_h]
        ])
        CreatConstraintsByText(self.time_num, power_constraint_h_max, -np.inf, 0, constraint_information_class)
        power_constraint_h_min = np.array([
            [self.name + "output_h1", 1],
            [self.name + "state_control_h1", -self.min_output_h]
        ])
        CreatConstraintsByText(self.time_num, power_constraint_h_min, 0, np.inf, constraint_information_class)
        power_constraint_c_max = np.array([
            [self.name + "output_c1", 1],
            [self.name + "state_control_c1", -self.max_output_c]
        ])
        CreatConstraintsByText(self.time_num, power_constraint_c_max, -np.inf, 0, constraint_information_class)
        power_constraint_c_min = np.array([
            [self.name + "output_c1", 1],
            [self.name + "state_control_c1", -self.min_output_c]
        ])
        CreatConstraintsByText(self.time_num, power_constraint_c_min, 0, np.inf, constraint_information_class)

        # 爬坡与滑坡功率约束(固定的)
        ramping_up_constraint = np.array([
            [self.name + "output_h2", 1],
            [self.name + "output_h1", -1]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_up_constraint, -np.inf, self.ramping_up,
                               constraint_information_class)
        ramping_down_constraint = np.array([
            [self.name + "output_h2", -1],
            [self.name + "output_h1", 1]
        ])
        CreatConstraintsByText(self.time_num-1, ramping_down_constraint, -np.inf, self.ramping_down,
                               constraint_information_class)

        # 与预测数据相关的功率约束与爬坡滑坡约束
        # 最大最小功率约束
        for i in range(self.time_num):
            power_constraint = np.array([
                [self.name + "output_h" + str(i + 1), 1]
            ])
            CreatConstraintsByText(1, power_constraint, self.p_min[i], self.p_max[i], constraint_information_class)
        # 爬坡与滑坡攻略约束
        # 爬坡
        ramping_constraint = np.array([
            [self.name + "output_h1", 1]
        ])
        CreatConstraintsByText(1, ramping_constraint, -np.inf, self.p_ramping_up[0], constraint_information_class)
        for i in range(self.time_num - 1):
            ramping_constraint = np.array([
                [self.name + "output_h" + str(i + 1), -1],
                [self.name + "output_h" + str(i + 2), 1]
            ])
            CreatConstraintsByText(1, ramping_constraint, -np.inf, self.p_ramping_up[i+1], constraint_information_class)
        # 滑坡
        ramping_constraint = np.array([
            [self.name + "output_h1", 1]
        ])
        CreatConstraintsByText(1, ramping_constraint, -np.inf, self.p_ramping_down[0], constraint_information_class)
        for i in range(self.time_num - 1):
            ramping_constraint = np.array([
                [self.name + "output_h" + str(i + 1), 1],
                [self.name + "output_h" + str(i + 2), -1]
            ])
            CreatConstraintsByText(1, ramping_constraint, -np.inf, self.p_ramping_down[i + 1],
                                   constraint_information_class)

    def draw(self):
        drawRG(self.x, self.p_max, self.p_min, self.p_ramping_up, self.p_ramping_down, None, title=self.name + "RG")

    def __data_after_handle(self, path, y_index):
        data_array = self.__data_capture(path, y_index)
        data_array_handle = self.__smooth_data(data_array)
        return data_array_handle * self.production_total

    def __smooth_data(self, data_array):
        x = np.arange(1, len(data_array), 1)
        x, data_array = smooth(x, data_array, self.time_num)
        return data_array

    def __data_capture(self, path, y_index):
        data_array = getDataFromExcel(path, y_index, y_index + self.day, 1, 25)
        return data_array


    # 依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
    def stochastic(self, step, num):

        # 我需要控制不确定变化后不会跳出范围
        self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * self.stochastic_value * 0.01))

        if self.real_x[step - 1] > self.p_max[step - 1]:
            num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_max[step - 1] = self.real_x[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_min[step - 1] = self.real_x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)

        if step > 1:
            if (self.real_x[step - 1] - self.real_x[step - 2]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (self.real_x[step - 2] - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1 ] = np.inf
        if step == 1:
            if (self.real_x[step - 1]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (-self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf

    def stochastic_perfect(self, step, num):
        # 我需要控制不确定变化后不会跳出范围
        self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value ) * 0.01))

        if self.real_x[step - 1] > self.p_max[step - 1]:
            num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_max[step - 1] = self.real_x[step - 1]
        if self.real_x[step - 1] < self.p_min[step - 1]:
            num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
            self.p_min[step - 1] = self.real_x[step - 1]

        B = np.array([
            [self.name + "P" + str(step), 1],
        ])
        CreatConstraintsByText(1, B, 0, self.real_x[step - 1], num)

        if step > 1 :
            if (self.real_x[step - 1] - self.real_x[step - 2]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (self.real_x[step - 2] - self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf
        if step == 1:
            if (self.real_x[step - 1]) > self.p_rampingh_up[step - 1]:
                num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
            if (-self.real_x[step - 1]) > self.p_rampingh_down[step - 1]:
                num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf


    def re_train(self, step, num):
        num.bu[self.constraint_num + self.time_num + step - 1] = np.inf
        num.bu[self.constraint_num + self.time_num * 2 + step - 1] = np.inf
        num.bu[self.constraint_num + self.time_num + step] = np.inf
        num.bu[self.constraint_num + self.time_num * 2 + step] = np.inf

    # 依据当前值得到真实随机出力值,并加入约束控制其值输出为确定性输出值
    def stochastic_env(self, step, num):
        #self.PrintBounds(num)

        # 我需要控制不确定变化后不会跳出范围
        #self.real_x[step - 1] = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value) * 0.01))

        temp = self.x[step - 1] * (1 - (random.random() * (self.stochastic_value) * 0.01))

        #max-min
        if temp > self.p_max[step - 1]:
            temp = self.p_max[step - 1]
        if temp < self.p_min[step - 1]:
            temp = self.p_min[step - 1]

        #render:
        #pro
        if step != 1:
            if temp > self.x[step - 2] + self.p_rampingh_up[step - 2]:
                temp = self.x[step - 2] + self.p_rampingh_up[step - 2]
            if temp < self.x[step - 2] - self.p_rampingh_down[step - 2]:
                temp = self.x[step - 2] - self.p_rampingh_down[step - 2]
        else:
            if temp > self.p_rampingh_up[step - 1]:
                temp = self.p_rampingh_up[step - 1]
            if temp < -self.p_rampingh_down[step - 1]:
                temp = -self.p_rampingh_down[step - 1]
        #next
        #我当前的值 用我的down 如果不可以到达下一个位置 修改波动
        #我这里是不是可以不用管呀
        # if step != self.time_num:
        #     if temp - self.p_rampingh_down[step - 1] > self.x[step]:
        #         #temp = self.p_rampingh_down[step - 1] + self.x[step]
        #         num.bu[self.constraint_num + step - 1 + self.time_num * 2] = temp - self.x[step]
        #     if temp < self.x[step] - self.p_rampingh_up[step - 1]:
        #         temp = self.x[step] - self.p_rampingh_up[step - 1]

        self.real_x[step - 1] = self.x[step - 1]

        #这里不能够直接添加额外的约束，会与之前的约束产生冲突
        #我需要去修改之前约束的值
        # B = np.array([
        #     [self.name + "P" + str(step), 1],
        # ])
        # CreatConstraintsByText(1, B, self.real_x[step - 1], self.real_x[step - 1], num)
        num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
        num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]

        #print("------------------------------------------------------------------------------------")
        #self.PrintBounds(num)

    '''
    小工具:将系数矩阵转化为公式
    '''
    def PrintBounds(self, Number, step):
        A = Number.A
        A = A.reshape((int(len(A) / len(Number.params)), len(Number.params)))
        bl = Number.bl
        bu = Number.bu
        print("\t\t", "Min", "\t", "Max")
        num = step + 1
        for k in range(3):
            for i in range(num):
                i = i + self.constraint_num  + self.time_num * k
                print("第", i + 1, "个：", bl[i], "\t", bu[i], "\t", end=" ")
                for j in range(Number.Getting_variableNum()):
                    if A[i][j] != 0:
                        if A[i][j] > 0:
                            print("+", A[i][j], Number.params[j], " ", end="\t")
                        else:
                            print(A[i][j], Number.params[j], " ", end="\t")
                print("")

    def remenber_realValue(self, step, num):
        # 这里因为没有涉及到强化学习控制，因此只需要将perfect——MILP下未考虑随机的控制结果输出即可，不需要做额外的控制
        self.real_x[step - 1] = self.x[step - 1]

        num.bl[self.constraint_num + step - 1] = self.real_x[step - 1]
        num.bu[self.constraint_num + step - 1] = self.real_x[step - 1]







