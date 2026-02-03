import { useEffect, useState} from "react";
import LuxSensorsView from "../views/LuxSensorsView";

const LuxSensors = ({enabled}) => {
    const [data, setData] = useState([]);
    const backendUrl = import.meta.env.VITE_BACKEND_URL;

    useEffect(()=>{
        if (!enabled) {
            try {
                fetch(`${backendUrl}/api/lux_sensors/stop`);
            } catch (err) {
                console.error("LUX DAQ feed stop failed:", err);
            }
            return;
        }
        const eventSource = new EventSource(`${backendUrl}/api/lux_sensors/stream`);
        eventSource.onmessage = (event) => {
            const payload = JSON.parse(event.data);
            const now = Date.now();

            setData((prev) =>
                [
                    ...prev,
                    { t: now, ...payload}
                ].filter((v) => now - v.t < 10000)
            );
        };
        eventSource.onerror = (err) => {
            console.error("SSE error:", err);
            eventSource.close();
        };
        return () => eventSource.close();
    }, [enabled]);

    return(
        <LuxSensorsView
            data={data}
        />
    );
};

export default LuxSensors;