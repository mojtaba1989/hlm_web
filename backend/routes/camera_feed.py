from fastapi import Request, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from picamera2 import Picamera2
import cv2
import threading
import asyncio
import time

from nodes.core import logger_ as logger
from nodes.constants import FPS_INVERSE
from nodes.utils import try_except, safe_call

router = APIRouter()

picam2 = None
frame_lock = threading.Lock()
current_frame = None
camera_thread = None
camera_running = False

def camera_loop():
    global current_frame, camera_running, picam2
    while camera_running:
        frame = picam2.capture_array()
        _, jpeg = cv2.imencode(".jpg", frame)
        with frame_lock:
            current_frame = jpeg.tobytes()
        time.sleep(FPS_INVERSE)

def start_camera():
    global picam2, camera_thread, camera_running
    time.sleep(0.3)
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    camera_running = True
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    logger.logger.info("Video Stream: Running")

def stop_camera():
    global picam2, camera_running, current_frame, camera_thread
    if not camera_running:
        return JSONResponse(content={"message": "Camera is not running!"}, status_code=200)

    camera_running = False
    time.sleep(0.2)
    safe_call(picam2.stop, label="close picam2")
    current_frame = None
    camera_thread = None
    picam2.close()
    picam2 = None
    time.sleep(15)
    logger.logger.info("Video Stream: Camera stopped")
    return JSONResponse(content={"message": "Camera stopped!"}, status_code=200)


# Async Streaming
async def mjpeg_generator(request: Request):
    global current_frame

    try:
        while camera_running:
            with frame_lock:
                if current_frame is None:
                    frame = None
                else:
                    frame = current_frame

            if frame is None:
                await asyncio.sleep(0.01)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + frame +
                b"\r\n"
            )
            await asyncio.sleep(FPS_INVERSE)
    finally:
        stop_camera()


@router.get("/stream")
async def stream(request: Request):
    start_camera()
    return StreamingResponse(
        mjpeg_generator(request),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/stop")
async def stop():
    stop_camera()
    return {"message": "Camera stopped!"}
