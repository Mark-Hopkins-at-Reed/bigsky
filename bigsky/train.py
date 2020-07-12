import torch
import random
import copy
import json
import os
from bigsky.tconfig import TrainingConfig, vary_dropout_prob
from bigsky.forecast import ForecastData, read_forecast_dir
import matplotlib.pyplot as plt
 
 
def data_loader(x_list, y_list, batchsize):
    z = list(zip(x_list, y_list))
    random.shuffle(z)
    x_tuple, y_tuple = zip(*z)
    i = 0
    while i*batchsize < len(x_tuple):
        evidence = torch.stack(x_tuple[i*batchsize:(i+1)*batchsize]).float()
        response = torch.LongTensor(y_tuple[i*batchsize:(i+1)*batchsize])
        yield evidence, response
        i += 1


def train(model, mgr, evidence, response, config, num_train, num_epochs, 
          save_path=None):
    best_model = model
    best_acc = 0.0
    modelX = mgr.select(evidence)  
    modely, _ = mgr.select_response('response')
    optimizer = config.create_optimizer_factory()(model.parameters())
    print("Starting first epoch...")
    trajectory = []
    for epoch in range(num_epochs):
        model.train()
        train_loader = data_loader(modelX[:num_train], modely[:num_train],
                                   config.get_batch_size())
        test_loader = data_loader(modelX[num_train:], modely[num_train:],
                                  config.get_batch_size())
        batch_cnt = 0
        total_loss = 0
        for x, y in train_loader:
            optimizer.zero_grad()
            z, loss = model(x, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.data.item()
            batch_cnt += 1
        print ('Epoch: [%d/%d], Average Loss: %.4f' % (epoch+1, num_epochs, total_loss / batch_cnt))
        model.eval()            
        num_characters = 0
        correct_predictions = 0
        for x, y in test_loader:
            z, loss = model(x, y)
            predictions = z.argmax(dim=1).tolist()
            golds = y.tolist()
            for (prediction, gold) in zip(predictions, golds):          
                if prediction == gold:
                    correct_predictions += 1
                num_characters += 1
        test_acc = (correct_predictions * 1.0 / num_characters)
        print('Test Accuracy: %.4f' % test_acc)
        trajectory.append((epoch, test_acc))
        if correct_predictions * 1.0 / num_characters > best_acc:
            print("Updating best model.")
            best_acc = correct_predictions * 1.0 / num_characters
            best_model = copy.deepcopy(model)
    if save_path is not None:
        torch.save(best_model, save_path)
    return best_model, trajectory

def run(keyword, config):
    print('reading csv')
    forecasts = read_forecast_dir('data/1k')
    mgr = ForecastData.from_hourly_data(forecasts)
    mgr = mgr.remap_response(keyword)
    print('num rows = {}'.format(len(mgr)))
    evidence_vars = [key for key in mgr.df.keys() 
                     if key not in ['response', 'time']]
    print('preparing data')
    input_size = len(mgr.select(evidence_vars)[0])
    _, output_size = mgr.select_response('response')
    net_factory = config.create_network_factory()
    model = net_factory(input_size, output_size)
    _, trajectory = train(model, mgr, evidence_vars, 'response', config,
                          int(.75 * len(mgr)), 100)
    return trajectory

def run_multiple_configs(experiment_log, configs):
    assert(experiment_log.endswith('.exp.json'))    
    _, log_file = os.path.split(experiment_log)
    keyword = log_file[:-9]
    results = []
    for config in configs:
        print(config)
        trajectory = run(keyword, config)
        x = [point[0] for point in trajectory]
        y = [point[1] for point in trajectory]
        results.append(x)
        results.append(y)
        try:
            with open(experiment_log) as reader:
                data = json.load(reader)
        except FileNotFoundError:
            data = []
        with open(experiment_log, 'w') as writer:
            data.append({'config': config.hyperparams, 'x': x, 'y': y})
            writer.write(json.dumps(data, indent=4))
        plt.plot(*results)


def graph_results(experiment_log):
    with open(experiment_log) as reader:
        data = json.load(reader)
    results = []
    for datum in data:
        results.append(datum['x'])
        results.append(datum['y'])
    plt.plot(*results)

def main():
    base_config = TrainingConfig() 
    configs = vary_dropout_prob(base_config, [0.0, 0.1, 0.2, 0.5])
    run_multiple_configs('data/results/rain.exp.json', configs)
    
if __name__ == '__main__':
    main()
    