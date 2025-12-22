import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const COLORS = {
  s1: "#e41a1c", // red
  s2: "#377eb8", // blue
  s3: "#4daf4a", // green
  s4: "#984ea3"  // purple
};

const LABELS = {
  s1: "Sensor 1",
  s2: "Sensor 2",
  s3: "Sensor 3",
  s4: "Sensor 4"
};

const LuxSensorsView = (
    { data }
) => {
    return (
        <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
            {/* X axis: seconds ago */}
            <XAxis
                dataKey="t"
                tickFormatter={(t) => ((Date.now() - t) / 1000).toFixed(1)}
                label={{ value: "Seconds ago", position: "insideBottom" }}
            />

            {/* Y axis */}
            <YAxis
                domain={["auto", "auto"]}
                label={{ value: "Lux Value", angle: -90, position: "insideLeft" }}
            />

            {/* Tooltip */}
            <Tooltip
                labelFormatter={(t) =>
                `${((Date.now() - t) / 1000).toFixed(2)} sec ago`
                }
            />

            {/* Legend */}
            <Legend />

            {/* Lines */}
            {Object.keys(COLORS).map((key) => (
                <Line
                key={key}
                type="monotone"
                dataKey={key}
                name={LABELS[key]}     // 👈 legend label
                stroke={COLORS[key]}   // 👈 color
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
                position="right"
                />
            ))}
            </LineChart>
        </ResponsiveContainer>
        </div>
    );
};

export default LuxSensorsView;