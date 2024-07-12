from DeepAR import *

def load_data(train_data, train_target, test_data=None, test_target=None, context_length=50, prediction_length=10,
              batch_size=32):
    train_dataset = TimeSeriesDataset(train_data, train_target, context_length, prediction_length)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    if test_data is not None and test_target is not None:
        test_dataset = TimeSeriesDataset(test_data, test_target, context_length, prediction_length)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    else:
        test_loader = None

    return train_loader, test_loader


# 假设有自己的训练和测试数据
train_data = np.random.rand(1000)
train_target = np.roll(train_data, -1)
test_data = np.random.rand(300)
test_target = np.roll(test_data, -1)

# 加载数据
train_loader, test_loader = load_data(train_data, train_target, test_data, test_target, context_length=50,
                                      prediction_length=10, batch_size=32)

# 训练模型
train_deepar(model, train_loader, num_epochs=1000)

# 测试模型
if test_loader:
    test_deepar(model, test_loader)
