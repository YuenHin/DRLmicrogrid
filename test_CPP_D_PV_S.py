import numpy as np
from Model.Node import Node
from Model.ConventionalPowerPlants_area_RL import CPP
from Model.Demand import D
from tools.Logic import MMGs_logic, x_callBack, draw
from tools.MILP import PrintBounds, EndCount
from Model.Microgrid import MG
from Model.Multi_Microgrid import MMGs
from Model.Line import Line
from Model.RenewableProductionUnit_RL import RT
from Model.Storage_RL import S

time = 24
path = "test_CPP_D_RE"
demand_total = 4000

"创建一个用户负荷"
demand_e_01 = D("D_e_01", "e", demand_total, 1, MG_id=1, ramping_rate=0.25, time_num=time)

"创建一个发电厂"
#CPP_e_01 = CPP("CPP_e_01", 1, 4500, production_price=-0.05, time_num=time)
CPP_e_01 = CPP("CPP_e_01", 1, 100000, time_num=time)

"创建一个光伏发电厂"
PV = RT("PV_01", "PV", 2, -0.048, demand_total*0.5, time_num=time)

"创建一个储能"
SE = S("S_e_01", 'e', 1, 10/1.1125, 3000, 80, 0.01/30/24, np.sqrt(0.95), np.sqrt(0.95), time)

"创建一根线连接发电厂和用户负荷"
line = Line("line_01", 50000, line_price=-0.001, Single=False, from_MG="CPP", to_MG="MG", time_num=time)

"创建一根线连接光伏和用户负荷"
line_RE_D = Line("L_PV_D_01", 50000, -0.0001, Single=True, time_num=time)

"创建一根线连接光伏和储能"
line_RE_S = Line("L_PV_S_01", 50000, -0.0001, Single=True, time_num=time)

"创建一根线连接储能和用户负荷"
line_S_D = Line("L_S_D_01", 50000, -0.0001, Single=False, time_num=time)

"创建一个节点，将发电厂放在该节点（可扩展），填参时注意该节点是发送端还是接收端"
node01 = Node("node_CPP", devices=np.array([CPP_e_01]), sLine=np.array([line]), rLine=np.array([]), time_num=time, type='e')

"创建一个节点，将用户负荷放在该节点（可扩展），填参时注意该节点是发送端还是接收端"
node02 = Node("node_Demand_e", devices=np.array([demand_e_01]), rLine=np.array([line, line_RE_D, line_S_D]), sLine=np.array([]), time_num=time, type='e')

"创建一个节点，将光伏发电厂放在该节点（可扩展），填参时注意该节点是发送端还是接收端"
node03 = Node("node_PV", devices=np.array([PV]), sLine=np.array([line_RE_D, line_RE_S]), rLine=np.array([]), time_num=time, type='e')

"创建一个节点，将储能放在该节点（可扩展），填参时注意该节点是发送端还是接收端"
node04 = Node("node_S", devices=np.array([SE]), sLine=np.array([line_S_D]), rLine=np.array([line_RE_S]), time_num=time)

"创建一个微网，将node01和node03节点放在该微网（可扩展）"
MG01 = MG("MG_CPP", node=np.array([node01]), id=1, type="MG01", time_num=time)

"创建一个微网，将node02节点放在该微网（可扩展）"
MG02 = MG("MG_D_e", node=np.array([node02, node03, node04]), id=1, type="MG02", time_num=time)

"创建一个多微网"
#MMGs = MMGs(np.array([MG01,MG02]))l
CPP_D_PV_S_MMGs = MMGs(np.array([MG01,MG02]))

# C, intergrality, num = MMGs_logic(MMGs, path)
#
# for i in range(len(num.params)):
#     print(num.params[i], "  :", np.round(C[i], 2))
# print(num.params)
# PrintBounds(num)
#
# res = EndCount(-C, intergrality, num)
#
# x_callBack(res, MMGs, path)
#
# draw(MMGs, np.array([]))
