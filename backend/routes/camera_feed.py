from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter
import cv2, time
try:
    import utils
    TESTING = False
except ImportError:
    from pathlib import Path
    import sys
    PARENT_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(PARENT_DIR))
    import utils
    TESTING = True
import subprocess
import re
import threading

cam_lock = threading.Lock()

@utils.try_except
def get_usb_cameras():
    with cam_lock:
        cameras = {}
        current_cam = None
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line and not line.startswith("\t"):
                current_cam = line.strip().rstrip(":")
                cameras[current_cam] = []
            elif "/dev/video" in line and current_cam:
                idx = int(re.search(r"/dev/video(\d+)", line).group(1))
                cameras[current_cam].append(idx)

        cameras = {cam: {'id': int(min(indices))} for cam, indices in cameras.items() if not 'platform' in cam}
        if utils.safe_call(lambda:CAMERA.isOpened(), label="release camera before indexing", default=False):
            utils.core_.logger.logger.warning("Skipping camera check, camera is already opened")
            return cameras
        
        for cam in cameras.keys():
            cap = cv2.VideoCapture(int(cameras[cam]['id']))
            cameras[cam]['is_ok'] = cap.isOpened()
            cap.release()

        return cameras

@utils.try_except
def get_first_camera():
    cameras = get_usb_cameras()
    for cam in cameras.keys():
        if cameras.get(cam, {}).get('is_ok', True):
            return cameras[cam]['id']

    return None

router = APIRouter()

# Initialize camera with 1st camera
CURRENT_CAM_DEV_ID = get_first_camera()
utils.core_.logger.logger.error(f"Cam 0: {CURRENT_CAM_DEV_ID}")
if CURRENT_CAM_DEV_ID is not None:
    CAMERA = cv2.VideoCapture(CURRENT_CAM_DEV_ID)
else:
    CAMERA = None

def camera_loop():
    while True:
        ret, frame = CAMERA.read()
        if not ret:
            continue

        utils.core_.counter.update()
        if utils.core_.recording and utils.core_.video_writer:
            utils.core_.video_writer.write(frame)

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
    if CAMERA is None:
        return StreamingResponse(
            b"",
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/list")
def get_cameras():
    cameras = get_usb_cameras()
    return JSONResponse(cameras, status_code=200)

@router.get("/current")
def get_current_camera():
    return JSONResponse({"id": CURRENT_CAM_DEV_ID}, status_code=200)

@router.get("/change/{cam_id}") #TODO: Check what input is needed?
def change_camera(cam_id):
    global CURRENT_CAM_DEV_ID
    CURRENT_CAM_DEV_ID = cam_id
    utils.safe_call(CAMERA.release, label="release camera", default=None)
    CAMERA = cv2.VideoCapture(cam_id)

if TESTING:
    print(get_usb_cameras())
    