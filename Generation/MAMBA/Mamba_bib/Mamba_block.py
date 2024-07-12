from Parameter import *
from S6 import S6
"""
MambaBlock 类是一个自定义神经网络模块，设计为 Mamba 模型的关键构建块。
它封装了几个层和操作来处理输入数据。 
MambaBlock 类表示一个复杂的神经网络块，包括线性投影、卷积、激活函数、自定义 S6 模块和残差连接。
该块是 Mamba 模型的基本组件，负责通过一系列转换来处理输入序列，以捕获数据中的相关模式和特征。
这些不同层和操作的组合使 MambaBlock 能够有效处理复杂的序列建模任务。
"""
class MambaBlock(nn.Module):
    def __init__(self, seq_len, d_model, state_size, device):
        super(MambaBlock, self).__init__()

        self.inp_proj = nn.Linear(d_model, 2 * d_model, device = device)
        self.out_proj = nn.Linear(2 * d_model, d_model, device = device)

        # For residual skip connection  用于残余跳跃链接额
        self.D = nn.Linear(d_model, 2 * d_model, device = device)

        # Set _no_weight_decay attribute on bias  设置不需要bias的偏置项
        self.out_proj.bias._no_weight_decay = True

        # Initialize bias to a small constant value
        nn.init.constant_(self.out_proj.bias, 1.0)

        self.S6 = S6(seq_len, 2 * d_model, state_size, device)

        # Add  1D convolution with kernel size 3
        self.conv = nn.Conv1d(seq_len, seq_len, kernel_size=3, padding=1, device=device)

        # Add linear layer for canv output
        self.conv_linear = nn.Linear(2 * d_model, 2 * d_model, device = device)

        # rmsnorm
        self.norm = RMSNorm(d_model, device = device)

    def forward(self, x):
        """
        x_proj.shape = torch.Size([batch_size, seq_len, 2*d_model])
        x_conv.shape = torch.Size([batch_size, seq_len, 2*d_model])
        x_conv_act.shape = torch.Size([batch_size, seq_len, 2*d_model])
        """

        # Refer to Figure 3 in the MAMBA paper

        x = self.norm(x)

        x_proj = self.inp_proj(x)
        #print(f"x_proj.shape = {x_proj.shape}")

        # Add 1D convolution with kernel size 3
        x_conv = self.conv(x_proj)
        #print(f"x_conv.shape = {x_conv.shape}")

        x_conv_act = F.silu(x_conv)
        #print(f"x_conv_act.shape = {x_conv_act.shape}")

        # Add linear layer for conv output
        x_conv_out = self.conv_linear(x_conv_act)
        #print(f"x_conv_out.shape = {x_conv_out.shape}")

        x_ssm = self.S6(x_conv_out)
        #Relu激活函数
        x_act = F.silu(x_ssm) # Swish activation can be implemented as x * sigmoid(x)
        #print(f"x_act.shape = {x_act.shape}")

        # residual skip connection with nonlinearity introduced by multiplication
        x_residual = F.silu(self.D(x))
        #print(f"x_residual.shape = {x_residual.shape}")
        x_combined = x_act * x_residual
        #print(f"x_combined.shape = {x_combined.shape}")

        x_out = self.out_proj(x_combined)
        #print(f"x_out.shape = {x_out.shape}")

        return x_out



