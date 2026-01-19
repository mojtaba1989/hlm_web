import { useEffect, useState } from "react"

function WebcamView({ enabled }) {
  // useEffect(() => {
  //   if (enabled) return;
  //   const stopCameraFeed = async () => {
  //     await fetch("/api/camera_feed/stop");
  //   };
  //   stopCameraFeed();
  // }, [enabled]);

  return (
    <div>
      {enabled && (
        <img
          src="http://localhost:8000/api/camera_feed/stream"
          alt="Webcam"
          width={640}
          height={480}
          style={{ border: "1px solid black" }}
        />
      )}
    </div>
  );
}

export default WebcamView;
