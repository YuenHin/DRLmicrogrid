from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np
class Num:
    variableNum = 26
    parms = None
    def __init__(self, variableNum, params, path="save_"):
        self.path = "./Data/Result/num/" + path
        self.variableNum = variableNum
        self.params = params
        self.A = np.zeros(0)
        self.bl = np.zeros(0)
        self.bu = np.zeros(0)

    def Save_A_bl_bu(self):
        # 保存num.A, num.bl, num.bu
        print("保存A矩阵")
        np.save(self.path + "A", self.A)
        np.save(self.path + "bl", self.bl)
        np.save(self.path + "bu", self.bu)

    def Get_A_bl_bu(self):
        self.path = "./Data/Result/num/" + "Perfecr-MILP"
        self.A = np.load(self.path +"A.npy")
        self.bl = np.load(self.path +"bl.npy")
        self.bu = np.load(self.path +"bu.npy")

    def Getting_variableNum(self):
        return self.variableNum
    def Getting_params(self):
        return self.params
    def Setting_variableNum(self, variableNum):
        self.variableNum = variableNum
    def Setting_params(self, params):
        self.params = params
    def Clear_format(self):
        self.A = self.A.reshape((int(len(self.A) / len(self.params)), len(self.params)))

'''
将字符串转化为下标
'''
def StringToNum(text, Number):
    num = -1
    i = 0
    while i < Number.Getting_variableNum():
        if(Number.params[i] == text):
            num = i
            return num
        i = i + 1
    return num

'''
创建一个条件表达式，并且将参与这个表达式的变量和它们的系数一起部署好
'''
def funcA(B, num, Number):
    A = np.zeros(int(Number.variableNum))
    for i in range(len(B)):
        A[int(B[i][0] + num)] = int(B[i][1])
    return A

def funcAByParams(B , num, Number):
    A = np.zeros(int(Number.variableNum))

    for i in range(len(B)):
        temp = StringToNum(B[i][0], Number)
        # print("temp:", temp)
        if temp == -1 or int(temp + num) >= len(A):
            print("编辑条件出错啦！", B[i][0])
            break
        A[int(temp + num)] = B[i][1]
    return A

'''
初始化一个存放num个条件表达式的方法，用于那种有规律的多个条件表达式：快速使用
'''
def CreatDoubleArray(num, Number):
    A = np.array([[0. for i in range(int(Number.variableNum))] for j in range(int(num))])
    return A

'''
目标函数 是最小值哦
'''
def CreatObjFunction():
    print("快快创建目标函数哟：")
    print("比如：c = np.array([20, 50, 35, 31, 48, 25])")
    return 0
'''
类型函数 ：
    0 - 表示连续
    1 - 表示整数
'''
def CreatIntegrality():
    print("在MILP的世界里，这里可是需要Integrality的存在的！")
    print("比如：integrality = ([0, 0, 0, 1, 1, 1,])")
    return 0

'''
创建单个条件表达式
A是一个二维数组，其中每一个数组存放两个值，该条件表达式位置和系数
返回：条件函数
     下限
     上限
'''
def CreatConstraint(B, down , up, number):
    A = CreatDoubleArray(1, number)
    bl = np.zeros(1)
    bu = np.zeros(1)


    for i in range(len(B)):
        A[0][int(B[i][0])] = B[i][1]
    bl[0] = down
    bu[0] = up
    return A, bl, bu

'''
创建多个有规律的一组条件函数
num:这组条件函数里面有num个条件函数
B：二维数组，每一个数字里面存在两个数字信息：每个变量启示位置、和系数
down: 最小值
up:最大值
返回值：接好你的A,bl,bu

可以使用vstack进行替代
'''
def CreatConstraints(num, B, down, up, number):
    A = CreatDoubleArray(num, number)
    bl = np.zeros(num)
    bu = np.zeros(num)
    for i in range(num):
        # print("num:", i)
        A[i] = funcA(np.array(B) , i, number)
        bl[i] = down
        bu[i] = up
    return A, bl, bu

