from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
import threading
import time

from nodes.core import logger_ as logger
from nodes.core import config_ as config
from nodes.camera_ import list_real_cameras

router = APIRouter()

class CameraStream:
    def __init__(self):
        self.cam = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if not config.get('camera.enabled') or not config.get('camera.device_id'):
            logger.logger.warning("Camera Stream: Camera not enabled")
            return
        
        with self.lock:
            if self.running:
                logger.logger.warning("Camera Stream: Camera already running")
                return
            
            self.cam = cv2.VideoCapture(config.get('camera.device_id'),
                                         cv2.CAP_V4L2)
            wh = config.get('camera.STREAMING_RESOLUTION')
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, wh[0])
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, wh[1])
            self.cam.set(cv2.CAP_PROP_FPS, config.get('camera.STREAMING_FRAMERATE'))
            self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.running = True
            for _ in range(5):
                ret, _ = self.cam.read()
                if not ret:
                    break

            time.sleep(0.05)
            logger.logger.info("Camera Stream: Camera started")

    def stop(self):
        with self.lock:
            self.running = False
            if self.cam:
                self.cam.release()
                self.cam = None
                logger.logger.info("Camera Stream: Camera stopped")

    def generate_frames(self):
        try:
            for _ in range(2):
                if not self.running:
                    return
                self.cam.read()

            while True:
                if not self.running or not self.cam:
                    break

                success, frame = self.cam.read()
                if not success:
                    break

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes +
                    b"\r\n"
                )

                time.sleep(1 / config.get('camera.STREAMING_FRAMERATE'))
        finally:
            self.stop()


CAM = CameraStream()

@router.get("/stream")
def video_feed():
    CAM.start()
    time.sleep(0.1)
    return StreamingResponse(
        CAM.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/stop")
def stop():
    CAM.stop()
    return {"message": "Camera stopped!"}

@router.get("/cameras")
async def list_cameras():
    return {"cameras": list_real_cameras()}