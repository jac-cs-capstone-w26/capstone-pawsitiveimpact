import React, { useEffect, useState } from "react";
import { LineChart } from "@mui/x-charts";

interface SensorReading {
  time: string;
  temperature: number;
  humidity: number;
}

const SensorGraph: React.FC = () => {
  const [data, setData] = useState<SensorReading[]>([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const tempRes = await fetch("http://172.20.10.2:8000/read/temp");
        const tempData = await tempRes.json(); // e.g. {"value": 24.3°C}

        const humRes = await fetch("http://172.20.10.2:8000/read/humidity");
        const humData = await humRes.json(); // e.g. {"value": 52%}

        setData((prev) => [
          ...prev.slice(-29), // keep last 30 readings
          {
            time: new Date().toLocaleTimeString(),
            temperature: parseFloat(tempData.value),
            humidity: parseFloat(humData.value),
          },
        ]);
      } catch (err) {
        console.error("Error fetching sensor data:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

return (
  <div className="w-full h-[300px] bg-gray-50 rounded-xl p-4">
    <LineChart
      series={[
        {
          data: data.map((d) => d.temperature),
          label: "Temperature (°C)",
        },
        {
          data: data.map((d) => d.humidity),
          label: "Humidity (%)",
        },
      ]}
      xAxis={[
        {
          data: data.map((d) => d.time),
          scaleType: "point",
        },
      ]}
      height={250}
    />
  </div>
);
};

export default SensorGraph;