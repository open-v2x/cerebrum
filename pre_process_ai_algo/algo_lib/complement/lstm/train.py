#   Copyright 99Cloud, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""LSTM's Weight Training process."""

import argparse
from common import modules
import numpy as np
import os
import torch
from tqdm import tqdm  # type: ignore

complement = modules.algorithms.pre_process_complement


def train_lstm():
    """Training weights of LSTM."""
    source, epoch, learning, history_length, batch, ratio = (
        opt.source,
        opt.epoch,
        opt.lr,
        opt.length,
        opt.batch_size,
        opt.train_ratio,
    )
    # 设置GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # 设置随机种子
    torch.manual_seed(0)

    if os.path.exists(opt.source):
        print("loading dataset...")
        loader = complement.lstm.loader.LstmDataLoader(
            track_length=history_length, batch_size=batch, train_ratio=ratio
        )
        trn_loader, val_loader, test_loader = loader.load_dataset(source)
        print("finish!")
    else:
        return False

    INPUT_FEATURES_NUM = 3 * history_length
    trn_num = len(trn_loader.dataset) // batch
    val_num = len(val_loader.dataset) // batch

    rnn = complement.lstm.corenet.RegLSTM(
        input_size=INPUT_FEATURES_NUM,
        hidden_size=4,
        output_size=2,
        num_layers=4,
        bidirectional=True,
    ).to(
        device
    )  # 使用GPU或CPU
    optimizer = torch.optim.Adam(rnn.parameters(), lr=learning)
    loss_func = torch.nn.MSELoss()
    # 学习率衰减，训练到50%和75%时学习率缩小为原来的1/10
    step_scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer, milestones=[epoch // 2, epoch // 4 * 3], gamma=0.1
    )
    # 训练+验证
    train_loss = []
    valid_loss = []
    min_valid_loss = np.inf
    for i in range(epoch):
        total_loss = 0
        total_dis = 0
        val_loss = 0
        val_total_dis = 0
        print("epoch: %d loading" % i)
        with tqdm(
            total=trn_num,
            desc=f"Epoch {i + 1}/{epoch}",
            postfix=dict,
            mininterval=0.3,
        ) as pbar:
            train_loss_list = []
            rnn.train()  # 进入训练模式
            for step, (b_x, b_y) in enumerate(trn_loader):
                b_x = b_x.type(torch.FloatTensor).to(device)
                b_y = b_y.type(torch.FloatTensor).to(device)
                prediction = rnn(b_x)  # rnn output
                output = prediction[:, -1, :].to(torch.float32)
                target = b_y.view(b_y.size()).to(torch.float32)
                loss = loss_func(output, target)  # 计算损失
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                train_loss_list.append(loss.item())
                with torch.no_grad():
                    dis = torch.cdist(torch.round(output), target)
                accuracy = torch.mean(dis.float())
                total_loss += loss.item()
                total_dis += accuracy.item()
                pbar.set_postfix(
                    **{
                        "total_loss": np.mean(total_loss) / (step + 1),
                        "mean_dis": total_dis / (step + 1),
                    }
                )
                pbar.update(1)
            train_loss.append(np.mean(train_loss_list))

        print("Start Validation")
        with tqdm(
            total=val_num,
            desc=f"Epoch {i + 1}/{epoch}",
            postfix=dict,
            mininterval=0.3,
        ) as pbar:
            total_valid_loss = []
            rnn.eval()
            for step, (b_x, b_y) in enumerate(val_loader):
                b_x = b_x.type(torch.FloatTensor).to(device)
                b_y = b_y.type(torch.FloatTensor).to(device)
                with torch.no_grad():
                    prediction = rnn(b_x)  # rnn output
                    output_val = prediction[:, -1, :].to(torch.float32)
                    target_val = b_y.view(b_y.size()).to(torch.float32)
                    dis = torch.eq(torch.round(output_val), target_val)
                    accuracy = torch.mean(dis.float())

                loss = loss_func(output_val, target_val)
                total_valid_loss.append(loss.item())
                val_loss += loss.item()
                val_total_dis += accuracy.item()
                pbar.set_postfix(
                    **{
                        "total_loss": val_loss / (step + 1),
                        "mean_dis": val_total_dis / (step + 1),
                    }
                )
                pbar.update(1)
            valid_loss.append(np.mean(total_valid_loss))

        if valid_loss[-1] < min_valid_loss:
            torch.save(rnn.state_dict(), "lstm.pkl")
            min_valid_loss = valid_loss[-1]
        log_string = (
            "iter: [{:d}/{:d}], train_loss: {:0.6f},"
            " valid_loss: {:0.6f}, "
            "best_valid_loss: {:0.6f},"
            " lr: {:0.7f}"
        ).format(
            (i + 1),
            epoch,
            train_loss[-1],
            valid_loss[-1],
            min_valid_loss,
            optimizer.param_groups[0]["lr"],
        )
        step_scheduler.step()  # 学习率更新
        print(log_string)  # 打印日志


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, default="train.csv", help="train data path"
    )
    parser.add_argument("--epoch", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--length", type=int, default=3)
    parser.add_argument("--train_ratio", type=float, default=0.8)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="total batch size for all GPUs",
    )
    opt = parser.parse_args()

    train_lstm()
