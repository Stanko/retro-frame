import time

import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
from displayio import Group


class FontDiagnostic:
    def __init__(self, width=64, height=64, bit_depth=4):
        self.matrix = Matrix(width=width, height=height, bit_depth=bit_depth, color_order="RBG")
        self.group = Group()
        self.font = self._load_font()
        self.pages = (
            ("digits", ("0123456789", "11:58 23:47", "0 1 2 3 4 5", "6 7 8 9  : /")),
            ("uppercase", ("ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ", "RETRO FRAME")),
            ("lowercase", ("abcdefghij", "klmnopqrst", "uvwxyz", "time wifi rtc")),
            ("mixed", ("Aa Bb Cc Dd", "Ee Ff Gg Hh", "Ii Jj Kk Ll", "Mm Nn Oo Pp")),
            ("symbols", ("! ? . , : ;", "+ - = / \\", "( ) [ ] { }", "# % @ * &")),
        )

        if hasattr(self.matrix.display, "root_group"):
            self.matrix.display.root_group = self.group
        else:
            self.matrix.display.show(self.group)

    def _load_font(self):
        try:
            font = bitmap_font.load_font("/assets/4by6.bdf")
            font.load_glyphs(b" !?.,:;+-=/\\()[]{}#%@*&0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            print("Loaded font: /assets/4by6.bdf")
            return font
        except Exception as error:
            print("Falling back to terminalio.FONT:", error)
            return terminalio.FONT

    def clear(self):
        while self.group:
            self.group.pop()

    def render_page(self, name, lines):
        self.clear()

        header = label.Label(terminalio.FONT, text=name, color=0xFFFF00, x=1, y=6)
        self.group.append(header)

        y = 14
        for line in lines:
            self.group.append(label.Label(self.font, text=line, color=0xFFFFFF, x=1, y=y))
            y += 8

    def run(self):
        print("Starting font diagnostic")
        if self.font is terminalio.FONT:
            print("Using terminalio.FONT")
        else:
            print("Using /assets/4by6.bdf")

        while True:
            for name, lines in self.pages:
                print("Displaying page:", name)
                self.render_page(name, lines)
                time.sleep(7)


FontDiagnostic().run()
