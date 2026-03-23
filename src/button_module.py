from adafruit_debouncer import Debouncer
from digitalio import DigitalInOut, Pull

try:
    from adafruit_seesaw import digitalio as seesaw_digitalio
    from adafruit_seesaw import seesaw
except ImportError:
    seesaw = None
    seesaw_digitalio = None


class _ButtonInputAdapter:
    def __init__(self, button_input, active_low: bool):
        self.button_input = button_input
        self.active_low = active_low

    @property
    def value(self):
        raw_value = self.button_input.value
        return not raw_value if self.active_low else raw_value


class ButtonModule:
    def __init__(self, button_ref=None, button_input=None, pull=Pull.UP, active_low=True):
        self.seesaw = None

        if button_input is not None:
            self.button_input = button_input
        elif button_ref is not None:
            self.button_input = DigitalInOut(button_ref)
            self.button_input.switch_to_input(pull=pull)
        else:
            raise ValueError("ButtonModule requires either button_ref or button_input.")

        self.button_adapter = _ButtonInputAdapter(self.button_input, active_low=active_low)
        self.button = Debouncer(self.button_adapter)

    @classmethod
    def from_seesaw(cls, i2c, addr=0x36, button_pin=24, active_low=True):
        if seesaw is None or seesaw_digitalio is None:
            raise RuntimeError("adafruit_seesaw is not installed on the device.")

        rotary_seesaw = seesaw.Seesaw(i2c, addr=addr)
        rotary_seesaw.pin_mode(button_pin, rotary_seesaw.INPUT_PULLUP)

        instance = cls(
            button_input=seesaw_digitalio.DigitalIO(rotary_seesaw, button_pin),
            active_low=active_low,
        )
        instance.seesaw = rotary_seesaw
        return instance

    def is_pressed(self) -> bool:
        self.button.update()
        return self.button.fell
