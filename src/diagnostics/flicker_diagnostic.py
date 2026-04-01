import time

import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
from displayio import Bitmap, Group, Palette, TileGrid


class FlickerDiagnostic:
    def __init__(self, width=64, height=64, bit_depth=4):
        self.matrix = Matrix(width=width, height=height, bit_depth=bit_depth, color_order="RBG")
        self.group = Group()
        self.font = self._load_font()
        self.bitmap = Bitmap(width, height, 4)
        self.palette = Palette(4)
        self.tile_grid = TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group.append(self.tile_grid)
        self.text_labels = (
            label.Label(self.font, text="", color=0x000000, x=1, y=14),
            label.Label(self.font, text="", color=0x000000, x=1, y=26),
            label.Label(self.font, text="", color=0x000000, x=1, y=38),
            label.Label(self.font, text="", color=0x000000, x=1, y=50),
        )
        for text_label in self.text_labels:
            self.group.append(text_label)
        self.pages = (
            ("full white", self.render_fullscreen, (0xFFFFFF,)),
            ("full gray", self.render_fullscreen, (0x808080,)),
            ("full red", self.render_fullscreen, (0xFF0000,)),
            ("full green", self.render_fullscreen, (0x00FF00,)),
            ("full blue", self.render_fullscreen, (0x0000FF,)),
            ("white gray split", self.render_vertical_split, (0xFFFFFF, 0x808080)),
            ("rgb split", self.render_vertical_triples, (0xFF0000, 0x00FF00, 0x0000FF)),
            ("gray steps", self.render_vertical_triples, (0x404040, 0x808080, 0xC0C0C0)),
            ("white text", self.render_text_page, (0x000000, 0xFFFFFF, ("NS Internatio", "Amsterdam", "24s < < <", "Rotterdam"))),
            ("gray text", self.render_text_page, (0x000000, 0x999999, ("NS Intercity", "Utrecht", "Next 1:24", "Heerlen"))),
        )

        if hasattr(self.matrix.display, "root_group"):
            self.matrix.display.root_group = self.group
        else:
            self.matrix.display.show(self.group)

    def _load_font(self):
        try:
            font = bitmap_font.load_font("/assets/4by6.bdf")
            font.load_glyphs(b" !().:/<>?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            return font
        except Exception:
            return terminalio.FONT

    def clear_text(self):
        for text_label in self.text_labels:
            text_label.text = ""

    def render_fullscreen(self, color):
        self.clear_text()
        self.palette[0] = color
        for x in range(self.bitmap.width):
            for y in range(self.bitmap.height):
                self.bitmap[x, y] = 0

    def render_vertical_split(self, left_color, right_color):
        self.clear_text()
        self.palette[0] = left_color
        self.palette[1] = right_color
        midpoint = int(self.bitmap.width / 2)
        for x in range(self.bitmap.width):
            color_index = 0 if x < midpoint else 1
            for y in range(self.bitmap.height):
                self.bitmap[x, y] = color_index

    def render_vertical_triples(self, left_color, middle_color, right_color):
        self.clear_text()
        self.palette[0] = left_color
        self.palette[1] = middle_color
        self.palette[2] = right_color
        segment_width = int(self.bitmap.width / 3)
        for x in range(self.bitmap.width):
            if x < segment_width:
                color_index = 0
            elif x < (segment_width * 2):
                color_index = 1
            else:
                color_index = 2
            for y in range(self.bitmap.height):
                self.bitmap[x, y] = color_index

    def render_text_page(self, background_color, text_color, lines):
        self.render_fullscreen(background_color)
        for index, text_label in enumerate(self.text_labels):
            text_label.color = text_color
            text_label.text = lines[index] if index < len(lines) else ""

    def run(self):
        print("Starting flicker diagnostic")
        while True:
            for name, render, args in self.pages:
                print("Displaying", name)
                render(*args)
                time.sleep(7)


FlickerDiagnostic().run()
