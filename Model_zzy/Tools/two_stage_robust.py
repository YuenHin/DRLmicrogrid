# from pyomo.environ import *
# from pyomo.opt import SolverFactory
# from Model_zzy.Tools.divide_num import DivideNum
#
#
# # 创建模型
# model = ConcreteModel()
#
# # 参数设置
# decision_var_num_1 = 3  # 第一阶段决策变量个数
#
# decision_var_num_2 = 4  # 第二阶段决策变量个数
# scenarios = 2  # 不确定场景数量
#
# # 定义第一阶段决策变量:x[i]为非负连续变量
# model.x = Var(range(decision_var_num_1), bounds=(0, 1000))  # 第一阶段发电计划
#
# # 定义第二阶段决策变量，对于每种不确定场景：y[j, s]为非负连续变量
# model.y = Var(range(decision_var_num_1), range(scenarios), bounds=(0, 1000))  # 第二阶段调整变量
#
# # 定义一个Pyomo变量来表示第二阶段的最大目标值
# model.max_cost = Var()
#
# print(f"第一阶段的决策变量：{model.x}")
# print(f"第一阶段的决策变量数量：{model.x.dim()}")
# print(f"第二阶段的决策变量：{model.y}")
# print(f"第二阶段的决策变量数量：{model.y.dim()}")
#
# # 参数：成本系数、约束矩阵和不确定性场景
# c1 = [20, 25, 30]  # 第一阶段运行成本系数
# c2 = [40, 45, 50]  # 第二阶段调整成本系数
# A1 = [[1, 1, 1], [2, 2, 2]]  # 第一阶段约束矩阵
# b1 = [100, 200]  # 第一阶段约束常数项
# A2 = [[1, 0, 1], [1, 1, 0], [0, 1, 1]]  # 第二阶段约束矩阵
# A3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # 第二阶段与第一阶段变量的关联矩阵
# b2_scenarios = [[120, 150, 160], [140, 160, 170]]  # 不同场景下的第二阶段约束常数项
#
#
# # 定义第一阶段的目标函数
# def first_stage_objective(model):
#     # 计算第一阶段的目标函数，即所有生成器的成本或收益总和
#     total_cost_or_benefit_first_stage = sum(c1[i] * model.x[i] for i in range(decision_var_num_1))
#     print(f"第一阶段的成本或收益总和：{total_cost_or_benefit_first_stage}")
#     return total_cost_or_benefit_first_stage
#
#
# # 定义第二阶段的目标函数
# def second_stage_objective(model):
#     # 返回max_cost作为第二阶段的目标函数
#     print(f"第二阶段的目标函数：{model.max_cost}")
#     return model.max_cost
#
#
# # 定义综合目标函数：合并第一阶段和第二阶段的目标函数
# def combined_objective(model):
#     return first_stage_objective(model) + second_stage_objective(model)
#
#
# # 添加合并后的目标函数到模型中，并设置为最小化问题
# model.CombinedObjective = Objective(rule=combined_objective, sense=minimize)
#
#
# # 定义约束条件来表示最大化的第二阶段目标
# def max_scenario_constraint(model, s):
#     # 每个情境的线性组合
#     scenario_cost = sum(c2[j] * model.y[j, s] for j in range(decision_var_num_1))
#     # 每个情境的线性组合必须小于或等于 max_cost
#     return model.max_cost >= scenario_cost
#
#
# # 添加每个情境的约束条件
# model.MaxScenarioConstraint = Constraint(range(scenarios), rule=max_scenario_constraint)
#
#
# # 定义第一阶段的约束规则
# def first_stage_constraint_rule(model, i):
#     # 计算第i个约束条件的线性表达式
#     constraint_expression = sum(A1[i][j] * model.x[j] for j in range(decision_var_num_1))
#     # 返回约束表达式，必须满足大于或等于b1[i]
#
#     print(f"第一阶段的约束规则：{constraint_expression >= b1[i]}")
#     return constraint_expression >= b1[i]
#
#
# # 使用Pyomo的Constraint类，将上述约束规则应用于模型
# model.first_stage_constraints = Constraint(range(len(b1)), rule=first_stage_constraint_rule)
#
#
# # 定义第二阶段的约束规则
# def second_stage_constraint_rule(model, j, s):
#     # 计算第二阶段约束的左边部分
#     second_stage_left_expression = sum(A2[j][i] * model.y[i, s] for i in range(decision_var_num_1))
#     # 计算约束右边的常量部分
#     first_stage_impact = sum(A3[j][k] * model.x[k] for k in range(decision_var_num_1))
#     # 右边的表达式是b2_scenarios[s][j]减去第一阶段的影响
#     second_stage_right_expression = b2_scenarios[s][j] - first_stage_impact
#
#     print(f"第二阶段的约束规则：{second_stage_left_expression >= second_stage_right_expression}")
#     # 返回完整的约束表达式
#     return second_stage_left_expression >= second_stage_right_expression
#
#
# # 使用Pyomo的Constraint类，将上述约束规则应用于模型
# model.second_stage_constraints = Constraint(range(len(A2)), range(scenarios), rule=second_stage_constraint_rule)
#
# # 使用Gurobi求解器求解
# solver = SolverFactory('gurobi')
# solver.options['DualReductions'] = 0  # 禁用对偶约简来更容易识别问题
# solver.solve(model, tee=True)
#
# # 输出结果
# print("Optimal First-Stage Decision (x):")
# for i in range(decision_var_num_1):
#     print(f"x[{i}] = {model.x[i].value}")
#
# print("\nOptimal Second-Stage Decision (y):")
# for j in range(decision_var_num_1):
#     for s in range(scenarios):
#         print(f"y[{j},{s}] = {model.y[j,s].value}")
#
# print("First Stage Constraints:")
# for i in range(len(b1)):
#     print(f"Constraint {i}: {model.first_stage_constraints[i].expr}")
#
# print("\nSecond Stage Constraints:")
# for j in range(len(A2)):
#     for s in range(scenarios):
#         print(f"Constraint {j, s}: {model.second_stage_constraints[j, s].expr}")
#

