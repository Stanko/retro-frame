from adafruit_debouncer import Debouncer
from digitalio import DigitalInOut, Pull


class ButtonModule:

    def __init__(self, button_ref):
        self.button_ref = DigitalInOut(button_ref)
        self.button_ref.switch_to_input(pull=Pull.UP)
        self.button = Debouncer(self.button_ref)

    def is_pressed(self) -> bool:
        self.button.update()
        return self.button.fell
