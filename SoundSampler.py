import numpy as np
import pyaudio
import threading, queue
import time

class Sampler:
    _instance = None
    
    ## for singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance :
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, detect_que, visual_que, args):
        self.args = args
        self.detect_que = detect_que
        self.visual_que = visual_que
        self.thread = None
    ## audio sampling format
        self.RATE = self.args.sr
        self.CHUNK = self.args.ws # or smaller than sample rate
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RECORD_SECONDS = self.args.rd   
    ## recording object
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_stop = False
        
    def _sampling(self):
        while(not self.is_stop):
            frames = []
            for i in range(0, int(self.RATE/self.CHUNK * self.RECORD_SECONDS)):
                data = self.stream.read(self.CHUNK, exception_on_overflow = False)
                frames.append(data) # data has type of string
                self.visual_que.put(np.fromstring(np.array(data), np.float32))
            
            # String type to Numerical type
            # frames = np.array(frames).flatten()
            # frames = np.fromstring(frames, np.float32)
            # self.detect_que.put(frames)
            
            
    def start(self):
        if self.stream is None:
            self.stream = self.audio.open(format = self.FORMAT,
                                channels = self.CHANNELS,
                                rate = self.RATE,
                                input = True,
                                frames_per_buffer = self.CHUNK)
            self.thread = threading.Thread(target=self._sampling)
            self.thread.start()
        else:
            try:
                self.stream.start_stream()
            except:
                pass
            finally:
                self.stream = self.audio.open(format = self.FORMAT,
                                channels = self.CHANNELS,
                                rate = self.RATE,
                                input = True,
                                frames_per_buffer = self.CHUNK)
                self.stream.start_stream()
            self.is_stop = False
            self.thread = threading.Thread(target=self._sampling)
            self.thread.start()
            
    def stop(self):
        self.is_stop = True
        self.thread.join()
        self.stream.stop_stream()
        
        