"""
实测
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB
import numpy as np

def two_stage_RO(num):
    # 输入数据（示例）
    # 第一阶段数据
    A1 = num.num.A  # 第一阶段系数矩阵
    A1 = A1.reshape((int(len(A1) / len(num.num.params)), len(num.num.params)))
    p1 = num.num.params  # 第一阶段决策变量的变量名
    bl1 = num.num.bl  # 第一阶段约束条件最小值
    bu1 = num.num.bu  # 第一阶段约束条件最大值
    c1 = num.c  # 对应变量名的目标值系数

    # 检查A矩阵
    # df = pd.DataFrame(A1)
    # df.to_excel("C:\software\Github\DRLmicrogrid\Data\Two_stage_information\A.xlsx", index=False, header=False)

    # 第二阶段数据
    A2 = num.num_2.A  # 第二阶段系数矩阵
    A2 = A2.reshape((int(len(A2) / len(num.num_2.params)), len(num.num_2.params)))
    p2 = num.num_2.params  # 第二阶段决策变量的变量名
    bl2 = num.num_2.bl  # 第二阶段约束条件最小值
    bu2 = num.num_2.bu  # 第二阶段约束条件最大值
    c2 = num.c_2  # 对应变量名的目标值系数

    # # 检查
    # print(f"A2:{A2}和A2的长度：{A2.shape}")
    # print(f"p2:{p2}和p2的长度：{len(p2)}")
    # print(f"bl2:{bl2}和bl的长度：{len(bl2)}")
    # print(f"bu2:{bu2}和bu的长度：{len(bu2)}")
    print(f"第一阶段的决策变量：{p1}")
    print(f"第二阶段的决策变量：{p2}")

    # # 创建模型
    # model = gp.Model('Two-Stage_Robust_Optimization')
    #
    # # 设置参数
    # model.setParam('MIPGap', 0.01)  # 设置相对间隙为1%，及允许次优解
    #
    # # model.setParam('DualReductions', 0)  # 关闭输出信息
    #
    # # 第一阶段决策变量
    # x = model.addVars(range(len(p1)), vtype=GRB.CONTINUOUS)
    # # 遍历并重命名变量
    # for i in range(len(p1)):
    #     x[i].VarName = p1[i]
    #
    # # 第一阶段目标函数
    # model.setObjective(gp.quicksum(c1[i] * x[i] for i in range(len(p1))), GRB.MINIMIZE)
    #
    # # 第一阶段约束
    # for j in range(A1.shape[0]):
    #     model.addConstr(gp.quicksum(A1[j, i] * x[i] for i in range(len(p1))) >= bl1[j])
    #     model.addConstr(gp.quicksum(A1[j, i] * x[i] for i in range(len(p1))) <= bu1[j])
    #
    # # 优化第一阶段 / 求解主问题
    # model.optimize()
    #
    # # 检查目标函数是否被设置
    # # print(f"打印第一阶段目标函数：{model.getObjective()}")
    #
    # # 获得第一阶段的解
    # # p_results = p1.X
    #
    # # 子问题（第二阶段），基于主问题的解寻找最恶劣场景
    #
    #
    # # 第二阶段变量（假设为情景变量，待进一步定义）
    # y = model.addVars(range(len(p2)), vtype=GRB.CONTINUOUS)
    # # 遍历并重命名变量
    # for i in range(len(p2)):
    #     y[i].VarName = p2[i]
    #
    # # 第二阶段约束（鲁棒优化约束）
    # for j in range(A2.shape[0]):
    #     # 将第一阶段的解 x 引入第二阶段的约束中
    #     model.addConstr(gp.quicksum(A2[j, i] * y[i] for i in range(len(p2))) >= bl2[j])
    #     model.addConstr(gp.quicksum(A2[j, i] * y[i] for i in range(len(p2))) <= bu2[j])
    #
    # # 第二阶段目标函数
    # model.setObjective(
    #     gp.quicksum(c1[j] * y[j] for j in range(len(p1))) +
    #     gp.quicksum(c2[i] * y[i] for i in range(len(p2))),
    #     gp.GRB.MINIMIZE
    # )
    #
    # # 求解模型
    # model.optimize()
    #
    # # 打印第二阶段目标函数
    # # print(f"打印第二阶段目标函数：{model.getObjective()}")
    #
    # # 查看变量表示
    # model.write('model.lp')
    #
    # # Unbounded model
    # # model.computeIIS()
    # # model.write("model.ilp")
    #
    # # # 打印结果
    # # if model.status == GRB.OPTIMAL:
    # #     print('Optimal Solution:')
    # #     for v in model.getVars():
    # #         print(f'{v.varName}: {v.x}')
    # #     print(f'Objective Value: {model.objVal}')
    # # else:
    # #     print('No optimal solution found.')
    #
    # # 打印结果
    # if model.status == GRB.OPTIMAL:
    #     print('Optimal Solution:')
    #     for i in range(len(p1)):
    #         print(f'{p1[i]}: {x[i].x}')  # 使用x[i].x来获取变量的值
    #     for j in range(len(p2)):
    #         print(f'{p2[j]}: {y[j].x}')    # 使用y[j].x来获取变量的值
    #     print(f'Objective Value: {model.objVal}')
    # else:
    #     print('No optimal solution found.')

    # 创建模型
    model = gp.Model('Two-Stage_Robust_Optimization')

    # 设置参数
    model.setParam('MIPGap', 0.01)  # 设置相对间隙为1%，及允许次优解

    # 第一阶段决策变量
    x = model.addVars(range(len(p1)), vtype=GRB.CONTINUOUS)
    for i in range(len(p1)):
        x[i].VarName = p1[i]

    # 第一阶段目标函数
    model.setObjective(gp.quicksum(c1[i] * x[i] for i in range(len(p1))), GRB.MINIMIZE)

    # 第一阶段约束
    for j in range(A1.shape[0]):
        model.addConstr(gp.quicksum(A1[j, i] * x[i] for i in range(len(p1))) >= bl1[j])
        model.addConstr(gp.quicksum(A1[j, i] * x[i] for i in range(len(p1))) <= bu1[j])

    # 主问题求解
    model.optimize()

    # 列生成算法：逐步加入最恶劣场景
    MAX_ITER = 10  # 最大迭代次数
    tol = 1e-4  # 终止条件
    worst_case_constraints = []

    for iter_count in range(MAX_ITER):
        # 获得第一阶段的解
        x_values = [x[i].X for i in range(len(p1))]

        # 第二阶段问题（子问题）：基于第一阶段解的最恶劣场景
        sub_model = gp.Model('SubProblem')

        # 第二阶段的决策变量
        y = sub_model.addVars(range(len(p2)), vtype=GRB.CONTINUOUS)
        for i in range(len(p2)):
            y[i].VarName = p2[i]

        # 第二阶段的目标函数：最恶劣场景下的成本
        sub_model.setObjective(
            gp.quicksum(c2[i] * y[i] for i in range(len(p2))),
            GRB.MINIMIZE
        )

        # 第二阶段约束
        for j in range(A2.shape[0]):
            sub_model.addConstr(gp.quicksum(A2[j, i] * y[i] for i in range(len(p2))) >= bl2[j])
            sub_model.addConstr(gp.quicksum(A2[j, i] * y[i] for i in range(len(p2))) <= bu2[j])

        # 子问题求解
        sub_model.optimize()

        # 获取子问题的解：找到最恶劣的灵活性供需缺口
        worst_case_value = sub_model.ObjVal
        y_values = [y[i].X for i in range(len(p2))]

        # 检查是否达到了终止条件
        if worst_case_value <= tol:
            print(f"终止条件已满足，迭代次数：{iter_count}")
            break

        # 将最恶劣场景的约束加入到主问题中（即将第二阶段的解引入主问题）
        worst_case_constraint = gp.quicksum(A2[j, i] * x[i] for i in range(len(p1))) <= worst_case_value
        worst_case_constraints.append(worst_case_constraint)
        model.addConstr(worst_case_constraint)

        # 重新优化主问题，加入新的最恶劣场景约束
        model.optimize()

    # 输出最终的最优解
    if model.status == GRB.OPTIMAL:
        print("最终的最优解:")
        for i in range(len(p1)):
            print(f"{p1[i]}: {x[i].X:.4f}")
    else:
        print("优化未成功")

    value1 = np.array([''])
    value2 = np.array([''])
    for i in range(len(p1)):
        value1 = np.append(value1, x[i].x)
    for j in range(len(p2)):
        value2 = np.append(value2, y[j].x)
    value1 = value1[1:]
    value2 = value2[1:]

    df = pd.DataFrame({
        'params1': p1,
        'value1': value1,
        'params2': p2,
        'value2': value2
    })
    path = r"C:\software\Github\DRLmicrogrid\Model_zzy\results_ro.xlsx"
    df.to_excel(path, index=False)

# 子问题（第二阶段，基于主问题的解寻找最恶劣场景）
def second_stage_callback(model, where):
    if where == GRB.Callback.MIPSOL:
        # 获得第一阶段解
        x_val = model.cbGetSolution(x)

        # 创建子问题模型
        sub_model = gp.Model('SecondStageRobustOptimization')

        # 定义第二阶段的决策变量

        # 设置目标函数

        # 基于第一阶段的解添加约束

        # 求解子问题

        # 将子问题添加

"""
试测——可以运行
"""

# import gurobipy as gp
# import numpy as np
#
# # 创建模型
# model = gp.Model('TwoStageRobustOptimization')
#
# # 第一阶段数据
# A1 = np.array([
#     [1, 2, 3],
#     [2, 5, 1],
#     [1, 3, 2],
#     [3, 2, 1]
# ])
# p1 = ['x1', 'x2', 'x3']  # 第一阶段决策变量的变量名
# bl1 = np.array([10, 20, 15, 10])  # 第一阶段约束条件最小值
# bu1 = np.array([50, 60, 55, 30])  # 第一阶段约束条件最大值
# c1 = np.array([0.5, 0.8, 0.9])  # 目标值系数
#
# # 第二阶段数据
# A2 = np.array([
#     [1, 2, 3],
#     [2, 5, 1],
#     [1, 2, 2],
#     [3, 2, 1],
#     [2, 3, 2],
#     [1, 1, 1],
#     [2, 2, 1]
# ])
# p2 = ['y1', 'y2', 'y3']  # 第二阶段决策变量的变量名
# bl2 = np.array([15, 20, 10, 30, 25, 15, 10])  # 第二阶段约束条件最小值
# bu2 = np.array([40, 50, 30, 60, 55, 35, 25])  # 第二阶段约束条件最大值
# c2 = np.array([0.4, 0.6, 0.5])  # 第二阶段目标值系数
#
# # 第一阶段变量 x
# x = model.addVars(len(p1), lb=-gp.GRB.INFINITY, name=p1)
#
# # 第二阶段变量 y
# y = model.addVars(len(p2), lb=-gp.GRB.INFINITY, name=p2)
#
# # 添加第一阶段约束 A1 * x ∈ [bl1, bu1]
# for i in range(A1.shape[0]):
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) >= bl1[i])
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) <= bu1[i])
#
# # 添加第二阶段约束 A2 * y ∈ [bl2, bu2]
# for i in range(A2.shape[0]):
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) >= bl2[i])
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) <= bu2[i])
#
# # 目标函数: 第一阶段目标 + 第二阶段最优值
# model.setObjective(
#     gp.quicksum(c1[j] * x[j] for j in range(len(p1))) +
#     gp.quicksum(c2[j] * y[j] for j in range(len(p2))),
#     gp.GRB.MINIMIZE
# )
#
# # 求解
# model.optimize()
#
# # 输出结果
# if model.status == gp.GRB.OPTIMAL:
#     print('Optimal Solution:')
#     for var in model.getVars():
#         print(f'{var.varName}: {var.x}')
#     print(f'Objective Value: {model.objVal}')
# else:
#     print('No optimal solution found.')


"""
试测——无结果
"""
# import gurobipy as gp
# import numpy as np
#
# # 创建模型
# model = gp.Model('TwoStageRobustOptimization')
#
# # 第一阶段数据
# A1 = np.array([
#     [1, 0, 2, 0, 3, 0],  # 第一A2矩阵1 2 4 5
#     [2, 0, 5, 0, 1, 0],
#     [0, 0, 0, 0, 0, 0],
#     [3, 0, 2, 0, 1, 0],
#     [2, 0, 3, 0, 2, 0],
#     [0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0],
# ])
# p1 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第一阶段决策变量的变量名
# bl1 = np.array([15, 20, 10, 30, 25, 15, 10])  # 第一阶段约束条件最小值
# bu1 = np.array([40, 50, 30, 60, 55, 35, 25])  # 第一阶段约束条件最大值
# c1 = np.array([0.5, 0, 0.8, 0, 0.9, 0])  # 目标值系数
#
# # 第二阶段数据
# A2 = np.array([
#     [1, 0, 2, 0, 3, 0],  #
#     [2, 0, 5, 0, 1, 0],  #
#     [0, 1, 0, 2, 0, 2],
#     [3, 0, 2, 0, 1, 0],  #
#     [2, 0, 3, 0, 2, 0],  #
#     [0, 1, 0, 1, 0, 1],
#     [0, 2, 0, 2, 0, 1]
# ])
# p2 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第二阶段决策变量的变量名
# bl2 = np.array([15, 20, 10, 30, 25, 15, 10])  # 第二阶段约束条件最小值
# bu2 = np.array([40, 50, 30, 60, 55, 35, 25])  # 第二阶段约束条件最大值
# c2 = np.array([0.5, 0.4, 0.8, 0.6, 0.9, 0.5])  # 第二阶段目标值系数
#
# # 第一阶段变量 x
# x = model.addVars(len(p1), lb=-gp.GRB.INFINITY, name=p1)
#
# # 第二阶段变量 y
# y = model.addVars(len(p2), lb=-gp.GRB.INFINITY, name=p2)
#
# # 添加第一阶段约束 A1 * x ∈ [bl1, bu1]
# for i in range(A1.shape[0]):
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) >= bl1[i])
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) <= bu1[i])
#
# # 添加第二阶段约束 A2 * y ∈ [bl2, bu2]
# for i in range(A2.shape[0]):
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) >= bl2[i])
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) <= bu2[i])
#
# # 目标函数: 第一阶段目标 + 第二阶段最优值
# model.setObjective(
#     gp.quicksum(c1[j] * x[j] for j in range(len(p1))) +
#     gp.quicksum(c2[j] * y[j] for j in range(len(p2))),
#     gp.GRB.MINIMIZE
# )
#
# # 求解
# model.optimize()
#
# # 输出结果
# if model.status == gp.GRB.OPTIMAL:
#     print('Optimal Solution:')
#     for var in model.getVars():
#         print(f'{var.varName}: {var.x}')
#     print(f'Objective Value: {model.objVal}')
# else:
#     print('No optimal solution found.')

"""
试测
"""
# import gurobipy as gp
# import numpy as np
#
# # 创建模型
# model = gp.Model('TwoStageRobustOptimization')
#
# # 第一阶段数据
# A1 = np.array([
#     [1, 0, 2, 0, 3, 0],  # 第一A2矩阵1 2 4 5
#     [2, 0, 5, 0, 1, 0],
#     [3, 0, 2, 0, 1, 0],
#     [2, 0, 3, 0, 2, 0],
# ])
# p1 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第一阶段决策变量的变量名
# bl1 = np.array([15, 20, 30, 25])  # 第一阶段约束条件最小值
# bu1 = np.array([40, 50, 60, 55])  # 第一阶段约束条件最大值
# c1 = np.array([0.5, 0, 0.8, 0, 0.9, 0])  # 目标值系数
#
# # 第二阶段数据
# A2 = np.array([
#     [1, 0, 2, 0, 3, 0],  #
#     [2, 0, 5, 0, 1, 0],  #
#     [0, 1, 0, 2, 0, 2],
#     [3, 0, 2, 0, 1, 0],  #
#     [2, 0, 3, 0, 2, 0],  #
#     [0, 1, 0, 1, 0, 1],
#     [0, 2, 0, 2, 0, 1]
# ])
# p2 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第二阶段决策变量的变量名
# bl2 = np.array([15, 20, 10, 30, 25, 15, 10])  # 第二阶段约束条件最小值
# bu2 = np.array([40, 50, 30, 60, 55, 35, 25])  # 第二阶段约束条件最大值
# c2 = np.array([0, 0.4, 0, 0.6, 0, 0.5])  # 第二阶段目标值系数
#
# # 第一阶段变量 x
# x = model.addVars(len(p1), lb=-gp.GRB.INFINITY, name=p1)
#
# # 第二阶段变量 y
# y = model.addVars(len(p2), lb=-gp.GRB.INFINITY, name=p2)
#
# # 添加第一阶段约束 A1 * x ∈ [bl1, bu1]
# for i in range(A1.shape[0]):
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) >= bl1[i])
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) <= bu1[i])
#
# # 添加第二阶段约束 A2 * y ∈ [bl2, bu2]
# for i in range(A2.shape[0]):
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) >= bl2[i])
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) <= bu2[i])
#
# # 目标函数: 第一阶段目标 + 第二阶段最优值
# model.setObjective(
#     gp.quicksum(c1[j] * x[j] for j in range(len(p1))) +
#     gp.quicksum(c2[j] * y[j] for j in range(len(p2))),
#     gp.GRB.MINIMIZE
# )
#
# # 求解
# model.optimize()
#
# # 输出结果
# if model.status == gp.GRB.OPTIMAL:
#     print('Optimal Solution:')
#     for var in model.getVars():
#         print(f'{var.varName}: {var.x}')
#     print(f'Objective Value: {model.objVal}')
# else:
#     print('No optimal solution found.')


"""
又是一个试测
"""
# import gurobipy as gp
# import numpy as np
#
# # 创建模型
# model = gp.Model('TwoStageRobustOptimization')
#
# # 第一阶段数据
# A1 = np.array([
#     [1, 0, 2, 0, 3, 0],  # 第一A2矩阵1 2 4 5
#     [2, 0, 5, 0, 1, 0],
#     [3, 0, 2, 0, 1, 0],
#     [2, 0, 3, 0, 2, 0],
# ])
# p1 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第一阶段决策变量的变量名
# bl1 = np.array([15, 20, 30, 25])  # 第一阶段约束条件最小值
# bu1 = np.array([40, 50, 60, 55])  # 第一阶段约束条件最大值
# c1 = np.array([0.5, 0, 0.8, 0, 0.9, 0])  # 目标值系数
#
# # 第二阶段数据
# A2 = np.array([
#     # [1, 0, 2, 0, 3, 0],  #
#     # [2, 0, 5, 0, 1, 0],  #
#     [0, 1, 0, 2, 0, 2],
#     # [3, 0, 2, 0, 1, 0],  #
#     # [2, 0, 3, 0, 2, 0],  #
#     [0, 1, 0, 1, 0, 1],
#     [0, 2, 0, 2, 0, 1]
# ])
# p2 = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3']  # 第二阶段决策变量的变量名
# # bl2 = np.array([15, 20, 10, 30, 25, 15, 10])  # 第二阶段约束条件最小值
# # bu2 = np.array([40, 50, 30, 60, 55, 35, 25])  # 第二阶段约束条件最大值
# bl2 = np.array([10, 15, 10])  # 第二阶段约束条件最小值
# bu2 = np.array([30, 35, 25])  # 第二阶段约束条件最大值
# c2 = np.array([0, 0.4, 0, 0.6, 0, 0.5])  # 第二阶段目标值系数
#
# # 第一阶段变量 x
# x = model.addVars(len(p1), lb=-gp.GRB.INFINITY, name=p1)
#
# # 第二阶段变量 y
# y = model.addVars(len(p2), lb=-gp.GRB.INFINITY, name=p2)
#
# # 添加第一阶段约束 A1 * x ∈ [bl1, bu1]
# for i in range(A1.shape[0]):
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) >= bl1[i])
#     model.addConstr(gp.quicksum(A1[i, j] * x[j] for j in range(A1.shape[1])) <= bu1[i])
#
# # 添加第二阶段约束 A2 * y ∈ [bl2, bu2]
# for i in range(A2.shape[0]):
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) >= bl2[i])
#     model.addConstr(gp.quicksum(A2[i, j] * y[j] for j in range(A2.shape[1])) <= bu2[i])
#
# # 目标函数: 第一阶段目标 + 第二阶段最优值
# model.setObjective(
#     gp.quicksum(c1[j] * x[j] for j in range(len(p1))) +
#     gp.quicksum(c2[j] * y[j] for j in range(len(p2))),
#     gp.GRB.MINIMIZE
# )
#
# # 求解
# model.optimize()
#
# # 输出结果
# if model.status == gp.GRB.OPTIMAL:
#     print('Optimal Solution:')
#     for var in model.getVars():
#         print(f'{var.varName}: {var.x}')
#     print(f'Objective Value: {model.objVal}')
# else:
#     print('No optimal solution found.')


