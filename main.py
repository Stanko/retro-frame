import gc
import time
from os import listdir

from board import BUTTON_DOWN, BUTTON_UP

# Modules
from src.accelerometer_module import AccelerometerModule, Axis

# Apps
from src.analogue_clock_app import AnalogueClockApp
from src.button_module import ButtonModule
from src.clock_app import ClockApp
from src.display_module import DisplayModule
from src.gif_player_app import GifPlayerApp
from src.network_module import NetworkModule
from src.real_time_module import RealTimeClockModule
from src.settings import settings
from src.splash_app import SplashApp


class RetroFrame:
    """Container class for all modules and apps."""

    def __init__(self):
        self.button_up: ButtonModule = ButtonModule(button_ref=BUTTON_UP)
        self.button_down: ButtonModule = ButtonModule(button_ref=BUTTON_DOWN)
        self.display: DisplayModule = DisplayModule(width=64, height=64, bit_depth=4)
        self.accelerometer: AccelerometerModule = AccelerometerModule()
        self.network: NetworkModule = NetworkModule(settings.wifi)
        self.real_time: RealTimeClockModule = RealTimeClockModule(self.network)

        self.gif_folder = "/gif"
        self.gif_file_list = sorted(
            [
                f"{self.gif_folder}/{f}"
                for f in listdir(self.gif_folder)
                if (f.endswith(".gif") and not f.startswith("."))
            ]
        )
        self.current_app = None
        # Store anonymous functions that return app objects to preserve memory
        # Dictonary order is irrelevant, it will be sorted when switching apps
        self.apps = {
            ClockApp.name: lambda: ClockApp(self.display, self.real_time),
            GifPlayerApp.name: lambda: GifPlayerApp(self.gif_file_list, self.display),
            AnalogueClockApp.name: lambda: AnalogueClockApp(self.display, self.real_time),
        }

    def next_app(self):
        app_list = sorted(self.apps.keys())
        current_app_index = app_list.index(self.current_app.name)
        current_app_index = (current_app_index + 1) % len(app_list)
        self.set_current_app(app_list[current_app_index])

    def previous_app(self):
        app_list = sorted(self.apps.keys())
        current_app_index = app_list.index(self.current_app.name)
        current_app_index = (current_app_index - 1) % len(app_list)
        self.set_current_app(app_list[current_app_index])

    def set_current_app(self, name: str):
        if name in self.apps.keys():
            # Clear reference before loading new app to allow GC to clean up
            # old_app_name = self.current_app.name if self.current_app else None
            # print(f"Memory usage with {self.current_app.name} loaded: {gc.mem_free()} bytes")
            self.current_app = None
            self.display.clear()
            # print(f"Memory usage after unloading {old_app_name}: {gc.mem_free()} bytes")
            self.current_app = self.apps[name]()
            # print(f"Available memory after loading {self.current_app.name}: {gc.mem_free()} bytes")
        else:
            raise ValueError(f"App {name} not found in {self.apps.keys()}")

    def check_for_scheduled_app_switch(self):
        now = time.localtime()
        hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec

        # At midnight change to clock
        if hour == 0 and minute == 0 and second == 0 and not isinstance(self.current_app, ClockApp):
            self.set_current_app(AnalogueClockApp.name)
        # In morning switch to images
        elif hour == 9 and minute == 0 and second == 0 and isinstance(self.current_app, GifPlayerApp):
            self.set_current_app(GifPlayerApp.name)

    def run(self) -> None:
        # print(f"Available memory before network connection: {gc.mem_free()} bytes")

        # Load splash screen before connecting to the network
        self.current_app = SplashApp(self.display, None, {"image_path": "/splash.bmp"})
        self.current_app.draw_frame()
        # Connect to the network and sync time
        self.network.connect()
        self.real_time.check_for_time_sync()
        # Switch to the gif player app
        self.set_current_app(GifPlayerApp.name)
        while True:
            # print(f"Current available memory: {gc.mem_free()} bytes")
            gc.collect()
            self.real_time.check_for_time_sync()
            self.check_for_scheduled_app_switch()

            # Handle button up - change app
            if self.button_up.is_pressed():
                self.next_app()

            # Handle button down - propagate the event to the current app
            if self.button_down.is_pressed():
                self.current_app.handle_button_down()

            # Handle accelerometer X axis - change app
            if self.accelerometer.check_next_by_axis(Axis.X):
                self.next_app()
            if self.accelerometer.check_previous_by_axis(Axis.X):
                self.previous_app()

            # Handle accelerometer Z axis - propagate the event to the current app
            if self.accelerometer.check_next_by_axis(Axis.Z):
                self.current_app.handle_accelerometer_z_next()
            if self.accelerometer.check_previous_by_axis(Axis.Z):
                self.current_app.handle_accelerometer_z_previous()

            sleep_duration = self.current_app.draw_frame()
            time.sleep(sleep_duration)


frame = RetroFrame()
frame.run()
