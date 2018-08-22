# import torch
# import librosa
import threading, queue
import random
from multiprocessing import Process


class Detector:
    def __init__(self, detect_que, event_que, args):
        self.detect_que = detect_que
        self.event_que = event_que
        # self.model = model
        # self.model.eval()
        self.args = args
        self.result_que = queue.Queue()
        self.is_stop = False

    def _detect(self, event_que):
        while(not self.is_stop):
            if not self.detect_que.empty():
                frame = self.detect_que.get()
                Time = frame[0][1] # start time stamp of the frame
                print(Time)
                # #[Testing] generate fake results
                result = random.randint(1,10)
                result = "cry" if result<=7 else "None"
                result = [result, Time]
                event_que.put(result)
    
    def start(self):
        self.is_stop=False
        # threading.Thread(target=self._detect).start()
        Process(target=self._detect, args=(self.event_que,)).start()
    def stop(self):
        self.is_stop=True
        

