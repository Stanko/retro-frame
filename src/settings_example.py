from src.apps.analogue_clock_app import AnalogueClockApp
from src.apps.blank_app import BlankApp
from src.apps.clock_app import ClockApp
from src.apps.gif_player_app import GifPlayerApp
from src.apps.train_radar import TrainRadarApp
from src.settings_utils import (
    AccelerometerSettings,
    AppSettings,
    DisplaySettings,
    RealTimeSettings,
    RotaryEncoderSettings,
    Settings,
    WifiSettings,
)

settings = Settings(
    apps=[
        AppSettings(
            app=AnalogueClockApp,
        ),
        AppSettings(
            app=TrainRadarApp,
            settings={
                'url': 'https://train-radar-nl.fly.dev/train/radar',
                'poll_interval_seconds': 10.0,
            },
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
    real_time=RealTimeSettings(
        timezone='Europe/Amsterdam',
        chip_name='PCF8523', # Optional, if not set, it keeps the time in memory and fetch online time on every boot
    ),
    display=DisplaySettings(color_order='RBG'),
    # Use the I2C Seesaw diagnostic to discover device addresses when needed.
    accelerometer=AccelerometerSettings(address=0x19),

    # rotary_encoder (Optional): If not provided, only accelerometer will be used
    # If you want to use a rotary encoder, make sure to provide the correct I2C address and button pin.
    # rotary_encoder=RotaryEncoderSettings(enabled=True, address=0x36, button_pin=24),
    rotary_encoder=None
)
