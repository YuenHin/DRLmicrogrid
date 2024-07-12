import torch
import torchaudio
import torchvision

a = torch.ones(16).reshape(4, 4) + 1
print(a)

mask = torch.tril(a.type(torch.BoolTensor))

print(mask)

a = a.masked_fill(mask == True, float(-1e10) )

print(a)

b = torch.nn.Softmax(a)

print(b)

print(torch.__version__)
print(torchvision.__version__)
print(torchaudio.__version__)
print(torch.version.cuda)