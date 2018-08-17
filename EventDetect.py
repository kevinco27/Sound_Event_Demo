import torch
import librosa
import threading, queue


class Detector:
    def __init__(self, audio_que, args):
        self.audio_que = audio_que
        self.model = model
        self.model.eval()
        self.args = args
        self.result_que = queue.Queue()
        self.is_stop = False

    def _detect(self):
        while(not is_stop):
            if not self.audio_que.empty():
                # trans wav to spectrogram
                wav = self.audio_que.get()
                fea = librosa.feature.melspectrogram(wav, sr=self.args.sr, n_fft=self.args.ws, 
                    hop_length=self.args.hs, n_mels=self.args.mel)
                fea = fea.reshape(1,1,128,82)
                with torch.no_grad():
                    data = Variable(torch.from_numpy(fea))
                result,_ = model(data, 0, 0)
                self.result_que.put(result)
    
    def start(self):
        if self.is_stop:
            thread = threading.Thread(target=_detect)
            thread.start()
            self.is_stop=False
    def stop(self):
        self.is_stop=True
        self.thread.join()
        

