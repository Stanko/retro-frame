import time
from os import listdir

from board import BUTTON_DOWN, BUTTON_UP

from src.button_module import ButtonModule
from src.clock_app import ClockApp
from src.display_module import DisplayModule
from src.loop_images_app import LoopImagesApp
from src.network_module import NetworkModule


class RetroFrame:
    """Container class for all modules and apps."""
    def __init__(self, bmp_folder: str = "/bmp", skip_connection: bool = False):
        self.button_up: ButtonModule = ButtonModule(button_ref=BUTTON_UP)
        self.button_down: ButtonModule = ButtonModule(button_ref=BUTTON_DOWN)
        self.display: DisplayModule = DisplayModule(width=64, height=64, bit_depth=4)
        self.network: NetworkModule = NetworkModule(skip_connection=skip_connection)

        self.bmp_folder =bmp_folder
        self.bmp_file_list = sorted(
            [
                f"{self.bmp_folder}/{f}"
                for f in listdir(self.bmp_folder)
                if (f.endswith(".bmp") and not f.startswith("."))
            ]
        )
        self.current_app = None
        # Store anonymous functions that return app objects to preserve memory
        # Dictonary order is irrelevant, it will be sorted when switching apps
        self.apps = {
            LoopImagesApp.name: lambda: LoopImagesApp(self.bmp_file_list, self.display),
            ClockApp.name: lambda: ClockApp(self.display, self.network),
        }

    def next_app(self):
        app_list = sorted(self.apps.keys())
        current_app_index = app_list.index(self.current_app.name)
        current_app_index = (current_app_index + 1) % len(app_list)
        self.current_app = self.apps[app_list[current_app_index]]()
    
    def set_current_app(self, name: str):
        if name in self.apps.keys():
            self.current_app = self.apps[name]()
        else:
            raise ValueError(f"App {name} not found in {self.apps.keys()}")

    def check_for_scheduled_app_switch(self):
        now = time.localtime()
        hour, minute, second = now.tm_hour, now.tm_min, now.tm_sec
        # At midnight change to clock
        if hour == 0 and minute == 0 and second == 0 and not isinstance(self.current_app, ClockApp):
            self.set_current_app(ClockApp.name)
        # In morning switch to images
        elif hour == 9 and minute == 0 and second == 0 and isinstance(self.current_app, ClockApp):
            self.set_current_app(LoopImagesApp.name)
    
    def run(self) -> None:
        self.current_app = LoopImagesApp(["./splash.bmp"], self.display)
        self.current_app.draw_frame()
        self.network.connect()
        self.next_app()
        while True:
            self.check_for_scheduled_app_switch()

            # Handle button up - change app
            if self.button_up.is_pressed():
                self.next_app()
            
            if self.button_down.is_pressed():
                self.current_app.handle_button_down()
            
            sleep_duration = self.current_app.draw_frame()
            time.sleep(sleep_duration)

frame = RetroFrame("/bmp", skip_connection=False)
frame.run()