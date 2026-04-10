# FastAPI web framework primitives.
from fastapi import FastAPI, HTTPException
# CORS middleware enables browser requests from frontend origins.
from fastapi.middleware.cors import CORSMiddleware
# Environment variable access (for configurable bus numbers, etc.).
import os
from threading import Lock

# AHT20 device alias and high-level sensor wrappers.
from aht20 import AHT20Device, HumiditySensor, TemperatureSensor
# Relay-based fan actuator class.
from fan import Fan
# PWM-based LED actuator class.
from led import LED

# Main FastAPI application object used by uvicorn/fastapi CLI.
app = FastAPI(title="Device Controller")

# Allow frontend dashboard origins during local and LAN development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://.*:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


AHT20_BUS = int(os.getenv("AHT20_BUS", "4"))


def _initialize_devices() -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    """Create device objects once and capture init errors per device ID."""
    # Map of device IDs to startup errors for clean API error reporting.
    errors: dict[str, str] = {}
    # Sensor registry keyed by public API sensor IDs.
    sensors: dict[str, object] = {}
    # Actuator registry keyed by public API actuator IDs.
    actuators: dict[str, object] = {}

    try:
        # Create one shared AHT20 device and split into two logical sensors.
        aht20 = AHT20Device(bus=AHT20_BUS)
        sensors["temperature-1"] = TemperatureSensor(aht20)
        sensors["humidity-1"] = HumiditySensor(aht20)
    except Exception as exc:
        # If hardware init fails, both sensor IDs should report this error.
        errors["temperature-1"] = str(exc)
        errors["humidity-1"] = str(exc)

    try:
        # Register fan actuator on relay GPIO pin 16.
        actuators["fan-1"] = Fan(pin=16)
    except Exception as exc:
        # Persist startup failure for API responses.
        errors["fan-1"] = str(exc)

    try:
        # Register LED actuator on PWM-capable GPIO pin 12.
        actuators["led-1"] = LED(pin=12)
    except Exception as exc:
        # Persist startup failure for API responses.
        errors["led-1"] = str(exc)

    # Return all registries even if some devices failed to initialize.
    return sensors, actuators, errors


# Device registries are initialized lazily to avoid import-time GPIO conflicts.
# None means "not created yet".
SENSORS: dict[str, object] | None = None
# None means "not created yet".
ACTUATORS: dict[str, object] | None = None
# None means "not created yet".
INIT_ERRORS: dict[str, str] | None = None
# Lock prevents two requests from initializing hardware at the same time.
_DEVICES_LOCK = Lock()


def _get_devices() -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    """Initialize hardware on first use and return device registries."""
    # Reassign module-level variables, so Python needs "global" here.
    global SENSORS, ACTUATORS, INIT_ERRORS
    # Fast path: if everything is already initialized, skip locking.
    if SENSORS is None or ACTUATORS is None or INIT_ERRORS is None:
        # Slow path: first request enters lock and performs initialization.
        with _DEVICES_LOCK:
            # Double-check inside lock in case another thread already initialized.
            if SENSORS is None or ACTUATORS is None or INIT_ERRORS is None:
                # Build sensors/actuators once and cache them for all future requests.
                SENSORS, ACTUATORS, INIT_ERRORS = _initialize_devices()
    # Type-wise they are no longer None after the branch above.
    return SENSORS, ACTUATORS, INIT_ERRORS


@app.get("/read/{sensor_id}")
def read_sensor(sensor_id: str) -> dict[str, str]:
    """Read one sensor by ID and return its latest formatted reading."""
    # Ensure device registries are initialized in the active server process.
    sensors, _, init_errors = _get_devices()
    # Return startup error if this sensor failed during boot.
    if sensor_id in init_errors:
        raise HTTPException(status_code=500, detail=init_errors[sensor_id])

    # Find requested sensor object by API ID.
    sensor = sensors.get(sensor_id)
    if sensor is None:
        # ID not recognized by registry.
        raise HTTPException(status_code=404, detail=f"Unknown sensor id: {sensor_id}")

    try:
        # Delegate actual read to sensor wrapper.
        reading = sensor.read_sensor()
    except Exception as exc:
        # Convert hardware/runtime exceptions into API 500s.
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Stable response shape consumed by frontend polling.
    return {"id": sensor_id, "reading": reading}


@app.put("/control/{actuator_id}")
def control_actuator(actuator_id: str, state: str) -> dict[str, str]:
    """Control one actuator by ID using a string state command."""
    # Ensure device registries are initialized in the active server process.
    _, actuators, init_errors = _get_devices()
    # Return startup error if this actuator failed during boot.
    if actuator_id in init_errors:
        raise HTTPException(status_code=500, detail=init_errors[actuator_id])

    # Find requested actuator object by API ID.
    actuator = actuators.get(actuator_id)
    if actuator is None:
        # ID not recognized by registry.
        raise HTTPException(status_code=404, detail=f"Unknown actuator id: {actuator_id}")

    try:
        # Delegate validation + state change to actuator class.
        new_state = actuator.control_actuator(state)
    except ValueError as exc:
        # Use 400 for invalid client inputs (bad state values).
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Use 500 for unexpected actuator/hardware failures.
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Stable response shape consumed by frontend controls.
    return {"id": actuator_id, "state": new_state}