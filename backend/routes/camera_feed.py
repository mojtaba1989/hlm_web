from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter, Request, WebSocket
import cv2, time
import asyncio
from contextlib import asynccontextmanager
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

def start_encoder(width, height, fps):
    return subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel", "error",
            "-f", "rawvideo",
            "-pix_fmt", "yuv420p",
            "-s", f"{width}x{height}",
            "-r", str(fps),
            "-i", "-",

            "-an",
            "-c:v", "h264_v4l2m2m",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov+default_base_moof",
            "-"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        bufsize=0
    )

router = APIRouter()
@router.websocket("/ws")
async def camera_ws(ws: WebSocket):
    await ws.accept()

    cap = cv2.VideoCapture(0)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = 30

    ffmpeg = start_encoder(width, height, fps)

    async def ffmpeg_reader():
        while True:
            data = ffmpeg.stdout.read(4096)
            if not data:
                break
            await ws.send_bytes(data)

    reader_task = asyncio.create_task(ffmpeg_reader())

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
            ffmpeg.stdin.write(yuv.tobytes())
            await asyncio.sleep(1 / fps)

    except Exception:
        pass

    finally:
        reader_task.cancel()
        cap.release()
        ffmpeg.kill()


# cam_lock = threading.Lock()
# CAMERA = None
# STREAM = None
# CURRENT_CAM_DEV_ID = None

# @asynccontextmanager
# async def camera_lifsspan(app):
#     global CAMERA, CURRENT_CAM_DEV_ID
#     utils.core_.logger.logger.error("Camera router starting")

#     CURRENT_CAM_DEV_ID = get_first_camera()
#     utils.core_.logger.logger.error(f"Detected camera: {CURRENT_CAM_DEV_ID}")

#     yield   # API is now live

#     utils.core_.logger.logger.info("Camera router shutting down")

#     if CAMERA:
#         CAMERA.release()
#         CAMERA = None
#         utils.core_.logger.logger.info("Camera released")

# @utils.try_except
# def get_usb_cameras():
#     with cam_lock:
#         cameras = {}
#         current_cam = None
#         result = subprocess.run(
#             ["v4l2-ctl", "--list-devices"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             check=True
#         )
#         for line in result.stdout.splitlines():
#             if line and not line.startswith("\t"):
#                 current_cam = line.strip().rstrip(":")
#                 cameras[current_cam] = []
#             elif "/dev/video" in line and current_cam:
#                 idx = int(re.search(r"/dev/video(\d+)", line).group(1))
#                 cameras[current_cam].append(idx)

#         cameras = {cam: {'id': int(min(indices))} for cam, indices in cameras.items() if not 'platform' in cam}
#         if utils.safe_call(lambda:CAMERA.isOpened(), label="release camera before indexing", default=False):
#             utils.core_.logger.logger.warning("Skipping camera check, camera is already opened")
#             return cameras
        
#         for cam in cameras.keys():
#             cap = cv2.VideoCapture(int(cameras[cam]['id']))
#             cameras[cam]['is_ok'] = cap.isOpened()
#             cap.release()

#         return cameras

# @utils.try_except
# def get_first_camera():
#     cameras = get_usb_cameras()
#     for cam in cameras.keys():
#         if cameras.get(cam, {}).get('is_ok', True):
#             return cameras[cam]['id']

#     return None

# def camera_loop():
#     while True:
#         ret, frame = CAMERA.read()
#         if not ret:
#             continue

#         utils.core_.counter.update()
#         if utils.core_.recording and utils.core_.video_writer:
#             utils.core_.video_writer.write(frame)
#         yield frame

# def get_frame():
#     if CAMERA is None:
#         return b""
    
#     ret, frame = CAMERA.read()
#     if not ret:
#         return b""
    
#     _, buffer = cv2.imencode(".jpg", frame)
#     return (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n\r\n" +
#             buffer.tobytes() +
#             b"\r\n"
#         )

# def mjpeg_stream():
#     for frame in camera_loop():
#         _, buffer = cv2.imencode(".jpg", frame)
#         yield (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n\r\n" +
#             buffer.tobytes() +
#             b"\r\n"
#         )
#         time.sleep(utils.FPS_INVERSE)

# # Initialize camera with 1st camera
# router = APIRouter(lifespan=camera_lifsspan)
# last_sent = time.time()
# @router.get("/stream")
# async def stream(request: Request):
#     global CAMERA, CURRENT_CAM_DEV_ID
#     if CAMERA is not None:
#         utils.core_.logger.logger.error("Camera is busy")
#         return StreamingResponse(
#             b"",
#             media_type="multipart/x-mixed-replace; boundary=frame"
#         )

#     CAMERA = cv2.VideoCapture(CURRENT_CAM_DEV_ID)
#     utils.core_.logger.logger.info(f"Camera {CURRENT_CAM_DEV_ID} is open? {CAMERA.isOpened()}")
#     if not CAMERA.isOpened():
#         CAMERA = None
#         return StreamingResponse(
#             b"",
#             media_type="multipart/x-mixed-replace; boundary=frame"
#         )
    
#     async def mjpeg_stream():
#         try:
#             while True:
#                 if await request.is_disconnected():
#                     utils.core_.logger.logger.error("Client disconnected - stop streaming")
#                     break

#                 yield get_frame()
#                 last_sent = time.time()
#                 if time.time() - last_sent > 1:
#                     utils.core_.logger.logger.error("Client disconnected - stop streaming")
#                     break

                
#                 await asyncio.sleep(utils.FPS_INVERSE)
#         finally:
#             CAMERA.release()
#             CAMERA = None
#             utils.core_.logger.logger.info('Camera released')
    
#     return StreamingResponse(
#         mjpeg_stream(),
#         media_type="multipart/x-mixed-replace; boundary=frame"
#     )


# @router.get("/list")
# def get_cameras():
#     cameras = get_usb_cameras()
#     return JSONResponse(cameras, status_code=200)

# @router.get("/current")
# def get_current_camera():
#     return JSONResponse({"id": CURRENT_CAM_DEV_ID}, status_code=200)

# @router.get("/change/{cam_id}") #TODO: Check what input is needed?
# def change_camera(cam_id):
#     global CURRENT_CAM_DEV_ID
#     CURRENT_CAM_DEV_ID = cam_id
#     utils.safe_call(CAMERA.release, label="release camera", default=None)
#     CAMERA = cv2.VideoCapture(cam_id)

# if TESTING:
#     print(get_usb_cameras())
    