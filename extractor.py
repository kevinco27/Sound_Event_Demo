import numpy as np
import librosa

def mel(y, args):
    #max_time_len = int((args.sr*args.msc)/args.hs) / 1
    print(y.shape)
    max_time_len = 32 * args.msc
    print(max_time_len)
    fea = librosa.feature.melspectrogram(y, sr=args.sr, n_fft=args.wws, 
                hop_length=args.hs, n_mels=args.mel)
    print(fea)
    return np.log(1 + args.et * fea[:,:max_time_len]).reshape(1, 1, args.mel, max_time_len)

