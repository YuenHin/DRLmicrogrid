# Token Embedding
import torch
from torch import nn
import torch.functional as F
from Attention import multi_head_attention

#作出连续化映射操作
class TokenEmbedding(nn.Embedding):
    def __init__(self, vocab_size, d_model):
        super(TokenEmbedding, self).__init__(vocab_size, d_model, padding_idx = 1)

#位置编码
class PositionalEmbedding(nn.Module):
    def __init__(self, d_model, maxlen, device):
        super(PositionalEmbedding, self).__init__()
        self.encoding = torch.zeros(maxlen, d_model, device)
        self.encoding.requires_grad(False)

        pos = torch.arange(0, maxlen, device)
        pos = pos.float().unsqueeze(1)
        _2i = torch.arange(0, d_model, 2, device = device)

        self.encoding[:, 0::2] = torch.sin(pos / (10000 ** (_2i / d_model)))
        self.encoding[:, 1::2] = torch.cos(pos / (10000 ** (_2i / d_model)))

    def forward(self, x):
        seq_len = x.shape[1]
        return self.encoding[:seq_len, :]

#归一化
class LayerNorm(nn.Module):
    def __init__(self, d_model, eps = 1e-10):
        super(LayerNorm, self).__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim = True)
        var = x.var(-1, unbiassed = False, keepdim = True)
        out = (x - mean) / torch.sqrt(var + self.eps)
        out = out * self.gamma + self.beta
        return out

#FFN(Postiton-Wise Fully Connection Feed-Forward Network) 前向传播块线性全连接
class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model, hidden, dropout=0.1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fc1 = nn.Linear(d_model, hidden)
        self.fc2 = nn.Linear(hidden, d_model)
        #正则化 在训练时随机讲某些张量的值设为0，从而减少模型对训练数据的依赖程序
        #变成0的数大约为p*100%  其他所有没有变0的参数  =  参数 / p
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)

class TransformerEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model, max_len, drop_prob, device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #连续化映射
        self.tok_emb = TokenEmbedding(vocab_size, d_model)
        #添加位置编码
        self.pos_emb = PositionalEmbedding(d_model, max_len, device)
        #归一化
        self.drop_out = nn.Dropout(p=drop_prob)


    def forward(self, x):
        tok_emb = self.tok_emb(x)
        pos_emb = self.pos_emb(x)
        return self.drop_out(tok_emb + pos_emb)

class EncoderLayer(nn.Module):
    def __init__(self, d_model, ffn_hidden, n_head, drop_prob)-> None:
        super(EncoderLayer, self).__init__()

        self.attention = multi_head_attention(d_model, n_head)
        self.norm1 = LayerNorm(d_model)
        self.drop1 = nn.Dropout(drop_prob)

        self.ffn = PositionwiseFeedForward(d_model, ffn_hidden, drop_prob)
        self.norm2 = LayerNorm(d_model)
        self.drop2 = nn.Dropout(drop_prob)

    def forward(self, x, mask):
        _x = x
        x = self.attention.forward(x, x, x, mask)

        x = self.drop1(x)
        x = self.norm1.forward(x + _x)

        _x = x
        x = self.ffn.forward(x)

        x = self.drop2(x)
        x = self.norm2.forward(x + _x)
        return x

X = torch.randn(2, 2, 8) # Batch, Time, Dimension

d_model = 8
n_head = 4
print(X)
print(X.shape)

encoder = EncoderLayer(d_model, 64, n_head, 0.1)

X = encoder.forward(X, False)

print(X)
print(X.shape)



