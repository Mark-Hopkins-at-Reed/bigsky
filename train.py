import torch
import random
import copy
import pandas as pd
  

  
class DropoutClassifier(torch.nn.Module):
    def __init__(self, mgr, evidence, response, hidden_size = 200):
        super(DropoutClassifier, self).__init__()
            
        self.X = mgr.select(evidence)
        self.y, output_size = mgr.select_response(response)
        input_size = len(self.X[0])
        
        self.dropout1 = torch.nn.Dropout(p=0.2)
        self.linear1 = torch.nn.Linear(input_size, hidden_size)
        self.dropout2 = torch.nn.Dropout(p=0.5)
        self.linear2 = torch.nn.Linear(hidden_size, output_size)

    def forward(self, input_vec, labels):
        nextout = torch.stack([input_vec]).float() #nextout = input_vec
        nextout = self.dropout1(nextout).float()
        nextout = self.linear1(nextout)
        nextout = nextout.clamp(min=0)
        nextout = self.dropout2(nextout)    
        nextout = self.linear2(nextout)
        result = nextout
        loss = None
        if labels is not None:
            loss_fct = torch.nn.CrossEntropyLoss()
            y = torch.LongTensor([labels.item()]) #torch.LongTensor(labels[:len(labels)])            
            loss = loss_fct(result, y)
        return result, loss
    
 
def data_loader(x_list, y_list):
    z = list(zip(x_list, y_list))
    random.shuffle(z)
    x_tuple, y_tuple = zip(*z)

    for i in range(len(x_tuple)):
        yield x_tuple[i], y_tuple[i]


def train(model, num_train, num_epochs, learning_rate, 
          save_path=None):
    best_model = model
    best_acc = 0.0
    
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    print("Starting first epoch...")
    for epoch in range(num_epochs):
        model.train()
        train_loader = data_loader(model.X[:num_train], model.y[:num_train])
        test_loader = data_loader(model.X[num_train:], model.y[num_train:])
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
            if z[0].argmax() == y.item():
                correct_predictions += 1
            num_characters += 1
        print('Test Accuracy: %.4f' % (correct_predictions * 1.0 / num_characters))
        if correct_predictions * 1.0 / num_characters > best_acc:
            print("Updating best model.")
            best_acc = correct_predictions * 1.0 / num_characters
            best_model = copy.deepcopy(model)
    if save_path is not None:
        torch.save(best_model, save_path)
    return best_model

def run():
    print('reading csv')
    df = pd.read_csv('plot_level/plt_spatial.csv')
    #df = pd.read_csv('plot_level/plot_response.csv')
    mgr = InteriorWestData(df)
    print('num rows = {}'.format(len(mgr)))
    evidence_vars =  ['OFFSET', #"forgrp", 
                      #'ASPECT', 'SLOPE', 'LAT_PUBLIC', 'LON_PUBLIC', 
                      #'ELEV_PUBLIC', "demLF","nlcd11","forprob",
                      "evtLF","forbio"]
    evidence_vars1 = ['OFFSET', 'ASPECT', 'SLOPE']#, 'LAT_PUBLIC', 'LON_PUBLIC', 
                     #'ELEV_PUBLIC']
    print('preparing data')
    model = DropoutClassifier(mgr, evidence_vars, 'FORTYPCD')
    train(model, int(.75 * len(mgr)), 100, 0.005)
    
def run_easy():
    df = easy_data()
    mgr = DataManager(df)
    evidence_vars = ['X0', 'X1', 'X2']
    print('preparing data')
    model = DropoutClassifier(mgr, evidence_vars, 'Y')
    train(model, 8000, 50, 0.005)
    
    
    