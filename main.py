import argparse
import queue
import multiprocessing as mp
from SoundSampler import Sampler
from soundEventUI import UI
from EventDetect import Detector

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--sr', default =16000, type=int, help='sample rate')
    # parser.add_argument('--ws', default=1000, type=int, help='windows size')
    # parser.add_argument('--hs',  default=492,   type=int, help='hop size')
    # parser.add_argument('--mel', default=128,   type=int, help='mel bands')
    # parser.add_argument('--rd', default=5,    type=int, help='recording duration')
    # parser.add_argument('--frame', default=3, type=int, help='number of recording duration showing on UI')

    pmp = './model/CNN_relu_bn_sig_re_epoch_86'
    # params for audio feature extraction (mel-spectrogram)
    parser = argparse.ArgumentParser(description= 'PyTorch M&ment Training using DCASE2017 Dataset')
    parser.add_argument('--dn',  default='CRW_baby_cry', type=str, help='dataset name')
    parser.add_argument('--sr',  default=16000, type=int, help='[fea_ext] sample rate')
    parser.add_argument('--ws',  default=2000,  type=int, help='[fea_ext] windows size')
    parser.add_argument('--wws',  default=2048,  type=int, help='[fea_ext] windows size')
    parser.add_argument('--hs',  default=497,   type=int, help='[fea_ext] hop size')
    parser.add_argument('--mel', default=128,   type=int, help='[fea_ext] mel bands')
    parser.add_argument('--msc', default=1,     type=int, help='[fea_ext] top duration of audio clip')
    parser.add_argument('--frame', default=10, type=int, help='number of recording duration showing on UI')
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

    audio_visual_que = queue.Queue() # audio data container for visualization
    audio_detect_que = mp.Queue() # audio data container for event detection
    audio_event_que = mp.Queue() # container for event detecting results
    sampler = Sampler(audio_detect_que, audio_visual_que, args) # sampling audio
    detector = Detector(audio_detect_que, audio_event_que, args) # detecting audio event
    ui = UI(audio_visual_que, audio_event_que, sampler, detector, args)

if __name__ == '__main__':
    # mp.set_start_method('fork')
    main()
