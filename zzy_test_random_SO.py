"""
UIES环境配置
"""
import numpy as np
import pandas as pd

import gurobipy as gp
from gurobipy import GRB

from Model_zzy.random_so.Node import Node
from Model_zzy.random_so.ConventionalPowerPlants_area import CPP
from Model_zzy.random_so.GasWell import GW
from Model_zzy.random_so.Demand_RO import D
from Model_zzy.random_so.RenewableProductionUnit_RO import RT, HP
from Model_zzy.random_so.Storage import ES
from Model_zzy.random_so.Conversion_units import CCHP, EB, ER
from Tools.two_stage_robust import two_stage_RO
from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount
from Model_zzy.random_so.Microgrid import MG
from Model_zzy.random_so.Multi_Microgrid import MMGs
from Model_zzy.random_so.Line import Line
from MILP import PrintBounds
from Model_zzy.random_so.Flexible_load import FL
from Model_zzy.random_so.Flexible_demand import FD
from Model_zzy.random_so.Flexible_analysis import FA
from Model_zzy.Tools.divide_num import DivideNum
from datetime import datetime


"时间尺度"
time = 24
path = "zzy_test_random_SO"

"""
所有源网荷储
"""

"负荷"
load_e_01 = D("load_e_01", "e", p_total=65000, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_c_01 = D("load_c_01", "c", p_total=1100, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_h_01 = D("load_h_01", "th", p_total=20000, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_g_01 = D("load_g_01", "g", p_total=48000, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)

"可再生能源"
pv_01 = RT("pv_01", type="PV", id=1, production_price=0.005, production_total=2000, time_num=time)

wt_01 = RT("wt_01", type="WT", id=1, production_price=0.005, production_total=2000, time_num=time)

line_hp_e_01 = Line("line_hp_e_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="node_hp_01", time_num=time, type="e", Convertion=False)
line_hp_h_01 = Line("line_hp_h_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_hp_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
hp_01 = HP("hp_01", type="HP", id=1, production_price=0.008, production_total=2000, time_num=time, line_e=line_hp_e_01,
           line_h=line_hp_h_01)

"能量转化设备"
# 电转冷
line_er_e_01 = Line("line_er_e_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="node_er_01", time_num=time, type="e", Convertion=False)
line_er_c_01 = Line("line_er_c_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_er_01", to_MG="node_c_01", time_num=time, type="c", Convertion=False)
er_01 = ER("er_01", conversion_rate=0.8, conversion_limits=5000, time_num=time, line_e=line_er_e_01, line_c=line_er_c_01)

# 电转热
line_eb_e_01 = Line("line_eb_e_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="eb_01", time_num=time, type="e", Convertion=False)
line_eb_h_01 = Line("line_eb_h_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="eb_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
eb_01 = EB("eb_01", conversion_rate=0.85, conversion_limits=5000, time_num=time, line_e=line_eb_e_01, line_h=line_eb_h_01)

# 气转电热
line_cchp_g_01 = Line("line_cchp_g_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="node_g_01", to_MG="cchp_01", time_num=time, type="g", Convertion=False)
line_cchp_e_01 = Line("line_cchp_e_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="cchp_01", to_MG="node_e_01", time_num=time, type="e", Convertion=False)
line_cchp_h_01 = Line("line_cchp_h_01", maxTransValue=8000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="cchp_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
cchp_01 = CCHP("cchp_01", type="CCHP", conversion_rate_e=0.5, conversion_rate_h=0.8, conversion_limit=5000, time_num=time,
               line_g=line_cchp_g_01, line_e=line_cchp_e_01, line_h=line_cchp_h_01)


"能量存储设备"
# 电能
storage_e_01 = ES("storage_e_01", type="e", id=1, storage_price=0.03, storage_limit=2000, storage_limit_min=500,
                  lifetimes=100000, self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9,
                  time_num=time, begin=None)
# 热能
storage_h_01 = ES("storage_h_01", type="th", id=1, storage_price=0.05, storage_limit=2000, storage_limit_min=200,
                  lifetimes=100000, self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85,
                  time_num=time, begin=None)
# 冷能
storage_c_01 = ES("storage_c_01", type="c", id=1, storage_price=0.05, storage_limit=1000, storage_limit_min=200,
                  lifetimes=100000, self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8,
                  time_num=time, begin=None)

"供能端"
cpp_01 = CPP("cpp_01", id=1, total_production=50000, production_price=1, time_num=time)
# cpp_02 = CPP("cpp_02", id=1, total_production=5000, production_price=-1, time_num=time)
gw_01 = GW("gw_01", id=1, total_production=12000, production_price=1.2, time_num=time)

"柔性负荷"
fl_e_01 = FL("fl_e_01", type="e", limit=500, time_num=time)
fl_g_01 = FL("fl_g_01", type="g", limit=500, time_num=time)
fl_h_01 = FL("fl_h_01", type="th", limit=300, time_num=time)


"""
区域1
"""
node_e_01 = Node("node_e_01", devices=np.array([load_e_01, cpp_01, pv_01, wt_01, storage_e_01, fl_e_01]),
                 sLine=np.array([line_er_e_01, line_eb_e_01, line_hp_e_01]), rLine=np.array([line_cchp_e_01]), time_num=time,
                 type="e")
node_c_01 = Node("node_c_01", devices=np.array([load_c_01, storage_c_01]), sLine=np.array([]), rLine=np.array([line_er_c_01]), time_num=time,
                 type="c")
node_h_01 = Node("node_h_01", devices=np.array([load_h_01, storage_h_01, fl_h_01]), sLine=np.array([]), rLine=np.array([line_eb_h_01, line_hp_h_01,
                                                                                                 line_cchp_h_01]),
                 time_num=time, type="th")
node_g_01 = Node("node_g_01", devices=np.array([load_g_01, gw_01, fl_g_01]), sLine=np.array([line_cchp_g_01]),
                 rLine=np.array([]), time_num=time, type="g")

node_er_01 = Node("node_er_01", devices=np.array([er_01]), sLine=np.array([line_er_c_01]), rLine=np.array([line_er_e_01]),
                  time_num=time, type="ER")
node_eb_01 = Node("node_eb_01", devices=np.array([eb_01]), sLine=np.array([line_eb_h_01]), rLine=np.array([line_eb_e_01]),
                  time_num=time, type="EB")
node_hp_01 = Node("node_hp_01", devices=np.array([hp_01]), sLine=np.array([line_hp_h_01]), rLine=np.array([line_hp_e_01]),
                  time_num=time, type="HP")
node_cchp_01 = Node("node_cchp_01", devices=np.array([cchp_01]), sLine=np.array([line_cchp_e_01, line_cchp_h_01]),
                    rLine=np.array([line_cchp_g_01]), time_num=time, type="CCHP")


"""
向上向下灵活性需求
"""
"""净负荷计算"""
net_load = np.array([node_e_01, node_hp_01])

fd_e = FD(name="fd_e", type="e", net_load_sets=net_load, fluctuation_rate=0.15, time_num=time)
# print(f"电力子系统向上灵活性需求：{fd_e.ud_set}")
# print(f"电力子系统向下灵活性需求：{fd_e.dd_set}")
fd_g = FD(name="fd_g", type="g", net_load_sets=net_load, fluctuation_rate=0.1, time_num=time)
# print(f"天然气子系统向上灵活性需求：{fd_g.ud_set}")
# print(f"天然气子系统向下灵活性需求：{fd_g.dd_set}")
fd_h = FD(name="fd_h", type="th", net_load_sets=net_load, fluctuation_rate=0.1, time_num=time)
# print(f"热能子系统向上灵活性需求：{fd_h.ud_set}")
# print(f"热能子系统向下灵活性需求：{fd_h.dd_set}")
fd_c = FD(name="fd_c", type="c", net_load_sets=net_load, fluctuation_rate=0.1, time_num=time)
# print(f"冷能子系统向上灵活性需求：{fd_c.ud_set}")
# print(f"冷能子系统向下灵活性需求：{fd_c.dd_set}")

node_fd_01 = Node("node_fd_01", devices=np.array([fd_e, fd_g, fd_h, fd_c]), sLine=np.array([]), rLine=np.array([]),
                  time_num=time, type="FD")

sets = np.array([node_fd_01])

"""灵活裕度计算"""
bus_01 = np.array([node_cchp_01, node_eb_01, node_e_01, node_c_01, node_er_01, node_h_01, node_g_01, node_hp_01,
                   node_fd_01])

fa_01 = FA("fa_01", nodes=bus_01, max_limit_rate=1.2, min_limit_rate=-1.2, fm_rate=0.35, fm_max=0.6, sets=sets,
           time_num=time)

node_fa_01 = Node("node_fa_01", devices=np.array([fa_01]), sLine=np.array([]), rLine=np.array([]),
                  time_num=time, type="FA")

bus = np.array([node_e_01, node_c_01, node_er_01, node_h_01, node_eb_01, node_g_01, node_cchp_01, node_hp_01,
                node_fd_01, node_fa_01])

"""加入灵活裕度约束"""
# flexible_analysis(nodes=bus_01, time_num=time)

area01 = MG("area01", node=bus, id=1, type="area01", time_num=time)


"UIES"
UIES = MMGs(np.array([area01]))



# print(f"num.params的长度：{len(num.params)}")
# print(f"num.A的长度：{len(num.A)}")


"""
两阶段鲁棒优化求解
"""
"求解所需参数"
# 第一阶段
# C1, integrality1, num1 = MMGs_logic(UIES, path, flag=False)
# # 第二阶段
# C2, integrality2, num2 = MMGs_logic(UIES, path, flag=False)
#
# # 运用到第一阶段中的设备
# first_stage_device = np.array([er_01, eb_01, cchp_01, fl_e_01, fl_h_01, fl_g_01, storage_e_01, storage_h_01,
#                                storage_c_01, cpp_01, gw_01])
#
# # 得到第一阶段num
# num = DivideNum(num1, num2, C1, C2, first_stage_device, time)
#
# # 打印约束
# # 第一阶段
# print("第一阶段的约束")
# PrintBounds(num.num)
# # 第二阶段
# print("第二阶段的约束")
# PrintBounds(num.num_2)
#
# # print(f"first_stage_num.params的长度：{len(first_stage_num.num.params)}")
# # print(f"first_stage_num.A的长度：{len(first_stage_num.num.A)}")
#
# two_stage_RO(num)
#
#
# # 记录结束时间
# end_time = datetime.now()
#
# # 计算并打印执行时间
# execution_time = end_time - start_time
# print(f"执行时间：{execution_time}")


"""
Gurobi求解
"""
# "求解所需参数"
# C, integrality, num = MMGs_logic(UIES, path, flag=False)
#
# "打印约束"
# PrintBounds(num)
#
# start_time = datetime.now()
#
# A = num.A
# params = num.params
# A = A.reshape((int(len(A) / len(params)), len(params)))
# bl = num.bl
# bu = num.bu
# c = C
#
# model = gp.Model("RO")
#
# # 创建决策变量
# vars = model.addVars(range(len(params)), vtype=gp.GRB.CONTINUOUS)
# for i in range(len(params)):
#     vars[i].varName = params[i]
#
# # 设置目标函数
# model.setObjective(gp.quicksum(c[i] * vars[i] for i in range(len(c))), gp.GRB.MINIMIZE)
#
# # 设置约束
# for j in range(A.shape[0]):
#     model.addConstr(gp.quicksum(A[j, i] * vars[i] for i in range(len(params))) >= bl[j])
#     model.addConstr(gp.quicksum(A[j, i] * vars[i] for i in range(len(params))) <= bu[j])
#
# "求解RO问题"
# model.optimize()
#
# if model.status != gp.GRB.OPTIMAL:
#     model.computeIIS()
#     model.write("model_ro.ilp")
# # 记录结束时间
# end_time = datetime.now()
#
# # 计算并打印执行时间
# execution_time = end_time - start_time
# print(f"执行时间：{execution_time}")
#
# # # 打印结果
# # for i in range(len(num.params)):
# #     print(f"{num.params[i]}的值：{results.x[i]}")
#
# "将求解结果保存至节点"
# # x_callBack(results, UIES, path)
#
# "画图"
# # draw(UIES, np.array([]))
#
# "保存问题的解"
# var_values = np.zeros(len(vars))
# for i in range(len(vars)):
#     var_values[i] = vars[i].x
#
# df = pd.DataFrame({
#     'params': num.params,
#     'value': var_values
# })
# path = "C:\\software\\Github\\DRLmicrogrid\\Model_zzy\\results_ro.xlsx"
# df.to_excel(path, index=False)



"""
MILP求解
"""
"求解所需参数"
C, integrality, num = MMGs_logic(UIES, path, flag=False)

"打印约束"
# PrintBounds(num)

# 开始记录时间
start_time = datetime.now()
print("开始时间：", start_time)

"计算结果"
results = EndCount(C, integrality, num)

# 记录结束时间
end_time = datetime.now()

# 计算并打印执行时间
execution_time = end_time - start_time
print(f"执行时间：{execution_time}")

df = pd.DataFrame({
    'params': num.params,
    'value': results.x
})
path = "C:\\software\\Github\\DRLmicrogrid\\Model_zzy\\random_so\\results_random_so.xlsx"
df.to_excel(path, index=False)




