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

"""The core-net of LSTM."""

from torch import nn  # type: ignore


class RegLSTM(nn.Module):
    """Long Short-term Memory Network."""

    Batch_first = True  # True则输入输出的数据格式为 (batch, seq, feature)
    Bias = True  # bias：False则bihbih=0和bhhbhh=0. 默认为True

    def __init__(
        self,
        input_size,
        hidden_size=1,
        output_size=1,
        num_layers=1,
        bidirectional=True,
    ):
        """Class initialization.

        input_size：
        feature dimension of x

        hidden_size：
        feature dimension of the hidden layer

        output_size:
        number of output features

        num_layers：
        The number of layers of the lstm hidden layer, the default is 1

        batch_first：
        If True : the input and output data format is (batch, seq, feature)

        bidirectional：
        If True, change to bidirectional lstm, default is False

        """
        super(RegLSTM, self).__init__()
        # 定义LSTM
        self.rnn = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            bias=self.Bias,
            bidirectional=bidirectional,
            batch_first=self.Batch_first,
        )
        # 定义回归层网络，输入的特征维度等于LSTM的输出，输出维度为1
        if bidirectional:
            self.reg = nn.Sequential(nn.Linear(hidden_size * 2, output_size))
        else:
            self.reg = nn.Sequential(nn.Linear(hidden_size, output_size))

    def forward(self, x):
        """Forward predict."""
        x = x.view(len(x), 1, -1)
        x, (ht, ct) = self.rnn(x)
        seq_len, batch_size, hidden_size = x.shape
        x = x.view(-1, hidden_size)
        x = self.reg(x)
        x = x.view(seq_len, batch_size, -1)
        return x


def lstm_def(input_size, hidden_size, output_size, num_layers, bidirectional):
    """Build the structure of lstm according to the parameters."""
    model = RegLSTM(
        input_size, hidden_size, output_size, num_layers, bidirectional
    )
    return model
