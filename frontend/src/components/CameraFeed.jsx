function WebcamView({enabled}) {
  return (
    <div>
        <h2>Live Webcam</h2>
        {enabled && (
            <img
            src="/api/camera_feed/stream"
            alt="Webcam"
            style={{ width: "640px", border: "1px solid black" }}
            />
        )}
    </div>
  );
}

export default WebcamView