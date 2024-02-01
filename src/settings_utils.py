from src.analogue_clock_app import AnalogueClockApp
from src.blank_app import BlankApp
from src.clock_app import ClockApp
from src.gif_player_app import GifPlayerApp


class WifiSettings:
    def __init__(self, ssid, password, skip_connection):
        self.ssid = ssid
        self.password = password
        self.skip_connection = skip_connection


class Settings:
    def __init__(self, apps, wifi: WifiSettings):
        self.apps = apps
        self.wifi = wifi


class AppSettings:
    def _init_(self, app, time=None, settings=None):
        self.app = app
        self.time = time
        self.settings = settings
