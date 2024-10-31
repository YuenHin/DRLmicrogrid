import pandas as pd
import matplotlib.pyplot as plt
from alg.alTools.rl_starting import moving_average  # 确保 moving_average 函数已定义

# 读取Excel文件（指定路径）
file_path = 'D:\HeYuanxing\BaiduSyncdisk\DRLmicrogrid\Data\RL_RO\Result\DDPG_actor_RO_3500v4.0.xlsx'
data = pd.read_excel(file_path, header=None, usecols=[1, 2, 3, 5])  # 读取B、C、D、F列数据

# file_path = 'D:\HeYuanxing\BaiduSyncdisk\DRLmicrogrid\Data\RL_RO\Result\DDPG_actor_RO_3000v4.0.xlsx'
# data2 = pd.read_excel(file_path, header=None, usecols=[1, 2, 3, 5])  # 读取B、C、D、F列数据

# data = pd.concat([data, data2], ignore_index=True)

# file_path = 'D:\HeYuanxing\BaiduSyncdisk\DRLmicrogrid\Data\RL_RO\Result\DDPG_actor_RO_3500v4.0.xlsx'
# data3 = pd.read_excel(file_path, header=None, usecols=[1, 2, 3, 5])  # 读取B、C、D、F列数据
# data = pd.concat([data, data3], ignore_index=True)

# 筛选出C、D、F列均为0的行
filtered_data = data[(data[2] == 0) & (data[3] == 0) & (data[5] == 0)]

# 生成横坐标，数据长度
x = range(len(filtered_data))

# 以B列数据为纵坐标（减去固定值）
fixed_value = 0  # 自定义减去的固定值
y_values = filtered_data[1] - fixed_value
mv_y = moving_average(y_values, 19)  # 计算移动平均值

# 打印B列数据的最小值
min_value = filtered_data[1].min()
print("筛选后B列数据的最小值:", min_value)

# 绘制折线图
plt.plot(x, y_values, label='Filtered Data (C, D, F = 0)')
plt.plot(x, mv_y, label='Moving Average', linestyle='--')  # 添加移动平均值的曲线
plt.xlabel('Data Length')
plt.ylabel('Data Value (B - fixed_value)')
plt.title('Filtered Data with C, D, F = 0 and Moving Average')
plt.legend()
plt.show()
