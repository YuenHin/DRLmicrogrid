import torch

a = torch.ones(16).reshape(4, 4) + 1
print(a)

mask = torch.tril(a.type(torch.BoolTensor))

print(mask)

a = a.masked_fill(mask == True, float(-1e10) )

print(a)

b = torch.nn.Softmax(a, dim= -1)

print(b)