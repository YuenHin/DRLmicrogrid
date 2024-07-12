from Generation.diffusion.Diffusion import Diffusion
import torch

#风力预测   24 1 30
#出力功率  24 1 30 （风速、风向、发电功率）
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
x = torch.randn(30, 24).to(device)# x_0


state = torch.randn(30, 72).to(device) # x_T

model = Diffusion(loss_type="l2", obs_dim=72, act_dim=24, hidden_dim=256, T=1000, device=device)

loss = 1.0

step = 1
while loss > 0.01 :
    step += 1
    action = model.forward(state)
    loss = model.loss(x, state)

    model.updata_W(loss)
    print('\r', {'loss': '%.3f' % loss, 'step':'%d' % step, 'device':'%s' % device }, end='', flush=True)

print(f"action:{action}; loss:{loss}")