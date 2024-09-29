import numpy as np

# 假设这是你的长度为500的列表
original_list = np.linspace(-500, -100, 500)

# 将列表重塑为 (20, 25)，每25个元素分为一组
reshaped_list = original_list.reshape(20, 25)

# 对每组求均值
compressed_list = np.mean(reshaped_list, axis=1)

# 打印结果
print(compressed_list)
