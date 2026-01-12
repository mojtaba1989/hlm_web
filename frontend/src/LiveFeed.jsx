import React , {useState, useEffect} from "react";
import { useParams, useNavigate } from "react-router-dom";

import WebcamView from "./components/CameraFeed";
import LuxSensors from "./components/LuxSensors";

function LiveFeed() {
    const [streaming, setStreaming] = useState(false);
    const [recording, setRecording] = useState(false);
    const [enabled, setEnabled] = useState(false);

    const toggleRecording = async () => {
        try {
            const url = recording
            ? "/api/record/stop"
            : "/api/record/start";

            await fetch(url, { method: "POST" });

            setRecording(!recording);

            // Optional: stop live view while recording
            setStreaming(false);
        } catch (err) {
            console.error("Recording toggle failed:", err);
        }
    };

    // const toggleStreaming = async () => {
    //     try{
    //         const cam_url = streaming
    //         ? "/api/camera_feed/stop"
    //         : "/api/camera_feed/start";

    //         await fetch(cam_url, { method: "POST"});
    //         setStreaming(!streaming);

    //         setRecording(false);
    //     } catch (err) {
    //         console.error("Streaming toggle failed:", err);
    //     }
    // };

    return (
        <div>
            <button onClick={() => setEnabled((v) => !v)}>
                {streaming ? "Stop Live Feed" : "Start Live Feed"}
            </button>

            <button
                onClick={toggleRecording}
                style={{
                    backgroundColor: recording ? "#b22222" : "#228b22",
                    color: "white",
                    padding: "10px 16px",
                    fontWeight: "bold"
                }}>
                {recording ? "Stop Recording" : "Start Recording"}
            </button>

            <h3>Status: {streaming ? "LIVE" : "STOPPED"}</h3>
            <WebcamView enabled={enabled} />
            <LuxSensors enabled={enabled}/>
        </div>
    );

}

export default LiveFeed;