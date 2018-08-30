import torch.nn as nn
import torch
import torch.nn.functional as F

class GLU(nn.Module):
    def __init__(self, inp, out, ms=(4,2), ds=1):
        super(GLU, self).__init__()
        fs = (3,3)
        ps = (1,1)
        self.ms = ms
        we = 0
        if we == 1:
            self.cnn_lin = nn.utils.weight_norm(nn.Conv2d(inp, out, fs, dilation=ds, padding=ps), name='weight')
            self.cnn_sig = nn.utils.weight_norm(nn.Conv2d(inp, out, fs, dilation=ds, padding=ps), name='weight')
            self.cnn_prd = nn.utils.weight_norm(nn.Conv2d(out, 2,3, padding=1), name='weight')
        else:
            if ms == 'up':
                self.cnn_lin = nn.ConvTranspose2d(inp, out, 3, stride=(4,2), padding=(0,1), output_padding=(1,1))
                ms = (1,1)
                self.cnn_1 = nn.Conv2d(out, out, fs, dilation=ds, padding=ps)
                self.bn1 = nn.BatchNorm2d(out)
            else:
                self.cnn_lin = nn.Conv2d(inp, out, fs, dilation=ds, padding=ps, bias=False)
                
            #self.cnn_sig = nn.Conv2d(inp, out, fs, dilation=ds, padding=ps)
            #self.cnn_prd = nn.Conv2d(out, 2,3, padding=1)

        self.bn = nn.BatchNorm2d(out)
        self.dp = nn.Dropout(.5)
        #self.bn2 = nn.BatchNorm2d(out)
        self.mp = nn.MaxPool2d(ms)
    
    def forward(self, x):
        lin = self.cnn_lin(x)
        #sig = F.sigmoid(self.cnn_sig(x))
        #sig = self.cnn_sig(x)
        #out = F.relu(self.bn2(lin)) * F.sigmoid(self.bn(sig))
        #out = lin * sig
        #out = F.relu(self.bn(lin * F.sigmoid(sig)))
        #out = F.relu(self.bn(lin * sig))
        out = F.relu(self.bn(lin))
        if self.ms == 'up':
            out = F.relu(self.bn1(self.cnn_1(out)))

        #out = F.relu(lin)
        #out_pd = self.cnn_prd(self.dp(out))
        #sig = self.cnn_sig(x)
        
        #return self.mp(F.sigmoid(self.bn1(sig)) * self.bn2(lin))
        #out_pd = F.avg_pool2d(out_pd, (out_pd.size()[2], 1))
        #out_pd = F.avg_pool2d(out_pd, (out_pd.size()[2], out_pd.size()[3]))
        #out_pd = F.avg_pool2d(out_pd, out_pd.size()

        #return out, self.mp(out), out_pd
        return self.mp(out)

class DNN(nn.Module):
    def __init__(self, inp, out, numl):
        super(DNN, self).__init__()
        self.dnn1 = nn.Linear(inp*2, out)
        self.bn1 = nn.BatchNorm1d(out)
        self.pred = nn.Linear(out, numl)
        self.dp = nn.Dropout(.5)

        #self.att = nn.Conv2d(out, 1,3, padding=1)
        #self.bn2 = nn.BatchNorm1d(out)
    
    def forward(self, x):
        avgo = F.avg_pool2d(x, x.size()[2:]).view(x.size()[0], -1)
        maxo = F.max_pool2d(x, x.size()[2:]).view(x.size()[0], -1)
        out = torch.cat([avgo, maxo], dim=1)
        out = self.dp(out)
        out = F.relu(self.bn1(self.dnn1(out)))
        #out = self.dp(out)
        out = self.pred(out)
        return out

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.numl = 2
        #self.model_name = 'CNN_GLU_bn_lin_sig_10'
        self.model_name = 'CNN_relu_bn_sig_re'
        ks = 32*4
        #self.bn = nn.BatchNorm2d(1)
        self.G1 = GLU(   1, ks*1)
        self.G2 = GLU(ks*1, ks*2)
        self.G3 = GLU(ks*2, ks*3, (1,1))
        #self.D1 = GLU(ks*5, ks*2, 'up')
        #self.D2 = GLU(ks*3, ks*1, 'up')
        
        #self.re = nn.Conv2d(ks*1, 1,3, padding=1)


        #self.D1 = GLU(ks*5, ks*2, (1,1))
        #self.D2 = GLU(ks*3, ks*1, (1,1))
        #self.G3 = GLU(ks*2, ks*3)
        #self.G4 = GLU(ks*3, ks*4)
        #self.G5 = GLU(ks*4, ks*5, (1,1))
        self.pred = DNN(ks*3, 128*2, self.numl)
    
    def forward(self, zx):
        #zx = (x - xavg)/xstd
        zx = (zx - 5.4928)/3.60983
        #zx = self.bn(zx)

        # oG1 -> 128, 64
        # oG2 -> 128/4, 64/4
        # oG3 -> 128/4/4, 64/4/4
        # D1 -> 128/4, 64/4
        # D2 -> 128, 64
        G1 = self.G1(zx)
        G2 = self.G2(G1)
        G3 = self.G3(G2)
        
        '''
        mode = 'nearest'
        mode = 'bilinear'
        G3 = F.upsample(G3, scale_factor=4, mode=mode)
        _, D1, P4 = self.D1(torch.cat([G3, oG2], dim=1))
        D1 = F.upsample(D1, scale_factor=4, mode=mode)
        _, D2, P5 = self.D2(torch.cat([D1, oG1], dim=1))
        '''
        #_, D1, P4 = self.D1(torch.cat([G3, G2], dim=1))
        #_, D2, P5 = self.D2(torch.cat([D1, G1], dim=1))

        #re = self.re(D2)
        #G4, P4 = self.G4(G3)
        #G5, P5 = self.G5(G4)
        Cpred = self.pred(G3)
        
        #return Cpred, F.avg_pool2d(P3,(1,8))
        return Cpred, []



