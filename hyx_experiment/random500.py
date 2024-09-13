import numpy as np

def sample_and_check_range(mean, std, num_samples):
    samples = np.random.normal(mean, std, num_samples)
    min_value = np.min(samples)
    max_value = np.max(samples)
    return min_value, max_value, (min_value >= -1 and max_value <= 1)

# 设置随机种子以确保结果可重复
np.random.seed(0)

# 尝试不同的均值和标准差
mean = 0
std = 0.1  # 初始尝试值

while True:
    min_value, max_value, in_range = sample_and_check_range(mean, std, 500)
    print(f"均值: {mean}, 标准差: {std}, 最小值: {min_value}, 最大值: {max_value}, 在范围内: {in_range}")
    if in_range:
        break
    std *= 0.9  # 逐步减小标准差

# 打印最终的采样结果
samples = np.random.normal(mean, std, 5)
print(f"均值: {mean}, 标准差: {std}") #mean=0, std=0.1
print("最终采样结果:", samples)
# print("最终采样结果的最小值:", np.min(samples))
# print("最终采样结果的最大值:", np.max(samples))