'''
需要有特殊处理，但是想使用循环创建一组条件函数
'''
def CreatConstraintsSpe():
    print("Example:A5x = CreatDoubleArray(6)\n"+
          "        bl5x = np.zeros(6)\n"+
          "        bu5x = np.zeros(6)\n"+
          "        key = 0\n" +
          "        for i in range(6):\n" +
          "            if i > 0:\n" +
          "                key = 1\n" +
          "                A5x[i] = funcA([\n" +
          "                [30 + i, 1],\n" +
          "                [29 + i, -key],\n" +
          "                [18 + i, +1/0.9],\n" +
          "                ])\n" +
          "                bl5x[i] = 0\n" +
          "                if i == 0:\n" +
          "                    bl5x[i] = 20\n" +
          "                    bu5x[i] = 20)\n")
    return 0

'''
使用字符串进行创建
'''
def CreatConstraintsByText(num, B, down, up, number):
    A = CreatDoubleArray(num, number)
    bl = np.zeros(num)
    bu = np.zeros(num)
    for i in range(num):
        # print(i, end=" ")
        A[i] = funcAByParams(B, i, number)
        bl[i] = down
        bu[i] = up
    # print()

    number.A = np.append(number.A, A)
    number.bl = np.append(number.bl, bl)
    number.bu = np.append(number.bu, bu)

    return A, bl, bu

'''
使用两种字符串进行创建
'''
def CreatConstraintsByTextAndText(num, B, down, up, number):
    A = CreatDoubleArray(num, number)
    bl = np.zeros(num)
    bu = np.zeros(num)
    for i in range(num):

        A[i] = funcAByParams(B, i, number)
        bl[i] = down
        bu[i] = up
    return A, bl, bu
'''
下面需要将A bl bu三个进行整合
'''
'''
这个是整合目标函数的，将之前创建的所有目标函数进行汇总
'''
def ComposeArray(*A, number):

    length = 0
    for i in range(len(A)):
        for j in range(len(A[i])):
            length += 1
    total = CreatDoubleArray(length, number)
    key = 0

    for i in range(len(A)):
        for j in range(len(A[i])):
         total[key] =  A[i][j]
         #print(A[i][j])
         key += 1
    #print(total)
    return total
'''
这个是整合目标函数的上下限的，bl和bu都可以使用这个函数
PS.记住每一个A、bl、bu都要在各自的数组中对其哦
'''
def ComposeB(*A):
    length = 0
    for i in range(len(A)):
        for j in range(len(A[i])):
            length += 1
    total = np.zeros(length)
    key = 0
    for i in range(len(A)):
        for j in range(len(A[i])):
            total[key] = A[i][j]
            #print(A[i][j])
            key += 1
    #print(total)
    return total

'''
最后一步传入参数，并进行计算得到结果
返回一个res的结果
'''
def EndCount(c,integrality,Number):
    A = Number.A
    A = A.reshape((int(len(A) / len(Number.params)), len(Number.params)))
    bl = Number.bl
    bu = Number.bu
    # print("Counting.......")
    # print("Counting....")
    # print("Counting.")
    # print("")
    b1 = np.zeros(Number.variableNum)
    b2 = np.zeros(Number.variableNum)
    for i in range(Number.variableNum):
        b1[i] = -np.inf
        b2[i] = np.inf
    res = milp(c = c,
               integrality = integrality,
               bounds=np.array([b1,b2]),
               constraints = LinearConstraint(A, bl, bu)
               )
    #print(res)
    return res



'''
小工具:将系数矩阵转化为公式
'''
def PrintBounds(Number):
    A = Number.A
    A = A.reshape((int(len(A) / len(Number.params)), len(Number.params)))
    bl = Number.bl
    bu = Number.bu
    print("\t\t", "Min", "\t", "Max")
    num = len(A)
    for i in range(num):
        print("第", i + 1, "个：", bl[i], "\t", bu[i], "\t", end=" ")
        for j in range(Number.Getting_variableNum()):
            if A[i][j] != 0:
                if A[i][j] > 0:
                    print("+", A[i][j], Number.params[j], " ", end="\t")
                else:
                    print( A[i][j], Number.params[j], " ", end="\t")
        print("")

