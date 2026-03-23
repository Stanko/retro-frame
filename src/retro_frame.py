import gc
import time

from src.display_module import DisplayModule
from src.network_module import BaseNetworkModule, create_network_module
from src.real_time_module import RealTimeClockModule
from src.settings import settings
from src.splash_app import SplashApp
from src.user_input_module import UserInputModule


class RetroFrame:
    """Container class for all modules and apps."""

    def __init__(self):
        self.display: DisplayModule = DisplayModule(width=64, height=64, bit_depth=4, settings=settings.display)
        self.user_input = UserInputModule(settings.accelerometer, settings.rotary_encoder)
        self.network: BaseNetworkModule = create_network_module(settings.wifi)
        self.real_time: RealTimeClockModule = RealTimeClockModule(self.network, settings.real_time)
        self.modules = {"real_time": self.real_time}

        self.current_app = None
        self.current_app_index = 0

    def next_app(self):
        self.current_app_index = (self.current_app_index + 1) % len(settings.apps)
        self.set_current_app(self.current_app_index)

    def previous_app(self):
        self.current_app_index = (self.current_app_index - 1) % len(settings.apps)
        self.set_current_app(self.current_app_index)

    def set_current_app(self, new_app_index: int):
        # Clear reference before loading new app to allow GC to clean up
        # old_app_name = self.current_app.name if self.current_app else None
        # print(f"Memory usage with {self.current_app.name} loaded: {gc.mem_free()} bytes")
        self.current_app = None
        self.current_app_index = new_app_index
        self.display.clear()
        # print(f"Memory usage after unloading {old_app_name}: {gc.mem_free()} bytes")
        new_app = settings.apps[new_app_index]
        self.current_app = new_app.app(self.display, self.modules, new_app.settings)
        # print(f"Available memory after loading {self.current_app.name}: {gc.mem_free()} bytes")

    def check_for_scheduled_app_switch(self):
        now = time.localtime()
        hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec

        for i, app in enumerate(settings.apps):
            if (
                app.time is not None
                and hour == app.time["hour"]
                and minute == app.time["minute"]
                and second == 0
                and self.current_app_index != i
            ):
                self.set_current_app(i)
                break

    def run(self) -> None:
        # print(f"Available memory before network connection: {gc.mem_free()} bytes")
        # Load splash screen before connecting to the network
        self.current_app = SplashApp(self.display, None, {"image_path": "/assets/splash.bmp"})
        self.current_app.draw_frame()
        # Connect to the network and sync time
        self.network.connect()
        self.real_time.check_for_time_sync()
        # Switch to the gif player app
        self.set_current_app(self.current_app_index)
        while True:
            # print(f"Current available memory: {gc.mem_free()} bytes")
            gc.collect()
            self.real_time.check_for_time_sync()
            self.check_for_scheduled_app_switch()
            input_events = self.user_input.poll()

            for _ in range(input_events.next_app_steps):
                self.next_app()

            for _ in range(input_events.previous_app_steps):
                self.previous_app()

            if input_events.button_down:
                self.current_app.handle_button_down()

            if input_events.app_action_next:
                self.current_app.handle_accelerometer_z_next()
            if input_events.app_action_previous:
                self.current_app.handle_accelerometer_z_previous()

            sleep_duration = self.current_app.draw_frame()
            time.sleep(sleep_duration)


frame = RetroFrame()
frame.run()
