from tools.RE.Logic_RE import get_total_day_re_narure_data

from tools.RE.Logic_RE import main

data = get_total_day_re_narure_data(7)
features = ["global radiation", "direct radiation", "diffusion radiation", "6ft-wind-speed", "19ft-wind-speed", "22ft-wind-speed", "33ft-wind-speed", "6ft-wind-direction", "19ft-wind-direction", "22ft-wind-direction", "33ft-wind-direction", "Station Pressure", "Temperature", "Air Density"]
# 选择特定特征的索引作为输入
feature_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
feature_indices = [6]
# 例如，选择第 4 列特征作为目标
target_feature_index = 6
# 参考数据
context_length = 24
#预测数据
prediction_length = 6
#批量大小
batch_size = 32
#神经网络的隐藏层数量
hidden_size = 256
#隐藏层的层数
num_layers = 4
#训练天数：
train_day = 6
#测试天数：
test_day = 1
#使用的训练模型
# model_type = 'GRUDeterministic'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer' 或'DeepAR_GRU' 或"GRUDeterministic"
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, train_day, test_day, only_test=False)

flag = False

model_type = 'DeepAR_LSTM'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer' 或'DeepAR_GRU' 或"GRUDeterministic"
main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, train_day, test_day, only_test=flag)

model_type = 'DeepAR_Transformer'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer' 或'DeepAR_GRU' 或"GRUDeterministic"
main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, train_day, test_day, only_test=flag)

model_type = 'DeepAR_GRU'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer' 或'DeepAR_GRU' 或"GRUDeterministic" 或“DeepAR”
main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, train_day, test_day, only_test=flag)

model_type = 'DeepAR'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer' 或'DeepAR_GRU' 或"GRUDeterministic" 或“DeepAR”
main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size, hidden_size, num_layers, model_type, train_day, test_day, only_test=flag)

# model_type = 'DeepAR_LSTM'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
#      hidden_size, num_layers, model_type, only_test=True)
# model_type = 'DeepAR_Transformer'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
#      hidden_size, num_layers, model_type, only_test=True)
#
# target_feature_index = 13  # 例如，选择第 4 列特征作为目标
# model_type = 'DeepAR_GRU'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
#      hidden_size, num_layers, model_type, only_test=True)
# model_type = 'DeepAR_LSTM'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
#      hidden_size, num_layers, model_type, only_test=True)
# model_type = 'DeepAR_Transformer'  # 或 'DeepAR_LSTM' 或 'DeepAR_Transformer'
# main(data, features, feature_indices, target_feature_index, context_length, prediction_length, batch_size,
#      hidden_size, num_layers, model_type, only_test=True)







