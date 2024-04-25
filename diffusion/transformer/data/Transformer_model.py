import torch
from Generation.Transformer import Transformer
# import os
# os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

def initialize_weights(m):
    if hasattr(m, "weight") and m.weight.dim() > 1:
        torch.nn.init.kaiming_uniform_(m.weight.data)


enc_voc_size = 5893
dec_voc_size = 7853
src_pad_idx = 1
trg_pad_idx = 1
trg_sos_idx = 2
batch_size = 128
max_len = 1024
d_model = 512
n_layers = 3
n_heads = 2
ffn_hidden = 1024
drop_prob = 0.1

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#device = torch.device("cpu")
model = Transformer(
    src_pad_idx=src_pad_idx,
    trg_pad_idx=trg_pad_idx,
    d_model=d_model,
    enc_voc_size=enc_voc_size,
    dec_voc_size=dec_voc_size,
    max_len=max_len,
    ffn_hidden=ffn_hidden,
    n_heads=n_heads,
    n_layers=n_layers,
    drop_prob=drop_prob,
    device=device,
).to(device)


model.apply(initialize_weights)
src = torch.load('tensor_src.pt').to(device)
# print(src.shape)
# print(src.shape[0])
src = torch.cat((src, torch.ones(src.shape[0], 2, dtype=torch.int).to(device)), dim=-1)
trg = torch.load('tensor_trg.pt').to(device)

result = model.forward(src, trg)
print(result, result.shape)
