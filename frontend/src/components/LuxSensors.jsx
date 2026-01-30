import React, { useEffect, useState} from "react";
import LuxSensorsView from "../views/LuxSensorsView";
import axios from "axios";

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
            const { s0, s1, s2, s3, s4, s5, s6, s7 } = JSON.parse(event.data);
            const now = Date.now();
            setData((prev)=>
                [...prev, {t: now, s0, s1, s2, s3, s4, s5, s6, s7}].filter((v) => now - v.t < 10000)
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