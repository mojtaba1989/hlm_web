import { useState } from "react";
import "./styles/config.css";

const configData = {
  camera: {
    ENABLED: [true, true],
    Device_ID: ["/dev/video0", false],
    Resolution: [[1280, 720], false],
    Framerate: [30, false],
    TCP_STREAM: [false, true],
    TCP_IP: ["127.0.0.1", false],
    TCP_PORT: [5556, false],
    Streaming_fps: [30, true],
  },
  DAQ: {
    ENABLED: [true, true],
    IP: ["10.0.0.105", false],
    PORT: [5555, false],
    Streaming_rate: [10, true],
    Frequency: [1612.8, false],
    Samples_per_packet: [16, false],
    Channel_map: {
      ch1: [0, true],
      ch2: [1, true],
      ch3: [2, true],
      ch4: [3, true],
    },
  },
};

export default function ConfigEditor() {
  const [config, setConfig] = useState(configData);

  const updateValue = (path, newValue) => {
    const updated = structuredClone(config);
    let ref = updated;

    for (let i = 0; i < path.length - 1; i++) {
      ref = ref[path[i]];
    }

    ref[path.at(-1)][0] = newValue;
    setConfig(updated);
  };

  const renderNode = (node, path = []) => {
    if (!node || typeof node !== "object") return null;

    return Object.entries(node).map(([key, value]) => {
      // Leaf node: [value, editable]
      if (Array.isArray(value) && value.length === 2) {
        const [val, editable] = value;
        if (!editable) return null;

        return (
          <div
            key={path.join(".") + key}
            className="flex items-center justify-between gap-4 py-1"
          >
            <span className="text-sm text-gray-300">{key}</span>
            {renderInput(val, (v) => updateValue([...path, key], v))}
          </div>
        );
      }

      // Nested section
      return (
        <div
          key={path.join(".") + key}
          className="border border-gray-700 rounded-lg p-4 mt-4"
        >
          <h3 className="text-sm font-semibold text-blue-400 mb-2">
            {key}
          </h3>
          <div className="pl-2 space-y-2">
            {renderNode(value, [...path, key])}
          </div>
        </div>
      );
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-xl font-bold">System Configuration</h1>

        {renderNode(config)}

        <div className="mt-6">
          <h2 className="text-sm text-gray-400 mb-2">Live JSON</h2>
          <pre className="bg-black text-green-400 p-3 rounded text-xs overflow-auto">
            {JSON.stringify(config, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}

/* ================= INPUT RENDERER ================= */

function renderInput(value, onChange) {
  if (typeof value === "boolean") {
    return (
      <input
        type="checkbox"
        checked={value}
        onChange={(e) => onChange(e.target.checked)}
        className="w-5 h-5 accent-blue-500"
      />
    );
  }

  if (typeof value === "number") {
    return (
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-24 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
      />
    );
  }

  if (typeof value === "string") {
    return (
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-48 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
      />
    );
  }

  // Arrays (like resolution)
  if (Array.isArray(value)) {
    return (
      <span className="text-gray-400 text-sm">
        {value.join(" × ")}
      </span>
    );
  }

  return null;
}
