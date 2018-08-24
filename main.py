import argparse
import queue
import multiprocessing as mp
from SoundSampler import Sampler
from soundEventUI import UI
from EventDetect import Detector

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sr', default =16000, type=int, help='sample rate')
    parser.add_argument('--ws', default=1000, type=int, help='windows size')
    parser.add_argument('--hs',  default=492,   type=int, help='hop size')
    parser.add_argument('--mel', default=128,   type=int, help='mel bands')
    parser.add_argument('--rd', default=5,    type=int, help='recording duration')
    parser.add_argument('--frame', default=3, type=int, help='number of recording duration showing on UI')
    args = parser.parse_args()

    audio_visual_que = queue.Queue() # audio data container for visualization
    audio_detect_que = mp.Queue() # audio data container for event detection
    audio_event_que = mp.Queue() # container for event detecting results
    sampler = Sampler(audio_detect_que, audio_visual_que, args) # sampling audio
    detector = Detector(audio_detect_que, audio_event_que, args) # detecting audio event
    ui = UI(audio_visual_que, audio_event_que, sampler, detector, args)

if __name__ == '__main__':
    mp.set_start_method('fork')
    main()
