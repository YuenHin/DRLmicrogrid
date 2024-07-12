import torch
from torch import nn
import torch.functional as F
import math

# X = torch.randn(2, 2, 8) # Batch, Time, Dimension
#
#
# d_model = 8
# n_head = 8

class multi_head_attention(nn.Module):
    def __init__(self, d_model, n_head, device) -> None:
        super(multi_head_attention, self).__init__()

        self.device =device
        self.n_head = n_head  # 几个并行计算模型
        self.d_model = d_model  #一共由多少维数据
        self.n_d = self.d_model // self.n_head
        self.w_q = nn.Linear(d_model, d_model).cuda()
        self.w_k = nn.Linear(d_model, d_model).cuda()
        self.w_v = nn.Linear(d_model, d_model).cuda()
        self.w_combine = nn.Linear(d_model, d_model)

        self.softmax = nn.Softmax(dim = -1)

    def forward(self, q, k, v, mask = None):
        batch, time, dimension = q.shape

        q = self.w_q(q)
        k = self.w_k(k)
        v = self.w_v(v)

        q = q.view(batch, time, self.n_head, self.n_d).permute(0, 2, 1, 3)
        k = k.view(batch, time, self.n_head, self.n_d).permute(0, 2, 1, 3)
        v = v.view(batch, time, self.n_head, self.n_d).permute(0, 2, 1, 3)

        score = q @ k.transpose(2, 3) / math.sqrt(self.n_d)
        #torch.tril --- 生成一个下三角矩阵
        # 1 0 0 0
        # 1 1 0 0
        # 1 1 1 0
        # 1 1 1 1
        #decoder当中带有mask的attention
        if mask != None:
            #mask = torch.tril(torch.ones(time, time, dtype = bool))
            #masked_fill(A,B) 使用B去替换A
            #因此，就是将0的位置改为负无穷大
            #softmax操作时会将负无穷处直接设置为0，就不会去关注这一部分的数据信息-----面具激活
            score = score.masked_fill(mask == 0, float(-1e10))
        score = self.softmax(score)
        score = score @ v
        #这里的contiguous()函数是保证变量在物理内存上也是连续的
        score = score.permute(0, 2, 1, 3).contiguous().view(batch, time, dimension)

        output = self.w_combine(score)
        return output
