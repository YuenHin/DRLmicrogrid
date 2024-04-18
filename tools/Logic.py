import numpy as np
from tools.MILP import Num
import time

from tools.maybeExcel import writeDatatoExcel

def MMGs_logic(MMGs, file_name, flag = False):
    start_time = time.time()
    "C、params、intergrality"
    params = np.array([""])
    C = np.zeros(0)
    intergrality = np.zeros(0)

    for MG in MMGs.MG:
        for node in MG.node:
            params = np.append(params, node.params)
            C = np.append(C, node.c)
            intergrality = np.append(intergrality, node.intergrality)


    #MMGs.price()

    params = params[1:]

    writeDatatoExcel(".\Data\Result\\"+file_name+".xlsx", 1, 0, params)

    "Num"
    num = Num(len(params), params, file_name)
    updata_time = time.time()
    print("数据加载完成, 用时：", updata_time - start_time)

    "constraints"
    if flag == False:
        start_num = 0
        for MG in MMGs.MG:
            for node in MG.node:
                start_num = node.constraints(num, start_num)
            MG.count_constraints_num()
        MMGs.count_contrainst_num()
        MMGs.save_contrainst_num(num)
        num.Save_A_bl_bu()
        print("潮流约束构造完成, 用时：", time.time() - updata_time)
    else:
        MMGs.Load_contrainst_num(num)
        num.Get_A_bl_bu()

    "return"
    return C, intergrality, num

def x_callBack(res, MMGs, file_name, flag = True): #作用是？
    start_index = 0
    for MG in MMGs.MG:
        for node in MG.node:
            for device in node.devices:
                #X值
                end_index = start_index + device.length
                device.x = res.x[start_index:end_index]
                start_index = end_index



            if len(node.sLine) != 0:
                for sLine in node.sLine:
                    end_index = start_index + sLine.length
                    sLine.x = res.x[start_index:end_index]
                    start_index =end_index
            # if node.rLine != None:
            #     for rLine in node.rLine:
            #         end_index = start_index + rLine.length
            #         rLine.x = res.x[start_index:end_index]
            #         start_index =end_index
    if flag:
        writeDatatoExcel(".\Data\Result\\"+file_name+".xlsx", 0, 0, res.x)
    #print("计算结果回调")

def save_data(file_name, data, id):
    writeDatatoExcel(".\Data\Result\\" + file_name + ".xlsx", id, 0, data)

def x_callBack_time(res, MMGs, time): #作用是？
    start_index = 0
    for MG in MMGs.MG:
        for node in MG.node:
            for device in node.devices:
                end_index = start_index + device.length
                device.x[time - 1] = res.x[start_index + time - 1]
                start_index = end_index

            if len(node.sLine) != 0:
                for sLine in node.sLine:
                    end_index = start_index + sLine.length
                    sLine.x[time - 1] = res.x[start_index + time - 1]
                    start_index =end_index
            # if node.rLine != None:
            #     for rLine in node.rLine:
            #         end_index = start_index + rLine.length
            #         rLine.x = res.x[start_index:end_index]
            #         start_index =end_index
    #writeDatatoExcel(".\Data\Result\Result_11_17.xlsx", 0, 0, res.x)
    print("计算结果回调")

def draw(MMGs, notDraw = np.array([])):
    for MG in MMGs.MG:
        if MG.type == "MG":
            MG.draw()
        for node in MG.node:
            for device in node.devices:
                if not np.isin(device.className, notDraw):
                    device.draw()
                # if len(node.sLine) != 0:
                #     for line in node.sLine:
                #         line.draw()