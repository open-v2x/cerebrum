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

"""Convert the data to the LSTM required format."""

import copy
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader


class LstmDataLoader:
    """Convert the data to the LSTM required format."""

    DEFAULT_RATRO = 0.8
    DEFAULT_LENGTH = 5

    def __init__(
        self,
        train_ratio=DEFAULT_RATRO,
        track_length=DEFAULT_LENGTH,
        batch_size=5,
        input_size=3,
        output_size=2,
        trans_rate=0.06,
        time_rate=0.03,
        std_num=200,
    ):
        """Class initialization."""
        self.trans_rate = trans_rate  # pixel * trans_rate = meter
        self.time_rate = time_rate
        self.std_num = std_num  # data / std_num = train_data
        self.train_ratio = train_ratio
        self.track_length = track_length
        self.batch = batch_size
        self.input_sz = input_size
        self.output_sz = output_size
        self.ld = DataLoader

    def load_dataset(self, csv_path):
        """External call function."""
        # 输入格式，轨迹csv
        self.data = pd.read_csv(csv_path)
        self.__create_preset()
        return self.__load_tensor()

    def __create_preset(self):
        # 基于预测的补全，用历史3帧数据预测未来一帧，重复调用补全。
        train_set = np.array([])
        label_set = np.array([])
        for ID, track in self.data.groupby(["car_id"]):
            # 输入：x y t
            train = np.array([track["x"], track["y"], track["frame_id"]])
            # 输出：x y
            label = np.array([track["x"], track["y"]])
            train, label = self.__stand(train, label)
            # 划分成训练对应的数据条
            divide_trn_set, divide_label_set = self.__divide(train, label)
            if len(divide_trn_set) == 0:
                continue
            if len(train_set):
                train_set = np.vstack((train_set, divide_trn_set))
                label_set = np.vstack((label_set, divide_label_set))
            else:
                train_set = divide_trn_set
                label_set = divide_label_set
        self.__backup(train_set, label_set)

    def __stand(self, train, label):
        train[0] = train[0] * self.trans_rate / self.std_num
        train[1] = train[1] * self.trans_rate / self.std_num
        label[0] = label[0] * self.trans_rate / self.std_num
        label[1] = label[1] * self.trans_rate / self.std_num
        # 为了时间输入能被有效利用，随机删除行来使时间不均匀
        while np.random.rand() < 0.5 and len(train[0]) > 0:
            rand = np.random.randint(0, len(train[0]))
            train = np.delete(train, rand, axis=1)
            label = np.delete(label, rand, axis=1)
        return train, label

    def __divide(self, train, label):
        # 函数所有的trn-label都变成了对应向量，一条数据就是1*input-1*output
        track_len = train.shape[1]
        divide_trn = []
        divide_label = []
        if track_len < self.track_length:
            return divide_trn, divide_label
        for i in range(track_len - self.track_length - 1):
            tmp = copy.deepcopy(
                train[:, i : i + self.track_length].T.reshape(
                    self.track_length, self.input_sz
                )
            )
            start_time = tmp[0, 2]
            tmp[:, 2] = tmp[:, 2] - start_time
            tmp[:, 2] = tmp[:, 2] * self.time_rate
            divide_trn.append(list(tmp))
            divide_label.append(list(label[:, i + self.track_length]))
        return np.array(divide_trn), np.array(divide_label)

    def __backup(self, train_set, label_set):
        all_num = len(train_set)
        rate_9 = int(all_num * 0.9)
        self.train_x = train_set[: int(all_num * self.train_ratio)]
        self.train_y = label_set[: int(all_num * self.train_ratio)]
        self.val_x = train_set[int(all_num * self.train_ratio) : rate_9]
        self.val_y = label_set[int(all_num * self.train_ratio) : rate_9]
        self.test_x = train_set[rate_9:]
        self.test_y = label_set[rate_9:]

    def __load_tensor(self):
        data_train = [self.train_x]
        data_valid = [self.val_x]
        data_test = [self.test_x]
        data_train.append(self.train_y)
        data_valid.append(self.val_y)
        data_test.append(self.test_y)

        data_train = list(zip(*data_train))
        data_valid = list(zip(*data_valid))
        data_test = list(zip(*data_test))
        trn_loader = self.ld(
            data_train,
            batch_size=self.batch,
            num_workers=0,
            pin_memory=True,
            shuffle=True,
        )
        val_loader = self.ld(
            data_valid,
            batch_size=self.batch,
            num_workers=0,
            pin_memory=True,
            shuffle=True,
        )
        test_loader = self.ld(
            data_test,
            batch_size=self.batch,
            num_workers=0,
            pin_memory=True,
            shuffle=False,
        )
        return trn_loader, val_loader, test_loader


if __name__ == "__main__":
    flnm = "train.csv"
    # 数据header: frame_id	car_id	x	y	w	h	class(0)
    LD = LstmDataLoader()
    dataset = LD.load_dataset(flnm)
