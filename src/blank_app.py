from src.base_app import BaseApp

class BlankApp(BaseApp):
    name = "Blank"

    def __init__(self, display, modules=None, settings=None):
        super().__init__()
        display.clear()

    def draw_frame(self) -> float:
        return 0.5
