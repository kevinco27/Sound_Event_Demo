import random
from multiprocessing import Process, Value, Manager
import time
from Trainer import *



class Detector:
    def __init__(self, detect_que, event_que, args):
        self.detect_que = detect_que
        self.event_que = event_que
        self.args = args
        self.is_stop = Manager().Value('i', True)
        self.net = Trainer(self.args)

    def _detect(self):
        while(not self.is_stop.value):
            if not self.detect_que.empty():
                frame = self.detect_que.get()
                Time = frame[1][0] # start time stamp of the frame
                data = np.array(frame[0])  
                result = self.net.Tester(data)
                self.event_que.put([result,Time])
    
    def start(self):
        self.is_stop.value=False
        Process(target=self._detect, daemon=True).start()

    def stop(self):
        self.is_stop.value=True
        

