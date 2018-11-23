import torch.nn as nn
import torch
import torch.nn.functional as F

class GLU(nn.Module):
    def __init__(self, inp, out, ms=(2,4), ds=1):
        super(GLU, self).__init__()
        fs = (3,3)
        ps = (1,1)
        self.ms = ms
        self.cnn_lin = nn.Conv2d(inp, out, fs, dilation=ds, padding=ps, bias=False)
        self.bn = nn.BatchNorm2d(out)
        self.mp = nn.MaxPool2d(ms, ceil_mode=False)
    
    def forward(self, x):
        out = F.relu(self.bn(self.cnn_lin(x)))
        return self.mp(out)

class DNN(nn.Module):
    def __init__(self, inp, out, numl):
        super(DNN, self).__init__()
        self.dnn1 = nn.Linear(inp*2, out)
        self.bn1 = nn.BatchNorm1d(out)
        self.pred = nn.Linear(out, numl)
        self.dp = nn.Dropout(.5)

    
    def forward(self, x):
        ker_size = x.detach().numpy().shape[2:]
        avgo = F.avg_pool2d(x, ker_size, ceil_mode=False).view(x.size()[0], -1)
        maxo = F.max_pool2d(x, ker_size, ceil_mode=False).view(x.size()[0], -1)
        # avgo = F.avg_pool2d(x, x.size()[2:], ceil_mode=False).view(x.size()[0], -1)
        # maxo = F.max_pool2d(x, x.size()[2:], ceil_mode=False).view(x.size()[0], -1)
        out = torch.cat([avgo, maxo], dim=1)
        out = self.dp(out)
        out = F.relu(self.bn1(self.dnn1(out)))
        return self.pred(self.dp(out))

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.numl = 2
        self.model_name = 'noisecnn'
        ks = 32*4
        self.G1 = GLU(   1, ks*1)
        self.G2 = GLU(ks*1, ks*2)
        self.G3 = GLU(ks*2, ks*3, (1,1))
        self.pred = DNN(ks*3, 128*2, self.numl)
        
    def forward(self, zx):
        zx = (zx - 5.4928)/3.60983
        G1 = self.G1(zx)
        G2 = self.G2(G1)
        G3 = self.G3(G2)
        Cpred = self.pred(G3)
        
        return Cpred, []



