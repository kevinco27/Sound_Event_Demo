from Trainer import *
from extractor import *
import numpy as np
import argparse
from utils.flops_benchmark import *
import librosa
import torch
from torch.autograd import Variable


def check_trans_correct(pmp, omp, args):
        import onnx
        import caffe2.python.onnx.backend

        dummy_data = np.random.rand(1000, args.sr)
        
        pmp_model = Trainer(args)
        omp_model = caffe2.python.onnx.backend.prepare(onnx.load(omp))

        pmp_result = []
        omp_result = []

        for i in range(dummy_data.shape[0]):
                data = dummy_data[i]
                
                # for pmp
                pmp_result.append(pmp_model.Tester(data))
                # for omp
                fea = mel(data, args).astype('float32')
                omp_result.append(np.argmax(omp_model.run(fea)))
        pmp_result = np.array(pmp_result)
        omp_result = np.array(omp_result)
        print("Checking correctness of model transforming")
        print("diff between two model results:", np.sum(np.abs(pmp_result-omp_result)))

def cal_FLOPs(args):
        path = 'audio_data/Baby_Cry_1.wav'
        wave_data = librosa.core.load(path,sr=args.sr, duration=10)[0]
        wave_data = np.array_split(wave_data, 10)

        # add flops counting func to model
        net = Trainer(args)
        net.model = add_flops_counting_methods(net.model)
        net.model.start_flops_count()
        for idx, data in enumerate(wave_data):
                if idx == 0:
                        net.Tester(data)
                        print(f"{args.pmp.split('/')[-1]}: {net.model.compute_average_flops_cost() / 1e9} GFLOPs")


if __name__ == '__main__':
        pre_model_path = './model/epoch_56'
        onnx_model_path = './model/epoch_56.onnx'

        # params for audio feature extraction (mel-spectrogram)
        parser = argparse.ArgumentParser(description='PyTorch M&ment Training using DCASE2017 Dataset')
        parser.add_argument('--dn', default='CRW_baby_cry', type=str, help='dataset name')
        parser.add_argument('--sr', default=16000, type=int, help='[fea_ext] sample rate')
        parser.add_argument('--ws', default=2000, type=int, help='[fea_ext] windows size')
        parser.add_argument('--wws', default=2048, type=int, help='[fea_ext] windows size')
        parser.add_argument('--hs', default=497, type=int, help='[fea_ext] hop size')
        parser.add_argument('--mel', default=128, type=int, help='[fea_ext] mel bands')
        parser.add_argument('--msc', default=1, type=int, help='[fea_ext] top duration of audio clip')
        parser.add_argument('--frame', default=3, type=int, help='number of recording duration showing on UI')
        parser.add_argument('--et', default=10000, type=int, help='[fea_ext] spect manti')

        # params for training
        parser.add_argument('--bs', default=32 / 4, type=int, help='[net] batch size')
        parser.add_argument('--lrde', default=30, type=int, help='[net] divided the learning rate 10 by every lrde epochs')
        parser.add_argument('--mom', default=0.9, type=float, help='[net] momentum')
        parser.add_argument('--wd', default=1e-4, type=float, help='[net] weight decay')
        parser.add_argument('--lr', default=0.01, type=float, help='[net] learning rate')
        parser.add_argument('--ep', default=31 * 3, type=int, help='[net] epoch')
        parser.add_argument('--beta', default=0.3, type=float, help='[net] hyperparameter for pre-class loss weight')
        parser.add_argument('--pmp', default=pre_model_path, type=str, help='[net] pre-trained model path')

        args = parser.parse_args()

        check_trans_correct(pre_model_path, onnx_model_path, args)
        cal_FLOPs(args)
        
