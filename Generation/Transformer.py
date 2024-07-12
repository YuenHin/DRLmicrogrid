from torch import nn
import torch
from Encoder_Layer import TransformerEmbedding, EncoderLayer
from Decoder_Layer import DecoderLayer

class Encoder(nn.Module):
    def __init__(self, env_voc_size, max_len, d_model, ffn_hidden, n_head, n_layer, drop_prob, device):
        super(Encoder, self).__init__()

        self.embedding = TransformerEmbedding(env_voc_size, d_model, max_len, drop_prob, device)

        self.layers = nn.ModuleList(
            [EncoderLayer(d_model, ffn_hidden, n_head, drop_prob, device)for _ in range(n_layer)]
        )

    def forward(self, x, s_mask):
        x = self.embedding.forward(x)
        for layer in self.layers:
            print(x)
            x = layer.forward(x, s_mask)
        return x


class Decoder(nn.Module):
    def __init__(self, dec_voc_size, max_len, d_model, ffn_hidden, n_head, n_layer, drop_prob, device):
        super(Decoder, self).__init__()

        self.embedding = TransformerEmbedding(dec_voc_size, d_model, max_len, drop_prob, device)

        self.layers = nn.ModuleList(
            [DecoderLayer(d_model, ffn_hidden, n_head, drop_prob, device) for _ in range(n_layer)]
        )

        self.fc = nn.Linear(d_model, dec_voc_size)

    def forward(self, dec, enc, t_mask, s_mask):
        dec = self.embedding.forward(dec)
        for layer in self.layers:
            dec = layer(dec, enc, t_mask, s_mask)
        dec = self.fc(dec)
        return dec

class Transformer(nn.Module):
    def __init__(self, src_pad_idx, trg_pad_idx, enc_voc_size, dec_voc_size, max_len, d_model, n_heads, ffn_hidden, n_layers, drop_prob, device):
        """

        :param src_pad_idx: 输入的padding表记
        :param trg_pad_idx: 目目标的padding标记
        :param enc_voc_size: 编码遮罩后的大小
        :param dec_voc_size: 解码输出的大小
        :param max_len: 最大接收长度
        :param d_model: 输入的大小
        :param n_heads: 分为多少个头
        :param ffn_hidden: 隐藏层的层数
        :param n_layers: 每一个编码器、解码器有多少层
        :param drop_prob: 神经网络的学习逆调用率
        :param device: 设备
        """
        super(Transformer, self).__init__()
        self.encoder = Encoder(enc_voc_size, max_len, d_model, ffn_hidden, n_heads, n_layers, drop_prob, device)
        self.decoder = Decoder(dec_voc_size, max_len, d_model, ffn_hidden, n_heads, n_layers, drop_prob, device)

        self.src_pad_idx = src_pad_idx
        self.trg_pad_idx = trg_pad_idx

        self.device = device

    def make_casual_mask(self, q, k):
        len_q, len_k = q.size(1), k.size(1)
        mask = torch.tril(torch.ones((len_q, len_k)).type(torch.BoolTensor)).to(self.device)
        return mask

    def make_padding_mask(self, q, k, pad_idx_q, pad_idx_k):
        len_q, len_k = q.size(1), k.size(1)

        # (Batch, Time, len_q, len_k)
        q = q.ne(pad_idx_q).unsqueeze(1).unsqueeze(3)
        q = q.repeat(1, 1, 1, len_k)
        k = k.ne(pad_idx_k).unsqueeze(1).unsqueeze(2)
        k = k.repeat(1, 1, len_q, 1)

        #只要是0就需要mask   1 1 ->1
        mask = q & k
        return mask

    def forward(self, src, trg):
        """

        :param src: source
        :param trg:  target
        :return:
        """
        src_mask = self.make_padding_mask(src, src, self.src_pad_idx, self.src_pad_idx)
        trg_mask = self.make_padding_mask(trg, trg, self.trg_pad_idx, self.trg_pad_idx) * self.make_casual_mask(trg, trg)
        src_trg_mask = self.make_padding_mask(trg, src, self.trg_pad_idx, self.src_pad_idx)

        enc = self.encoder.forward(src, src_mask)
        #print(enc)
        print("编码成功，现在开始解码")
        output = self.decoder.forward(trg, enc, trg_mask, src_trg_mask)
        return output





            

