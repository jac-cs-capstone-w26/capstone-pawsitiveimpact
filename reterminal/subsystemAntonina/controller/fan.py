from __future__ import annotations

# Used only by the local hardware test loop.
from time import sleep

# GPIO output primitive suitable for relay on/off control.
from gpiozero import OutputDevice

# Base actuator contract used by the API layer.
from model import Actuator


class Fan(Actuator):
    """Relay-controlled fan actuator with on/off states."""

    def __init__(self, pin: int = 16) -> None:
        """Initialize relay output pin and default state."""
        # active_high=True means logical ON drives pin HIGH.
        # initial_value=False keeps the relay OFF at startup.
        super().__init__(OutputDevice(pin=pin, active_high=True, initial_value=False))
        # Mirror software state for quick API responses.
        self.state = "off"

    def control_actuator(self, state: str) -> str:
        """Apply on/off command and return normalized state."""
        # Normalize user input to make API case-insensitive.
        normalized = state.strip().lower()
        if normalized not in {"on", "off"}:
            # Reject unknown commands with clear guidance.
            raise ValueError("Invalid fan state. Use 'on' or 'off'.")

        # Relay output is numeric: 1.0 for ON, 0.0 for OFF.
        self.device.value = 1.0 if normalized == "on" else 0.0
        # Keep internal state in sync with physical output.
        self.state = normalized
        return self.state

    def close(self) -> None:
        """Release GPIO resources for clean shutdown."""
        # Important when restarting services/tests repeatedly.
        self.device.close()


if __name__ == "__main__":
    # Manual hardware test loop for the fan relay.
    fan = Fan(pin=16)

    try:
        # Alternate ON/OFF every 2 seconds until interrupted.
        while True:
            print("Fan ON")
            fan.control_actuator("on")
            sleep(2)

            print("Fan OFF")
            fan.control_actuator("off")
            sleep(2)
    except KeyboardInterrupt:
        # Graceful stop on Ctrl+C.
        print("Stopping fan test...")
    finally:
        # Always release GPIO line before exit.
        fan.close()