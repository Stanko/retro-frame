import gc

from adafruit_matrixportal.matrix import Matrix
from displayio import Group, TileGrid


class DisplayModule:
    def __init__(self, width: int, height: int, bit_depth: int):
        self.matrix = Matrix(width=width, height=height, bit_depth=bit_depth)
        self.sprite_group = Group()
        self.matrix.display.show(self.sprite_group)

    def clear(self) -> None:
        while self.sprite_group:
            self.sprite_group.pop()
        gc.collect()

    def draw(self, sprite: TileGrid) -> None:
        self.sprite_group.append(sprite)
