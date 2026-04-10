# Controls the LED

# Has LED class
# Handles brightness / pulsing (PWM)
# Talks directly to GPIO

from __future__ import annotations

import os
from time import sleep

from gpiozero import PWMLED  # PWM = Pulse Width Modulation, lets us dim the LED

from model import Actuator

# Load .env file before anything else reads os.environ
from dotenv import load_dotenv
load_dotenv()  # this reads .env and sets LED_GPIO, FAN_GPIO etc.

def _led_gpio_pin() -> int:
    """Read the LED GPIO pin from the environment, defaulting to 18."""
    return int(os.environ.get("LED_GPIO", "18"))


class LED(Actuator):
    """Controls a PWM-capable LED on a GPIO pin.

    PWMLED.value ranges from 0.0 (fully off) to 1.0 (full brightness).
    The HTTP API only uses 'on' (full brightness) and 'off', but the
    _demo_pulse helper below shows how dimming works.
    """

    def __init__(self, device: PWMLED) -> None:
        super().__init__(device)  # Stores PWMLED on self.device
        self.state = "off"
        self.device.off()         # Start with LED off

    def control_actuator(self, state: str) -> str:
        """Turn the LED fully on or off.

        Args:
            state: 'on' or 'off' (case-insensitive, whitespace-tolerant).

        Returns:
            The new state string.

        Raises:
            ValueError: if state is not 'on' or 'off'.
        """
        normalized = state.strip().lower()
        if normalized == "on":
            self.device.value = 1.0   # Full brightness
            self.state = "on"
        elif normalized == "off":
            self.device.off()          # PWM duty cycle -> 0
            self.state = "off"
        else:
            raise ValueError('LED state must be "on" or "off"')
        return self.state


def _demo_pulse(pwm: PWMLED, pulse_seconds: float = 2.0, steps: int = 100) -> None:
    """Smooth brightness fade: 0 -> 100% -> 0 over pulse_seconds."""
    step_delay = pulse_seconds / (2 * steps)
    # Ramp up
    for step in range(steps + 1):
        pwm.value = step / steps
        sleep(step_delay)
    # Ramp down
    for step in range(steps - 1, -1, -1):
        pwm.value = step / steps
        sleep(step_delay)


if __name__ == "__main__":
    # For test: run `uv run python led.py` on the reTerminal.
    # LED should flash on/off, then pulse smoothly twice.
    pwm = PWMLED(_led_gpio_pin())
    actuator = LED(pwm)

    print("LED on...")
    actuator.control_actuator("on")
    sleep(0.5)
    print("LED off...")
    actuator.control_actuator("off")
    sleep(0.5)

    print("Pulsing twice...")
    _demo_pulse(pwm, pulse_seconds=2.0)
    _demo_pulse(pwm, pulse_seconds=2.0)
    pwm.off()
    print("Done.")