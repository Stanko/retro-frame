class WifiSettings:
    def __init__(self, ssid, password, skip_connection):
        self.ssid = ssid
        self.password = password
        self.skip_connection = skip_connection


class RealTimeSettings:
    def __init__(self, timezone: str):
        self.timezone = timezone


class DisplaySettings:
    def __init__(self, color_order="RGB"):
        self.color_order = color_order


class Settings:
    def __init__(self, apps, wifi: WifiSettings, real_time: RealTimeSettings, display=None):
        self.apps = apps
        self.wifi = wifi
        self.real_time = real_time
        self.display = display or DisplaySettings()


class AppSettings:
    def __init__(self, app, time=None, settings=None):
        self.app = app
        self.time = time
        self.settings = settings

    def __repr__(self) -> str:
        return f"AppSettings(app={self.app}, time={self.time}, settings={self.settings})"
