import time
from re import search

import displayio
import gifio

from src.base_app import BaseApp
from src.utils import compute_dimensions_and_offset, fps_from_filename


class GifPlayerApp(BaseApp):
    name = "GifPlayer"

    def __init__(self, filepaths, display, loop_time_seconds=300):
        super().__init__()
        self.filepaths = filepaths
        self.display = display
        self.current_image_index = 0
        self.current_frame = 0
        self.current_gif = None
        self.current_git_start_time = None
        self.loop_time_seconds = loop_time_seconds
        self.fps = None

        self.load_gif()

    def load_gif(self):
        if len(self.filepaths) == 0:
            return
        # Stop reference to the current gif so GC can clean it up
        if self.current_gif:
            self.current_gif.deinit()
        self.current_gif = None
        self.display.clear()

        image_path = self.filepaths[self.current_image_index]
        filename = image_path.split("/")[-1]
        self.current_gif = gifio.OnDiskGif(image_path)
        self.fps = fps_from_filename(filename)

        tile_width, tile_height, x_offset, y_offset = compute_dimensions_and_offset(self.current_gif.bitmap, filename)
        sprite = displayio.TileGrid(
            self.current_gif.bitmap,
            pixel_shader=displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565_SWAPPED),
            width=1,
            height=1,
            tile_width=tile_width,
            tile_height=tile_height,
            x=x_offset,
            y=y_offset,
        )

        self.display.draw(sprite)
        self.current_frame = 0
        self.current_git_start_time = time.time()

    def next_gif(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.filepaths)
        self.load_gif()

    def handle_button_down(self) -> None:
        self.next_gif()

    def draw_frame(self) -> float:
        if self.current_gif is None:
            return 0.1
        self.current_frame += 1
        if self.current_frame == self.current_gif.frame_count:
            self.current_frame = 0
            if (time.time() - self.current_git_start_time) > self.loop_time_seconds:
                self.next_gif()
        suggested = self.current_gif.next_frame()
        if self.fps is None:
            return suggested
        else:
            return float(1 / self.fps)
