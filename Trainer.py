import torch
#import torch.optim as optim
#import torch.nn.functional as F
from torch.autograd import Variable
from net import *

import os
from extractor import *
from fun import *

class Trainer:
    def __init__(self, args):
        self.args = args
        # build model
        #self.model = nn.DataParallel(Net())
        self.model = Net()
        self.model.eval()
        self.show_dataset_model_params()
        self.load_pretrained_model()
    
    def Tester(self, audio):
        fea = mel(audio, self.args).astype('float32')
        fea = torch.from_numpy(fea)
        X = Variable(fea)
        CP, SP  = self.model(X)
        _, CP = torch.max(CP.data, 1)
        #_, SP = torch.max(SP.data, 1)
        #cc = SP.data.numpy()
        #cc = np.argmax(cc[0].mean(1),0)
        return CP.item()
    
    def load_pretrained_model(self):
        # pre-training
        if os.path.exists(self.args.pmp):
            pretrained_model = torch.load(self.args.pmp, map_location=lambda storage, loc: storage)
            model_param = self.model.state_dict()
            for k in pretrained_model['state_dict'].keys():
               try:
                    model_param[k[7:]].copy_(pretrained_model['state_dict'][k])
               except:
                    pass
                    #print '[ERROR] Load pre-trained model'
                    #self.model.apply(model_init)
                    #break
            print('Load Pre_trained Model : ' + self.args.pmp)
        
        else:
            print('Learning from scrath')
            self.model.apply(model_init)
            
    def show_dataset_model_params(self):
        # show model structure
        #print self.model
        # show params
        print(show_model_params(self.model))
        #print show_model_params(self.Snet)
    
