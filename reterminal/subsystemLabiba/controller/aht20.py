#!/usr/bin/env python3
from gpiozero import Device
from time import sleep
from smbus2 import SMBus
from typing import Tuple
from model import Sensor


# Adapted AHT20 device class
class AHT20(Device):
    def __init__(self, address: int = 0x38, bus: int = 4) -> None:
        self.address = address

        # Create I2C bus connection
        self.bus = SMBus(bus)

        # Send initialization command to the sensor
        self.bus.write_i2c_block_data(self.address, 0xBE, [0x08, 0x00])

        # Wait for sensor to initialize
        sleep(0.02)

    def read(self) -> Tuple[float, float]:
        # Send measurement command
        self.bus.write_i2c_block_data(self.address, 0xAC, [0x33, 0x00])

        # Wait for measurement to complete
        sleep(0.08)

        # Read 7 bytes of data from the sensor
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)

        # --- Extract humidity ---
        # Combine bytes into a single raw value
        humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4

        # Convert raw value to percentage
        humidity = humidity * 100 / 1048576.0

        # --- Extract temperature ---
        # Combine bytes into a single raw value
        temperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        # Convert raw value to degrees Celsius
        temperature = temperature * 200 / 1048576.0 - 50

        return temperature, humidity

# Sensor class
class TemperatureSensor(Sensor):
    UNIT = "°C"

    def read_sensor(self) -> str:
        temperature, _ = self.device.read()
        return f"{temperature:.2f} {self.UNIT}"


class HumiditySensor(Sensor):
    UNIT = "%"

    def read_sensor(self) -> str:
        _, humidity = self.device.read()
        return f"{humidity:.2f} {self.UNIT}"


