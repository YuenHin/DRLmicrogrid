import torch.nn as nn
import torch
import torch.nn.functional as F

from Generation.diffusion.Losses import WeightLoss1, WeightLoss2

from Generation.diffusion.MLP import MLP


def extract(a, t, x_shape):
    b, *_ = t.shape
    out = a.gather(-1, t)
    return out.reshape(b, *((1,) * (len(x_shape) - 1)))

#Diffusion(tsinghua=True)
class Diffusion(nn.Module):
    def __init__(self, loss_type, beta_schedule = "linear", clip_denoised = True, predict_epsilon = True, **kwargs):
        super().__init__()
        self.state_dim = kwargs["obs_dim"]
        self.action_dim =kwargs["act_dim"]
        self.hidden_dim = kwargs["hidden_dim"]
        self.T = kwargs["T"]
        self.clip_denoised = clip_denoised
        self.predict_epsilon = predict_epsilon
        self.device = torch.device(kwargs["device"])
        self.model = MLP(self.state_dim, self.action_dim, self.hidden_dim, self.device)

        self.optimizer = torch.optim.SGD(self.model.time_mlp.parameters(), lr=0.2)
        self.optimizer1 = torch.optim.SGD(self.model.mid_layer.parameters(), lr=0.2)
        self.optimizer2 = torch.optim.SGD(self.model.final_layer.parameters(), lr=0.2)

        if beta_schedule == "linear":
            betas = torch.linspace(0.0001, 0.02, self.T, dtype = torch.float32).to(self.device)

        alphas = 1.0 - betas
        # [1, 2, 3] -> [1, 2, 6]
        alphas_cumprod = torch.cumprod(alphas, axis = 0).to(self.device)
        alphas_cumprod_prev = torch.cat([torch.ones(1).to(self.device), alphas_cumprod[:-1]]).to(self.device)

        #构建buffer
        self.register_buffer("betas", betas)
        self.register_buffer("alphas", alphas)
        self.register_buffer("alphas_cumprod", alphas_cumprod)
        self.register_buffer("alphas_cumprod_prev", alphas_cumprod_prev)

        #前向过程
        self.register_buffer("sqrt_alphas_cumprod", torch.sqrt(alphas_cumprod))
        self.register_buffer("sqrt_one_minus_alphas_cumprod", torch.sqrt(1.0 - alphas_cumprod))

        #反向过程
        #逆向方差
        posterior_variance = (
            betas * (1.0 - alphas_cumprod_prev) / (1.0 - alphas_cumprod)
        ).to(self.device)
        self.register_buffer("posterior_variance", posterior_variance)
        self.register_buffer("posterior_log_variance_clipped", torch.log(posterior_variance.clamp(min = 1e-20)))

        #逆向均值
        #用于将xt反向推出x0的两个参数
        self.register_buffer("sqrt_recip_alphas_cumprod", torch.sqrt(1.0 / alphas_cumprod))
        self.register_buffer("sqrt_recipm_alphas_cumprod", torch.sqrt(1.0 / alphas_cumprod - 1))
        #均值
        self.register_buffer("posterior_mean_coef1", betas * torch.sqrt(alphas_cumprod_prev) / (1.0 - alphas_cumprod))
        self.register_buffer("posterior_mean_coef2", (1.0 - alphas_cumprod_prev) * torch.sqrt(alphas) / (1.0 - alphas_cumprod))
        if loss_type == 'l1':
            self.loss_fn = WeightLoss1().to(self.device)
        elif loss_type == 'l2':
            self.loss_fn = WeightLoss2().to(self.device)


    def predict_start_from_noise(self, x, t, pred_noise):
        """
        从xt去反向计算x0
        :param x:
        :param t:
        :param pred_noise:
        :return:
        """
        return (extract(self.sqrt_recip_alphas_cumprod, t, x.shape) * x
                - extract(self.sqrt_recipm_alphas_cumprod, t, x.shape) * pred_noise)

    def q_posterior(self, x_start, x, t):
        """
        后验概率
        :param x_start:
        :param x:
        :param t:
        :return:
        """
        posterior_mean = (
            extract(self.posterior_mean_coef1, t, x.shape) * x_start
            + extract(self.posterior_mean_coef2, t, x.shape) * x
        )

        posterior_variance = extract(self.posterior_variance, t, x.shape)
        posterior_log_variance = extract(self.posterior_log_variance_clipped, t, x.shape)

        return posterior_mean, posterior_variance, posterior_log_variance

    def p_mean_variance(self, x, t, state):
        #预测噪声 ---- 神经网络
        pred_noise = self.model.forward(x, t, state).to(self.device)
        #计算x0
        x_recon = self.predict_start_from_noise(x, t, pred_noise)
        x_recon.clamp_(-1, 1)
        #由x0、xt得到x（t-1）
        model_mean, posterior_variance, posterior_log_variance = self.q_posterior(x_recon, x, t)
        return model_mean, posterior_log_variance



    def p_sample(self, x, t, state):
        """
        反向采样全流程
        :param x:
        :param t:
        :param state:
        :return:
        """
        b, *_, device = *x.shape, x.device
        model_mean, model_log_variance = self.p_mean_variance(x, t, state)
        noise = torch.randn_like(x)

        nonzero_mask = (1 - (t == 0).float()).reshape((b, *((1,)*(len(x.shape) - 1))))
        return model_mean + nonzero_mask * (0.5 * model_log_variance).exp() * noise

    def p_sample_loop(self, state, shape, *args, **kwargs):
        device = self.device
        batch_size = state.shape[0]
        x = torch.randn(shape, device = device, requires_grad = True)

        for i in reversed(range(0, self.T)):
            t = torch.full((batch_size, ), i, device =device, dtype = torch.long )
            x = self.p_sample(x, t, state)
        return x

    #采样
    def sample(self, state, *args, **kwargs):
        batch_size = state.shape[0]
        #初始化噪声的形状
        shape = [batch_size, self.action_dim]
        action = self.p_sample_loop(state, shape, *args, **kwargs)
        return action.clamp_(-1, 1)

    #--------------------------------------------------training---------------------------------------------#

    def q_sample(self, x_start, t, noise):
        sample = (
            extract(self.sqrt_alphas_cumprod, t, x_start.shape) * x_start
            + extract(self.sqrt_one_minus_alphas_cumprod, t, x_start.shape) * noise
        )
        # X_t 扩散过程得到的
        return sample

    def p_losses(self, x_start, state, t, weights = 1.0):
        noise = torch.randn_like(x_start)
        #生成的噪声标签
        x_t = self.q_sample(x_start, t, noise)
        x_recon = self.model.forward(x_t, t, state)

        loss = self.loss_fn.forward(x_recon, noise, weights)
        return loss


    def loss(self, x, state, weights = 1.0):
        """

        :param x: 数据集中的一个样本 x0
        :param state:
        :param weights:
        :return:
        """
        batch_size = len(x)
        t = torch.randint(0, self.T, (batch_size,), device = self.device).long()
        return self.p_losses(x, state, t, weights)

    def updata_W(self, loss):
        self.optimizer.zero_grad()  # 梯度清0
        self.optimizer1.zero_grad()
        self.optimizer2.zero_grad()
        loss.backward()  # 误差反向传播
        self.optimizer.step()  # 神经网络参数更新
        self.optimizer1.step()  # 神经网络参数更新
        self.optimizer2.step()  # 神经网络参数更新

    #采用 *args：列表  **kwargs：字典
    def forward(self, state, *args, **kwargs):
        return self.sample(state, *args, **kwargs)

