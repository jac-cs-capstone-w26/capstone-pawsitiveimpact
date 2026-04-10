#!/usr/bin/env python3 

# from gpiozero import LED
from gpiozero import PWMLED
from model import Actuator

class LED(Actuator):
    # Constructor: runs when an LED object is created
    # It initializes the PWMLED connected to the specified GPIO pin
    def __init__(self, led_pin_number: int):
        super().__init__(PWMLED(led_pin_number))
        # Default pulse duration (time for fade in or fade out)
        self.pulse_duration = 1

    def control_actuator(self, state: str) -> str:
            state = state.lower()

            # --- ON ---
            if state == "on":
                self.device.on()
                return "LED turned ON"

            # --- OFF ---
            elif state == "off":
                self.device.off()
                return "LED turned OFF"

            # --- PULSE (number) ---
            else:
                try:
                    pulse_duration = float(state)
                except ValueError:
                    return "Invalid state (use 'on', 'off', or a number)"

                self.pulse_duration = pulse_duration
                # makes the LED pulse (fade in and out)
                self.device.pulse(
                    fade_in_time=self.pulse_duration,   # time to reach full brightness
                    fade_out_time=self.pulse_duration,  # time to fade back to off
                    n=1                                 # number of pulses
                )
                return f"LED pulsing with duration {self.pulse_duration}"
