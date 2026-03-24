import board
import busio
from board import BUTTON_DOWN, BUTTON_UP

from src.modules.accelerometer_module import AccelerometerModule, Axis
from src.modules.button_module import ButtonModule
from src.modules.rotary_encoder_module import RotaryEncoderModule


class UserInputEvents:
    def __init__(self):
        self.next_app_steps = 0
        self.previous_app_steps = 0
        self.button_down = False
        self.app_action_next = False
        self.app_action_previous = False


class UserInputModule:
    def __init__(self, accelerometer_settings, rotary_encoder_settings):
        self.button_up = ButtonModule(button_ref=BUTTON_UP)
        self.button_down = ButtonModule(button_ref=BUTTON_DOWN)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = AccelerometerModule(
            i2c=self.i2c,
            address=accelerometer_settings.address,
        )
        self.rotary_encoder = self._create_rotary_encoder(rotary_encoder_settings)

    def _create_rotary_encoder(self, rotary_encoder_settings):
        if not rotary_encoder_settings:
            return None

        try:
            return RotaryEncoderModule(
                self.i2c,
                address=rotary_encoder_settings.address,
                button_pin=rotary_encoder_settings.button_pin,
            )
        except Exception as error:
            print("Could not initialize rotary encoder.")
            print(error)
            return None

    def poll(self):
        events = UserInputEvents()

        if self.button_up.is_pressed():
            events.next_app_steps += 1

        if self.button_down.is_pressed():
            events.button_down = True

        if self.rotary_encoder is not None:
            delta = self.rotary_encoder.read_delta()
            if delta > 0:
                events.next_app_steps += delta
            elif delta < 0:
                events.previous_app_steps += -delta

            if self.rotary_encoder.is_pressed():
                events.button_down = True

        if self.accelerometer.check_next_by_axis(Axis.X):
            events.next_app_steps += 1
        if self.accelerometer.check_previous_by_axis(Axis.X):
            events.previous_app_steps += 1
        if self.accelerometer.check_next_by_axis(Axis.Z):
            events.app_action_next = True
        if self.accelerometer.check_previous_by_axis(Axis.Z):
            events.app_action_previous = True

        return events
