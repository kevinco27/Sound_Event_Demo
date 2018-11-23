import os
import numpy as np 
import argparse
import librosa
import torch
import torch.onnx
import onnx
import caffe2.python.onnx.backend
from caffe2.python import core, net_drawer, net_printer, visualize, workspace, utils
from caffe2.proto.caffe2_pb2 import NetDef
from Trainer import *
from extractor import *


pmp = './model/epoch_56'
# params for audio feature extraction (mel-spectrogram)
parser = argparse.ArgumentParser(description= 'PyTorch M&ment Training using DCASE2017 Dataset')
parser.add_argument('--dn',  default='CRW_baby_cry', type=str, help='dataset name')
parser.add_argument('--sr',  default=16000, type=int, help='[fea_ext] sample rate')
parser.add_argument('--ws',  default=2000,  type=int, help='[fea_ext] windows size')
parser.add_argument('--wws',  default=2048,  type=int, help='[fea_ext] windows size')
parser.add_argument('--hs',  default=497,   type=int, help='[fea_ext] hop size')
parser.add_argument('--mel', default=128,   type=int, help='[fea_ext] mel bands')
parser.add_argument('--msc', default=1,     type=int, help='[fea_ext] top duration of audio clip')
parser.add_argument('--frame', default=3, type=int, help='number of recording duration showing on UI')
parser.add_argument('--et',  default=10000, type=int, help='[fea_ext] spect manti')

# params for training
parser.add_argument('--bs',   default=32/4,    type=int,   help='[net] batch size')
parser.add_argument('--lrde', default=30,    type=int,   help='[net] divided the learning rate 10 by every lrde epochs')
parser.add_argument('--mom',  default=0.9,   type=float, help='[net] momentum')
parser.add_argument('--wd',   default=1e-4,  type=float, help='[net] weight decay')
parser.add_argument('--lr',   default=0.01,   type=float, help='[net] learning rate')
parser.add_argument('--ep',   default=31*3,   type=int,   help='[net] epoch')
parser.add_argument('--beta', default=0.3,   type=float, help='[net] hyperparameter for pre-class loss weight')
parser.add_argument('--pmp',  default=pmp,   type=str,   help='[net] pre-trained model path')

args = parser.parse_args()

path = 'audio_data/Baby_Cry_1.wav'
wave_data = librosa.core.load(path,sr=args.sr, duration=10)[0]
wave_data = np.array_split(wave_data, 10)
fea = mel(wave_data[0], args).astype('float32')


onnx_path = './model/epoch_56.onnx'
# Model transfering: pytorch -> caffee2 using onnx (if caffe2 model exists, then model tranfering snippet will be ignored)
# 1) pytorch model -> onnx model
net = Trainer(args)
tor_fea = torch.from_numpy(fea)
X = Variable(tor_fea)
torch_out = torch.onnx.export(net.model, X, onnx_path, export_params=True, verbose=False)

# 2) run onnx model in caffe2
model = onnx.load(onnx_path)
prepared_backend = caffe2.python.onnx.backend.prepare(model)
rnd_input = np.random.rand(1,1,128,32)*10
rnd_input = rnd_input.astype('float32')

print(prepared_backend.run(fea))
print(prepared_backend.run(rnd_input))
c2_workspace = prepared_backend.workspace


c2_model = prepared_backend.predict_net
c2_workspace.FeedBlob('28', np.array(5.4928))
c2_workspace.FeedBlob('30', np.array(3.6098))
c2_workspace.FeedBlob('60', np.array([[-1]]))
c2_workspace.FeedBlob('51', np.array([[-1]]))
from caffe2.python.predictor import mobile_exporter
init_net, predict_net = mobile_exporter.Export(c2_workspace, c2_model,  c2_model.external_input)

workspace.RunNetOnce(init_net.SerializeToString())
workspace.CreateNet(predict_net.SerializeToString(), overwrite=True)

workspace.FeedBlob('0', fea) # input
workspace.RunNetOnce(predict_net)
print(workspace.FetchBlob('73')) # output


# onnx -> caffe2 model
# pytorch dropout layer 讓 onnx -> init_net, predict_net 有問題


