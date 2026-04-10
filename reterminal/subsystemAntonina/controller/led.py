from __future__ import annotations

# Used only by the local hardware test loop.
from time import sleep

# PWM LED primitive that supports fading/pulsing behavior.
from gpiozero import PWMLED

# Base actuator contract used by the API layer.
from model import Actuator


class LED(Actuator):
    """PWM LED actuator supporting on/off and pulse commands."""

    def __init__(self, pin: int = 12, pulse_duration: float = 2.0) -> None:
        """Initialize PWM pin and default pulse duration."""
        # PWM pin allows brightness control instead of binary on/off only.
        super().__init__(PWMLED(pin))
        # Full pulse cycle duration (dim->bright->dim).
        self._pulse_duration = pulse_duration
        # Mirror software state for quick API responses.
        self.state = "off"

    def control_actuator(self, state: str) -> str:
        """Apply LED state command and return normalized state."""
        # Normalize user input to make API case-insensitive.
        normalized = state.strip().lower()

        if normalized == "on":
            # Set duty cycle to full brightness.
            self.device.on()
            self.state = "on"
            return self.state

        if normalized == "off":
            # Set duty cycle to zero brightness.
            self.device.off()
            self.state = "off"
            return self.state

        if normalized == "pulse":
            # Run two smooth pulses as a visible feedback effect.
            self.pulse_twice()
            self.state = "pulse"
            return self.state

        # Reject unknown commands with clear guidance.
        raise ValueError("Invalid LED state. Use 'on', 'off', or 'pulse'.")

    def pulse_twice(self) -> None:
        """Run a blocking two-cycle smooth pulse animation."""
        # Split total duration across fade-in and fade-out phases.
        transition = self._pulse_duration / 2
        # Blocking call ensures pulse completes before returning.
        self.device.pulse(fade_in_time=transition, fade_out_time=transition, n=2, background=False)

    def on(self) -> None:
        """Convenience helper that maps to control_actuator('on')."""
        self.control_actuator("on")

    def off(self) -> None:
        """Convenience helper that maps to control_actuator('off')."""
        self.control_actuator("off")

    def close(self) -> None:
        """Release GPIO resources for clean shutdown."""
        # Important when restarting services/tests repeatedly.
        self.device.close()


if __name__ == "__main__":
    # Manual hardware test loop for LED commands.
    actuator = LED(pin=12, pulse_duration=2.0)

    try:
        # Cycle through ON, OFF, and PULSE repeatedly.
        while True:
            print("LED ON")
            actuator.control_actuator("on")
            sleep(1)

            print("LED OFF")
            actuator.control_actuator("off")
            sleep(1)

            print("Pulsing twice")
            actuator.control_actuator("pulse")
            sleep(1)
    except KeyboardInterrupt:
        # Graceful stop on Ctrl+C.
        print("Stopping LED test...")
    finally:
        # Always release GPIO line before exit.
        actuator.close()