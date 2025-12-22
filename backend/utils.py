import itertools
import threading

frame_counter = itertools.count()


FPS_INVERSE = 1/30
SPS_INVERSE = 1/100

latest_frame = {
    "frame_id": None,
    "ts": None
}

recording = False
video_writer = None
csv_file = None
writer = None

lock = threading.Lock()

