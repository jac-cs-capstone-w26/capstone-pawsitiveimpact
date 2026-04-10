// Full dashboard for the reTerminal Control Center.
// - Polls temperature and humidity every 1.5 seconds via GET requests
// - Displays a live line chart of the last 20 readings using Recharts
// - Toggle buttons send PUT requests to turn the LED and Fan on/off

import { useEffect, useRef, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

// One data point on the chart
interface DataPoint {
  time: string;       // e.g. "12:34:05"
  temperature: number;
  humidity: number;
}

// What the API returns for PUT /control/{id}
interface ActuatorResponse {
  actuator_id: string;
  state: string;
}

// ---------------------------------------------------------------------------
// Helper: call the API
// ---------------------------------------------------------------------------

// Read a sensor and return the numeric value parsed from the string
async function fetchSensor(sensorId: string): Promise<number> {
  const res = await fetch(`/read/${sensorId}`);
  if (!res.ok) throw new Error(`sensor ${sensorId} returned ${res.status}`);
  const data = await res.json();
  // The reading looks like "23.45 °C" or "35.10 %" — grab the number part
  return parseFloat(data.reading);
}

// Send a PUT request to turn an actuator on or off
async function setActuator(
  actuatorId: string,
  state: "on" | "off"
): Promise<ActuatorResponse> {
  const res = await fetch(`/control/${actuatorId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
  if (!res.ok) throw new Error(`actuator ${actuatorId} returned ${res.status}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Sub-component: a simple on/off toggle button
// ---------------------------------------------------------------------------

function ToggleButton({
  label,
  actuatorId,
}: {
  label: string;
  actuatorId: string;
}) {
  // Track whether this actuator is currently on or off
  const [isOn, setIsOn] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setBusy(true);
    setError(null);
    const nextState = isOn ? "off" : "on";
    try {
      const result = await setActuator(actuatorId, nextState);
      // Use the state the server confirms, not just what we asked for
      setIsOn(result.state === "on");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>{label}</h2>
      <button
        onClick={handleClick}
        disabled={busy}
        style={{
          ...styles.button,
          background: isOn ? "#22c55e" : "#ef4444",
        }}
      >
        {busy ? "..." : isOn ? "ON" : "OFF"}
      </button>
      {error && <p style={styles.error}>{error}</p>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main dashboard component
// ---------------------------------------------------------------------------

export default function App() {
  // Latest single readings shown in the stat cards
  const [temperature, setTemperature] = useState<number | null>(null);
  const [humidity, setHumidity] = useState<number | null>(null);

  // Rolling history for the chart — keep the last 20 points
  const [chartData, setChartData] = useState<DataPoint[]>([]);

  // Any error from the polling loop
  const [pollError, setPollError] = useState<string | null>(null);

  // Use a ref for the interval so we can clear it on unmount
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Poll both sensors every 1.5 seconds
  useEffect(() => {
    async function poll() {
      try {
        const [temp, humi] = await Promise.all([
          fetchSensor("sensor-temperature"),
          fetchSensor("sensor-humidity"),
        ]);

        setTemperature(temp);
        setHumidity(humi);
        setPollError(null);

        // Add a new point to the chart, keeping only the last 20
        const now = new Date().toLocaleTimeString();
        setChartData((prev) => {
          const next = [...prev, { time: now, temperature: temp, humidity: humi }];
          return next.length > 20 ? next.slice(next.length - 20) : next;
        });
      } catch (e) {
        setPollError(String(e));
      }
    }

    // Run immediately on mount, then every 1.5 s
    poll();
    intervalRef.current = setInterval(poll, 1500);

    // Cleanup: stop polling when the component unmounts
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>reTerminal Control Center</h1>

      {/* ---- Sensor readings ---- */}
      <section style={styles.row}>
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Temperature</h2>
          <p style={styles.bigNumber}>
            {temperature !== null ? `${temperature.toFixed(1)} °C` : "—"}
          </p>
        </div>
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Humidity</h2>
          <p style={styles.bigNumber}>
            {humidity !== null ? `${humidity.toFixed(1)} %` : "—"}
          </p>
        </div>
      </section>

      {pollError && <p style={styles.error}>Sensor error: {pollError}</p>}

      {/* ---- Live chart ---- */}
      <section style={styles.chartSection}>
        <h2 style={styles.cardTitle}>Live Readings</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="temperature"
              stroke="#f97316"
              dot={false}
              name="Temp (°C)"
            />
            <Line
              type="monotone"
              dataKey="humidity"
              stroke="#3b82f6"
              dot={false}
              name="Humidity (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* ---- Actuator toggles ---- */}
      <section style={styles.row}>
        <ToggleButton label="LED" actuatorId="actuator-led" />
        <ToggleButton label="Fan" actuatorId="actuator-fan" />
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Inline styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  page: {
    fontFamily: "sans-serif",
    maxWidth: 800,
    margin: "0 auto",
    padding: 24,
    background: "#0f172a",
    minHeight: "100vh",
    color: "#f1f5f9",
  },
  title: {
    textAlign: "center",
    marginBottom: 32,
    fontSize: 28,
    color: "#f1f5f9",
  },
  row: {
    display: "flex",
    gap: 16,
    marginBottom: 24,
    justifyContent: "center",
    flexWrap: "wrap",
  },
  card: {
    background: "#1e293b",
    borderRadius: 12,
    padding: "20px 32px",
    minWidth: 180,
    textAlign: "center",
    boxShadow: "0 2px 8px rgba(0,0,0,0.4)",
  },
  cardTitle: {
    margin: "0 0 12px 0",
    fontSize: 16,
    color: "#94a3b8",
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  bigNumber: {
    fontSize: 36,
    fontWeight: "bold",
    margin: 0,
    color: "#f1f5f9",
  },
  button: {
    border: "none",
    borderRadius: 8,
    padding: "12px 32px",
    fontSize: 18,
    fontWeight: "bold",
    color: "white",
    cursor: "pointer",
    minWidth: 100,
  },
  chartSection: {
    background: "#1e293b",
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  error: {
    color: "#f87171",
    textAlign: "center",
    marginBottom: 16,
  },
};