import React, { useEffect, useRef, useState } from "react";

function LoggerFeed() {
  const [logs, setLogs] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    const evtSource = new EventSource("/api/logger/logs");

    evtSource.onmessage = (event) => {
      setLogs((prev) => [...prev, event.data]);
    };

    evtSource.onerror = (err) => {
      console.error("SSE error:", err);
      evtSource.close();
    };

    return () => {
      evtSource.close();
    };
  }, []);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div
      style={{
        height: "200px",          // fixed height
        overflowY: "auto",       // vertical scroll
        border: "1px solid #ccc",
        padding: "8px",
        fontFamily: "monospace",
        fontSize: "12px",
        backgroundColor: "#ffffff",
        color: "rgb(255, 0, 0)",
        whiteSpace: "pre-wrap"
      }}
    >
      {logs.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

export default LoggerFeed;
