import {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import { homeStyles } from "./styles/home_style";

import WebcamView from "./components/CameraFeed";
import LuxSensors from "./components/LuxSensors";
import LoggerFeed from "./components/LoggerFeed";

export default function HomePage() {
    const [streaming, setStreaming] = useState(false);
    const [recording, setRecording] = useState(false);
    const [disabled, setDisabled] = useState(false);
    const [testCatalog, setTestCatalog] = useState([]);
    const navigate = useNavigate();
    const backendUrl = import.meta.env.VITE_BACKEND_URL;

    const toggleRecording = async () => {
        try {
            setDisabled(true);
            setStreaming(false);
            const url = recording
            ? `${backendUrl}/api/record/stop`
            : `${backendUrl}/api/record/start`;

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
                await fetch(`${backendUrl}/api/camera_feed/stop`, { method: "GET" });
            }
            setStreaming(!streaming);
            setDisabled(false);
        } catch (err) {
            console.error("Streaming toggle failed:", err);
        }
    };

    useEffect(() => {
        fetch(`${backendUrl}/api/test_catalog`, { method: "GET" }).
        then(res => res.json()).
        then(data => setTestCatalog(data.scenarios)).
        catch(err => console.error("Failed to fetch test catalog:", err));
    }, []);

    return(
        <div style={homeStyles.page}>
            {/* Header / Top Control Bar */}
            <header style={homeStyles.header}>
                <div style={homeStyles.brand}>
                <h2 style={{ margin: 0, fontSize: "1.2rem" }}>Head Light Control Suite</h2>
                <span style={homeStyles.liveIndicator(streaming)}>
                    {streaming ? "● LIVE" : "○ OFFLINE"}
                </span>
                </div>

                <div style={homeStyles.buttonGroup}>
                <button onClick={toggleStreaming} disabled={disabled} style={homeStyles.actionBtn(streaming, "#0984e3")}>
                    {streaming ? "Stop Live Feed" : "Start Live Feed"}
                </button>
                <button onClick={toggleRecording} disabled={disabled} style={homeStyles.actionBtn(recording, "#27ae60")}>
                    {recording ? "Stop Recording" : "Start Recording"}
                </button>
                <button onClick={() => navigate("/records")} style={homeStyles.navBtn}>
                    Browse Recordings
                </button>
                <button onClick={() => navigate("/config")} style={homeStyles.navBtn}>
                    Configuration
                </button>
                </div>
            </header>

            {/* Main Fixed Grid */}
            <main style={homeStyles.grid}>
              {/* TOP LEFT: Camera */}
              <section style={{ ...homeStyles.panel, gridArea: "video" }}>
                <div style={homeStyles.panelHeader}>Live Stream (640x480)</div>
                <div style={homeStyles.viewport}>
                    <div style={homeStyles.videoWrapper}>
                        <WebcamView enabled={streaming} />
                    </div>
                </div>
              </section>

              {/* TOP RIGHT: Test Config Placeholder */}
              <section style={{ ...homeStyles.panel, gridArea: "test" }}>
                <div style={homeStyles.panelHeader}>Test Configuration</div>
                <p style={{ fontWeight: 'bold', color: '#888' }}>Test Catalog</p>
                <select 
                    onChange={(e) => console.log(e.target.value)} 
                    style={{ padding: '8px', borderRadius: '4px' }}
                    >
                    <option value="">Select a test...</option>
                    {Array.isArray(testCatalog) && testCatalog.map((desc, index) => (
                        <option key={index} value={desc}>
                        {desc}
                        </option>
                    ))}
                </select>
                <div style={{ ...homeStyles.placeholder, flex: 1, overflowY: 'auto' }}>
                    
                </div>
              </section>

              {/* BOTTOM LEFT: Sensors */}
              <section style={{ ...homeStyles.panel, gridArea: "sensors" }}>
                <div style={homeStyles.panelHeader}>Sensor Telemetry</div>
                <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
                <LuxSensors enabled={streaming} />
                </div>
              </section>

              {/* BOTTOM RIGHT: Logs */}
              <section style={{ ...homeStyles.panel, gridArea: "logs" }}>
                <div style={homeStyles.panelHeader}>System Logs</div>
                <div style={{ flex: 1, overflowY: 'auto' }}>
                <LoggerFeed />
                </div>
              </section>
            </main>

            <footer style={homeStyles.footer}>
              <span style={{ color: "#2f80ed", fontWeight: "800" }}>ACM</span>
              <span style={{ margin: "0 8px", color: "#ffffff" }}>|</span>
              <span style={{ color: "#ffffff" }}>
                  Powered by <strong style={{ color: "#ffcc00", fontWeight: "700" }}>MTU</strong>
              </span>
              <span style={{ marginLeft: "8px", color: "#ffffff" }}>© 2026</span>
            </footer>
        </div>

    );
}