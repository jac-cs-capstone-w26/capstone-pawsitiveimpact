## Device Controller Backend

FastAPI backend for reading sensors and controlling actuators.

### Device IDs

- Temperature sensor: `temperature-1`
- Humidity sensor: `humidity-1`
- Fan actuator: `fan-1`
- LED actuator: `led-1`

### Install dependencies

```bash
uv sync
```

### Run the API

Make sure you cd in the directory: a1/controller

```bash
uv run fastapi dev app.py
```

By default, the server runs at `http://127.0.0.1:8000`.

### API Endpoints

- `GET /read/{sensor_id}`
- `PUT /control/{actuator_id}?state=<state>`

### Example requests

Read temperature:

```bash
curl "http://127.0.0.1:8000/read/temperature-1"
```

Read humidity:

```bash
curl "http://127.0.0.1:8000/read/humidity-1"
```

Turn fan on/off:

```bash
curl -X PUT "http://127.0.0.1:8000/control/fan-1?state=on"
curl -X PUT "http://127.0.0.1:8000/control/fan-1?state=off"
```

Control LED:

```bash
curl -X PUT "http://127.0.0.1:8000/control/led-1?state=on"
curl -X PUT "http://127.0.0.1:8000/control/led-1?state=off"
curl -X PUT "http://127.0.0.1:8000/control/led-1?state=pulse"
```

### Notes

- If hardware is not connected or unavailable, the API may return a `500` error for that device ID.
- Interactive docs are available at `http://127.0.0.1:8000/docs`.
