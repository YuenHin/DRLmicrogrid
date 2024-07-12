import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.nn import functional as F
from einops import rearrange
from tqdm import tqdm

import math
import os
import urllib.request
from zipfile import ZipFile

from transformers import AutoTokenizer

torch.autograd.set_detect_anomaly(True)

#Configuration flags and hyperparameters
USE_MAMBA = 1
DIFFERENT_H_STATES_UPDATE_MECHANISM = 0

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# User-defined hyperparameters
d_model = 8
state_size = 128  # Example state size
seq_len = 100 # Example sequence length
batch_size = 256 # Example batch size
last_batch_size = 81 # only for the very Last batch of the dataset
current_batch_size = batch_size
different_batch_size = False
h_new = None
temp_buffer = None

class RMSNorm(nn.Module):
    def __init__(self, d_model: int, eps: float = 1e-5, device: str ='cuda'):
        super().__init__()

        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d_model, device = device))

    def forward(self, x):
        output = x * torch.rsqrt(x.pow(2).mean(-1, keepdim = True) + self.eps) * self.weight
        return output