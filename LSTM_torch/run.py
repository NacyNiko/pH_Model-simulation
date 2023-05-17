# -*- coding: utf-8 -*- 
# @Time : 2023/2/7 15:00 
# @Author : Yinan 
# @File : run.py

import argparse
import time

import torch
import lstm_train
import validation


parser = argparse.ArgumentParser(description='Input state stable LSTM')
parser.add_argument('--device', default='cuda:0', choices=['cpu', 'cuda:0', 'cuda:1', 'cuda:2', 'cuda:3'])
parser.add_argument('--dataset', default='robot_forward', choices=['pHdata', 'robot_forward', 'coupled electric drives'], help='LSTM dataset')
parser.add_argument('--hidden_size', default=150, help='hidden size of LSTM', type=int)

parser.add_argument('--input_size', default=6, help='input size of LSTM', type=int)
parser.add_argument('--output_size', default=6, help='output size of output layer', type=int)
parser.add_argument('--layers', default=2, help='number of layers of LSTM', type=int)
parser.add_argument('--batch_size', default=128, help='train batch size', type=int)
parser.add_argument('--epochs', default=100, help='maximum train epochs', type=int)
parser.add_argument('--tolerance', default=-1e-3, help='minimum tolerance of loss', type=float)
parser.add_argument('--tol_stop', default=-0.1, help='minimum tolerance between 2 epochs', type=float)
parser.add_argument('--len_sequence', default=40, help='length of input sequence to LSTM', type=int)

parser.add_argument(
    '--curriculum_learning', default='exp', choices=[None, '2part', '2zero', 'balance', 'exp', 'PID', 'IncrePID'], help='apply curriculum_learning or not')
parser.add_argument('--dynamic_K', default=False, type=bool)
parser.add_argument('--PID_coefficient', default=([5, 10], [0.01, 0.2], [0., 0.]), type=tuple)
parser.add_argument('--reg_methode', default='vanilla', choices=['relu', 'log_barrier_BLS', 'vanilla'], help='regularization methode')
parser.add_argument('--gamma', default=torch.tensor([1., 1.]), help='value of gamma', type=torch.Tensor)
parser.add_argument('--threshold', default=torch.tensor([0.05, 0.1]), help='value of threshold', type=torch.Tensor)


if __name__ == '__main__':
    # grid_Search = False
    # if grid_Search:
    #     # threshold_values = [x for x in range(0, 10)]
    #     # gamma_values = [x for x in range(0, 10)]
    #     # for threshold in threshold_values:
    #     #     for gamma in gamma_values:
    #     #         print('threshold:{}, gamma:{}'.format(threshold, gamma))
    #     #
    #     #         args = parser.parse_args()
    #     #         args.threshold = torch.tensor([threshold, threshold])
    #     #         args.gamma = torch.tensor([gamma, gamma])
    #
    #     hidden_values = [100, 150, 200, 250, 300]
    #     len_sequence_values = [40]
    #     for hs in hidden_values:
    #         for ls in len_sequence_values:
    #             print('hidden size:{}, seq length:{}'.format(hs, ls))
    #
    #             args = parser.parse_args()
    #             args.hidden_size = hs
    #             args.len_sequence = ls
    #
    #             lstm_train.main(args)
    #             validation.main(args, piecewise=True)
    # else:
    #     start = time.time()
    #     lstm_train.main(parser.parse_args())
    #     end = time.time()
    #     print(f'total times:{-start+end}')
    #     validation.main(parser.parse_args(), piecewise=True)
    for cl, rm in [('PID', 'vanilla')]:
        # (None, 'relu'), ('2part', 'vanilla'), ('2zero', 'vanilla'), ('balance', 'relu'), ('exp', 'vanilla')
        for dataset in ['pHdata', 'robot_forward']:
            if dataset == 'pHdata':
                for dy in [True]:
                    hs = 5
                    l = 1
                    size_i = 1
                    size_o = 1
                    ls = 10
                    ep = 100
                    bs = 64
            else:
                for dy in [True]:
                    hs = 250
                    l = 1
                    size_i = 6
                    size_o = 6
                    ls = 40
                    ep = 100
                    bs = 128

            print(f'training start on: {dataset} with cl: {cl}, rm: {rm}')
            args = parser.parse_args()
            args.dataset = dataset
            args.hidden_size = hs
            args.len_sequence = ls
            args.layers = l
            args.input_size = size_i
            args.output_size = size_o
            args.curriculum_learning = cl
            args.reg_methode = rm
            args.epochs = ep
            args.batch_size = bs
            args.dynamic_K = dy

            lstm_train.main(args)
            validation.main(args, piecewise=True)

