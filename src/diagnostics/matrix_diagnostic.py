import time

from adafruit_matrixportal.matrix import Matrix
from displayio import Bitmap, Group, Palette, TileGrid


class MatrixDiagnostic:
    def __init__(self, width=64, height=64, bit_depth=4):
        self.matrix = Matrix(width=width, height=height, bit_depth=bit_depth, color_order="RBG")
        self.group = Group()
        self.levels = [step / 10 for step in range(11)]
        self.colors = (
            ("red", 0xFF0000),
            ("green", 0x00FF00),
            ("blue", 0x0000FF),
            ("white", 0xFFFFFF),
        )
        self.bitmap = Bitmap(width, height, len(self.levels))
        self.palette = Palette(len(self.levels))
        self.tile_grid = TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group.append(self.tile_grid)

        if hasattr(self.matrix.display, "root_group"):
            self.matrix.display.root_group = self.group
        else:
            self.matrix.display.show(self.group)

    def scale_color(self, color, brightness):
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF

        red = int(red * brightness)
        green = int(green * brightness)
        blue = int(blue * brightness)

        return (red << 16) | (green << 8) | blue

    def render_brightness_columns(self, color):
        width = self.bitmap.width
        height = self.bitmap.height
        steps = len(self.levels)

        for index, brightness in enumerate(self.levels):
            self.palette[index] = self.scale_color(color, brightness)

        for x in range(width):
            column_index = min((x * steps) // width, steps - 1)
            for y in range(height):
                self.bitmap[x, y] = column_index

    def run(self):
        print("Starting matrix diagnostic")
        print("Rendering 11 brightness bands from 0.0 to 1.0")
        for index, brightness in enumerate(self.levels):
            print("Band", index, "brightness", brightness)

        while True:
            for name, color in self.colors:
                print("Displaying", name, "brightness bands")
                self.render_brightness_columns(color)
                time.sleep(7)


MatrixDiagnostic().run()
