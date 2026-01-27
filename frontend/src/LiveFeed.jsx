import React , {useState, useEffect} from "react";
import { useParams, useNavigate } from "react-router-dom";

import WebcamView from "./components/CameraFeed";
import LuxSensors from "./components/LuxSensors";
import LoggerFeed from "./components/LoggerFeed";

function LiveFeed() {
    const [streaming, setStreaming] = useState(false);
    const [recording, setRecording] = useState(false);
    const [disabled, setDisabled] = useState(false);
    const navigate = useNavigate();

    const toggleRecording = async () => {
        try {
            setDisabled(true);
            setStreaming(false);
            const url = recording
            ? "/api/record/stop"
            : "/api/record/start";

            await fetch(url);
            setRecording(!recording); 
            setDisabled(false);          
        } catch (err) {
            console.error("Recording toggle failed:", err);
        }
    };

    const toggleStreaming = async () => {
        try{
            setDisabled(true);
            setRecording(false);
            if (streaming) {
                await fetch("/api/camera_feed/stop", { method: "GET" });
            }
            setStreaming(!streaming);
            setDisabled(false);
        } catch (err) {
            console.error("Streaming toggle failed:", err);
        }
    };

    return (
        <div>
            <button
                onClick={toggleStreaming}
                disabled={disabled}
                style={{
                    backgroundColor: streaming ? "#b22222" : "#226d8b",
                    color: "white",
                    padding: "10px 16px",
                    fontWeight: "bold"
                }}>
                {streaming ? "Stop Live Feed" : "Start Live Feed"}
            </button>

            <button
                onClick={toggleRecording}
                disabled={disabled} 
                style={{
                    backgroundColor: recording ? "#b22222" : "#228b22",
                    color: "white",
                    padding: "10px 16px",
                    fontWeight: "bold"
                }}>
                {recording ? "Stop Recording" : "Start Recording"}
            </button>

            <button
                onClick={() => navigate("/records")}
                style={{
                    backgroundColor: "#226d8b",
                    color: "white",
                    padding: "10px 16px",
                    fontWeight: "bold"
                }}>
                Recordings
            </button>

            <h3>Status: {streaming ? "LIVE" : "STOPPED"}</h3>
            <LoggerFeed/>
            <WebcamView enabled={streaming}/>
            <LuxSensors enabled={streaming}/>
            
        </div>
    );

}

export default LiveFeed;