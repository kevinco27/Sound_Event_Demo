import numpy as np
from collections import deque
import threading, queue
import multiprocessing as mp
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import time

class UI:
    def __init__(self, visual_que, event_que, audio_sampler, audio_detector, args):
        self.visual_que = visual_que
        self.event_que = event_que
        self.sampler = audio_sampler
        self.detector = audio_detector
        self.args = args
        self.threadLock = threading.RLock()
        self.is_recording = False
        self.buffer_size = (args.sr//args.ws)*args.ws*args.rd*args.frame
        self.audio_buffer = deque(np.zeros(self.buffer_size), maxlen=self.buffer_size)
        self.colored_buffer = deque(np.zeros(self.buffer_size, dtype=np.int), maxlen=self.buffer_size)
        # wsData_pos and wsData_in_buffer_pos_map are for tracking group of same window size data in audio buffer
        self.wsData_pos = deque(np.zeros(self.buffer_size), maxlen=self.buffer_size//args.ws)
        self.wsData_in_buffer_pos_map = [[idx*self.args.ws, idx*self.args.ws+(self.args.ws-1)] for idx in range(0, self.buffer_size//args.ws)]
        self.TIME = np.linspace(0, self.buffer_size//args.sr, num=self.buffer_size)

        ## User Interface widgets
        self.window_width = 1000
        self.window_height = int((1/2)*self.window_width) # W:H = 2:1
        self.root = tk.Tk()
        self.root.title("Sound Event")
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.animate = None
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(-0.2, 0.2)
        self.line, = self.ax.plot(self.TIME, np.array(self.audio_buffer))
        self.audio_graph = FigureCanvasTkAgg(self.fig, master=self.root)
        self.start_button = tk.Button(self.root, text="start", command=self.press_start)
        self.pause_button = tk.Button(self.root, text="pause", command=self.press_pause)
        # place the widgets on the window
        self.audio_graph.get_tk_widget().place(relwidth=1.0, relheight=0.75)
        self.start_button.place(relwidth=0.5, relheight=0.15, relx=0.5, rely=0.85, anchor="nw")
        self.pause_button.place(relwidth=0.5, relheight=0.15, relx=0.0, rely=0.85, anchor="nw")
        self.root.mainloop()

    def fill_audio_buffer_with_que(self):
        while self.is_recording:
            while not self.visual_que.empty():
                print("visual que size: {}".format(self.visual_que.qsize()))
                data, timeStamp = self.visual_que.get()
                self.audio_buffer.extendleft(data)
                with self.threadLock: # wsData_pos and colored_buffer 
                    self.colored_buffer.extendleft([0]*self.args.ws)
                    self.wsData_pos.appendleft(timeStamp)
    
    def change_audio_buffer_state_by_event(self):        
        while self.is_recording:
            while not self.event_que.empty():
                event, frame_start_time = self.event_que.get()
                if event != "None":
                    with self.threadLock: # wsData_pos and colored_buffer 
                        try:
                            # mark the samples in colored buffer to decide which samples to be colored
                            start_idx = self.wsData_pos.index(frame_start_time)
                            end_idx = start_idx + self.args.sr*self.args.rd//self.args.ws
                            start_idx_in_buffer = self.wsData_in_buffer_pos_map[start_idx][0]
                            end_idx_in_buffer = self.wsData_in_buffer_pos_map[end_idx][1] if end_idx < len(self.wsData_pos) else self.buffer_size-1
                            for i in range(start_idx_in_buffer, end_idx_in_buffer+1):
                                self.colored_buffer[i] = 1
                        except:
                            pass
    
    def plot_audio_in_buffer(self, frame):
        plot_data = np.array(self.audio_buffer)
        self.line.set_data(self.TIME, plot_data)
        return self.line
    
    def pause_animation(self):
        while not self.visual_que.empty():
            pass
        self.animate.event_source.stop()

    def press_start(self):
        if self.is_recording==False:
            print('start button')
            self.is_recording=True
            self.sampler.start()
            self.detector.start()
            threading.Thread(target=self.fill_audio_buffer_with_que).start()
            threading.Thread(target=self.change_audio_buffer_state_by_event).start()
            if self.animate is None:
                self.animate = FuncAnimation(self.fig, 
                                            self.plot_audio_in_buffer, 
                                            frames=self.buffer_size, 
                                            interval=50, 
                                            blit=False, 
                                            repeat=False)
                self.animate._start()
            else:
                self.animate.event_source.start()
    
    def press_pause(self):
        if self.is_recording==True:
            print('pause button')
            threading.Thread(target=self.pause_animation).start()
            self.sampler.stop()
            self.detector.stop()
            self.is_recording=False