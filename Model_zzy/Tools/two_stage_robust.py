from pyomo.environ import *
from pyomo.opt import SolverFactory

# 创建模型
model = ConcreteModel()

# 参数设置
num_generators = 3  # 发电机数量
scenarios = 7  # 不确定场景数量

# 第一阶段决策变量
model.x = Var(range(num_generators))  # 第一阶段发电计划

# 第二阶段决策变量，对于每种不确定场景
model.y = Var(range(num_generators), range(scenarios))  # 第二阶段调整变量

# 参数：成本系数、约束矩阵和不确定性场景
c1 = [20, 25, 30]  # 第一阶段运行成本系数
c2 = [40, 45, 50]  # 第二阶段调整成本系数
A1 = [[1, 1, 1], [2, 2, 2]]  # 第一阶段约束矩阵
b1 = [100, 200]  # 第一阶段约束常数项
A2 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # 第二阶段约束矩阵
A3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # 第二阶段与第一阶段变量的关联矩阵
b2_scenarios = [[120, 150, 160], [140, 160, 170]]  # 不同场景下的第二阶段约束常数项

# 第一阶段目标函数
def first_stage_objective(model):
    return sum(c1[i] * model.x[i] for i in range(num_generators))

# 第二阶段目标函数
def second_stage_objective(model):
    return sum(max(sum(c2[j] * model.y[j, s] for j in range(num_generators)) for s in range(scenarios)))

# 合并目标函数
model.obj = Objective(expr=first_stage_objective(model) + second_stage_objective(model), sense=minimize)

# 第一阶段约束
def first_stage_constraint_rule(model, i):
    return sum(A1[i][j] * model.x[j] for j in range(num_generators)) >= b1[i]
model.first_stage_constraints = Constraint(range(len(b1)), rule=first_stage_constraint_rule)

# 第二阶段约束
def second_stage_constraint_rule(model, j, s):
    return sum(A2[j][i] * model.y[i, s] for i in range(num_generators)) >= b2_scenarios[s][j] - sum(A3[j][k] * model.x[k] for k in range(num_generators))
model.second_stage_constraints = Constraint(range(len(A2)), range(scenarios), rule=second_stage_constraint_rule)

# 使用GLPK求解器求解
solver = SolverFactory('gurobi')  # 使用求解器
solver.solve(model, tee=True)

# 输出结果
print("Optimal First-Stage Decision (x):")
for i in range(num_generators):
    print(f"x[{i}] = {model.x[i].value}")

print("\nOptimal Second-Stage Decision (y):")
for j in range(num_generators):
    for s in range(scenarios):
        print(f"y[{j},{s}] = {model.y[j,s].value}")
