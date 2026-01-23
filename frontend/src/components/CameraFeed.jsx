import { useEffect, useState } from "react"

function WebcamView({ enabled }) {
  const [src, setSrc] = useState("");
  useEffect(() => {
    if (!enabled) {
      try {
          fetch("/api/camera_feed/stop");
          setSrc("");
      } catch (err) {
          console.error("Camera feed stop failed:", err);
      }
      return;
    }
    setSrc("/api/camera_feed/stream");
  }, [enabled]);

  return (
    <div>
        <img
          src={src}
          alt="Webcam"
          width={640}
          height={480}
          style={{ border: "1px solid black" }}
        />
    </div>
  );
}

export default WebcamView;
