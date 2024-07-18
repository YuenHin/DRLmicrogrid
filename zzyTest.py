"""UIES环境配置"""
import numpy as np
from Model_zzy.Node import Node
from Model_zzy.ConventionalPowerPlants_area import CPP
from Model_zzy.GasWell import GW
from Model_zzy.Demand import D
from Model_zzy.RenewableProductionUnit import RT
from Model_zzy.Storage import S
from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount
from Model_zzy.Microgrid import MG
from Model_zzy.Multi_Microgrid import MMGs
from Model_zzy.Line import Line

"时间尺度"
time = 24
path = "zzyTest"

"""
    所有的源网荷储
"""

"负荷"
# "时代广场负荷节点1和写字楼负荷节点2"
load_e_01 = D("D_e_01", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_01 = D("D_g_01", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_01 = D("D_h_01", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_01 = D("D_c_01", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# "建材城负荷节点4"
load_e_02 = D("D_e_02", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_02 = D("D_g_02", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_02 = D("D_h_02", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_02 = D("D_c_02", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# "居民区负荷节点3和菜市场负荷节点9"
load_e_03 = D("D_e_03", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_03 = D("D_g_03", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_03 = D("D_h_03", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_03 = D("D_c_03", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# "居民区负荷节点11和广场负荷节点8"
load_e_04 = D("D_e_04", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_04 = D("D_g_04", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_04 = D("D_h_04", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_04 = D("D_c_04", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 学校负荷节点10
load_e_05 = D("D_e_05", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_05 = D("D_g_05", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_05 = D("D_h_05", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_05 = D("D_c_05", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 居民区负荷节点5和医院负荷节点12
load_e_06 = D("D_e_06", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_06 = D("D_g_06", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_06 = D("D_h_06", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_06 = D("D_c_06", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 居民区负荷节点6和广场负荷节点13
load_e_07 = D("D_e_07", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_07 = D("D_g_07", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_07 = D("D_h_07", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_07 = D("D_c_07", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 居民区负荷节点11、居民区负荷节点14和医院负荷节点15
load_e_08 = D("D_e_08", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_08 = D("D_g_08", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_08 = D("D_h_08", "h", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_08 = D("D_c_08", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

"可再生能源出力"
"光伏"
engine_e_pv01 = RT("RT_e_pv01", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
engine_e_pv02 = RT("RT_e_pv02", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
"风机"
engine_e_wt01 = RT("RT_e_wt01", "WT", 1, production_price=0.05, production_total=3000, time_num=time)
engine_e_wt02 = RT("RT_e_wt02", "WT", 1, production_price=0.05, production_total=3000, time_num=time)
"地缘热泵"
engine_h_hp01 = RT("RT_h_hp01", "h", 1, production_price=0.05, production_total=3000, time_num=time)
engine_c_hp01 = RT("RT_c_hp01", "c", 1, production_price=0.05, production_total=3000, time_num=time)
engine_h_hp02 = RT("RT_h_hp02", "h", 1, production_price=0.05, production_total=3000, time_num=time)
engine_c_hp02 = RT("RT_c_hp02", "c", 1, production_price=0.05, production_total=3000, time_num=time)

"能量转化设备"
"冷热电联产"

"电锅炉"

"电制冷机"

"能量存储设备"
"储电装置"
storage_e_01 = S("S_e_01", "e", 1, storage_price=0.03, storage_limit=3000, lifetimes=10000, self_discharging=0.002,
                 charging_rate=0.95, discharging_rate=0.9, time_num=time, begin=None)
"电动汽车集群"

"蓄热罐"
storage_h_01 = S("S_h_01", "h", 1, storage_price=0.03, storage_limit=3000, lifetimes=10000, self_discharging=0.002,
                 charging_rate=0.95, discharging_rate=0.9, time_num=time, begin=None)
"蓄冷罐"
storage_c_01 = S("S_c_01", "c", 1, storage_price=0.03, storage_limit=3000, lifetimes=10000, self_discharging=0.002,
                 charging_rate=0.95, discharging_rate=0.9, time_num=time, begin=None)

"传统电厂"
cpp_e_01 = CPP("CPP_e_01", 1, 4500, production_price=-1, time_num=time)

"天然气井"
gs_g_01 = GW("GW_g_01", 1, 3500, production_price=-1, time_num=time)


"""
    区域01
"""

"Bus01"
"创建线路"
# # 连接光伏与负荷区域01
# bus01_line_01 = Line("bus01_line_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="PV", to_MG="UIES",
#                      time_num=time)
# # 连接风机与负荷区域01
# bus01_line_02 = Line("bus01_line_02", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="WT", to_MG="UIES",
#                      time_num=time)

"创建节点"
# 电节点
node_01_e_01 = Node("bus_01_e_01", devices=np.array([load_e_01, engine_e_pv01, engine_e_wt01, cpp_e_01]),
                      rLine=np.array([]), sLine=np.array([]), time_num=time, type='e')
# 气节点
node_01_g_01 = Node("bus_01_g_01", devices=np.array([load_g_01, gs_g_01]),
                      rLine=np.array([]), sLine=np.array([]), time_num=time, type='g')
# 热节点
# 冷节点



"创建一个区域，将以上节点放在区域01中"
area01 = MG("area01", node=np.array([node_01_e_01, node_01_g_01]), id=1, type="area01", time_num=time)

"创建UIES"
UIES = MMGs(np.array([area01]))

"求解所需参数"
C, integrality, num = MMGs_logic(UIES, path, flag=False)

# for i in range(len(num.params)):
#     print(num.params[i], "  :", np.round(C[i], 2))
# print(num.params)
PrintBounds(num)

"计算结果"
result = EndCount(-C, integrality, num)

"将求解结果保存至节点"
x_callBack(result, UIES, path)

"画图"
draw(UIES, np.array([]))

