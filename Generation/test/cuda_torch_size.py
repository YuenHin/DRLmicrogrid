import torch
# print(torch.cuda.get_device_name(0))
# print(torch.cuda.get_arch_list())
print(torch.__version__)
print("是否可用：", torch.cuda.is_available())  # 查看GPU是否可用
print("GPU数量：", torch.cuda.device_count())  # 查看GPU数量
print("torch方法查看CUDA版本：", torch.version.cuda)  # torch方法查看CUDA版本
print("GPU索引号：", torch.cuda.current_device())  # 查看GPU索引号
print("GPU名称：", torch.cuda.get_device_name(0))  # 根据索引号得到GPU名称

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


a = torch.ones((3, 1))
a = a.to(device)
b = torch.ones((3, 1)).to(device)
print(a + b)



