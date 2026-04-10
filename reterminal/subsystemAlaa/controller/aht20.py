# Reads temperature + humidity

# Has the AHT20Sensor class
# Uses I2C communication
# Returns sensor data as strings with units, e.g. "23.45 °C" and "55.10 %"

from __future__ import annotations

import os

# adafruit_extended_bus lets us open an I2C bus by number 
# rather than only bus 1. Import fails gracefully on machines without GPIO.
try:
    from adafruit_extended_bus import ExtendedI2C as I2C
except ImportError:
    I2C = None  

import adafruit_ahtx0  # Adafruit CircuitPython driver for AHT10/AHT20

from model import Sensor


def _i2c_bus_number() -> int:
    """Read the I2C bus number from the environment, defaulting to 4.

    Bus 4 is the software-bit-bang bus we create in /boot/firmware/config.txt
    to avoid the address conflict with the reTerminal's built-in I/O expander.
    """
    return int(os.environ.get("AHT20_I2C_BUS", "4"))


class AHT20:
    """Hardware handle for the AHT20 temperature/humidity chip.

    Wraps the Adafruit AHTx0 CircuitPython driver. Both TemperatureSensor and
    HumiditySensor share a single AHT20 instance so the chip is only
    initialised once.
    """

    def __init__(self, bus_number: int | None = None) -> None:
        if I2C is None:
            raise ImportError(
                "Install adafruit-extended-bus (e.g. uv add adafruit-extended-bus)."
            )
        bus = bus_number if bus_number is not None else _i2c_bus_number()
        # Open the I2C bus and hand it to the Adafruit driver.
        # The AHT20 always lives at address 0x38 on whatever bus we choose.
        self._sensor = adafruit_ahtx0.AHTx0(I2C(bus))

    @property
    def temperature(self) -> float:
        """Return the current temperature in degrees Celsius."""
        return float(self._sensor.temperature)

    @property
    def relative_humidity(self) -> float:
        """Return the current relative humidity as a percentage (0-100)."""
        return float(self._sensor.relative_humidity)


class TemperatureSensor(Sensor):
    """Sensor subclass that reads temperature from an AHT20 chip."""

    device: AHT20
    UNIT = "°C"

    def __init__(self, device: AHT20) -> None:
        super().__init__(device)  # Stores device on self.device

    def read_sensor(self) -> str:
        """Return temperature as a string, e.g. '23.45 °C'."""
        value = self.device.temperature
        return f"{value:.2f} {self.UNIT}"


class HumiditySensor(Sensor):
    """Sensor subclass that reads relative humidity from an AHT20 chip."""

    device: AHT20
    UNIT = "%"

    def __init__(self, device: AHT20) -> None:
        super().__init__(device)

    def read_sensor(self) -> str:
        """Return humidity as a string, e.g. '55.10 %'."""
        value = self.device.relative_humidity
        return f"{value:.2f} {self.UNIT}"


if __name__ == "__main__":
    # for testing: run `uv run python aht20.py` on the reTerminal.
    # should see two lines like: 23.45 °C  and  38.10 %
    chip = AHT20()
    temp = TemperatureSensor(chip)
    hum = HumiditySensor(chip)
    print(temp.read_sensor())
    print(hum.read_sensor())