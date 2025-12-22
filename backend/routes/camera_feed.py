from fastapi.responses import StreamingResponse
from fastapi import APIRouter
import cv2, time
import utils

router = APIRouter()

CAMERA = cv2.VideoCapture(0)

def camera_loop():
    while True:
        ret, frame = CAMERA.read()
        if not ret:
            continue

        ts = time.time()
        frame_id = next(utils.frame_counter)
        with utils.lock:
            utils.latest_frame['frame_id'] = frame_id
            utils.latest_frame['ts'] = ts

        if utils.recording and utils.video_writer:
            utils.video_writer.write(frame)

        yield frame

def mjpeg_stream():
    for frame in camera_loop():
        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

@router.get("/stream")
def video_feed():
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )