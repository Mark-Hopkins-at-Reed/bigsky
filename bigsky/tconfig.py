import torch
from bigsky.networks import FeedForwardClassifier
   
class TrainingConfig:

    def __init__(self):
        self.hyperparams = dict()
        self.hyperparams['batchsize'] = 32
        self.hyperparams['optimizer'] = {'name': 'adam',
                                         'rate': 0.001}
        self.hyperparams['network'] = {'name': 'feedforward',
                                       'numlayers': 0,
                                       'hiddensize': 200,
                                       'dropout': {'prob': 0.2},
                                       'layernorm': False,
                                       }
        self.network_names = {'feedforward': FeedForwardClassifier}
    
    
    def __getitem__(self, hparam):
        return self.hyperparams[hparam]

    def get_batch_size(self):
        return self.hyperparams['batchsize']

    def create_optimizer_factory(self):
        optim_params = self.hyperparams['optimizer']
        optim_name = optim_params['name']
        if optim_name == 'adam':
            factory = lambda params: torch.optim.Adam(params, 
                                                      lr=optim_params['rate'])
        else:
            raise Exception("Unsupported optimizer name: {}".format(optim_name))
        return factory
        
    def create_network_factory(self):
        network_name = self.hyperparams['network']['name']
        if network_name in self.network_names:
            network_class = self.network_names[network_name]
            result = network_class.create_factory_method(self.hyperparams['network'])
        else:
            result = None
        return result
    
       
    def replace(self, param_name, value):
        result = TrainingConfig()
        result.hyperparams = self.hyperparams.copy()
        result.hyperparams[param_name] = value
        return result
    
    def __str__(self):
        return str(self.hyperparams)
    
def vary_num_layers(config, min_num, max_num):
    return [config.replace('network',  {'name': 'feedforward',
                                        'numlayers': x,
                                        'hiddensize': 200,
                                        'dropout': {'prob': 0.2}
                                        }) 
            for x in range(min_num, max_num)]   

def vary_hidden_size(config, min_num, max_num):
    return [config.replace('network',  {'name': 'feedforward',
                                        'numlayers': 2,
                                        'hiddensize': x,
                                        'dropout': {'prob': 0.2}
                                        }) 
            for x in range(min_num, max_num)]   
    
def vary_dropout_prob(config, probs):
    return [config.replace('network',  {'name': 'feedforward',
                                        'numlayers': 2,
                                        'hiddensize': 200,
                                        'dropout': {'prob': x}
                                        }) 
            for x in probs]   
        
def vary_learning_rate(config, rates):
    return [config.replace('optimizer', {'name': 'adam', 'rate': x}) 
            for x in rates]   

    