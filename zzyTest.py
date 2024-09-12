"""UIES环境配置"""
import numpy as np
from Model_zzy.Node import Node
from Model_zzy.ConventionalPowerPlants_area import CPP
from Model_zzy.GasWell import GW
from Model_zzy.Demand import D
from Model_zzy.RenewableProductionUnit import RT, HP
from Model_zzy.Storage import S, ES, EV
from Model_zzy.Conversion_units import CCHP, EB, ER, CTP
from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount
from Model_zzy.Microgrid import MG
from Model_zzy.Multi_Microgrid import MMGs
from Model_zzy.Line import Line
from MILP import PrintBounds

"时间尺度"
time = 24
path = "zzyTest"

"""
    所有的源网荷储
"""

"所有的负荷节点"
# "时代广场负荷节点1和写字楼负荷节点2"
# Bus_01
load_e_01 = D("D_e_01", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_01 = D("D_g_01", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_01 = D("D_h_01", "th", 1500, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_01 = D("D_c_01", "c", 1000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# "居民区负荷节点3和菜市场负荷节点9"
# Bus_02
load_e_02 = D("D_e_02", "e", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_02 = D("D_g_02", "g", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_02 = D("D_h_02", "th", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_02 = D("D_c_02", "c", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# "建材城负荷节点4"
# Bus_03
load_e_03 = D("D_e_03", "e", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_03 = D("D_g_03", "g", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_03 = D("D_h_03", "th", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_03 = D("D_c_03", "c", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 学校负荷节点10
# Bus_04
load_e_04 = D("D_e_04", "e", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_g_04 = D("D_g_04", "g", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_h_04 = D("D_h_04", "th", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
load_c_04 = D("D_c_04", "c", 400, 1, MG_id=1, ramping_rate=0.25, time_num=time)
#
# # "居民区负荷节点7和广场负荷节点8"
# # Bus_05
# load_e_05 = D("D_e_05", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_g_05 = D("D_g_05", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_h_05 = D("D_h_05", "th", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_c_05 = D("D_c_05", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

# 居民区负荷节点5和医院负荷节点12
# Bus_06
# load_e_06 = D("D_e_06", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_g_06 = D("D_g_06", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_h_06 = D("D_h_06", "th", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_c_06 = D("D_c_06", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
#
# # 居民区负荷节点6和广场负荷节点13
# # Bus_07
# load_e_07 = D("D_e_07", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_g_07 = D("D_g_07", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_h_07 = D("D_h_07", "th", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_c_07 = D("D_c_07", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
#
# # 居民区负荷节点11、居民区负荷节点14和医院负荷节点15
# # Bus_08
# load_e_08 = D("D_e_08", "e", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_g_08 = D("D_g_08", "g", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_h_08 = D("D_h_08", "th", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)
# load_c_08 = D("D_c_08", "c", 4000, 1, MG_id=1, ramping_rate=0.25, time_num=time)

"所有的可再生能源出力节点"
"光伏"
engine_e_pv01 = RT("RT_e_pv01", "PV", 1, production_price=0.05, production_total=2000, time_num=time)
engine_e_pv02 = RT("RT_e_pv02", "PV", 1, production_price=0.05, production_total=2000, time_num=time)
engine_e_pv04 = RT("RT_e_pv04", "PV", 1, production_price=0.05, production_total=2000, time_num=time)
# engine_e_pv05 = RT("RT_e_pv05", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
# engine_e_pv06 = RT("RT_e_pv06", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
# engine_e_pv07 = RT("RT_e_pv07", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
# engine_e_pv08 = RT("RT_e_pv08", "PV", 1, production_price=0.05, production_total=5000, time_num=time)
"风机"
engine_e_wt01 = RT("RT_e_wt01", "WT", 1, production_price=0.05, production_total=2000, time_num=time)
engine_e_wt02 = RT("RT_e_wt02", "WT", 1, production_price=0.05, production_total=2000, time_num=time)
engine_e_wt04 = RT("RT_e_wt04", "WT", 1, production_price=0.05, production_total=2000, time_num=time)
# engine_e_wt05 = RT("RT_e_wt05", "WT", 1, production_price=0.05, production_total=3000, time_num=time)
# engine_e_wt07 = RT("RT_e_wt07", "WT", 1, production_price=0.05, production_total=3000, time_num=time)
"地缘热泵"
# 需要先定义线路
line_hp_e_01 = Line("line_hp_e_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_01",
                    to_MG="hp_01", time_num=time)
line_hp_h_01 = Line("line_hp_h_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_01",
                    to_MG="bus_h_01", time_num=time)
engine_h_hp01 = HP("RT_h_hp01", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
                   line_e=line_hp_e_01, line_h=line_hp_h_01)

line_hp_e_02 = Line("line_hp_e_02", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_02",
                    to_MG="hp_02", time_num=time)
line_hp_h_02 = Line("line_hp_h_02", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_02",
                    to_MG="bus_h_02", time_num=time)
engine_h_hp02 = HP("RT_h_hp02", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
                   line_e=line_hp_e_02, line_h=line_hp_h_02)

line_hp_e_04 = Line("line_hp_e_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_04",
                    to_MG="hp_04", time_num=time)
line_hp_h_04 = Line("line_hp_h_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_04",
                    to_MG="bus_h_04", time_num=time)
engine_h_hp04 = HP("RT_h_hp04", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
                   line_e=line_hp_e_04, line_h=line_hp_h_04)
#
# line_hp_e_05 = Line("line_hp_e_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_05",
#                     to_MG="hp_05", time_num=time)
# line_hp_h_05 = Line("line_hp_h_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_05",
#                     to_MG="bus_h_05", time_num=time)
# engine_h_hp05 = HP("RT_h_hp05", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
#                    line_e=line_hp_e_05, line_h=line_hp_h_05)

# line_hp_e_07 = Line("line_hp_e_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_07",
#                     to_MG="hp_07", time_num=time)
# line_hp_h_07 = Line("line_hp_h_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_07",
#                     to_MG="bus_h_07", time_num=time)
# engine_h_hp07 = HP("RT_h_hp07", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
#                    line_e=line_hp_e_07, line_h=line_hp_h_07)
#
# line_hp_e_08 = Line("line_hp_e_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_08",
#                     to_MG="hp_08", time_num=time)
# line_hp_h_08 = Line("line_hp_h_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="hp_08",
#                     to_MG="bus_h_08", time_num=time)
# engine_h_hp08 = HP("RT_h_hp08", "HP", 1, production_price=0.05, production_total=3000, time_num=time,
#                    line_e=line_hp_e_08, line_h=line_hp_h_08)

"能量转化设备"
"冷热电联产"
line_cchp_g_01 = Line("line_cchp_g_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_01",
                      to_MG="cchp_01", time_num=time)
line_cchp_e_01 = Line("line_cchp_e_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_01",
                      to_MG="bus_e_01", time_num=time)
line_cchp_h_01 = Line("line_cchp_h_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_01",
                      to_MG="bus_h_01", time_num=time)
cchp_01 = CCHP("cchp_01", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
               time_num=time, line_g=line_cchp_g_01, line_e=line_cchp_e_01, line_h=line_cchp_h_01)
# cchp_01 = CTP("cchp_01", 0.8, 0.5, 1000, time, line_cchp_g_01, line_cchp_e_01, line_cchp_h_01)

line_cchp_g_03 = Line("line_cchp_g_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_03",
                      to_MG="cchp_03", time_num=time)
line_cchp_e_03 = Line("line_cchp_e_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_03",
                      to_MG="bus_e_03", time_num=time)
line_cchp_h_03 = Line("line_cchp_h_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_03",
                      to_MG="bus_h_03", time_num=time)
cchp_03 = CCHP("CCHP_03", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
               time_num=time, line_g=line_cchp_g_03, line_e=line_cchp_e_03, line_h=line_cchp_h_03)

line_cchp_g_04 = Line("line_cchp_g_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_04",
                      to_MG="cchp_04", time_num=time)
line_cchp_e_04 = Line("line_cchp_e_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_04",
                      to_MG="bus_e_04", time_num=time)
line_cchp_h_04 = Line("line_cchp_h_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_04",
                      to_MG="bus_h_04", time_num=time)
cchp_04 = CCHP("CCHP_04", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
               time_num=time, line_g=line_cchp_g_04, line_e=line_cchp_e_04, line_h=line_cchp_h_04)

# line_cchp_g_05 = Line("line_cchp_g_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_05",
#                       to_MG="cchp_05", time_num=time)
# line_cchp_e_05 = Line("line_cchp_e_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_05",
#                       to_MG="bus_e_05", time_num=time)
# line_cchp_h_05 = Line("line_cchp_h_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_05",
#                       to_MG="bus_h_05", time_num=time)
# cchp_05 = CCHP("CCHP_05", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
#                time_num=time, line_g=line_cchp_g_05, line_e=line_cchp_e_05, line_h=line_cchp_h_05)

# line_cchp_g_06 = Line("line_cchp_g_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_06",
#                       to_MG="cchp_06", time_num=time)
# line_cchp_e_06 = Line("line_cchp_e_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_06",
#                       to_MG="bus_e_06", time_num=time)
# line_cchp_h_06 = Line("line_cchp_h_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_06",
#                       to_MG="bus_h_06", time_num=time)
# cchp_06 = CCHP("CCHP_06", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
#                time_num=time, line_g=line_cchp_g_06, line_e=line_cchp_e_06, line_h=line_cchp_h_06)
#
# line_cchp_g_07 = Line("line_cchp_g_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_07",
#                       to_MG="cchp_07", time_num=time)
# line_cchp_e_07 = Line("line_cchp_e_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_07",
#                       to_MG="bus_e_07", time_num=time)
# line_cchp_h_07 = Line("line_cchp_h_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_07",
#                       to_MG="bus_h_07", time_num=time)
# cchp_07 = CCHP("CCHP_07", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
#                time_num=time, line_g=line_cchp_g_07, line_e=line_cchp_e_07, line_h=line_cchp_h_07)
#
# line_cchp_g_08 = Line("line_cchp_g_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_g_08",
#                       to_MG="cchp_08", time_num=time)
# line_cchp_e_08 = Line("line_cchp_e_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_08",
#                       to_MG="bus_e_08", time_num=time)
# line_cchp_h_08 = Line("line_cchp_h_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="cchp_08",
#                       to_MG="bus_h_08", time_num=time)
# cchp_08 = CCHP("CCHP_08", conversion_rate_e=0.8, conversion_rate_h=0.5, conversion_rate_c=0.4, conversion_limit=1000,
#                time_num=time, line_g=line_cchp_g_08, line_e=line_cchp_e_08, line_h=line_cchp_h_08)

"电锅炉"
line_eb_e_01 = Line("line_eb_e_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_01",
                    to_MG="eb_01", time_num=time)
line_eb_h_01 = Line("line_eb_h_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_01",
                    to_MG="bus_h_01", time_num=time)
eb_01 = EB("eb_01", conversion_rate=0.9, conversion_limits=5000, time_num=time, line_e=line_eb_e_01,
           line_h=line_eb_h_01)

line_eb_e_03 = Line("line_eb_e_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_03",
                    to_MG="eb_03", time_num=time)
line_eb_h_03 = Line("line_eb_h_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_03",
                    to_MG="bus_h_03", time_num=time)
eb_03 = EB("eb_03", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_03,
           line_h=line_eb_h_03)

line_eb_e_04 = Line("line_eb_e_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_04",
                    to_MG="eb_04", time_num=time)
line_eb_h_04 = Line("line_eb_h_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_04",
                    to_MG="bus_h_04", time_num=time)
eb_04 = EB("eb_04", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_04,
           line_h=line_eb_h_04)

# line_eb_e_05 = Line("line_eb_e_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_05",
#                     to_MG="eb_05", time_num=time)
# line_eb_h_05 = Line("line_eb_h_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_05",
#                     to_MG="bus_h_05", time_num=time)
# eb_05 = EB("eb_05", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_05,
#            line_h=line_eb_h_05)

# line_eb_e_06 = Line("line_eb_e_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_06",
#                     to_MG="eb_06", time_num=time)
# line_eb_h_06 = Line("line_eb_h_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_06",
#                     to_MG="bus_h_06", time_num=time)
# eb_06 = EB("eb_06", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_06,
#            line_h=line_eb_h_06)
#
# line_eb_e_07 = Line("line_eb_e_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_07",
#                     to_MG="eb_07", time_num=time)
# line_eb_h_07 = Line("line_eb_h_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_07",
#                     to_MG="bus_h_07", time_num=time)
# eb_07 = EB("eb_07", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_07,
#            line_h=line_eb_h_07)
#
# line_eb_e_08 = Line("line_eb_e_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_08",
#                     to_MG="eb_08", time_num=time)
# line_eb_h_08 = Line("line_eb_h_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="eb_08",
#                     to_MG="bus_h_08", time_num=time)
# eb_08 = EB("eb_08", conversion_rate=0.9, conversion_limits=500, time_num=time, line_e=line_eb_e_08,
#            line_h=line_eb_h_08)

"电制冷机"
line_er_e_01 = Line("line_er_e_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_01",
                    to_MG="er_01", time_num=time)
line_er_c_01 = Line("line_er_c_01", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_01",
                    to_MG="bus_c_01", time_num=time)
er_01 = ER("er_01", conversion_rate=0.8, conversion_limits=5000, time_num=time, line_e=line_er_e_01,
           line_c=line_er_c_01)

line_er_e_02 = Line("line_er_e_02", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_02",
                    to_MG="er_02", time_num=time)
line_er_c_02 = Line("line_er_c_02", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_02",
                    to_MG="bus_c_02", time_num=time)
er_02 = ER("er_02", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_02,
           line_c=line_er_c_02)

line_er_e_03 = Line("line_er_e_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_03",
                    to_MG="er_03", time_num=time)
line_er_c_03 = Line("line_er_c_03", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_03",
                    to_MG="bus_c_03", time_num=time)
er_03 = ER("er_03", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_03,
           line_c=line_er_c_03)

line_er_e_04 = Line("line_er_e_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_04",
                    to_MG="er_04", time_num=time)
line_er_c_04 = Line("line_er_c_04", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_04",
                    to_MG="bus_c_04", time_num=time)
er_04 = ER("er_04", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_04,
           line_c=line_er_c_04)



# line_er_e_05 = Line("line_er_e_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_05",
#                     to_MG="er_05", time_num=time)
# line_er_c_05 = Line("line_er_c_05", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_05",
#                     to_MG="bus_c_05", time_num=time)
# er_05 = ER("er_05", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_05,
#            line_c=line_er_c_05)

# line_er_e_06 = Line("line_er_e_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_06",
#                     to_MG="er_06", time_num=time)
# line_er_c_06 = Line("line_er_c_06", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_06",
#                     to_MG="bus_c_06", time_num=time)
# er_06 = ER("er_06", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_06,
#            line_c=line_er_c_06)
#
# line_er_e_07 = Line("line_er_e_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_07",
#                     to_MG="er_07", time_num=time)
# line_er_c_07 = Line("line_er_c_07", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_07",
#                     to_MG="bus_c_07", time_num=time)
# er_07 = ER("er_07", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_07,
#            line_c=line_er_c_07)
#
# line_er_e_08 = Line("line_er_e_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="bus_e_08",
#                     to_MG="er_08", time_num=time)
# line_er_c_08 = Line("line_er_c_08", 4000, line_price=-0.001, Single=True, MG_point=True, from_MG="er_08",
#                     to_MG="bus_c_08", time_num=time)
# er_08 = ER("er_08", conversion_rate=0.8, conversion_limits=800, time_num=time, line_e=line_er_e_08,
#            line_c=line_er_c_08)

"能量存储设备"
"储电装置"
storage_e_01 = ES("S_e_01", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
                  self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
storage_e_02 = ES("S_e_02", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
                  self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
storage_e_03 = ES("S_e_03", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
                  self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
storage_e_04 = ES("S_e_04", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
                  self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# storage_e_05 = ES("S_e_05", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
#                   self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# storage_e_06 = ES("S_e_06", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
#                   self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# storage_e_07 = ES("S_e_07", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
#                   self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# storage_e_08 = ES("S_e_08", "e", 1, storage_price=0.03, storage_limit=5000, storage_limit_min=500, lifetimes=10000,
#                   self_discharging=0.002, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
"电动汽车集群"
"目前只是每一个Bus里面只有一辆新能源汽车"
# ev_01 = EV("ev_01", 1, storage_price=1.5, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_02 = EV("ev_02", 1, storage_price=0.5, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_03 = EV("ev_03", 1, storage_price=1.3, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_04 = EV("ev_04", 1, storage_price=0.8, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_05 = EV("ev_05", 1, storage_price=1.3, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_06 = EV("ev_06", 1, storage_price=1.8, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_07 = EV("ev_07", 1, storage_price=0.5, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)
# ev_08 = EV("ev_08", 1, storage_price=1, storage_limit_max=75, storage_limit_min=5, lifetimes=300000,
#            self_discharging=0.0001, charging_rate=0.9, discharging_rate=0.9, time_num=time, begin=None)

"蓄热罐"
storage_h_01 = ES("S_h_01", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
                  self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
storage_h_02 = ES("S_h_02", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
                  self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
storage_h_03 = ES("S_h_03", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
                  self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
storage_h_04 = ES("S_h_04", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
                  self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
# storage_h_05 = ES("S_h_05", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
#                   self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
# storage_h_06 = ES("S_h_06", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
#                   self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
# storage_h_07 = ES("S_h_07", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
#                   self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
# storage_h_08 = ES("S_h_08", "th", 1, storage_price=0.03, storage_limit=2500, storage_limit_min=300, lifetimes=10000,
#                   self_discharging=0.015, charging_rate=0.85, discharging_rate=0.85, time_num=time, begin=None)
"蓄冷罐"
storage_c_01 = ES("S_c_01", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
                  self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
storage_c_02 = ES("S_c_02", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
                  self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
storage_c_03 = ES("S_c_03", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
                  self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
storage_c_04 = ES("S_c_04", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
                  self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
# storage_c_05 = ES("S_c_05", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
#                   self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
# storage_c_06 = ES("S_c_06", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
#                   self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
# storage_c_07 = ES("S_c_07", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
#                   self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)
# storage_c_08 = ES("S_c_08", "c", 1, storage_price=0.03, storage_limit=2000, storage_limit_min=200, lifetimes=10000,
#                   self_discharging=0.02, charging_rate=0.8, discharging_rate=0.8, time_num=time, begin=None)

"外网供能量"
"传统电厂"
# cpp_e_01 = CPP("CPP_e_01", 1, 4500, production_price=-1, time_num=time)
# cpp_e_02 = CPP("CPP_e_02", 1, 4500, production_price=-1, time_num=time)
# cpp_e_03 = CPP("CPP_e_03", 1, 4500, production_price=-1, time_num=time)
# cpp_e_04 = CPP("CPP_e_04", 1, 4500, production_price=-1, time_num=time)

cpp_e_01 = CPP("CPP_e_01", 1, 4500, production_price=-1, time_num=time)
cpp_e_02 = CPP("CPP_e_02", 1, 4000, production_price=-1, time_num=time)
cpp_e_03 = CPP("CPP_e_03", 1, 4000, production_price=-1, time_num=time)
cpp_e_04 = CPP("CPP_e_04", 1, 4000, production_price=-1, time_num=time)
# cpp_e_05 = CPP("CPP_e_05", 1, 4500, production_price=-1, time_num=time)
# cpp_e_06 = CPP("CPP_e_06", 1, 4500, production_price=-1, time_num=time)
# cpp_e_07 = CPP("CPP_e_07", 1, 4500, production_price=-1, time_num=time)
# cpp_e_08 = CPP("CPP_e_08", 1, 4500, production_price=-1, time_num=time)

"天然气井"
# gs_g_01 = GW("GW_g_01", 1, 4500, production_price=-1, time_num=time)
# gs_g_02 = GW("GW_g_02", 1, 4500, production_price=-1, time_num=time)
# gs_g_03 = GW("GW_g_03", 1, 4500, production_price=-1, time_num=time)
# gs_g_04 = GW("GW_g_04", 1, 4500, production_price=-1, time_num=time)

gs_g_01 = GW("GW_g_01", 1, 4000, production_price=-1, time_num=time)
gs_g_02 = GW("GW_g_02", 1, 4000, production_price=-1, time_num=time)
gs_g_03 = GW("GW_g_03", 1, 4000, production_price=-1, time_num=time)
gs_g_04 = GW("GW_g_04", 1, 4000, production_price=-1, time_num=time)

# gs_g_05 = GW("GW_g_05", 1, 4500, production_price=-1, time_num=time)
# gs_g_06 = GW("GW_g_06", 1, 4500, production_price=-1, time_num=time)
# gs_g_07 = GW("GW_g_07", 1, 4500, production_price=-1, time_num=time)
# gs_g_08 = GW("GW_g_08", 1, 4500, production_price=-1, time_num=time)

"""
    区域01
"""
# 电节点
node_01_e = Node("bus_01_e", devices=np.array([load_e_01, cpp_e_01, engine_e_pv01, engine_e_wt01, storage_e_01]),
                 rLine=np.array([line_cchp_e_01]), sLine=np.array([line_eb_e_01, line_hp_e_01, line_er_e_01]),
                 time_num=time, type='e')
# 气节点
node_01_g = Node("bus_01_g", devices=np.array([load_g_01, gs_g_01]), rLine=np.array([]),
                 sLine=np.array([line_cchp_g_01]),
                 time_num=time, type="g")
# 热节点
node_01_h = Node("bus_01_h", devices=np.array([load_h_01, storage_h_01]), rLine=np.array([line_eb_h_01, line_cchp_h_01,
                                                                                          line_hp_h_01])
                 , sLine=np.array([]), time_num=time, type="th")
# 冷节点
node_01_c = Node("bus_01_c", devices=np.array([load_c_01, storage_c_01]), rLine=np.array([]),
                 sLine=np.array([]), time_num=time, type="c")
# 地缘热泵节点
node_01_hp = Node("bus_01_hp", devices=np.array([engine_h_hp01]), rLine=np.array([line_hp_e_01]),
                  sLine=np.array([line_hp_h_01]), time_num=time, type="HP")
# 冷热电联产节点
node_01_cchp = Node("bus_01_cchp", devices=np.array([cchp_01]), rLine=np.array([line_cchp_g_01]),
                    sLine=np.array([line_cchp_e_01, line_cchp_h_01]), time_num=time, type="CCHP")
# 电热锅炉节点
node_01_eb = Node("bus_01_eb", devices=np.array([eb_01]), rLine=np.array([line_eb_e_01]),
                  sLine=np.array([line_eb_h_01]), time_num=time, type="EB")
# 电制冷节点
node_01_er = Node("bus_01_er", devices=np.array([er_01]), rLine=np.array([line_er_e_01]),
                  sLine=np.array([line_er_c_01]), time_num=time, type="ER")

"创建一个区域，将以上节点放在区域01中"
area01 = MG("area01", node=np.array([node_01_e, node_01_h, node_01_eb, node_01_g, node_01_cchp, node_01_c, node_01_er,
                                     ]),
            id=1, type="area01", time_num=time)

# """
# 区域02
# """
# # 电节点
# node_02_e = Node("bus_02_e", devices=np.array([load_e_02, cpp_e_02, engine_e_pv02, engine_e_wt02, storage_e_02]),
#                  rLine=np.array([]), sLine=np.array([line_er_e_02, line_hp_e_02]),
#                  time_num=time, type='e')
# # 气节点
# node_02_g = Node("bus_02_g", devices=np.array([load_g_02, gs_g_02]), rLine=np.array([]),
#                  sLine=np.array([]),
#                  time_num=time, type="g")
# # 热节点
# node_02_h = Node("bus_02_h", devices=np.array([load_h_02, storage_h_02]), rLine=np.array([line_hp_h_02]),
#                  sLine=np.array([]), time_num=time, type="th")
# # 冷节点
# node_02_c = Node("bus_02_c", devices=np.array([load_c_02, storage_c_02]), rLine=np.array([line_er_c_02]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 地缘热泵节点
# node_02_hp = Node("bus_02_hp", devices=np.array([engine_h_hp02]), rLine=np.array([line_hp_e_02]),
#                   sLine=np.array([line_hp_h_02]), time_num=time, type="HP")
# # 电制冷节点
# node_02_er = Node("bus_02_er", devices=np.array([er_02]), rLine=np.array([line_er_e_02]),
#                   sLine=np.array([line_er_c_02]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域02中"
# area02 = MG("area02", node=np.array([node_02_e, node_02_h, node_02_g, node_02_c, node_02_er,
#                                      node_02_hp]),
#             id=1, type="area02", time_num=time)
#
# """
# 区域03
# """
# # 电节点
# node_03_e = Node("bus_03_e", devices=np.array([load_e_03, cpp_e_03, storage_e_03]),
#                  rLine=np.array([line_cchp_e_03]), sLine=np.array([line_eb_e_03, line_er_e_03]),
#                  time_num=time, type='e')
# # 气节点
# node_03_g = Node("bus_03_g", devices=np.array([load_g_03, gs_g_03]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_03]),
#                  time_num=time, type="g")
# # 热节点
# node_03_h = Node("bus_03_h", devices=np.array([load_h_03, storage_h_03]), rLine=np.array([line_eb_h_03, line_cchp_h_03])
#                  , sLine=np.array([]), time_num=time, type="th")
#
# # 冷节点
# node_03_c = Node("bus_03_c", devices=np.array([load_c_03, storage_c_03]), rLine=np.array([line_er_c_03]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 冷热电联产节点
# node_03_cchp = Node("bus_03_cchp", devices=np.array([cchp_03]), rLine=np.array([line_cchp_g_03]),
#                     sLine=np.array([line_cchp_e_03, line_cchp_h_03]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_03_eb = Node("bus_03_eb", devices=np.array([eb_03]), rLine=np.array([line_eb_e_03]),
#                   sLine=np.array([line_eb_h_03]), time_num=time, type="EB")
# # 电制冷节点
# node_03_er = Node("bus_03_er", devices=np.array([er_03]), rLine=np.array([line_er_e_03]),
#                   sLine=np.array([line_er_c_03]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域03中"
# area03 = MG("area03", node=np.array([node_03_e, node_03_h, node_03_eb, node_03_g, node_03_cchp, node_03_c, node_03_er]),
#             id=1, type="area03", time_num=time)
#
# """
#     区域04
# """
# # 电节点
# node_04_e = Node("bus_04_e", devices=np.array([load_e_04, cpp_e_04, engine_e_pv04, engine_e_wt04, storage_e_04]),
#                  rLine=np.array([line_cchp_e_04]), sLine=np.array([line_eb_e_04, line_er_e_04, line_hp_e_04]),
#                  time_num=time, type='e')
# # 气节点
# node_04_g = Node("bus_04_g", devices=np.array([load_g_04, gs_g_04]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_04]),
#                  time_num=time, type="g")
# # 热节点
# node_04_h = Node("bus_04_h", devices=np.array([load_h_04, storage_h_04]), rLine=np.array([line_eb_h_04, line_cchp_h_04,
#                                                                                           line_hp_h_04])
#                  , sLine=np.array([]), time_num=time, type="th")
# # 冷节点
# node_04_c = Node("bus_04_c", devices=np.array([load_c_04, storage_c_04]), rLine=np.array([line_er_c_04]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 地缘热泵节点
# node_04_hp = Node("bus_04_hp", devices=np.array([engine_h_hp04]), rLine=np.array([line_hp_e_04]),
#                   sLine=np.array([line_hp_h_04]), time_num=time, type="HP")
# # 冷热电联产节点
# node_04_cchp = Node("bus_04_cchp", devices=np.array([cchp_04]), rLine=np.array([line_cchp_g_04]),
#                     sLine=np.array([line_cchp_e_04, line_cchp_h_04]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_04_eb = Node("bus_04_eb", devices=np.array([eb_04]), rLine=np.array([line_eb_e_04]),
#                   sLine=np.array([line_eb_h_04]), time_num=time, type="EB")
# # 电制冷节点
# node_04_er = Node("bus_04_er", devices=np.array([er_04]), rLine=np.array([line_er_e_04]),
#                   sLine=np.array([line_er_c_04]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域01中"
# area04 = MG("area04", node=np.array([node_04_e, node_04_h, node_04_eb, node_04_g, node_04_cchp, node_04_c, node_04_er,
#                                      node_04_hp]),
#             id=1, type="area04", time_num=time)

"""
    区域05
"""
# 电节点
# node_05_e = Node("bus_05_e", devices=np.array([load_e_05, cpp_e_05, engine_e_pv05, engine_e_wt05, storage_e_05]),
#                  rLine=np.array([line_cchp_e_05]), sLine=np.array([line_eb_e_05, line_er_e_05, line_hp_e_05]),
#                  time_num=time, type='e')
# # node_01_e = Node("bus_01_e", devices=np.array([load_e_01, engine_e_pv01, engine_e_wt01, storage_e_01,]),
# #                  rLine=np.array([line_cchp_e_01]), sLine=np.array([line_eb_e_01, line_er_e_01, line_hp_e_01]),
# #                  time_num=time, type='e')
# # 气节点
# node_05_g = Node("bus_05_g", devices=np.array([load_g_05, gs_g_05]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_05]),
#                  time_num=time, type="g")
# # 热节点
# node_05_h = Node("bus_05_h", devices=np.array([load_h_05, storage_h_05]), rLine=np.array([line_eb_h_05, line_cchp_h_05,
#                                                                                           line_hp_h_05])
#                  , sLine=np.array([]), time_num=time, type="th")
#
# # 冷节点
# node_05_c = Node("bus_05_c", devices=np.array([load_c_05, storage_c_05]), rLine=np.array([line_er_c_05]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 地缘热泵节点
# node_05_hp = Node("bus_05_hp", devices=np.array([engine_h_hp05]), rLine=np.array([line_hp_e_05]),
#                   sLine=np.array([line_hp_h_05]), time_num=time, type="HP")
# # 冷热电联产节点
# node_05_cchp = Node("bus_05_cchp", devices=np.array([cchp_05]), rLine=np.array([line_cchp_g_05]),
#                     sLine=np.array([line_cchp_e_05, line_cchp_h_05]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_05_eb = Node("bus_05_eb", devices=np.array([eb_05]), rLine=np.array([line_eb_e_05]),
#                   sLine=np.array([line_eb_h_05]), time_num=time, type="EB")
# # 电制冷节点
# node_05_er = Node("bus_05_er", devices=np.array([er_05]), rLine=np.array([line_er_e_05]),
#                   sLine=np.array([line_er_c_05]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域01中"
# area05 = MG("area05", node=np.array([node_05_e, node_05_h, node_05_eb, node_05_g, node_05_cchp, node_05_c, node_05_er,
#                                      node_05_hp]),
#             id=1, type="area05", time_num=time)

"""
    区域06
"""
# 电节点
# node_06_e = Node("bus_06_e", devices=np.array([load_e_06, cpp_e_06, engine_e_pv06, storage_e_06]),
#                  rLine=np.array([line_cchp_e_06]), sLine=np.array([line_eb_e_06, line_er_e_06]),
#                  time_num=time, type='e')
# # node_01_e = Node("bus_01_e", devices=np.array([load_e_01, engine_e_pv01, engine_e_wt01, storage_e_01,]),
# #                  rLine=np.array([line_cchp_e_01]), sLine=np.array([line_eb_e_01, line_er_e_01, line_hp_e_01]),
# #                  time_num=time, type='e')
# # 气节点
# node_06_g = Node("bus_06_g", devices=np.array([load_g_06, gs_g_06]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_06]),
#                  time_num=time, type="g")
# # 热节点
# node_06_h = Node("bus_06_h", devices=np.array([load_h_06, storage_h_06]), rLine=np.array([line_eb_h_06, line_cchp_h_06])
#                  , sLine=np.array([]), time_num=time, type="th")
# # 冷节点
# node_06_c = Node("bus_06_c", devices=np.array([load_c_06, storage_c_06]), rLine=np.array([line_er_c_06]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 冷热电联产节点
# node_06_cchp = Node("bus_06_cchp", devices=np.array([cchp_06]), rLine=np.array([line_cchp_g_06]),
#                     sLine=np.array([line_cchp_e_06, line_cchp_h_06]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_06_eb = Node("bus_06_eb", devices=np.array([eb_06]), rLine=np.array([line_eb_e_06]),
#                   sLine=np.array([line_eb_h_06]), time_num=time, type="EB")
# # 电制冷节点
# node_06_er = Node("bus_06_er", devices=np.array([er_06]), rLine=np.array([line_er_e_06]),
#                   sLine=np.array([line_er_c_06]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域01中"
# area06 = MG("area06", node=np.array([node_06_e, node_06_h, node_06_eb, node_06_g, node_06_cchp, node_06_c, node_06_er]),
#             id=1, type="area06", time_num=time)
#
# """
#     区域07
# """
# # 电节点
# node_07_e = Node("bus_07_e", devices=np.array([load_e_07, cpp_e_07, engine_e_pv07, engine_e_wt07, storage_e_07]),
#                  rLine=np.array([line_cchp_e_07]), sLine=np.array([line_eb_e_07, line_er_e_07, line_hp_e_07]),
#                  time_num=time, type='e')
# # 气节点
# node_07_g = Node("bus_07_g", devices=np.array([load_g_07, gs_g_07]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_07]),
#                  time_num=time, type="g")
# # 热节点
# node_07_h = Node("bus_07_h", devices=np.array([load_h_07, storage_h_07]), rLine=np.array([line_eb_h_07, line_cchp_h_07,
#                                                                                           line_hp_h_07])
#                  , sLine=np.array([]), time_num=time, type="th")
# # 冷节点
# node_07_c = Node("bus_07_c", devices=np.array([load_c_07, storage_c_07]), rLine=np.array([line_er_c_07]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 地缘热泵节点
# node_07_hp = Node("bus_07_hp", devices=np.array([engine_h_hp07]), rLine=np.array([line_hp_e_07]),
#                   sLine=np.array([line_hp_h_07]), time_num=time, type="HP")
# # 冷热电联产节点
# node_07_cchp = Node("bus_07_cchp", devices=np.array([cchp_07]), rLine=np.array([line_cchp_g_07]),
#                     sLine=np.array([line_cchp_e_07, line_cchp_h_07]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_07_eb = Node("bus_07_eb", devices=np.array([eb_07]), rLine=np.array([line_eb_e_07]),
#                   sLine=np.array([line_eb_h_07]), time_num=time, type="EB")
# # 电制冷节点
# node_07_er = Node("bus_07_er", devices=np.array([er_07]), rLine=np.array([line_er_e_07]),
#                   sLine=np.array([line_er_c_07]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域01中"
# area07 = MG("area07", node=np.array([node_07_e, node_07_h, node_07_eb, node_07_g, node_07_cchp, node_07_c, node_07_er,
#                                      node_07_hp]),
#             id=1, type="area07", time_num=time)
#
# """
#     区域08
# """
# # 电节点
# node_08_e = Node("bus_08_e", devices=np.array([load_e_08, cpp_e_08, engine_e_pv08, storage_e_08]),
#                  rLine=np.array([line_cchp_e_08]), sLine=np.array([line_eb_e_08, line_er_e_08, line_hp_e_08]),
#                  time_num=time, type='e')
# # 气节点
# node_08_g = Node("bus_08_g", devices=np.array([load_g_08, gs_g_08]), rLine=np.array([]),
#                  sLine=np.array([line_cchp_g_08]),
#                  time_num=time, type="g")
# # 热节点
# node_08_h = Node("bus_08_h", devices=np.array([load_h_08, storage_h_08]), rLine=np.array([line_eb_h_08, line_cchp_h_08,
#                                                                                           line_hp_h_08])
#                  , sLine=np.array([]), time_num=time, type="th")
# # 冷节点
# node_08_c = Node("bus_08_c", devices=np.array([load_c_08, storage_c_08]), rLine=np.array([line_er_c_08]),
#                  sLine=np.array([]), time_num=time, type="c")
# # 地缘热泵节点
# node_08_hp = Node("bus_08_hp", devices=np.array([engine_h_hp08]), rLine=np.array([line_hp_e_08]),
#                   sLine=np.array([line_hp_h_08]), time_num=time, type="HP")
# # 冷热电联产节点
# node_08_cchp = Node("bus_08_cchp", devices=np.array([cchp_08]), rLine=np.array([line_cchp_g_08]),
#                     sLine=np.array([line_cchp_e_08, line_cchp_h_08]), time_num=time, type="CCHP")
# # 电热锅炉节点
# node_08_eb = Node("bus_08_eb", devices=np.array([eb_08]), rLine=np.array([line_eb_e_08]),
#                   sLine=np.array([line_eb_h_08]), time_num=time, type="EB")
# # 电制冷节点
# node_08_er = Node("bus_08_er", devices=np.array([er_08]), rLine=np.array([line_er_e_08]),
#                   sLine=np.array([line_er_c_08]), time_num=time, type="ER")
#
# "创建一个区域，将以上节点放在区域01中"
# area08 = MG("area08", node=np.array([node_08_e, node_08_h, node_08_eb, node_08_g, node_08_cchp, node_08_c, node_08_er,
#                                      node_08_hp]),
#             id=1, type="area08", time_num=time)

# 放在一个区域
# area = MG("area", node=np.array([node_01_e, node_01_h, node_01_eb, node_01_g, node_01_cchp, node_01_c, node_01_er,
#                                 node_01_hp, node_02_e, node_02_h, node_02_g, node_02_c, node_02_er,
#                                 node_02_hp, node_03_e, node_03_h, node_03_eb, node_03_g, node_03_cchp, node_03_c,
#                                  node_03_er, node_04_e, node_04_h, node_04_eb, node_04_g, node_04_cchp, node_04_c,
#                                  node_04_er, node_04_hp]),
#           id=1, type="area", time_num=time)


"创建UIES"
UIES = MMGs(np.array([area01]))

"求解所需参数"
C, integrality, num = MMGs_logic(UIES, path, flag=False)

PrintBounds(num)

# for i in range(len(num.params)):
#     print(num.params[i], "  :", np.round(C[i], 2))
# print(num.params)
#PrintBounds(num)

"计算结果"
result = EndCount(-C, integrality, num)

"将求解结果保存至节点"
x_callBack(result, UIES, path)

"画图"
draw(UIES, np.array([]))


