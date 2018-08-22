# import torch
# import librosa
import threading, queue


class Detector:
    def __init__(self, detect_que, event_que, args):
        self.detect_que = detect_que
        self.event_que = event_que
        # self.model = model
        # self.model.eval()
        self.args = args
        self.result_que = queue.Queue()
        self.is_stop = False

    def _detect(self):
        while(not self.is_stop):
            if not self.detect_que.empty():
                frame = self.detect_que.get()
                # trans wav to spectrogram
                # fea = librosa.feature.melspectrogram(wav, sr=self.args.sr, n_fft=self.args.ws, 
                #     hop_length=self.args.hs, n_mels=self.args.mel)
                # fea = fea.reshape(1,1,128,82)
                # with torch.no_grad():
                #     data = Variable(torch.from_numpy(fea))
                # result,_ = model(data, 0, 0)
                # self.result_que.put(result)
    
    def start(self):
        self.is_stop=False
        threading.Thread(target=self._detect).start()
    def stop(self):
        self.is_stop=True
        

