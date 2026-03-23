import time

from adafruit_matrixportal.matrix import Matrix
from displayio import Bitmap, Group, Palette, TileGrid


class BitDepthDiagnostic:
    def __init__(self, width=64, height=64, bit_depths=(3, 4, 5)):
        self.width = width
        self.height = height
        self.bit_depths = bit_depths
        self.current_matrix = None
        self.current_group = None

    def _show_gradient(self, bit_depth):
        self.current_matrix = Matrix(
            width=self.width,
            height=self.height,
            bit_depth=bit_depth,
            color_order="RBG",
        )
        self.current_group = Group()

        bitmap = Bitmap(self.width, self.height, self.width)
        palette = Palette(self.width)

        for x in range(self.width):
            value = int((x / (self.width - 1)) * 255)
            palette[x] = (value << 16) | (value << 8) | value
            for y in range(self.height):
                bitmap[x, y] = x

        tile_grid = TileGrid(bitmap, pixel_shader=palette)
        self.current_group.append(tile_grid)

        if hasattr(self.current_matrix.display, "root_group"):
            self.current_matrix.display.root_group = self.current_group
        else:
            self.current_matrix.display.show(self.current_group)

    def _cleanup(self):
        if self.current_matrix is not None and hasattr(self.current_matrix.display, "root_group"):
            self.current_matrix.display.root_group = None
        self.current_group = None
        self.current_matrix = None

    def run(self):
        print("Starting bit depth diagnostic")
        print("Displaying grayscale gradient for each bit depth")

        while True:
            for bit_depth in self.bit_depths:
                print("Displaying bit depth", bit_depth)
                self._show_gradient(bit_depth)
                time.sleep(7)
                self._cleanup()


BitDepthDiagnostic().run()
