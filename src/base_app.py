from src.display_module import DisplayModule


class BaseApp:
    name = "BaseApp"

    def __init__(self, display: DisplayModule, modules: dict, settings: dict = None):
        self.display = display
        self.modules = modules
        self.settings = settings or {}

    def draw_frame(self) -> float:
        raise Exception(f"Draw frame function is not implemented for app {self.name}")

    def handle_button_down(self) -> None:
        print(f"Handle button down not implemented for app {self.name}")
        return

    def handle_accelerometer_z_next(self) -> None:
        print(f"Handle accelerometer z next not implemented for app {self.name}")
        return

    def handle_accelerometer_z_previous(self) -> None:
        print(f"Handle accelerometer z previous not implemented for app {self.name}")
        return

    # When you print an object from BaseApp it will print its internal state
    def __repr__(self):
        return " ".join([f"{key}={self.__dict__[key]}" for key in self.__dict__])
