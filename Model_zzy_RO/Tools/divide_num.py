import numpy as np
import openpyxl
import pandas as pd
from tools import MILP


class DivideNum:
    """
    这个类用于将已知的num按照两阶段鲁棒优化所需的第一阶段决策变量和约束条件&第二阶段决策变量和约束条件进行拆分
    """
    def __init__(self, num1, num2, c1, c2, devices, time_num):

        # 得到最终的num（存放所有约束及决策变量的类）
        self.num = num1

        # 第二阶段的num（存放所有约束及决策变量的类）
        self.num_2 = num2

        # 目标函数系数
        self.c = c1

        # 第二阶段的目标系数
        self.c_2 = c2

        # 得到设备类型(数组)
        self.devices = devices

        # 得到时间步长
        self.time_num = time_num

        # 决策变量分阶段
        self.var_1 = np.array([''])
        self.var_2 = np.array([''])

        # 约束条件分阶段
        self.constraint_1 = np.array([''])
        self.constraint_2 = np.array([''])

        # params的信息来源
        self.params_filepath = 'C:\software\Github\DRLmicrogrid\Data\Two_stage_information\params.xlsx'
        self.first_column_name = 'first_params_name'
        self.second_column_name = 'second_params_name'

        # 存放第一阶段决策变量
        self.first_params = np.array([''])
        # 存放第二阶段决策变量
        self.second_params = np.array([''])

        # 决策变量在params中的位置
        # 第一阶段决策变量的位置
        self.fist_location = np.array([''])
        # 第二阶段决策变量的位置
        self.second_location = np.array([''])

        self.begin_location_array = np.array([''])
        self.first_location_array = np.array([''])
        self.begin_location_bl_array = np.array([''])
        self.first_location_bl_array = np.array([''])

        self.c_location = np.array([''])

        # 初始化
        self.__init()

    def __init(self):
        # 得到决策变量的变量名
        self.divide_decision_var()
        # 将决策变量后加上时间尺度
        self.var_set_time_num()
        # 得到对应设备的第一阶段的约束条件
        self.divide_device_constraint()
        # 得到第一阶段的决策变量所对应的目标函数值
        self.divide_params_c()

        # self.getFirstStageInformation()
        # self.getSecondStageInformation()

    def get_params_data(self):
        params_data = pd.read_excel(self.params_filepath)
        return params_data

    def divide_decision_var(self):
        data = self.get_params_data()
        self.params_name_1 = data[self.first_column_name].values
        self.params_name_2 = data[self.second_column_name].values

        # 移除数组中的nan
        # 使用 pandas 将数组转换为 Series
        series_array = pd.Series(self.params_name_1)
        # 使用 isna() 方法检查 NaN，并通过布尔索引过滤掉 NaN 和空字符串
        self.params_name_1 = series_array[~series_array.isna() & (series_array != '')].values

        # print(f"第一阶段决策变量:{self.params_name_1}")
        # print(f"第二阶段决策变量:{self.params_name_2}")
        #
        # 得到决策变量的名字后去params中找到他们的位置


        # 再利用位置获取对应A矩阵的系数

    def var_set_time_num(self):
        # 第一阶段决策变量
        for i in range(len(self.params_name_1)):
            for j in range(self.time_num):
                # self.first_params[i * self.time_num + j] = self.params_name_1[i] + str(j)
                self.first_params = np.append(self.first_params, f"{self.params_name_1[i]}{j+1}")

        # 第二阶段决策变量
        for i in range(len(self.params_name_2)):
            for j in range(self.time_num):
                # self.second_params[i * self.time_num + j] = self.params_name_2[i] + str(j)
                self.second_params = np.append(self.second_params, f"{self.params_name_2[i]}{j+1}")

        self.first_params = self.first_params[1:]
        self.second_params = self.second_params[1:]

        # print(f"加时间步长的第一阶段决策变量：{self.first_params}")
        # print(f"加时间步长的第二阶段决策变量：{self.second_params}")

    def divide_device_constraint(self):
        print(f"self.num.params的长度是:{len(self.num.params)}")

        # 将num中的A矩阵进行更新，只留下所需的约束系数
        for i in range(len(self.devices)):
            self.begin_location_array = np.append(self.begin_location_array, self.devices[i].begin_location)
            self.first_location_array = np.append(self.first_location_array, self.devices[i].first_location)

        self.begin_location_array = self.begin_location_array[1:]
        self.first_location_array = self.first_location_array[1:]
        print(f"第一阶段约束系数开始的位置:{self.begin_location_array}")
        print(f"第一阶段约束系数结束的位置:{self.first_location_array}")

        # 检查每个location的值都提取正确
        for i in range(len(self.begin_location_array)):
            location_start = (int(self.begin_location_array[i])) / len(self.num.params)
            location_end = (int(self.first_location_array[i])) / len(self.num.params)
            if location_start % 1 == 0 and location_end % 1 == 0:
                print(f"第{i}个设备的location_start：{location_start}")
                print(f"第{i}个设备的location_end：{location_end}")
            else:
                print(f"位置选取错误:{self.begin_location_array[i]}")
                print(f"位置选取错误:{self.first_location_array[i]}")
                print(f"参数个数：{len(self.num.params)}")

        # 创建一个与A矩阵同样大小的掩码矩阵，初始化为False
        mask = np.zeros_like(self.num.A, dtype=bool)

        # 第一阶段：将需要保留的约束系数的位置设为True
        for start, end in zip(self.begin_location_array, self.first_location_array):
            mask[int(start): min(int(end), len(self.num.A))] = True
        # 打印mask中为true的位置
        # true_location = np.array([''])
        # for i in range(len(mask)):
        #     if mask[i]:
        #         true_location = np.append(true_location, i)
        # true_location = true_location[1:]
        # print(f"mask中为true的位置：{true_location}")
        # print(f"mask的长度:{len(mask)}")
        # print(f"self.num.A的长度:{len(self.num.A)}")
        # 将A矩阵中需要保留的系数提取出来
        self.num.A = self.num.A[mask]
        # print(f"self.num.A删减后的长度:{len(self.num.A)}")

        "第二阶段"
        # 第二阶段：将需要删除的约束系数的位置设为False
        for i in range(len(self.num_2.A)):
            mask[i] = True
        for start, end in zip(self.begin_location_array, self.first_location_array):
            mask[int(start): min(int(end), len(self.num_2.A))] = False
        print(f"mask的长度：{len(mask)}")
        print(f"self.num_2.A的长度：{len(self.num_2.A)}")
        # 将A2矩阵中需要保留的系数提取出来
        self.num_2.A = self.num_2.A[mask]

        # 检查掩码矩阵
        # for i in range(len(mask)):
        #     print(f"掩码矩阵第{i}个元素：{mask[i]}")
        #
        # print(f"self.num.A的长度：{len(self.num.A)}")

        # 使用掩码矩阵过滤A矩阵，让其他位置为0
        # self.num.A = np.where(mask, self.num.A, 0)


        # 得到A矩阵之后，得到bl与bu
        for i in range(len(self.devices)):
            self.begin_location_bl_array = np.append(self.begin_location_bl_array, self.devices[i].begin_location_bl)
            self.first_location_bl_array = np.append(self.first_location_bl_array, self.devices[i].first_location_bl)

        self.begin_location_bl_array = self.begin_location_bl_array[1:]
        self.first_location_bl_array = self.first_location_bl_array[1:]

        # 检查位置
        print(f"bl开始位置：{self.begin_location_bl_array}")
        print(f"bl结束位置：{self.first_location_bl_array}")

        # 创建一个与bl同样大小的掩码矩阵，初始化为False
        mask_bl = np.zeros_like(self.num.bl, dtype=bool)

        # 将需要保留的约束系数的位置设为True
        for start, end in zip(self.begin_location_bl_array, self.first_location_bl_array):
            mask_bl[int(start): min(int(end), len(self.num.bl))] = True

        # 打印mask中为true的位置
        # for i in range(len(mask_bl)):
        #     if mask_bl[i]:
        #         print(f"mask中为true的位置：{i}")

        # print(f"A的长度：{len(self.num.A)}")
        # print(f"bl的长度：{len(self.num.bl)}")
        # print(f"bu的长度：{len(self.num.bu)}")

        # 使用掩码矩阵过滤bl，让其他位置为0
        self.num.bl = self.num.bl[mask_bl]
        self.num.bu = self.num.bu[mask_bl]

        # 第二阶段将需要删除的位置设为Flase
        # print(f"self.num_2.bl的长度: {len(self.num_2.bl)}")
        """第二阶段"""
        for i in range(len(self.num_2.bl)):
            mask_bl[i] = True
        for start, end in zip(self.begin_location_bl_array, self.first_location_bl_array):
            mask_bl[int(start): min(int(end), len(self.num_2.bl))] = False
        # 第二阶段
        self.num_2.bl = self.num_2.bl[mask_bl]
        self.num_2.bu = self.num_2.bu[mask_bl]

        # 检查掩码矩阵
        # for i in range(len(mask)):
        #     print(f"掩码矩阵第{i}个元素：{mask[i]}")

        # 测试
        # print(f"A: {self.num.A}")
        # print(f"bl: {self.num.bl}")
        # print(f"bu: {self.num.bu}")
        # print(f"params: {self.num.params}")

    def divide_params_c(self):
        # 创建一个与c同样大小的掩码矩阵，初始化为False
        mask = np.zeros_like(self.c, dtype=bool)
        for i in range(len(mask)):
            mask[i] = False
        # 创建一个与c同样大小的掩码矩阵，初始化为True
        mask_2 = np.zeros_like(self.c_2, dtype=bool)
        for i in range(len(mask_2)):
            mask_2[i] = True

        # 去除字符串的前后空格
        self.num.params = np.char.strip(self.num.params)
        self.first_params = np.char.strip(self.first_params)

        self.num.params = np.array(self.num.params, dtype=str)
        self.first_params = np.array(self.first_params, dtype=str)

        # print(f"self.num.params.type:{self.num.params.dtype}")
        # print(f"self.first_params.type:{self.first_params.dtype}")

        # for i in range(len(self.first_params)):
        #     j = 0
        #     temp = 0
        #     while j < self.num.Getting_variableNum():
        #         if(self.num.params[j] == self.first_params[i]):
        #             self.c_location = np.append(self.c_location, j)
        #             break
        #         else:
        #             temp = -1
        #         j += 1
        #     if temp == -1:
        #         print(f"没有找到:{self.first_params[i]}")

        # 找到params在c中对应的位置
        print(f"第一阶段决策变量：{self.first_params}")
        for i in range(len(self.first_params)):
            location = np.where(np.char.equal(self.num.params, self.first_params[i]))
            self.c_location = np.append(self.c_location, location)
        self.c_location = self.c_location[1:]
        print(f"第一阶段决策变量在c中的位置:{self.c_location}")

        # 确保c_location是整数数组
        self.c_location = self.c_location.astype(int)
        # 将需要保留的位置设为True
        mask[self.c_location] = True
        # 第二阶段将不需要保留的位置设为False
        mask_2[self.c_location] = False

        # 使用掩码矩阵过滤c，让其他位置为0
        self.c = np.where(mask, self.c, 0)
        print(f"第一阶段的目标函数：{self.c}")

        # 使用掩码矩阵过滤c_2，让其他位置为0
        self.c_2 = np.where(mask_2, self.c_2, 0)
        print(f"第二阶段的目标函数：{self.c_2}")

        # print(f"self.c:{self.c}")


    def getFirstStageInformation(self):
        pass

    def getSecondStageInformation(self):
        pass

