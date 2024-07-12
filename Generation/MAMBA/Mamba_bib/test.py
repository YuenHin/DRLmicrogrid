# from Parameter import *
# from Mamba import Mamba
#
# x = torch.rand(batch_size, seq_len, d_model, device = device)
# # Create the Mamba model
# mamba = Mamba(seq_len, d_model, state_size, device)
#
# #rmsnorm
# norm = RMSNorm(d_model)
# x = norm(x)
#
# #Forward pass
# test_output = mamba(x)
# # Should be [batch_size, seq_len, d_model]
# print(f"test_output.shape = {test_output.shape}")

import torch

A = torch.tensor([[1, 2], [3, 4]])
B = torch.tensor([[5, 6]])
print(B.shape)

result = torch.einsum('ij,ik->ijk', A, B)
print(result)  # 输出: tensor([[[ 5,  6], [10, 12]], [[15, 18], [20, 24]]])

# torch.Size([3, 2, 1])

# result = torch.einsum('jki->jk', C)
# print(result)  # 输出: tensor([3, 7])
# 'ijk->i'    10, 26
# 'ijk->j'    14, 22
# 'ijk->k'    16, 20

# 'ijk->ij'    [[3, 7], [11, 15]]   1   3     1+3+5, 2+4+6   9, 12
# "ijk->ik"    [[4, 6], [12, 14]]   2   2     1+2 3+4 5+6   3, 7, 11
# 'ijk->jk'    [[6, 8], [10, 12]]   3   1     1, 2, 3, 4, 5, 6
