import os
import numpy as np 
import argparse
import librosa
import torch
import torch.onnx
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


# Model transfering: pytorch -> caffee2 using onnx (if caffe2 model exists, then model tranfering snippet will be ignored)
if (not os.path.exists('./model/epoch_56.onnx')):
    # 1) pytorch model -> onnx model
    net = Trainer(args)
    fea = mel(wave_data[0], args).astype('float32')
    fea = torch.from_numpy(fea)
    X = Variable(fea)
    torch.onnx._export(net.model, X, './model/epoch_56.onnx', export_params=True)
    
    # 2) onnx model -> caffe2 model (in order to run on mobile device)
    