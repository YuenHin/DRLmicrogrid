from DeepAR import *



# 训练函数
def train_deepar(model, dataloader, num_epochs=1000, lr=0.00001):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = nn.GaussianNLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_values = []

    for epoch in range(num_epochs):
        model.train()
        for context, target in dataloader:
            context = context.unsqueeze(-1).to(device)
            target = target.to(device)

            mu, sigma = model(context)
            mu = mu.view(-1, model.prediction_length)
            sigma = sigma.view(-1, model.prediction_length)
            target = target.view(-1, model.prediction_length)

            loss = criterion(mu, target, sigma)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        loss_values.append(loss.item())
        if (epoch + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    plt.plot(loss_values)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.show()


# 生成示例数据
data, target = generate_synthetic_data()

# 数据集和数据加载器
context_length = 50
prediction_length = 10
batch_size = 32

train_dataset = TimeSeriesDataset(data, target, context_length, prediction_length)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

# 定义和训练模型
input_size = 1
hidden_size = 50
num_layers = 2
model = DeepAR(input_size, hidden_size, num_layers, prediction_length)

train_deepar(model, train_loader, num_epochs=1000)
