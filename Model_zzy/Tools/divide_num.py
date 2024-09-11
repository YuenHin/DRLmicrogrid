import numpy as np
import pandas as pd


class DivideNum:
    """
    这个类用于将已知的num按照两阶段鲁棒优化所需的第一阶段决策变量和约束条件&第二阶段决策变量和约束条件进行拆分
    """
    def __init__(self, num):
        # 得到最终的num
        self.num = num

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

    def __init(self):
        self.divide_decision_var()
        self.divide_constraint()
        self.getFirstStageInformation()
        self.getSecondStageInformation()

    def get_params_data(self):
        params_data = pd.read_excel(self.params_filepath)
        return params_data

    def divide_decision_var(self):
        data = self.get_params_data()
        params_name_1 = data[self.first_column_name].values
        params_name_2 = data[self.second_column_name].values

        # 得到决策变量的名字后去A矩阵中找到他们的位置

    def divide_constraint(self):
        pass

    def getFirstStageInformation(self):
        pass

    def getSecondStageInformation(self):
        pass