import { useEffect, useRef } from "react";

function WebcamView({ enabled }) {
  const videoRef = useRef();

  useEffect(() => {
    if (!enabled) return;

    const mediaSource = new MediaSource();
    videoRef.current.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener("sourceopen", () => {
      const buffer = mediaSource.addSourceBuffer(
        'video/mp4; codecs="avc1.42E01E"'
      );

      const ws = new WebSocket("ws://localhost:8000/api/camera_feed/ws");
      ws.binaryType = "arraybuffer";

      ws.onmessage = e => {
        buffer.appendBuffer(new Uint8Array(e.data));
      };

      return () => {
        ws.close();
        mediaSource.endOfStream();
      };
    });

  }, [enabled]);

  return <video ref={videoRef} autoPlay playsInline />;
}


export default WebcamView