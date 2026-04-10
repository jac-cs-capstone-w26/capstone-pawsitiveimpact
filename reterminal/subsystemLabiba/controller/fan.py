#!/usr/bin/env python3

from gpiozero import OutputDevice

from model import Actuator



class Fan(Actuator):

    # Constructor: initialize the relay connected to the GPIO pin
    def __init__(self, pin_number: int):
        device = OutputDevice(pin_number, active_high=True, initial_value=False)
        super().__init__(device)
        self.isOn = False

    # Method to control the fan actuator
    # Takes a new state (True = ON, False = OFF)
    def control_actuator(self, state: str) -> str:
        # Convert string → boolean
        if state.lower() == "on":
            new_state = True
        elif state.lower() == "off":
            new_state = False
        else:
            return "Invalid state (use 'on' or 'off')"

        if self.isOn == new_state:
            return f"Fan already {'on' if self.isOn else 'off'}"

        self.isOn = new_state

        if self.isOn:
            self.device.on()
        else:
            self.device.off()

        return f"Fan turned {'on' if self.isOn else 'off'}"

