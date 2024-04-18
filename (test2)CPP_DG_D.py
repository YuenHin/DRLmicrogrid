import numpy as np

from Model.Node import Node
from Model.Line import Line
from Model.Demand import D
from Model.ConventionalPowerPlants import DG
from Model.ConventionalPowerPlants_area import CPP
from Model.Microgrid import MG
from Model.Multi_Microgrid import MMGs

from tools.MILP import PrintBounds, EndCount
from tools.Logic import MMGs_logic, x_callBack, draw

time = 24
path = "(test2)CPP_DG_D_4-14"

"创建一个用户负荷"
demand_e_01 = D("D_e_01", 'e', 4000, 2, ramping_rate=0.25, MG_id=1, time_num=time)

"创建一个发电厂"
CPP_e_01 = CPP("CPP_e_01", 1, 5000, -0.09, time_num=time)

"创建一个DG"
DG = DG("DG_01", 1, 3000, -0.05, time)

"创建一个line传输能量"
line = Line("line", 4000, -0.001, Single=True, MG_point=True, from_MG="CPP", to_MG="MG", time_num=time)

"创建一个节点，接受能量"
node01 = Node("N_e_01", np.array([demand_e_01, DG]), np.array([]), np.array([line]), time_num=time)

MG1 = MG("MG1", np.array([node01]), 1, "MG", time_num=time)

"创建一个节点，发送能量"
node02 = Node("N_CPP", np.array([CPP_e_01]), np.array([line]), np.array([]), time_num=time)

MG2 = MG("MG_CPP", np.array([node02]), 2, "CPP", time)

"创建多微网"
MMGs = MMGs(np.array([MG1, MG2]))

C, intergrality, num = MMGs_logic(MMGs, path)

res = EndCount(-C, intergrality, num)

x_callBack(res, MMGs, path)

draw(MMGs, np.array([]))

