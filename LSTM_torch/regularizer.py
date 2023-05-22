# -*- coding: utf-8 -*- 
# @Time : 2023/2/13 20:35 
# @Author : Yinan 
# @File : regularizer.py
import math

import torch.nn as nn
import torch


class Regularizer(nn.Module):
    def __init__(self):
        super(Regularizer, self).__init__()
        self.reg_loss = None
        self.loss = None

    def forward(self, loss, reg_loss):
        pass


class PIDRegularizer(Regularizer):
    def __init__(self, k, dynamic):
        super(PIDRegularizer, self).__init__()
        self.prev_reg_loss = [0, 0]
        self.acc_reg_loss = [0, 0]
        self.Kp, self.Ki, self.Kd = k
        self.gamma = [0, 0]
        self.dynamic = dynamic

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        for i in range(2):
            if self.dynamic:
                self.gamma[i] = self.Kp[i].item() * self.reg_loss[i].item() + \
                        self.Ki[i].item() * self.acc_reg_loss[i] + \
                        self.Kd[i].item() * (self.reg_loss[i].item() - self.prev_reg_loss[i])
            else:
                self.gamma[i] = self.Kp[i] * self.reg_loss[i].item() + \
                        self.Ki[i] * self.acc_reg_loss[i] + \
                        self.Kd[i] * (self.reg_loss[i].item() - self.prev_reg_loss[i])
            self.acc_reg_loss[i] += self.reg_loss[i].item()
            self.prev_reg_loss[i] = self.reg_loss[i].item()
        return self.gamma[0], self.gamma[1]


class Incremental_PIDRegularizer(PIDRegularizer):
    def __init__(self, k):
        super(Incremental_PIDRegularizer, self).__init__(k)
        self.pprev_reg_loss = [0, 0]

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        delta_gamma = [0, 0]
        for i in range(2):
            delta_gamma[i] = self.Kp[i] * (self.reg_loss[i].item() - self.prev_reg_loss[i]) +\
                            self.Ki[i] * self.reg_loss[i].item() - \
                            self.Kd[i] * (self.reg_loss[i].item() - 2 * self.prev_reg_loss[i] + self.pprev_reg_loss[i])
            self.pprev_reg_loss[i] = self.prev_reg_loss[i]
            self.prev_reg_loss[i] = self.reg_loss[i].item()

        self.gamma[0] += delta_gamma[0]
        self.gamma[1] += delta_gamma[1]
        return self.gamma[0], self.gamma[1]


class TwopartRegularizer(Regularizer):
    def __init__(self):
        super(TwopartRegularizer, self).__init__()

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        temp = []
        for i in range(2):
            if self.reg_loss[i] < 0:
                gamma = 0.01
            else:
                gamma = 1
            temp.append(gamma)
        gamma1, gamma2 = temp
        return gamma1, gamma2


class ToZeroRegularizer(Regularizer):
    def __init__(self):
        super(ToZeroRegularizer, self).__init__()

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        temp = []
        for i in range(2):
            if self.reg_loss[i] < 0:
                gamma = -0.05
            else:
                gamma = 1
            temp.append(gamma)
        gamma1, gamma2 = temp
        return gamma1, gamma2


class ExpRegularizer(Regularizer):
    def __init__(self):
        super(ExpRegularizer, self).__init__()

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        temp = []
        for i in range(2):
            if self.reg_loss[i] < 0:
                gamma = -math.exp(max(self.reg_loss[i].item(), -10))
            else:
                gamma = math.exp(min(self.reg_loss[i].item(), 10))
            temp.append(gamma)
        gamma1, gamma2 = temp
        return gamma1, gamma2


class BlaRegularizer(Regularizer):
    def __init__(self):
        super(BlaRegularizer, self).__init__()

    def forward(self, loss, reg_loss):
        self.reg_loss = reg_loss
        self.loss = loss
        temp = []
        for i in range(2):
            if self.reg_loss[i].detach() > 0:
                gamma = self.loss.item() * self.reg_loss[i].item() / (self.reg_loss[0].item() + self.reg_loss[1].item())
            else:
                gamma = 0
            temp.append(gamma)
        gamma1, gamma2 = temp
        return gamma1, gamma2

