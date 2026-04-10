from typing import Any

class Sensor():
    device: Any
    UNIT: str = ""

    def __init__(self, device: Any):
        self.device = device

    def read_sensor(self) -> str:
        """Takes a reading of the sensor, and returns the result as a string."""
        pass

class Actuator():
    device: Any
    state: str = ""

    def __init__(self, device: Any):
        self.device = device

    def control_actuator(self, state: str) -> str:
        """Changes the internal state of the actuator, and returns the new state as
        a string."""
        pass