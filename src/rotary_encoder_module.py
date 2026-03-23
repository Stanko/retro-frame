try:
    from adafruit_seesaw import digitalio as seesaw_digitalio
    from adafruit_seesaw import rotaryio as seesaw_rotaryio
    from adafruit_seesaw import seesaw
except ImportError:
    seesaw = None
    seesaw_digitalio = None
    seesaw_rotaryio = None

from src.button_module import ButtonModule


class RotaryEncoderModule:
    def __init__(self, i2c, address=0x36, button_pin=24):
        if seesaw is None or seesaw_digitalio is None or seesaw_rotaryio is None:
            raise RuntimeError("adafruit_seesaw is not installed on the device.")

        self.device = seesaw.Seesaw(i2c, addr=address)
        self.device.pin_mode(button_pin, self.device.INPUT_PULLUP)
        self.button = ButtonModule(
            button_input=seesaw_digitalio.DigitalIO(self.device, button_pin),
            active_low=True,
        )
        self.encoder = seesaw_rotaryio.IncrementalEncoder(self.device)
        self.last_position = -self.encoder.position

    def read_delta(self) -> int:
        position = -self.encoder.position
        delta = position - self.last_position
        self.last_position = position
        return delta

    def is_pressed(self) -> bool:
        return self.button.is_pressed()
