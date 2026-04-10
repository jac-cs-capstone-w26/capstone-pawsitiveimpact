# Controls the fan using the relay

# Has Fan class
# Turns fan ON / OFF
# Uses GPIO to control relay

from __future__ import annotations

import os
from time import sleep

from gpiozero import OutputDevice

from model import Actuator

# Load .env file before anything else reads os.environ
from dotenv import load_dotenv
load_dotenv()  # this reads .env and sets LED_GPIO, FAN_GPIO etc.

def _fan_gpio_pin() -> int:
    """Read the fan relay GPIO pin from the environment, defaulting to 17."""
    return int(os.environ.get("FAN_GPIO", "17"))


class Fan(Actuator):
    """Controls a 5V fan via a relay wired to a GPIO pin.

    The relay is a simple on/off switch, so valid states are 'on' and 'off'.
    OutputDevice.on() energises the relay coil -> closes the 5V circuit -> fan spins.
    OutputDevice.off() de-energises the coil -> opens the circuit -> fan stops.
    """

    def __init__(self, device: OutputDevice) -> None:
        super().__init__(device)  # Stores relay on self.device
        self.state = "off"        # Track current state
        self.device.off()         # Ensure relay starts open (fan off)

    def control_actuator(self, state: str) -> str:
        """Turn the fan on or off.

        Args:
            state: 'on' or 'off' (case-insensitive, whitespace-tolerant).

        Returns:
            The new state string ('on' or 'off').

        Raises:
            ValueError: if state is anything other than 'on' or 'off'.
        """
        normalized = state.strip().lower()
        if normalized == "on":
            self.device.on()       # Energise relay -> fan spins
            self.state = "on"
        elif normalized == "off":
            self.device.off()      # De-energise relay -> fan stops
            self.state = "off"
        else:
            raise ValueError('Fan state must be "on" or "off"')
        return self.state


if __name__ == "__main__":
    # For test: run `uv run python fan.py` on the reTerminal.
    # The fan should spin for 2 seconds, then stop for 2 seconds
    relay = OutputDevice(_fan_gpio_pin(), initial_value=False)
    fan = Fan(relay)

    print("Turning fan ON...")
    fan.control_actuator("on")
    sleep(2)

    print("Turning fan OFF...")
    fan.control_actuator("off")
    sleep(2)
    print("Done.")