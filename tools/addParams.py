import numpy as np
def AddParams(params, num, name):
    for j in range(len(name)):
        for i in range(num):
            temp = np.array([name[j] + str(i + 1)])
            params = np.append(params, temp)
    return params