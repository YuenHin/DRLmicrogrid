import numpy as np

from Model.Node import Node
from Model.Line import  Line
from Model.Demand import D
from Model.RenewableProductionUnit import RT
from Model.Storage import S
from Model.ConventionalPowerPlants_area import CPP
from Model.ConventionalPowerPlants import DG
from Model.Microgrid import MG
from Model.Multi_Microgrid import MMGs

from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount

time = 24
path = "(test4)CPP_DG_D_RE_S_4-15"
demand_total = 5500

"创建一个用户负荷"
demand_e_01 = D("D_e_01",  "e", demand_total , MG_id=1, ramping_rate=0.25, time_num=time)

"创建一个发电厂"
CPP_e_01 = CPP("CPP_e_01", 1, 6000, -0.5, time_num=time)

"创建一个DG"
DG = DG("DG_01", 1, demand_total*0.4, -0.06, time_num=time)

"创建一个光伏发电厂"
PV = RT("PV_01", "PV", 2, -0.048, demand_total*0.28, time_num=time)

"创建一个风力发电厂"
WT = RT("WT_01", "WT", 1, -0.033, demand_total*0.32, time_num=time)

"创建一个储能"
SE = S("S_e_01", "e", 1, 10/1.1125, 3000, 80, 0.01/30/24, np.sqrt(0.95), np.sqrt(0.95), time)

"创建潮流"
line01 = Line("L_e_01", 50000, -0.0001, time_num=time)
line_RE_D = Line("L_e_01", 50000, -0.0001, Single=True, time_num=time)
line02 = Line("L_e_02", 50000, -0.0001, Single=True, MG_point=True, from_MG="CPP", to_MG="MG", time_num=time)
line_CPP_D = Line("L_e_02", 50000, -0.0001, Single=True, MG_point=True, from_MG="CPP", to_MG="MG", time_num=time)
line03 = Line("L_e_03", 50000, -0.0001, time_num=time)
line_RE_S = Line("L_e_03", 50000, -0.0001, time_num=time)
line04 = Line("L_e_04", 50000, -0.0001, time_num=time)
line_S_D = Line("L_e_04", 50000, -0.0001, time_num=time)

"创建节点，demand+DG"
node1 = Node("N_e_01", np.array([demand_e_01, DG]), np.array([]), np.array([line_S_D, line_CPP_D, line_RE_D]), time)

"创建节点，CPP"
node2 = Node("N_e_02", np.array([CPP_e_01]), np.array([line_CPP_D]), np.array([]), time)

"创建节点，PV+WT"
node3 = Node("N_e_03", np.array([PV, WT]), np.array([line_RE_S, line_RE_D]), np.array([]), time)

"创建节点，S"
node4 = Node("N_e_04", np.array([SE]), np.array([line_S_D]),np.array([line_RE_S]), time)

"创建微网，包含demand+DG+RE+SE所在节点"
MG1 = MG("Microgrid01", np.array([node1, node3, node4]), 1, "MG", time_num=time)

"CPP单独作为一个微网"
MG_CPP = MG("MG_CPP", np.array([node2]), 1, "CPP", time_num=time)

MMGs = MMGs(np.array([MG1, MG_CPP]))

# node_CPP = Node("N_e_02", np.array([CPP_e_01]), np.array([line02]), np.array([]), time)
# node_all = Node("N_all", np.array([demand_e_01, DG, PV, WT, SE]), np.array([]), np.array([line02]), time)
# MG = MG("MG_all", np.array([node_all]), 1, "MG", time)
# MMGs = MMGs(np.array([MG, MG1]))

C, intergrality, num = MMGs_logic(MMGs, path)

res = EndCount(-C, intergrality, num)
print(res.x)
x_callBack(res, MMGs, path)

draw(MMGs)


















