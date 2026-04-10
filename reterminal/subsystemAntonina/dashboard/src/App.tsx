import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

// Allowed actuator IDs exposed by backend API.
type ActuatorId = "fan-1" | "led-1";

// One chart sample containing timestamp + both sensor values.
type ReadingPoint = {
  time: string;
  temperature: number;
  humidity: number;
};

// Base URL for backend API calls (proxied in dev by Vite).
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";
// Keep only the most recent points to avoid unbounded chart growth.
const MAX_POINTS = 60;

async function readSensor(sensorId: string): Promise<number> {
  // Request a sensor reading from the backend.
  const response = await fetch(`${API_BASE}/read/${sensorId}`);
  if (!response.ok) {
    // Surface network/API failures to UI error state.
    throw new Error(`Read failed for ${sensorId}`);
  }

  // Parse a numeric value from strings like "24.50 °C".
  const data = (await response.json()) as { reading: string };
  const parsed = Number.parseFloat(data.reading);
  if (Number.isNaN(parsed)) {
    // Guard against malformed backend response formats.
    throw new Error(`Invalid numeric reading for ${sensorId}`);
  }

  return parsed;
}

async function setActuatorState(actuatorId: ActuatorId, state: "on" | "off"): Promise<void> {
  // Send actuator control command to backend.
  const response = await fetch(`${API_BASE}/control/${actuatorId}?state=${state}`, {
    method: "PUT"
  });

  if (!response.ok) {
    // Surface command failures so user sees immediate feedback.
    throw new Error(`Control failed for ${actuatorId}`);
  }
}

function nowLabel(): string {
  // Format chart x-axis timestamp in HH:MM:SS.
  return new Date().toLocaleTimeString([], {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

export default function App() {
  // UI state for actuator toggles.
  const [fanOn, setFanOn] = useState(false);
  const [ledOn, setLedOn] = useState(false);
  const [busyActuator, setBusyActuator] = useState<ActuatorId | null>(null);
  const [controlError, setControlError] = useState<string>("");

  // UI state for time-series sensor plotting.
  const [points, setPoints] = useState<ReadingPoint[]>([]);
  const [sensorError, setSensorError] = useState<string>("");
  // Latest reading shown above the chart.
  const latest = useMemo(() => points[points.length - 1], [points]);

  useEffect(() => {
    // Prevent state updates after component unmount.
    let cancelled = false;

    const poll = async () => {
      try {
        // Poll temperature and humidity in parallel.
        const [temperature, humidity] = await Promise.all([
          readSensor("temperature-1"),
          readSensor("humidity-1")
        ]);

        if (cancelled) {
          // Ignore late async results after component unmount.
          return;
        }

        // Clear previous errors after successful poll.
        setSensorError("");
        setPoints((previous) => {
          // Append latest point and trim to rolling window.
          const next = [...previous, { time: nowLabel(), temperature, humidity }];
          return next.slice(-MAX_POINTS);
        });
      } catch (error) {
        if (!cancelled) {
          // Show polling errors while keeping previous chart points.
          setSensorError(error instanceof Error ? error.message : "Sensor polling failed");
        }
      }
    };

    // Run once immediately so UI is not empty for 2 seconds.
    poll();
    // Refresh readings every 2 seconds.
    const timer = window.setInterval(poll, 2000);

    return () => {
      // Mark effect as inactive to avoid setState-on-unmounted warnings.
      cancelled = true;
      // Stop background polling when leaving page.
      window.clearInterval(timer);
    };
  }, []);

  const onToggle = async (actuatorId: ActuatorId, current: boolean, setState: (next: boolean) => void) => {
    // Flip current toggle into the backend command string.
    const nextState = current ? "off" : "on";
    setBusyActuator(actuatorId);
    setControlError("");

    try {
      // Send command to backend first to keep UI in sync with hardware.
      await setActuatorState(actuatorId, nextState);
      // Only update local toggle if backend command succeeded.
      setState(!current);
    } catch (error) {
      // Show control errors close to actuator controls.
      setControlError(error instanceof Error ? error.message : "Failed to update actuator");
    } finally {
      // Re-enable buttons once request is done.
      setBusyActuator(null);
    }
  };

  return (
    // Page container with two cards: controls and live readings.
    <main>
      <h1>Device Dashboard</h1>

      {/* Actuator control panel. */}
      <section className="panel">
        <h2>Actuators</h2>
        <div className="controls">
          <div className="actuator">
            {/* Fan status text reflects local UI state. */}
            <span>Fan (fan-1): {fanOn ? "on" : "off"}</span>
            <button
              // Send toggle command for fan.
              onClick={() => onToggle("fan-1", fanOn, setFanOn)}
              // Disable while fan request is in flight.
              disabled={busyActuator === "fan-1"}
            >
              Toggle
            </button>
          </div>

          <div className="actuator">
            {/* LED status text reflects local UI state. */}
            <span>LED (led-1): {ledOn ? "on" : "off"}</span>
            <button
              // Send toggle command for LED.
              onClick={() => onToggle("led-1", ledOn, setLedOn)}
              // Disable while LED request is in flight.
              disabled={busyActuator === "led-1"}
            >
              Toggle
            </button>
          </div>
        </div>
        {/* Control error appears when PUT request fails. */}
        {controlError ? <p className="error">{controlError}</p> : null}
      </section>

      {/* Live readings panel with summary values + trend chart. */}
      <section className="panel">
        <h2>Live Sensor Readings</h2>
        <div className="readings">
          {/* Latest point summary for quick glance. */}
          <span>Temperature: {latest ? `${latest.temperature.toFixed(2)} °C` : "--"}</span>
          <span>Humidity: {latest ? `${latest.humidity.toFixed(2)} %` : "--"}</span>
        </div>

        {/* Responsive chart area for historical trend lines. */}
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <LineChart data={points}>
              {/* Background grid improves readability. */}
              <CartesianGrid strokeDasharray="3 3" />
              {/* Time axis for each sampled point. */}
              <XAxis dataKey="time" minTickGap={24} />
              {/* Shared numeric value axis for both lines. */}
              <YAxis />
              {/* Hover tooltip shows precise values at a point. */}
              <Tooltip />
              {/* Temperature trend line. */}
              <Line type="monotone" dataKey="temperature" name="Temperature (°C)" dot={false} />
              {/* Humidity trend line. */}
              <Line type="monotone" dataKey="humidity" name="Humidity (%)" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* Sensor error appears when GET polling fails. */}
        {sensorError ? <p className="error">{sensorError}</p> : null}
      </section>
    </main>
  );
}
