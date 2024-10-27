import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

"""
不同不确定集下，各个设备的运行功率及灵活性供给能力
"""

# # 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path)
#
# # 数据准备
# x = np.arange(1, 25)  # 24个柱体的x坐标
# y1 = np.random.randint(10, 30, size=24)  # 第一根折线的y值
# y2 = np.random.randint(5, 25, size=24)   # 第二根折线的y值
#
# # 柱体数据
# bar1_values = np.random.randint(1, 10, size=24)  # 每个柱体的第一个内容
# bar2_values = np.random.randint(1, 10, size=24)  # 每个柱体的第二个内容
#
# # 绘制柱体（叠加）
# x_bar = np.arange(1, 25)  # 柱体x坐标
# plt.bar(x_bar, bar1_values, label='内容1', color='#007acc')  # 柔和蓝色
# plt.bar(x_bar, bar2_values, bottom=bar1_values, label='内容2', color='#ff9933')  # 柔和橙色，叠加在第一组上
#
# # 绘制折线
# plt.plot(x, y1, marker='o', color='#003366', label='折线1')  # 深蓝色
# plt.plot(x, y2, marker='o', color='#990000', label='折线2')  # 深红色
#
# # 设置图形属性
# plt.xlabel('柱体编号', fontproperties=font_prop)
# plt.ylabel('值', fontproperties=font_prop)
# plt.title('两根折线与24个叠加柱体的图形', fontproperties=font_prop)
# plt.xticks(x)  # 设置x轴刻度为1到24
# plt.legend(prop=font_prop)
# plt.grid(axis='y')
#
# # 显示图形
# plt.tight_layout()
# plt.show()

"""
不同的不确定集
"""

"""
区间概率不确定集
"""
# # 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path)
#
# # 数据准备
# x = np.arange(1, 25)  # 24个柱体的x坐标
# # path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx"
# path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\pv.xlsx"
# dataset = pd.read_excel(path)
# min = dataset['min'].values
# max = dataset['max'].values
# mu = dataset['mu'].values
# real_value = dataset['real_value'].values
# min = min[0:24]
# max = max[0:24]
# mu = mu[0:24]
# real_value = real_value[0:24]
#
# predicted_min = min  # 随机生成预测最小值
# predicted_max = max  # 随机生成预测最大值
# predicted_values = mu  # 随机生成预测值
# actual_values = real_value  # 随机生成真实值
#
# # 创建填充区域
# plt.fill_between(x, predicted_min, predicted_max, color='lightblue', alpha=0.5, label='概率区间')
#
# # 绘制预测值最大值和最小值的折线
# plt.plot(x, predicted_max, color='#003366', label='区间上界')  # 深蓝色
# plt.plot(x, predicted_min, color='#990000', label='区间下届')  # 深红色
#
# # 绘制预测值和真实值的点
# plt.scatter(x, predicted_values, color='#007acc', label='预测值', marker='o')  # 柔和蓝色
# plt.scatter(x, actual_values, color='#ff9933', label='真实值', marker='x')  # 柔和橙色
#
# # 设置图形属性
# plt.xlabel('时间尺度', fontproperties=font_prop)
# plt.ylabel('出力功率', fontproperties=font_prop)
# plt.title('区间概率不确定集', fontproperties=font_prop)
# plt.xticks(x)  # 设置x轴刻度为1到24
# plt.legend(prop=font_prop)
# plt.grid(axis='y')
#
# # 显示图形
# plt.tight_layout()
# plt.show()

"""
盒式不确定集
"""
# 设置字体
font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
font_prop = font_manager.FontProperties(fname=font_path)

# 数据准备
x = np.arange(1, 25)  # 24个柱体的x坐标
# path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\load_e.xlsx"
path = r"C:\software\Github\DRLmicrogrid\Data\uncertainty\pv.xlsx"
dataset = pd.read_excel(path)
min = dataset['min'].values
max = dataset['max'].values
mu = dataset['mu'].values
real_value = dataset['real_value'].values
min = min[0:24]
max = max[0:24]
mu = mu[0:24]
real_value = real_value[0:24]
rate = mu * 0.25
min = mu - rate
max = mu + rate

predicted_min = min  # 随机生成预测最小值
predicted_max = max  # 随机生成预测最大值
predicted_values = mu  # 随机生成预测值
actual_values = real_value  # 随机生成真实值

# 创建填充区域
plt.fill_between(x, predicted_min, predicted_max, color='lightblue', alpha=0.5, label='概率区间')

# 绘制预测值最大值和最小值的折线
plt.plot(x, predicted_max, color='#003366', label='区间上界')  # 深蓝色
plt.plot(x, predicted_min, color='#990000', label='区间下届')  # 深红色

# 绘制预测值和真实值的点
plt.scatter(x, predicted_values, color='#007acc', label='预测值', marker='o')  # 柔和蓝色
plt.scatter(x, actual_values, color='#ff9933', label='真实值', marker='x')  # 柔和橙色

# 设置图形属性
plt.xlabel('时间尺度', fontproperties=font_prop)
plt.ylabel('出力功率', fontproperties=font_prop)
plt.title('区间概率不确定集', fontproperties=font_prop)
plt.xticks(x)  # 设置x轴刻度为1到24
plt.legend(prop=font_prop)
plt.grid(axis='y')

# 显示图形
plt.tight_layout()
plt.show()

"""
功率平衡图
"""
# # 设置字体
# font_path = r"C:\Windows\Fonts\simsun.ttc"  # 替换为您的字体路径
# font_prop = font_manager.FontProperties(fname=font_path)
#
# # 数据准备
# num_bars = 24  # 柱体数量
# num_layers = 5  # 每个柱体的叠层数量
#
# # 随机生成数据，确保每个柱体的叠层总和不为负
# positive_layers = np.random.rand(num_bars, num_layers) * 10  # 正半轴
# negative_layers = np.random.rand(num_bars, num_layers) * 10  # 负半轴
#
# # 莫兰迪色系配色（淡雅、柔和的颜色）
# colors = ['#B2A6B8', '#E4B7A0', '#A3D6D4', '#F3D9B3', '#EAB8C6']
#
# # 创建叠加柱体的正半轴
# x = np.arange(1, num_bars + 1)  # x坐标（1到24）
# bottom = np.zeros(num_bars)  # 叠加的底部起始位置
#
# for i in range(num_layers):
#     plt.bar(x, positive_layers[:, i], bottom=bottom, color=colors[i % len(colors)], label=f'正层{i+1}' if i == 0 else "")
#     bottom += positive_layers[:, i]  # 更新底部位置
#
# # 创建叠加柱体的负半轴
# bottom_neg = np.zeros(num_bars)  # 负半轴叠加的底部起始位置
#
# for i in range(num_layers):
#     plt.bar(x, -negative_layers[:, i], bottom=-bottom_neg, color=colors[i % len(colors)], alpha=0.6, label=f'负层{i+1}' if i == 0 else "")
#     bottom_neg += negative_layers[:, i]  # 更新负半轴的底部位置
#
# # 设置图形属性
# plt.xlabel('样本编号', fontproperties=font_prop)
# plt.ylabel('值', fontproperties=font_prop)
# plt.title('叠加柱体图（正负半轴）', fontproperties=font_prop)
# plt.xticks(x)  # 设置x轴刻度为1到24
# plt.axhline(0, color='black', linewidth=0.8)  # 添加水平基线
# plt.legend(prop=font_prop)
# plt.grid(axis='y')
#
# # 显示图形
# plt.tight_layout()
# plt.show()



