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