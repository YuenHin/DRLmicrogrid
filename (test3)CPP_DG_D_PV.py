import numpy as np

from Model.Node import Node
from Model.Line import Line
from Model.Demand import D
from Model.ConventionalPowerPlants import DG
from Model.ConventionalPowerPlants_area import CPP
from Model.Microgrid import MG
from Model.Multi_Microgrid import MMGs
from Model.RenewableProductionUnit import RT

from tools.MILP import PrintBounds, EndCount
from tools.Logic import MMGs_logic, x_callBack, draw

time = 24
path = "(test3)CPP_DG_D_PV_4-14"

"创建一个用户负荷"
demand_e_01 = D("D_e_01", 'e', 3000, 4, MG_id=3, time_num=time)

"创建一个发电厂"
CPP_e_01 = CPP("CPP_e_01", 1, 5000, -0.09, time_num=time)

"创建一个DG"
DG = DG("DG_01", 1, 3000 * 0.4, -0.06, time_num=time)

"创建一个光伏发电厂"
PV = RT("PV_01", "PV", 2, -0.048, 3000 * 0.28, time_num=time)

"创建一个风力发电厂"
WT = RT("WT_01", "WT", 1, -0.033, 3000 * 0.32, time)

"创建潮流"
line01 = Line("L_e_01", 50000, -0.0001, time_num=time)
line02 = Line("L_e_02", 5000, -0.0001, Single=True, MG_point=True, from_MG="CPP", to_MG="MG", time_num=time)

"创建一个节点，包含负荷和DG"
node1 = Node("N_e_01",np.array([demand_e_01, DG]), np.array([line01]), np.array([line02]), time)

"创建一个节点，包含CPP"
node2 = Node("N_e_02", np.array([CPP_e_01]), np.array([line02]), np.array([]),time_num=time)

"创建一个节点，包含PV，WT"
node3 = Node("N_e_03", np.array([PV, WT]), np.array([]), np.array([line01]), time)

MG1 = MG("MG1", np.array([node1, node3]), 1, "MG", time_num=time)

MG2 = MG("MG_CPP", np.array([node2]), 1, "CPP", time_num=time)

MMGs = MMGs(np.array([MG1, MG2]))

C, intergrality, num = MMGs_logic(MMGs, path)

for i in range(len(num.params)):
    print(num.params[i], "  :", np.round(C[i], 5))
print(num.params)
PrintBounds(num)

res = EndCount(-C, intergrality, num)

x_callBack(res, MMGs, path)

draw(MMGs, np.array([]))



