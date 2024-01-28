import time

from displayio import OnDiskBitmap, TileGrid

from src.base_app import BaseApp
from src.utils import (compute_dimensions_and_offset, fps_from_filename,
                       frame_count_from_bitmap)


class LoopImagesApp(BaseApp):
    name = "Loop"

    def __init__(self, filepaths, display, loop_time_seconds=300):
        super().__init__()
        self.filepaths = filepaths
        self.display = display
        self.loop_time_seconds = loop_time_seconds
        self.loop_started_time = None
        self.current_image_index = 0
        self.current_frame = 0
        self.frame_duration_in_s = 0.1

        self.load_image()

    def change_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.filepaths)
        self.current_frame = 0
        self.load_image()

    def load_image(self):
        if len(self.filepaths) == 0:
            return
        self.display.clear()

        image_path = self.filepaths[self.current_image_index]
        filename = image_path.split("/")[-1]
        bitmap = OnDiskBitmap(open(image_path, "rb"))

        fps = fps_from_filename(filename)
        if fps:
            self.frame_duration_in_s = 1.0 / float(fps)
        else:
            self.frame_duration_in_s = 0.1

        tile_width, tile_height, x_offset, y_offset = compute_dimensions_and_offset(bitmap, filename)
        self.frame_count = frame_count_from_bitmap(bitmap)
        # print("filename", filename)
        # print("width", tile_width, "height", tile_height)
        # print("offset_x", x_offset, "offset_y", y_offset)
        # print("frame count", self.frame_count)
        # print("frame duration", self.frame_duration_in_s, "s")

        sprite = TileGrid(
            bitmap,
            pixel_shader=bitmap.pixel_shader,
            width=1,
            height=1,
            tile_width=tile_width,
            tile_height=tile_height,
            x=x_offset,
            y=y_offset,
        )

        self.display.draw(sprite)
        self.loop_started_time = time.time()
        self.current_frame = 0

    def handle_button_down(self):
        self.change_image()

    def draw_frame(self) -> float:
        if len(self.filepaths) == 0:
            return 0.1
        self.display.sprite_group[0][0] = self.current_frame
        self.current_frame = (self.current_frame + 1) % self.frame_count
        if self.current_frame == 0:
            # Image has been looping for max time, switch to the next one
            if (time.time() - self.loop_started_time) > self.loop_time_seconds:
                self.change_image()
        return self.frame_duration_in_s