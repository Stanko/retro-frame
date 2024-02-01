from displayio import OnDiskBitmap, TileGrid

from src.base_app import BaseApp


class SplashApp(BaseApp):
    name = "Splash"

    def __init__(self, display, modules, settings):
        super().__init__(display, modules, settings)
        self.image_path = settings['image_path']
        self.display = display

        bitmap = OnDiskBitmap(open(self.image_path, "rb"))

        # Splash screen should always be 64x64
        self.sprite = TileGrid(
            bitmap,
            pixel_shader=bitmap.pixel_shader,
            width=1,
            height=1,
            tile_width=64,
            tile_height=64,
            x=0,
            y=0,
        )

    def draw_frame(self) -> float:
        self.display.draw(self.sprite)
        return 0.1
