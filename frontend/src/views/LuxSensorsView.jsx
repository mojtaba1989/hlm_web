import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/* ---------- Stable color ---------- */
const hashColor = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = hash * 50 % 360;
  
  return `hsl(${hue}, 70%, 50%)`;
};


const LuxSensorsView = ({ data }) => {
  const hasData = data && data.length > 0;

  /* Dynamic signal names */
  const signalNames = useMemo(() => {
        if (!data || data.length === 0) return [];
        return Object.keys(data[data.length - 1]).filter((k) => k !== "t");
  }, [data]);


  /* Visibility state */
  const [visible, setVisible] = useState({});

  /* Sync when signals change */
  useEffect(() => {
    setVisible((prev) => {
      const next = { ...prev };
      signalNames.forEach((name) => {
        if (!(name in next)) next[name] = true;
      });
      return next;
    });
  }, [signalNames]);

  if (!hasData) {
    return <div style={{ height: 360 }}>Waiting for data…</div>;
  }

  return (
    <div style={{ width: "100%", height: 360 }}>
      {/* ---------- Control panel ---------- */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 12,
          padding: "6px 10px",
          borderBottom: "1px solid #ddd",
          background: "#fafafa",
          fontSize: 13,
        }}
      >
        {signalNames.map((name) => (
          <label
            key={name}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              cursor: "pointer",
              color: visible[name] ? "#000" : "#aaa",
            }}
          >
            <input
              type="checkbox"
              checked={!!visible[name]}
              onChange={() =>
                setVisible((v) => ({
                  ...v,
                  [name]: !v[name],
                }))
              }
            />
            <span style={{ color: hashColor(name) }}>●</span>
            {name}
          </label>
        ))}

        {/* Optional controls */}
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button
            onClick={() =>
              setVisible(
                Object.fromEntries(signalNames.map((n) => [n, true]))
              )
            }
          >
            All
          </button>
          <button
            onClick={() =>
              setVisible(
                Object.fromEntries(signalNames.map((n) => [n, false]))
              )
            }
          >
            None
          </button>
        </div>
      </div>

      {/* ---------- Chart ---------- */}
      <div style={{ width: "100%", height: 300, minHeight: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis
              dataKey="t"
              tickFormatter={(t) =>
                ((Date.now() - t) / 1000).toFixed(1)
              }
            />
            <YAxis />
            <Tooltip />
            <Legend />

            {signalNames.map((name) =>
              visible[name] ? (
                <Line
                  key={name}
                  dataKey={name}
                  name={name}
                  stroke={hashColor(name)}
                  dot={false}
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              ) : null
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default LuxSensorsView;
