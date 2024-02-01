from src.base_app import BaseApp


class BlankApp(BaseApp):
    name = "Blank"

    def __init__(self, display, modules, settings):
        super().__init__(display, modules, settings)

    def draw_frame(self) -> float:
        return 0.5
