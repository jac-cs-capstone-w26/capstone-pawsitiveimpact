from __future__ import annotations

# Used for tiny waits required by the sensor timing protocol.
from time import sleep

# Base class for GPIOZero-compatible device objects.
from gpiozero import Device
# Low-level Linux I2C communication library.
from smbus2 import SMBus
# Shared Sensor interface used by API-facing sensor wrappers.
from model import Sensor


class AHT20(Device):
    """Low-level AHT20 I2C device wrapper using smbus2."""

    def __init__(self, address: int = 0x38, bus: int = 4) -> None:
        """Open the I2C bus and send the sensor initialization command."""
        # 0x38 is the fixed I2C address of the AHT20 sensor.
        self.address = address
        # Bus 4 is used to avoid address conflicts on default bus 1.
        self.bus = SMBus(bus)
        # Initialization command from AHT20 datasheet.
        self.bus.write_i2c_block_data(self.address, 0xBE, [0x08, 0x00])
        # Give sensor time to complete initialization.
        sleep(0.02)

    def read(self) -> tuple[float, float]:
        """Trigger one measurement and return (temperature_c, humidity_percent)."""
        # Trigger measurement command with required control bytes.
        self.bus.write_i2c_block_data(self.address, 0xAC, [0x33, 0x00])
        # Wait for conversion to finish before reading bytes.
        sleep(0.08)

        # Read 7-byte response buffer from the sensor.
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)

        # Extract 20-bit raw humidity value from packed bytes.
        humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        # Convert raw humidity to percentage (0 to 100).
        humidity = humidity * 100 / 1048576.0

        # Extract 20-bit raw temperature value from packed bytes.
        temperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        # Convert raw temperature to Celsius according to formula.
        temperature = temperature * 200 / 1048576.0 - 50

        # Return plain floats for downstream formatting.
        return float(temperature), float(humidity)


# Backward-compatible alias used by app imports.
AHT20Device = AHT20


class TemperatureSensor(Sensor):
    """High-level temperature sensor view over a shared AHT20 device."""

    UNIT = "°C"

    def read_sensor(self) -> str:
        """Return temperature formatted with unit for API responses."""
        # AHT20 returns (temperature, humidity); we only need temperature.
        temperature, _ = self.device.read()
        # Keep two decimals for stable dashboard display.
        return f"{temperature:.2f} {self.UNIT}"


class HumiditySensor(Sensor):
    """High-level humidity sensor view over a shared AHT20 device."""

    UNIT = "%"

    def read_sensor(self) -> str:
        """Return humidity formatted with unit for API responses."""
        # AHT20 returns (temperature, humidity); we only need humidity.
        _, humidity = self.device.read()
        # Keep two decimals for stable dashboard display.
        return f"{humidity:.2f} {self.UNIT}"


if __name__ == "__main__":
    # Create one physical device instance and share it across both sensor wrappers.
    shared_device = AHT20(bus=4)
    # Wrapper focused on formatting temperature readings.
    temperature_sensor = TemperatureSensor(shared_device)
    # Wrapper focused on formatting humidity readings.
    humidity_sensor = HumiditySensor(shared_device)

    try:
        # Print fresh readings in a loop for manual hardware testing.
        while True:
            print(f"Temperature: {temperature_sensor.read_sensor()}")
            print(f"Humidity: {humidity_sensor.read_sensor()}")
            print("---")
            # Slow loop so output stays readable.
            sleep(2)
    except KeyboardInterrupt:
        print("Stopping AHT20 test...")