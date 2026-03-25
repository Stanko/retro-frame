class WifiSettings:
    def __init__(self, ssid, password, skip_connection):
        self.ssid = ssid
        self.password = password
        self.skip_connection = skip_connection


class RealTimeSettings:
    def __init__(
        self,
        timezone: str,
        chip_name=None,
    ):
        self.timezone = timezone
        self.chip_name = self.normalize_chip_name(chip_name)

    @staticmethod
    def normalize_chip_name(chip_name):
        if chip_name is None:
            return None
        return chip_name.replace("-", "").replace("_", "").replace(" ", "").lower()


class DisplaySettings:
    def __init__(self, color_order="RGB"):
        self.color_order = color_order


class AccelerometerSettings:
    def __init__(self, address=0x19):
        self.address = address


class RotaryEncoderSettings:
    def __init__(self, address=0x36, button_pin=24):
        self.address = address
        self.button_pin = button_pin


class Settings:
    def __init__(
        self,
        apps,
        wifi: WifiSettings,
        real_time: RealTimeSettings,
        display=None,
        accelerometer=None,
        rotary_encoder=None,
    ):
        self.apps = apps
        self.wifi = wifi
        self.real_time = real_time
        self.display = display or DisplaySettings()
        self.accelerometer = accelerometer or AccelerometerSettings()
        self.rotary_encoder = rotary_encoder


class AppSettings:
    def __init__(self, app, time=None, settings=None):
        self.app = app
        self.time = time
        self.settings = settings

    def __repr__(self) -> str:
        return f"AppSettings(app={self.app}, time={self.time}, settings={self.settings})"
