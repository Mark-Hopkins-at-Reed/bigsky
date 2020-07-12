import torch

class FeedForwardClassifier(torch.nn.Module):
    def __init__(self, input_size, output_size, hidden_size,
                 num_hidden_layers, dropout_prob = None):
        super(FeedForwardClassifier, self).__init__()              
        if dropout_prob is not None:
            self.dropout = torch.nn.Dropout(dropout_prob)
        else:
            self.dropout = None
        self.initial_layer = torch.nn.Linear(input_size, hidden_size)
        self.hidden_layers = [torch.nn.Linear(hidden_size, hidden_size)
                              for i in range(num_hidden_layers)]
        self.final_layer = torch.nn.Linear(hidden_size, output_size)

    def _apply_dropout(self, vec):
        if self.dropout is not None:
            return self.dropout(vec).float()
        else:
            return vec

    def forward(self, input_vec, labels):
        nextout = input_vec
        nextout = self._apply_dropout(nextout)
        nextout = self.initial_layer(nextout)
        nextout = nextout.clamp(min=0)
        for layer in self.hidden_layers:
            nextout = self._apply_dropout(nextout)
            nextout = layer(nextout)
            nextout = nextout.clamp(min=0)
        nextout = self._apply_dropout(nextout)
        nextout = self.final_layer(nextout)
        result = nextout
        loss = None
        if labels is not None:
            loss_fct = torch.nn.CrossEntropyLoss()
            y = torch.LongTensor(labels[:len(labels)])            
            loss = loss_fct(result, y)
        return result, loss
    
    @staticmethod
    def create_factory_method(config):
        assert(config['name'] == 'feedforward')
        hidden_size = config['hiddensize']
        num_hidden_layers = config['numlayers']
        if 'dropout' in config:
            dropout_prob = config['dropout']['prob']
        else:
            dropout_prob = None
        return lambda x, y: FeedForwardClassifier(x, y, hidden_size, 
                                                  num_hidden_layers,
                                                  dropout_prob)
    
 