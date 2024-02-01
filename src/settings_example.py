from src.analogue_clock_app import AnalogueClockApp
from src.blank_app import BlankApp
from src.clock_app import ClockApp
from src.gif_player_app import GifPlayerApp
from src.settings_utils import AppSettings, Settings, WifiSettings

settings = Settings(
    apps=[
        AppSettings(
            app=AnalogueClockApp,
        ),
        AppSettings(
            app=GifPlayerApp,
            time={
              'hour': 8,
              'minute': 30,
            },
            settings={
                'gif_folder': '/gif',
                'loop_time_seconds': 300,
            },
        ),
        AppSettings(
            app=ClockApp, time={
                'hour': 23,
                'minute': 30,
            },
            settings={'twelve_hour': False}
        ),
        AppSettings(
            app=BlankApp,
            time={
              'hour': 0,
              'minute': 30,
            }
        ),
    ],
    wifi=WifiSettings('SSID_NAME', 'SSDI_PASSWORD', skip_connection=True),
)
