import numpy as np
from collections import deque
import argparse
import queue, threading
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
from SoundSampler import Sampler
# from EventDetect import Detector

parser = argparse.ArgumentParser()
parser.add_argument('--sr', default =44100, type=int, help='sample rate')
parser.add_argument('--ws', default=2048, type=int, help='windows size')
parser.add_argument('--hs',  default=492,   type=int, help='hop size')
parser.add_argument('--mel', default=128,   type=int, help='mel bands')
parser.add_argument('--rd', default=5,    type=int, help='recording duration')
args = parser.parse_args()

audio_visual_que = queue.Queue() # audio data container for visualization
audio_detect_que = queue.Queue() # audio data container for event detection
sampler = Sampler(audio_detect_que, audio_visual_que, args) # sampling audio
# detector = Detector(audio_detect_que, args) # detecting audio event


'''
UI
'''
is_recording = False
buffer_size = (args.sr//args.ws)*args.ws*args.rd*5
audio_buffer = deque(np.zeros(buffer_size), maxlen=buffer_size)
def fill_audio_buffer_with_que():
    global is_recording, audio_visual_que, audio_buffer, buffer_size
    while is_recording:
        while not audio_visual_que.empty():
            data = audio_visual_que.get()
            assert len(audio_buffer) == buffer_size
            audio_buffer.extendleft(data)
    print("exit fill_audio_buffer_with_que()")

def plot_audio_in_buffer():
    global ax, audio_graph, audio_buffer, buffer_size, audio_visual_que, is_recording            
    while is_recording:
        TIME = np.linspace(0, buffer_size//args.sr, num=buffer_size)
        while not audio_visual_que.empty():
            plot_data = np.array(audio_buffer)
            ax.cla()
            ax.plot(TIME, plot_data)
            audio_graph.draw()
    print("exit plot_audio_in_buffer()")

def press_start():
    global is_recording, audio_buffer_thread
    if is_recording==False:
        print('start button')
        is_recording=True
        sampler.start()
        # detector.start()
        threading.Thread(target=fill_audio_buffer_with_que).start()
        threading.Thread(target=plot_audio_in_buffer).start()
        
def press_pause():
    global is_recording, audio_buffer_thread
    if is_recording==True:
        print('pause button')
        sampler.stop()
        # detector.stop()
        is_recording=False    
            
window_width = 1000
window_height = int((1/2)*window_width) ## W:H = 2:1
root = tk.Tk() # window
root.title("Sound Event")
root.geometry("{}x{}".format(window_width, window_height))

# initiate the widgets
fig = Figure()
ax = fig.add_subplot(111)
audio_graph = FigureCanvasTkAgg(fig, master=root)
event_frame = tk.Frame(root) # showing detected event label
start_button = tk.Button(root, text="start", command=press_start)
stop_button = tk.Button(root, text="pause", command=press_pause)

# place the widgets on the window
audio_graph.get_tk_widget().place(relwidth=1.0, relheight=0.75)
event_frame.place(relwidth=1.0, relheight=0.1, relx=0.0, rely=0.75, anchor="nw")
start_button.place(relwidth=0.5, relheight=0.15, relx=0.5, rely=0.85, anchor="nw")
stop_button.place(relwidth=0.5, relheight=0.15, relx=0.0, rely=0.85, anchor="nw")

root.mainloop()