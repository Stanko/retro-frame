import gc

from adafruit_matrixportal.matrix import Matrix
from displayio import Group, TileGrid
from src.settings_utils import DisplaySettings


class DisplayModule:
    def __init__(self, width: int, height: int, bit_depth: int, settings: DisplaySettings):
        self.matrix = Matrix(
            width=width,
            height=height,
            bit_depth=bit_depth,
            color_order=settings.color_order,
        )
        self.sprite_group = Group()
        if hasattr(self.matrix.display, "root_group"):
            self.matrix.display.root_group = self.sprite_group
        else:
            self.matrix.display.show(self.sprite_group)

    def clear(self) -> None:
        while self.sprite_group:
            self.sprite_group.pop()
        gc.collect()

    def draw(self, sprite: TileGrid) -> None:
        self.sprite_group.append(sprite)
