import numpy as np
from collections import deque
import threading, queue
import multiprocessing as mp
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import matplotlib as mpl
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
        self.buffer_size = int((args.sr//args.ws)*args.ws*args.msc*args.frame)
        self.num_windows = self.buffer_size//(args.ws)
        self.num_frames = self.buffer_size//(args.sr*args.msc)
        self.audio_buffer = deque(np.zeros(self.buffer_size), maxlen=self.buffer_size)
        self.colored_buffer = []
        self.backColor_buffer = deque(np.zeros(5), maxlen = 5)
        self.count = 0
        
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax_position = self.ax.get_position()
        self.ax.set_ylim(-0.5, 0.5)
        # self.ax.axis('off')
        self.TIME = np.linspace(0, self.buffer_size//args.sr, num=self.buffer_size)
        self.line, = self.ax.plot(self.TIME, np.array(self.audio_buffer))
         # wsData_pos and wsData_in_buffer_pos_map are for tracking group of same window size data in audio buffer
        self.wsData_pos = deque(np.zeros(self.buffer_size//args.ws), maxlen=self.buffer_size//args.ws)
        self.wsData_pos_map = np.linspace(self.ax_position.x0, self.ax_position.x1, num=self.num_windows, endpoint=False)

        ## User Interface widgets
        self.window_width = 1000
        self.window_height = int((1/2)*self.window_width) # W:H = 2:1
        self.root = tk.Tk()
        self.root.title("Sound Event")
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.animate = None
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
                # print("visual que size: {}".format(self.visual_que.qsize()))
                data, timeStamp = self.visual_que.get()
                self.audio_buffer.extendleft(data)
                with self.threadLock: # wsData_pos 
                    self.wsData_pos.appendleft(timeStamp)
                if len(self.colored_buffer)>0:
                    for rect in self.colored_buffer:
                        pos = rect.get_x()
                        if pos <= self.ax_position.x1:
                            rect.set_x(pos + self.ax_position.x1/self.num_windows)
                        else:
                            rect.remove()
                            self.colored_buffer.remove(rect)
    
    def mark_audio_frame_by_audio_event(self):        
        while self.is_recording:
            while not self.event_que.empty():
                event, frame_start_time = self.event_que.get()
                self.backColor_buffer.appendleft(event)
                ii = 0
                for i in self.backColor_buffer:
                    if(i==1):
                        ii+=1
                self.count = ii

                if event != 0:
                    with self.threadLock: # wsData_pos and colored_buffer 
                        try:
                            start_idx = self.wsData_pos.index(frame_start_time)
                            fig_pos_x = self.wsData_pos_map[start_idx]
                            rect = Rectangle((fig_pos_x, self.ax_position.y0+self.ax_position.height*0.25), 
                                        self.ax_position.width/self.num_frames,
                                        self.ax_position.height/2,
                                        transform=self.ax.transAxes,
                                        color= 'r',
                                        alpha=0.3,
                                        zorder=1000)
                            self.ax.add_patch(rect)
                            self.colored_buffer.append(rect)
                        except err :
                            print(err)
                            pass
                            
    def plot_audio_in_buffer(self, frame):
        plot_data = np.array(self.audio_buffer)
        self.line.set_data(self.TIME, plot_data)
        if self.count>=3:
            self.line.set_color('red')
        else:
            self.line.set_color('blue')
        return [self.line] + self.colored_buffer
    
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
            threading.Thread(target=self.mark_audio_frame_by_audio_event).start()
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