import torch.nn as nn

class RNNSiameseNet(nn.Module):
    def __init__(self, encode_dim, hidden_dim, output_dim, num_layers, dropout):
        super(RNNSiameseNet, self).__init__()
        self.encode_dim = encode_dim
        self.lstm = nn.LSTM(
            encode_dim,
            hidden_dim,
            num_layers=num_layers,
            dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def embed(self, inputs):
        inputs = inputs.T.view(*inputs.T.shape, self.encode_dim)
        packed_outputs, (hidden, cell) = self.lstm(inputs)
        hidden = self.dropout(hidden[-1, :, :].squeeze(0))
        return hidden

    def forward_once(self, inputs):
        hidden = self.embed(inputs)
        outputs = self.fc(hidden)
        return outputs

    def forward(self, item1, item2):
        output1 = self.forward_once(item1)
        output2 = self.forward_once(item2)
        return output1, output2

config = {
    'batch_size': 64,
    'shuffle': True,
    'num_workers': 6,
    'top_k': 5,
    'drop_last': True,
    'num_epochs': 400,
    'encode_dim': 1,
    'hidden_dim': 128,
    'output_dim': 2,
    'num_layers': 2,
    'dropout': 0.5,
}

model = RNNSiameseNet(
    config['encode_dim'],
    config['hidden_dim'],
    config['output_dim'],
    config['num_layers'],
    config['dropout']
)