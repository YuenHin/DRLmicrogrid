import matplotlib.pyplot as plt
import tools.rl_utils
import pandas as pd
import numpy as np


def load_return_from_excel(file_name=''):
    """从 Excel 文件加载数据"""
    # 读取 Excel 文件
    df = pd.read_excel('.\save_return\data_500' + file_name + '.xlsx', header=None)
    # df = pd.read_excel('.\save_return\data_500.xlsx')
    # 遍历每一行，将数据加入 ReplayBuffer
    # return_list = df.values
    # return_list = return_list.flatten()
    return_list = df.iloc[:, 0].tolist()
    return return_list
#
#
# return_list = load_return_from_excel('test')
#
# env_name = "test500"
#
# episodes_list = list(range(len(return_list)))
# plt.plot(episodes_list, return_list)
# plt.xlabel('Episodes')
# plt.ylabel('Returns')
# plt.title('SAC on {}'.format(env_name))
# # plt.show()
#
# mv_return = tools.rl_utils.moving_average(return_list, 9)
# plt.plot(episodes_list, mv_return)
# plt.xlabel('Episodes')
# plt.ylabel('Returns')
# plt.title('SAC on {}'.format(env_name))
# plt.show()


# 参数
num_lists = 5  # 列表的数量（即行数）
list_length = 500  # 每个列表的长度（即列数）
base_size = 2  # 基础网格尺寸
spacing = 0.1  # 行与行之间的间距
"""
# 生成数值从-500到-100递增的列表
# values = np.linspace(-500, -100, list_length)  # 生成一个从-500到-100的数组
values1 = load_return_from_excel(file_name='')
values1 = tools.rl_utils.moving_average(values1, 49)
normalized_values1 = (values1 - np.min(values1)) / (np.max(values1) - np.min(values1))
values2 = load_return_from_excel(file_name='_9.5')
values2 = tools.rl_utils.moving_average(values2, 49)
normalized_values2 = (values2 - np.min(values2)) / (np.max(values2) - np.min(values2))
values3 = load_return_from_excel(file_name='_10.5')
values3 = tools.rl_utils.moving_average(values3, 49)
normalized_values3 = (values3 - np.min(values3)) / (np.max(values3) - np.min(values3))
values4 = load_return_from_excel(file_name='_ran5')
values4 = tools.rl_utils.moving_average(values4, 49)
normalized_values4 = (values4 - np.min(values4)) / (np.max(values4) - np.min(values4))
values5 = load_return_from_excel(file_name='_ran500')
values5 = tools.rl_utils.moving_average(values5, 49)
normalized_values5 = (values5 - np.min(values5)) / (np.max(values5) - np.min(values5))
normalized_values = np.stack([normalized_values1, normalized_values2, normalized_values3, normalized_values4, normalized_values5])
# values = np.tile(values, (num_lists, 1))  # 将此数组复制num_lists次，每个列表相同
"""
num_lists = 10
normalized_values = np.zeros((num_lists, 10))
aaa = np.zeros((num_lists, 500))

for i in range(num_lists):
    file_name = '_SAC_ori' + str(round(10.0 + i*0.1, 1))
    returns = load_return_from_excel(file_name)
    returns = tools.rl_utils.moving_average(returns, 9)
    aaa[i] = returns

returns_max = np.max(aaa)+50
returns_min = np.min(aaa)

for i in range(10):
    # file_name = '_SAC' + str(round(10.0 + i*5, 1))
    # file_name = '_SAC' + str(round(5.0+i, 1))
    # returns = load_return_from_excel(file_name)
    # returns = tools.rl_utils.moving_average(returns, 49)
    # artificial_max = np.max(returns) + 100  # 人工设置最大值
    # artificial_min = np.min(returns) - 100  # 人工设置最小值
    normalized_r = (aaa[i] - returns_min) / (returns_max - returns_min)
    # normalized_r = 0.1 + (i+1)*0.002 + normalized_r * (0.9 - (i+1)*0.001 - ( 0.1 + (i+1)*0.002) )
    normalized_r = 0.1 + normalized_r * (0.9 - 0.1)

    # 将列表重塑为 (20, 25)，每25个元素分为一组
    # reshaped_list = normalized_r.reshape(20, 25)
    reshaped_list = normalized_r.reshape(10, 50)
    # 对每组求均值
    compressed_list = np.mean(reshaped_list, axis=1)

    normalized_values[i] = compressed_list

# for i in range(10):
#     file_name = '_SAC10.' + str(i)
#     returns = load_return_from_excel(file_name)
#     returns = tools.rl_utils.moving_average(returns, 79)
#     artificial_max = np.max(returns) + 100  # 人工设置最大值
#     artificial_min = np.min(returns) - 100  # 人工设置最小值
#     normalized_r = (returns - artificial_min) / (artificial_max - artificial_min)
#     normalized_r = 0.1 + normalized_r * (0.9 - 0.1)
#
#     # 将列表重塑为 (20, 25)，每25个元素分为一组
#     reshaped_list = normalized_r.reshape(20, 25)
#     # 对每组求均值
#     compressed_list = np.mean(reshaped_list, axis=1)
#
#     normalized_values[10+i] = compressed_list

list_length = len(normalized_values[0])
# 动态调整网格的宽度和高度，使得图像比例更合理
# grid_width = base_size * (40 / list_length)  # 列数越多，网格宽度适当减小
grid_width = base_size * 1.5
# grid_height = base_size * (20 / num_lists)  # 行数越多，网格高度适当减小
grid_height = base_size

# 归一化每个列表的数值到0到1之间
# normalized_values = (values - np.min(values)) / (np.max(values) - np.min(values))

# 绘制网格
fig, ax = plt.subplots()
ax.set_aspect('equal')

# 设置图像的总大小，动态调整网格大小
# fig.set_size_inches(list_length * grid_width * 0.02, num_lists * (grid_height + spacing) * 0.5)

# 绘制每行网格（每个列表对应一行）
for i in range(num_lists):
    for j in range(list_length):
        # 根据归一化值设置颜色，越大颜色越浅（蓝色到白色）
        color_value = normalized_values[i, j]
        # color = [color_value, color_value, 1]  # 蓝色到白色的渐变
        color = [1.0, 0.5 + color_value * 0.5, color_value]
        # 在图上绘制矩形，去掉边框，使用自定义的颜色
        rect = plt.Rectangle((j * grid_width, i * (grid_height + spacing)), grid_width, grid_height, facecolor=color,
                             edgecolor='none')
        ax.add_patch(rect)

    # 在每一行最左侧显示该行的标号（或其他自定义标签）
    ax.text(-3, i * (grid_height + spacing) + grid_height / 2, f'g={round(10.0 + i*0.1, 1)}', va='center', ha='center', fontsize=8)

# 在最底部横坐标每隔50个网格显示一次数值
for j in range(0, list_length, 5):
    ax.text(j * grid_width + grid_width / 2, num_lists * (grid_height + spacing) + 0.5, str(j*50), va='center',
            ha='center', fontsize=8)

# 调整显示范围，使网格的大小保持固定
plt.xlim(-3, list_length * grid_width)
plt.ylim(-1, num_lists * (grid_height + spacing) + 1)  # 向上扩展一点显示横坐标标签
plt.gca().invert_yaxis()  # 反转y轴，使得顶部在上方
plt.axis('off')  # 关闭坐标轴
plt.show()










