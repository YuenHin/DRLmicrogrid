import torch.nn as nn
import torch
import torch.nn.functional as F

class WeightLoss(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, pred, targ, weighted = 1.0):
        """

        :param pred:  预测
        :param targ:  目标
        :param weighted:
        :return:
        """
        loss = self._loss(pred, targ)
        WeightedLoss = (loss * weighted).mean()
        return   WeightedLoss

class WeightLoss1(WeightLoss):
    def _loss(self, pred, targ):
        return torch.abs(pred - targ)

class WeightLoss2(WeightLoss):
    def _loss(self, pred, targ):
        return F.mse_loss(pred, targ, reduction = "none")

