import numpy as np
from collections import deque
import threading, queue
import multiprocessing as mp
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from PIL import Image, ImageTk
import matplotlib as mpl
import time

class UI:
    def __init__(self, visual_que, event_que, audio_sampler, audio_detector, args):
        # user interface setting
        self.window_height = 1000
        self.window_width = int((1/2)*self.window_height) # H:W = 2:1
        self.bgColor = "#009ADC"
        self.eventColor = "red"
        
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
        
        self.fig = Figure(facecolor=self.bgColor)
        self.ax = self.fig.add_subplot(111)
        self.ax_position = self.ax.get_position()
        self.ax.set_ylim(-1.0, 1.0)
        self.ax.axis('off')
        self.TIME = np.linspace(0, self.buffer_size//args.sr, num=self.buffer_size)
        self.line, = self.ax.plot(self.TIME, np.array(self.audio_buffer), color='white')
         # wsData_pos and wsData_in_buffer_pos_map are for tracking group of same window size data in audio buffer
        self.wsData_pos = deque(np.zeros(self.num_windows), maxlen=self.num_windows)
        self.wsData_pos_map = np.linspace(0, self.ax_position.x1, num=self.num_windows, endpoint=False)
        
        ## User Interface widgets
        self.root = tk.Tk()
        self.root.title("Sound Event {}".format(args.pmp))
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        def on_closing_window():
            self.sampler.stop()
            self.detector.stop()
            self.root.destroy()
        self.root.protocol("WM_DELETE_WINDOW", on_closing_window)
        self.animate = None
        self.bgFrame = tk.Frame(self.root, background=self.bgColor)
        self.audio_graph = FigureCanvasTkAgg(self.fig, master=self.bgFrame)
        self.img = ImageTk.PhotoImage(Image.open("./img/baby_cry.png").convert("RGBA"))
        self.baby_cry_img = tk.Label(self.bgFrame, image=self.img, background=self.eventColor)
        # place the widgets on the window
        self.bgFrame.place(relwidth=1.0, relheight=1.0)
        self.audio_graph.get_tk_widget().place(relwidth=1.0, relheight=0.4)
        self.baby_cry_img.place(relx=0.25, rely= 0.5)
        self.start()
        self.root.mainloop()

    def fill_audio_buffer_with_que(self):
        while self.is_recording:
            while not self.visual_que.empty():
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
                print(self.count)
                            
    def plot_audio_in_buffer(self, frame):
        plot_data = np.array(self.audio_buffer)
        self.line.set_data(self.TIME, plot_data)
        # change UI color based on event 
        if self.count>=3:
            self.bgFrame.after(50, self.bgFrame.configure(background=self.eventColor))
            self.fig.set_facecolor(self.eventColor)
            self.baby_cry_img.place(relx=0.25, rely= 0.5)
        else:
            self.bgFrame.after(50, self.bgFrame.configure(background=self.bgColor))
            self.fig.set_facecolor(self.bgColor)
            self.baby_cry_img.place_forget()
        return [self.line, self.fig] + self.colored_buffer
    
    def pause_animation(self):
        while not self.visual_que.empty():
            pass
        self.animate.event_source.stop()

    def start(self):
        if self.is_recording==False:
            self.is_recording=True
            self.sampler.start()
            self.detector.start()
            threading.Thread(target=self.fill_audio_buffer_with_que, daemon=True).start()
            threading.Thread(target=self.mark_audio_frame_by_audio_event, daemon=True).start()
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
    
    def stop(self):
        if self.is_recording==True:
            threading.Thread(target=self.pause_animation).start()
            self.sampler.stop()
            self.detector.stop()
            self.is_recording=False