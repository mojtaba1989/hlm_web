import React , {useState, useEffect} from "react";
import { useParams, useNavigate } from "react-router-dom";

import WebcamView from "./components/CameraFeed";
import LuxSensors from "./components/LuxSensors";

function LiveFeed() {
    const [enabled, setEnabled] = useState(false);
    const [recording, setRecording] = useState(false);

    const toggleRecording = async () => {
        try {
            const url = recording
            ? "/api/record/stop"
            : "/api/record/start";

            await fetch(url, { method: "POST" });

            setRecording(!recording);

            // Optional: stop live view while recording
            setEnabled(false);
        } catch (err) {
            console.error("Recording toggle failed:", err);
        }
    };

    return (
        <div>
            <button onClick={() => setEnabled((v) => !v)}>
                {enabled ? "Stop Live Feed" : "Start Live Feed"}
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

            <h3>Status: {enabled ? "LIVE" : "STOPPED"}</h3>
            <WebcamView enabled={enabled} />
            <LuxSensors enabled={enabled}/>
        </div>
    );

}

export default LiveFeed;