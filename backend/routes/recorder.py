from fastapi import APIRouter
import utils
import cv2, csv

router = APIRouter()

@router.post("/start")
def start_record():
    print("Starting recording...")
    utils.recording = True
    utils.video_writer = cv2.VideoWriter(
        "recording.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        30,
        (640, 480)
    )

    utils.csv_file = open("recording.csv", "w", newline="")
    utils.writer = csv.DictWriter(utils.csv_file, fieldnames=["ts", "frame_id", "s1", "s2", "s3", "s4"])
    utils.writer.writeheader()
    
    return {"status": "recording started"}

@router.post("/stop")
def stop_record():
    print("Stopping recording...")
    utils.recording = False
    if utils.video_writer:
        utils.video_writer.release()
        utils.video_writer = None

    if utils.csv_file:
        utils.csv_file.close()
        utils.csv_file = None
        utils.writer = None
    return {"status": "recording stopped"}