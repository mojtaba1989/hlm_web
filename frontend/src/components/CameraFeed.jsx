import { useEffect, useState } from "react"

function WebcamView({ enabled }) {
  const [src, setSrc] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  useEffect(() => {
    if (!enabled) {
      try {
          fetch(`${backendUrl}/api/camera_feed/stop`);
          setSrc(null);
      } catch (err) {
          console.error("Camera feed stop failed:", err);
      }
      return;
    }
    setSrc(`${backendUrl}/api/camera_feed/stream`);
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
