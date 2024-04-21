from Attention import multi_head_attention
from torch import nn
from Encoder_Layer import LayerNorm, PositionwiseFeedForward

class DecodeLayer(nn.Module):
    def __init__(self, d_model, ffn_hidden, n_head, drop_prob):
        super(DecodeLayer, self).__init__()
        #self-attention(自注意力)
        self.atttention = multi_head_attention(d_model, n_head)
        #归一化
        self.norm1 = LayerNorm(d_model)
        #仅启动部分神经网络--Dropout：增加能够收敛的概率
        self.dropout1 = nn.Dropout(drop_prob)

        #encoder-decoder-attention(取decoder的Q在encoder里面找K和V)
        self.cross_attention = multi_head_attention(d_model, n_head)
        self.norm2 = LayerNorm(d_model)
        self.dropout2 = nn.Dropout(drop_prob)

        self.ffn = PositionwiseFeedForward(d_model, ffn_hidden, drop_prob)
        self.norm3 = LayerNorm(d_model)
        self.dropout3 = nn.Dropout(drop_prob)

    def forward(self, dec, enc, t_mask, s_mask):
        """
        :param dec: 解码器输入的信息：提示词、步骤等
        :param enc: 编码器输出到解码器的信息
        :param t_mask: 用于遮盖未来真实信息的掩码（面具），相当于将答案先遮住再试图还原--因果关系的下三角掩码 ---- 因果掩码，我们不希望看到未来的信息
        :param s_mask: 用于补齐输入数据长度，使得处理数据处于同一个长度的掩码（面具）---s_mask是表示未知掩码 ---- 因为为了保持数据一致性会做一些padding的操作，s_mask是表示不用去考虑这些扩充的信息
        :return:
        """
        _x = dec
        x = self.atttention(dec, dec, dec, t_mask)
        x = self.dropout1(x)
        x = self.norm1(x + _x)

        if enc is not None:
            _x = x
            x = self.cross_attention(x, enc, enc, s_mask)
            x = self.dropout2(x)
            x = self.norm2(x + _x)

        _x = x
        x = self.ffn(x)
        x = self.dropout3(x)
        x = self.norm3(x + _x)








