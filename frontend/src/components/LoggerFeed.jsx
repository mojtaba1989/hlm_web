import { useEffect, useRef, useState } from "react";

// Updated Levels to include DEBUG
const LEVELS = {
  DEBUG: 1,
  INFO: 2,
  WARN: 3,
  ERROR: 4,
  ALL: 0
};

function LoggerFeed() {
  const [logs, setLogs] = useState([]);
  const [minLevel, setMinLevel] = useState(LEVELS.ALL);
  const bottomRef = useRef(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const parseLevel = (line) => {
    const upper = line.toUpperCase();
    // 1. Check for ERROR / FAIL
    if (upper.includes("ERROR") || upper.includes("FAIL") || upper.includes("CRITICAL")) return LEVELS.ERROR;
    // 2. Check for WARNING / WARN
    if (upper.includes("WARNING") || upper.includes("WARN")) return LEVELS.WARN;
    // 3. Check for DEBUG
    if (upper.includes("DEBUG")) return LEVELS.DEBUG;
    // 4. Default to INFO (since most lines are INFO: or - INFO -)
    return LEVELS.INFO;
  };

  const getLogColor = (level) => {
    switch (level) {
      case LEVELS.ERROR: return "#ff4757"; // Bright Red
      case LEVELS.WARN:  return "#ffa502"; // Warning Orange
      case LEVELS.INFO:  return "#2ed573"; // Success Green
      case LEVELS.DEBUG: return "#56ccf2"; // Debug Blue
      default: return "#9ca3af";           // Muted Grey
    }
  };

  useEffect(() => {
    const evtSource = new EventSource(`${backendUrl}/api/logger/logs`);
    evtSource.onmessage = (event) => {
      const line = event.data;
      const level = parseLevel(line);
      setLogs((prev) => [...prev, { text: line, level }]);
    };
    evtSource.onerror = () => evtSource.close();
    return () => evtSource.close();
  }, [backendUrl]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs, minLevel]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#0f0f0f" }}>
      {/* Control Bar */}
      <div style={{ 
        padding: "6px 12px", background: "#1a1a1a", borderBottom: "1px solid #333",
        display: "flex", alignItems: "center", justifyContent: "space-between", flexShrink: 0 
      }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <span style={{ fontSize: "10px", color: "#666", fontWeight: "bold" }}>THRESHOLD</span>
          <select 
            value={minLevel} 
            onChange={(e) => setMinLevel(Number(e.target.value))}
            style={{ background: "#000", color: "#eee", border: "1px solid #444", fontSize: "11px", borderRadius: "4px" }}
          >
            <option value={LEVELS.ALL}>ALL</option>
            <option value={LEVELS.DEBUG}>DEBUG+</option>
            <option value={LEVELS.INFO}>INFO+</option>
            <option value={LEVELS.WARN}>WARN+</option>
            <option value={LEVELS.ERROR}>ERROR ONLY</option>
          </select>
        </div>
        <button onClick={() => setLogs([])} style={{ background: "transparent", border: "1px solid #444", color: "#555", fontSize: "10px", padding: "2px 8px", cursor: "pointer" }}>
          CLEAR
        </button>
      </div>

      {/* Log Body */}
      <div style={{
        flex: 1, overflowY: "auto", padding: "10px",
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: "11px", lineHeight: "1.6", whiteSpace: "pre-wrap"
      }}>
        {logs
          .filter(log => log.level >= minLevel)
          .map((log, idx) => (
            <div key={idx} style={{ color: getLogColor(log.level), marginBottom: "2px", display: "flex", gap: "12px" }}>
              <span style={{ opacity: 0.15, minWidth: "30px", userSelect: "none" }}>{idx + 1}</span>
              <span style={{ flex: 1 }}>{log.text}</span>
            </div>
          ))
        }
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export default LoggerFeed;