# import torch
# import librosa
import threading, queue
import random
from multiprocessing import Process, Value, Manager
import time


class Detector:
    def __init__(self, detect_que, event_que, args):
        self.detect_que = detect_que
        self.event_que = event_que
        # self.model = model
        # self.model.eval()
        self.args = args
        self.is_stop = Manager().Value('i', True)

    def _detect(self):
        i = 0
        while(not self.is_stop.value):
            result = random.randint(1,10)
            result = "cry {}".format(i) if result<=5 else "None"
            i+=1
            self.event_que.put(result)
            
            # if not self.detect_que.empty():
            #     frame = self.detect_que.get()
            #     Time = frame[0][1] # start time stamp of the frame
            #     # #[Testing] generate fake results
            #     result = random.randint(1,10)
            #     result = "cry" if result<=5 else "None"
            #     result = [result, Time]
            #     with  self.Lock:
            #         self.event_que.put(result)
    
    def start(self):
        self.is_stop.value=False
        # threading.Thread(target=self._detect).start()
        Process(target=self._detect, daemon=True).start()

    def stop(self):
        self.is_stop.value=True
        

