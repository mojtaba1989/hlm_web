import { useEffect, useMemo, useState } from "react";
import { sensorStyles } from "../styles/sensor_style";
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
  return(
    <div style={sensorStyles.container}>
      {/* ---------- Control panel ---------- */}
      <div style={sensorStyles.controlPanel}>
        <div style={sensorStyles.checkboxGroup}>
          {signalNames.map((name) => (
            <label key={name} style={sensorStyles.label(visible[name])}>
              <input
                type="checkbox"
                style={sensorStyles.checkbox}
                checked={!!visible[name]}
                onChange={() =>
                  setVisible((v) => ({ ...v, [name]: !v[name] }))
                }
              />
              <span style={{ color: hashColor(name), fontSize: '18px' }}>●</span>
              {name}
            </label>
          ))}
        </div>

        <div style={sensorStyles.actionGroup}>
          <button onClick={() => setVisible(Object.fromEntries(signalNames.map(n => [n, true])))} style={sensorStyles.miniBtn}>All</button>
          <button onClick={() => setVisible(Object.fromEntries(signalNames.map(n => [n, false])))} style={sensorStyles.miniBtn}>None</button>
        </div>
      </div>

      {/* ---------- Chart Area ---------- */}
      <div style={sensorStyles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="t"
              stroke="#ffffff"
              tick={{ fontSize: 10 }}
              label={{ value: "Time",
                 offset: 0,
                 position: "insideBottom",
                 fontSize: 12,
                 fill: '#ffffff' }}
              tickFormatter={(t) => ((Date.now() - t) / 1000).toFixed(1) + "s"}
            />
            <YAxis 
              stroke="#ffffff"
              tick={{ fontSize: 10, fill: '#ffffff' }} 
              /* Increase width to give the rotated label room to breathe */
              width={60} 
              label={{ 
                value: "Lux",
                angle: -90, 
                // position: 'outLeft',
                /* Offset pulls the text away from the center of the axis */
                offset: 0,
                style: { 
                  textAnchor: 'middle', 
                  fill: '#ffffff', 
                  fontSize: 10,
                  fontWeight: '600'
                }
              }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333', fontSize: '12px' }}
              itemStyle={{ padding: '2px 0' }}
            />
            {signalNames.map((name) =>
              visible[name] ? (
                <Line
                  key={name}
                  dataKey={name}
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
