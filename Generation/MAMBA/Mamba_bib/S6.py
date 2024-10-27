import torch

from Parameter import *


"""
该类S6代表 Mamba 架构中的复杂组件，负责通过一系列线性变换和离散化过程来处理输入序列。
它在捕获序列的时间动态方面发挥着关键作用，这是序列建模任务（例如语言建模）的一个关键方面。
该课程展示了张量运算和自定义离散化方法等先进技术，以处理序列数据的复杂要求。
"""
class S6(nn.Module):
    def __init__(self, seq_len, d_model, state_size, device):
        super(S6, self).__init__()

        self.fc1 = nn.Linear(d_model, d_model, device = device)
        self.fc2 = nn.Linear(d_model, state_size, device = device)
        self.fc3 = nn.Linear(d_model, state_size, device = device)

        self.seq_len = seq_len
        self.d_model = d_model
        self.state_size = state_size

        temp_A1 = torch.ones(d_model, state_size, device=device)
        temp_A2 = F.normalize(temp_A1, p = 2, dim = -1)  #需要确定作用 搞定 这里是进行L2范数处理
        self.A = nn.Parameter(temp_A2)
        nn.init.xavier_normal_(self.A)  #需要确定作用  采用特定方式来初始化神经网络参数

        self.B = torch.zeros(batch_size, self.seq_len, self.state_size, device = device)
        self.C = torch.zeros(batch_size, self.seq_len, self.state_size, device = device)

        self.delta = torch.zeros(batch_size, self.seq_len, self.d_model, device = device)
        self.dA = torch.zeros(batch_size, self.seq_len, self.d_model, self.state_size, device = device)
        self.dB = torch.zeros(batch_size, self.seq_len, self.d_model, self.state_size, device = device)

        # h should have dimensions [batch_size, sqe_len, d_model, state_size]
        self.h = torch.zeros(batch_size, self.seq_len, self.d_model, self.state_size, device = device)
        self.y = torch.zeros(batch_size, self.seq_len, self.d_model, device = device)

    def discretization(self):


        # discretization function is defined based on the MAMBA paper's description using ZOH on page 28
        # in Section C : Mechanics on Selective SSMs
        # See also "Zero-order hold discretization" maths proof inside https://studywolf.wordpress.com/tag/zero-order-hold/
        """
        Here is an explanation of the mathematical rationale for the formulation of Δt used in Mamba:
        The key idea is that Δt controls the discretization rate of the continuous SSM dynamics. By making Δt input-dependent, it introduces selectivity into the discrete transition matrices.
        Specifically, in Mamba they parameterize Δt as:
        Δt = τΔ(Parameter + sΔ(xt))
        Where:
        - Parameter is a learned scalar parameter that controls the baseline discretization rate
        - sΔ(xt) is a projection that makes Δt input-dependent by computing a value based on xt
        - τΔ(x) = softplus(x) transforms the Result to be positive through the softplus nonlinearity
        The rationale for this formulation is:
        - Parameter provides a reasonable default discretization rate
        - sΔ(xt) injects input-dependence through the projection
        - softplus ensures Δt is positive as required to be a valid timestep
        - The projection sΔ allows the model to learn to modulate Δt based on the input xt
        - This modulation creates selectivity in how rapidly or slowly the states update
        So in summary, the learned input-dependent projection allows Δt, and thus the discrete dynamics, to become selective. The softplus and scalar parameter provide useful inductive biases on top of this flexibility.
        The end Result is discrete transition matrices that are selective on the input, enabling powerful sequence modeling capabilities.
        Credit: Claude2 AI chatbot
        """

        # inverse() only supports square matrix
        # dB = torch.matmul(torch.inverse(A * delta), torch.matmul(dA - torch.eye(A.shape[0]), B))
        self.dB = torch.einsum("bld,bln->bldn", self.delta, self.B)

        # https://github.com/state-spaces/mamba/blob/0131c1e94a46fc9f70bcfc9d57962963bb2f0b9e/mamba_ssm/modules/mamba_simple.py#L240
        # dA = torch.matrix_exp(A * delta)  # matrix_exp() only supports square matrix
        self.dA = torch.exp(torch.einsum("bld,dn->bldn", self.delta, self.A))
        # print(f"self.dA.shape = {self.dA.shape}")
        # print(f"self.dA.requires_grad = {self.dA.requires_grad}")

        return self.dA, self.dB

    def forward(self, x):
        # Refer to Algorithm 2 in the Mamba paper
        self.B = self.fc2(x)
        self.C = self.fc3(x)
        self.delta = F.softplus(self.fc1(x))

        # Uses ZOH as in MAMBA, Hungry Hippo still uses bilinear transform for discretization
        self.discretization()

        # 不同的状态更新机制
        # this will trigger in-place runtime error if without using `h_new`
        if DIFFERENT_H_STATES_UPDATE_MECHANISM :

            global current_batch_size
            current_batch_size = x.shape[0]

            if self.h.shape[0] != current_batch_size:
                # print("Adjusting h_new for the different batch size of input data `x`")
                different_batch_size = True

                # Resize self.h to match the current batch size
                h_new = torch.einsum('bldn, bldn -> bldn', self.dA, self.h[:current_batch_size, ...]) + rearrange(x, "b l d -> b l d 1") * self.dB
            else:
                different_batch_size = False
                h_new = torch.einsum('bldn, bldn -> bldn', self.dA, self.h) + rearrange(x, "b l d -> b l d 1") * self.dB

            # y needs to have a shape of [batch_size, seq_len. d_model]
            self.y = torch.einsum('bln, bldn -> bld', self.C, h_new)

            # Update self.h with the detached state of h_new   （用 h_new 的分离状态去更新 self.h, h_new去更新h)
            # Only to this if retaining gradients for self.h is not necessary for backprop (只有在反向循环不需要保留 self.h 的梯度时才这样做)
            # Otherwise, store h_new in a temporary list and update self.h after thr loop (否则，将 h_new 保存在临时列表中，并在 thr 循环后更新 self.h)
            global temp_buffer
            if not self.h.requires_grad:
                temp_buffer = h_new.detach().clone()
            else:
                temp_buffer = h_new.clone()

            return self.y
        else:
            # this will not trigger in-place runtime error
            # h should have dimensions [batch_size, seq_len, d_model, state_size]
            self.h = torch.zeros(x.size(0), self.seq_len, self.d_model, self.state_size, device = device)
            y = torch.zeros_like(x)

            self.h = torch.einsum('bldn, bldn -> bldn', self.dA, self.h) + rearrange(x, "b l d -> b l d 1") * self.dB

            # y needs to have a shape of [batch_size, seq_len, d_model]
            self.y = torch.einsum('bln, bldn -> bld', self.C, self.h)

            return self.y

