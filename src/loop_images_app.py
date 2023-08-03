import time
from re import search

from displayio import OnDiskBitmap, TileGrid

from src.base_app import BaseApp


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
        self.display.clear()

        image_path = self.filepaths[self.current_image_index]
        filename = image_path.split("/")[-1]
        bitmap = OnDiskBitmap(open(image_path, "rb"))

        # Check for "\d\dfps" pattern in the filename
        # If detected the number is used a fps value
        fps = search("(\d\d)fps", filename)
        if fps:
            self.frame_duration_in_s = 1.0 / float(fps.group(1))
        else:
            self.frame_duration_in_s = 0.1

        # Check for "(\d\d)x(\d\d)" pattern in the filename
        # If detected numbers are used as tile width and height
        size = search("(\d\d)x(\d\d)", filename)
        if size:
            tile_width = int(size.group(1))
            tile_height = int(size.group(2))

        # Detect sprite orientation
        # if there is no size in the filename, each frame is considered to be a square
        if (bitmap.height > bitmap.width):
            if not size:
                tile_width = bitmap.width
                tile_height = bitmap.width

            self.frame_count = int(bitmap.height / tile_height)
        else:
            if not size:
                tile_height = bitmap.height
                tile_width = bitmap.height

            self.frame_count = int(bitmap.width / tile_width)

        x_offset = int((64 - tile_width) / 2)
        y_offset = int((64 - tile_height) / 2)

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
        self.display.sprite_group[0][0] = self.current_frame
        self.current_frame = (self.current_frame + 1) % self.frame_count
        if self.current_frame == 0:
            # Image has been looping for max time, switch to the next one
            if (time.time() - self.loop_started_time) > self.loop_time_seconds:
                self.change_image()
        return self.frame_duration_in_s