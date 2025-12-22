import React, { useEffect, useState} from "react";
import LuxSensorsView from "../views/LuxSensorsView";

const LuxSensors = ({enabled}) => {
    const [data, setData] = useState([]);

    useEffect(()=>{
        if (!enabled) return;
        const eventSource = new EventSource("/api/lux_sensors/stream");
        eventSource.onmessage = (event) => {
            const { s1, s2, s3, s4 } = JSON.parse(event.data);
            const now = Date.now();
            setData((prev)=>
                [...prev, {t: now, s1, s2, s3, s4}].filter((v) => now - v.t < 10000)
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