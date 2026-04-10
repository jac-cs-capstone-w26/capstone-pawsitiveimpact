from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from led import LED
from fan import Fan
from aht20 import TemperatureSensor, HumiditySensor
from aht20 import AHT20  # your actual sensor class

app = FastAPI()

# Allow your frontend origin
origins = [
    "http://172.20.10.2:5173",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create devices
fan = Fan(16)
led = LED(12)
aht20_device = AHT20()
temp_sensor = TemperatureSensor(aht20_device)
humidity_sensor = HumiditySensor(aht20_device)


# Store them with IDs
sensors = {
    "temp": temp_sensor,
    "humidity": humidity_sensor
}

actuators = {
    "fan": fan,
    "led": led
}


# ROUTES 
@app.get("/read/{sensor_id}")
def read_sensor(sensor_id: str):
    sensor = sensors.get(sensor_id)

    if not sensor:
        return {"error": "Sensor not found"}

    return {"value": sensor.read_sensor()}


@app.put("/control/{actuator_id}")
def control_actuator(actuator_id: str, state: str):
    actuator = actuators.get(actuator_id)

    if not actuator:
        return {"error": "Actuator not found"}

    return {"result": actuator.control_actuator(state)}