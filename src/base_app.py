class BaseApp:
    name = "BaseApp"
    def __init__(self):
        pass

    def draw_frame(self) -> float:
        raise (f"Draw frame function is not implemented for app {self.name}")

    def handle_button_down(self) -> None:
        raise (f"Handle button down not implemented for app {self.name}")

    # When you print an object from BaseApp it will print its internal state
    def __repr__(self):
        return " ".join([f"{key}={self.__dict__[key]}" for key in self.__dict__])
