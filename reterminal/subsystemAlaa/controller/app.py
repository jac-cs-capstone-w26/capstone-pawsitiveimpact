# This is the main controller / entry point

# Runs the program
# Calls functions from model.py
# Could:
    # start everything
    # loop
    # send data to dashboard

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

# Load .env file before anything else reads os.environ
from dotenv import load_dotenv
load_dotenv()  # this reads .env and sets LED_GPIO, FAN_GPIO etc.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gpiozero import OutputDevice, PWMLED
from pydantic import BaseModel

from aht20 import AHT20, HumiditySensor, TemperatureSensor
from fan import Fan
from led import LED
from model import Actuator, Sensor

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stable string IDs.  The dashboard and /docs both use these exact strings.
# ---------------------------------------------------------------------------
SENSOR_TEMPERATURE_ID = "sensor-temperature"
SENSOR_HUMIDITY_ID    = "sensor-humidity"
ACTUATOR_LED_ID       = "actuator-led"
ACTUATOR_FAN_ID       = "actuator-fan"

# the _init_devices() function fills them once the server starts
# They are filled so API endpoint functions can look up devices by id:
# - /read/{sensor_id} reads from sensors[sensor_id]
# - /control/{actuator_id} controls actuators[actuator_id]
# This keeps hardware setup in one place and reuse in requests.
sensors:   dict[str, Sensor]   = {}
actuators: dict[str, Actuator] = {}


def _init_devices() -> None:
    """Instantiate every GPIO / I2C device exactly once when the server starts.

    Separating this from the FastAPI app object makes it easy to call from
    tests or from a plain Python script without spinning up the full server.
    """
    global sensors, actuators
    sensors   = {}
    actuators = {}

    # Read pin numbers from environment so we can override them without editing code.
    led_pin = int(os.environ.get("LED_GPIO", "18"))
    fan_pin = int(os.environ.get("FAN_GPIO", "17"))

    # PWMLED lets us do dimming via PWM, OutputDevice is plain on/off for the relay.
    pwm   = PWMLED(led_pin)
    relay = OutputDevice(fan_pin, initial_value=False)

    actuators[ACTUATOR_LED_ID] = LED(pwm)
    actuators[ACTUATOR_FAN_ID] = Fan(relay)

    try:
        # AHT20 will raise if the i2c-4 overlay isn't loaded or wiring is wrong.
        # We catch the error so the rest of the API still works (actuators are fine).
        aht = AHT20()
        sensors[SENSOR_TEMPERATURE_ID] = TemperatureSensor(aht)
        sensors[SENSOR_HUMIDITY_ID]    = HumiditySensor(aht)
    except Exception:
        logger.exception(
            "AHT20 not available — check the i2c-4 overlay, wiring, and permissions."
        )


# FastAPI calls this async context manager once when the app starts.
# - code before yield runs at startup (we initialise sensors/actuators)
# - yield hands control back to FastAPI to serve requests
# - code after yield would run at shutdown (cleanup, not used here)
@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _init_devices()
    yield


app = FastAPI(
    title="reTerminal Control Center",
    version="0.1.0",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models define the JSON shapes FastAPI validates automatically.
# ---------------------------------------------------------------------------

class ActuatorPutBody(BaseModel):
    state: str  # Expected: "on" or "off"


class ReadingResponse(BaseModel):
    sensor_id: str
    reading: str   # e.g. "23.45 °C"


class ActuatorResponse(BaseModel):
    actuator_id: str
    state: str     # The new state after the command, e.g. "on"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/read/{sensor_id}", response_model=ReadingResponse)
def read_sensor(sensor_id: str) -> ReadingResponse:
    """GET /read/sensor-temperature  or  GET /read/sensor-humidity

    Returns the latest reading from the requested sensor.
    503 if the AHT20 failed to initialise (hardware problem).
    """
    if sensor_id not in sensors:
        raise HTTPException(
            status_code=503,
            detail="Sensor unavailable or unknown id. Is the AHT20 on i2c-4?",
        )
    reading = sensors[sensor_id].read_sensor()
    return ReadingResponse(sensor_id=sensor_id, reading=reading)


@app.put("/control/{actuator_id}", response_model=ActuatorResponse)
def control_actuator(actuator_id: str, body: ActuatorPutBody) -> ActuatorResponse:
    """PUT /control/actuator-led  or  PUT /control/actuator-fan

    Body JSON: { "state": "on" }  or  { "state": "off" }
    Returns the new state.  400 if the state value is unrecognised.
    """
    if actuator_id not in actuators:
        raise HTTPException(status_code=404, detail="Unknown actuator id")
    try:
        new_state = actuators[actuator_id].control_actuator(body.state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ActuatorResponse(actuator_id=actuator_id, state=new_state)


@app.get("/")
def root() -> dict[str, Any]:
    """Health-check / discovery endpoint.  Lists all registered IDs."""
    return {
        "sensor_ids":   list(sensors.keys()),
        "actuator_ids": list(actuators.keys()),
        "docs": "/docs",
    }