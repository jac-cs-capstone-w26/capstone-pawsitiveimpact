from typing import Any

""" Interface that all sensors must implement. """
class Sensor:
    # Underlying hardware/driver object (AHT20, etc.).
    device: Any
    # unit string added to formatted readings.
    UNIT: str = ""

    def __init__(self, device: Any):
        # Save concrete hardware device for subclass use.
        self.device = device

    def read_sensor(self) -> str:
        # Subclasses should return a formatted reading string.
        """Takes a reading of the sensor, and returns the result as a string."""
        pass


""" Interface that all actuators must implement. """
class Actuator:
    # Underlying hardware/driver object (PWMLED, relay output, etc.).
    device: Any
    # Current actuator state string mirrored for API responses.
    state: str = ""

    def __init__(self, device: Any):
        # Save concrete hardware device for subclass use.
        self.device = device

    def control_actuator(self, state: str) -> str:
        # Subclasses should apply command and return normalized state.
        """Changes the internal state of the actuator, and returns the new state as
        a string."""
        pass