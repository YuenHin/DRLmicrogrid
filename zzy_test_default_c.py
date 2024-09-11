"""
UIES环境配置
"""
import numpy as np
from Model_zzy.Node import Node
from Model_zzy.ConventionalPowerPlants_area import CPP
from Model_zzy.GasWell import GW
from Model_zzy.Demand import D
from Model_zzy.RenewableProductionUnit import RT, HP
from Model_zzy.Storage import S, ES
from Model_zzy.Conversion_units import CCHP, EB, ER, CTP
from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount
from Model_zzy.Microgrid import MG
from Model_zzy.Multi_Microgrid import MMGs
from Model_zzy.Line import Line
from MILP import PrintBounds
from Model_zzy.Flexible_load import FL
from Model_zzy.Flexible_demand import FD
from Model_zzy.Flexible_analysis import FA


"时间尺度"
time = 24
path = "zzy_test_defeat_c"

"向上、向下灵活性需求"
fd_e = FD(name="fd_e", type="e", fluctuation_rate=0.15, time_num=time)
fd_g = FD(name="fd_g", type="g", fluctuation_rate=0.1, time_num=time)
fd_h = FD(name="fd_h", type="th", fluctuation_rate=0.1, time_num=time)
fd_c = FD(name="fd_c", type="c", fluctuation_rate=0.1, time_num=time)
ud_set = fd_e.ud_set + fd_g.ud_set + fd_h.ud_set + fd_c.ud_set
dd_set = fd_e.dd_set + fd_g.dd_set + fd_h.dd_set + fd_c.dd_set

"""
所有源网荷储
"""

"负荷"
load_e_01 = D("load_e_01", "e", p_total=4000, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_c_01 = D("load_c_01", "c", p_total=1500, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_h_01 = D("load_h_01", "th", p_total=1500, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)
load_g_01 = D("load_g_01", "g", p_total=1500, id=1, MG_id=1, ramping_rate=0.15, time_num=time, stochastic_value=10)

"可再生能源"
pv_01 = RT("pv_01", type="PV", id=1, production_price=0.05, production_total=2000, time_num=time)

wt_01 = RT("wt_01", type="WT", id=1, production_price=0.05, production_total=2000, time_num=time)

line_hp_e_01 = Line("line_hp_e_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="node_hp_01", time_num=time, type="e", Convertion=False)
line_hp_h_01 = Line("line_hp_h_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_hp_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
hp_01 = HP("hp_01", type="HP", id=1, production_price=0.05, production_total=2000, time_num=time, line_e=line_hp_e_01,
           line_h=line_hp_h_01)

"能量转化设备"
# 电转冷
line_er_e_01 = Line("line_er_e_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="node_er_01", time_num=time, type="e", Convertion=False)
line_er_c_01 = Line("line_er_c_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_er_01", to_MG="node_c_01", time_num=time, type="c", Convertion=False)
er_01 = ER("er_01", conversion_rate=0.8, conversion_limits=5000, time_num=time, line_e=line_er_e_01, line_c=line_er_c_01,
           ud_set=ud_set, dd_set=dd_set)

# 电转热
line_eb_e_01 = Line("line_eb_e_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="node_e_01", to_MG="eb_01", time_num=time, type="e", Convertion=False)
line_eb_h_01 = Line("line_eb_h_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                    from_MG="eb_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
eb_01 = EB("eb_01", conversion_rate=0.85, conversion_limits=5000, time_num=time, line_e=line_eb_e_01, line_h=line_eb_h_01,
           ud_set=ud_set, dd_set=dd_set)

# 气转电热
line_cchp_g_01 = Line("line_cchp_g_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="node_g_01", to_MG="cchp_01", time_num=time, type="g", Convertion=False)
line_cchp_e_01 = Line("line_cchp_e_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="cchp_01", to_MG="node_e_01", time_num=time, type="e", Convertion=False)
line_cchp_h_01 = Line("line_cchp_h_01", maxTransValue=4000, line_price=-0.001, Single=True, MG_point=True,
                      from_MG="cchp_01", to_MG="node_h_01", time_num=time, type="th", Convertion=False)
cchp_01 = CCHP("cchp_01", type="CCHP", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_limit=2000, time_num=time,
               line_g=line_cchp_g_01, line_e=line_cchp_e_01, line_h=line_cchp_h_01, ud_set=ud_set, dd_set=dd_set)

"能量存储设备"
# 电能
storage_e_01 = ES("storage_e_01", type="e", id=1, storage_price=0.03, storage_limit=5000, storage_limit_min=500,
                  lifetimes=100000, self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time,
                  ud_set=ud_set, dd_set=dd_set, begin=None)
# 热能
storage_h_01 = ES("storage_h_01", type="th", id=1, storage_price=0.05, storage_limit=3000, storage_limit_min=200,
                  lifetimes=100000, self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time,
                  ud_set=ud_set, dd_set=dd_set, begin=None)
# 冷能
storage_c_01 = ES("storage_c_01", type="c", id=1, storage_price=0.05, storage_limit=2000, storage_limit_min=150,
                  lifetimes=100000, self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time,
                  ud_set=ud_set, dd_set=dd_set, begin=None)

"供能端"
cpp_01 = CPP("cpp_01", id=1, total_production=10000, production_price=-1, time_num=time)
cpp_02 = CPP("cpp_02", id=1, total_production=5000, production_price=-1, time_num=time)
gw_01 = GW("gw_01", id=1, total_production=8000, production_price=-1, time_num=time)

"柔性负荷"
fl_e_01 = FL("fl_e_01", type="e", fl_min=30, fl_max=300, time_num=time)
fl_g_01 = FL("fl_g_01", type="g", fl_min=10, fl_max=100, time_num=time)
fl_h_01 = FL("fl_h_01", type="th", fl_min=20, fl_max=200, time_num=time)


"区域1"
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

bus_01 = np.array([node_e_01, node_c_01, node_er_01, node_h_01, node_eb_01, node_g_01, node_cchp_01, node_hp_01])


# "灵活性缺额放入约束"
# fa = FA("flexible_analysis", bus_01, time, ud_set, dd_set)

area01 = MG("area01", node=bus_01, id=1, type="area01", time_num=time)


"UIES"
UIES = MMGs(np.array([area01]))

"求解所需参数"
C, integrality, num = MMGs_logic(UIES, path, flag=False)
PrintBounds(num)

"计算结果"
results = EndCount(-C, integrality, num)

# print("num的A矩阵")
# print(num.A)
# print(num.A.shape)
# print("num的决策变量")
# print(num.params)
# print(num.params.shape)

"将求解结果保存至节点"
x_callBack(results, UIES, path)

"画图"
draw(UIES, np.array([]))
