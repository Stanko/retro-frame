import time

import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
from displayio import Group

from src.ui.animated_text import AnimatedText
from src.ui.scrolling_line import ScrollingLine


class UiComponentsDiagnostic:
    def __init__(self, width=64, height=64, bit_depth=4):
        self.matrix = Matrix(width=width, height=height, bit_depth=bit_depth, color_order="RBG")
        self.group = Group()
        self.font = self._load_font()

        self.title = label.Label(terminalio.FONT, text="UI Components", color=0xFFFF00, x=1, y=6)
        self.scroll_line = ScrollingLine(
            self.font,
            0xFFFFFF,
            text="ScrollingLine: long text moves when it does not fit.",
            x=1,
            y=15,
            align=ScrollingLine.ALIGN_LEFT,
            width=62,
            scroll_direction=ScrollingLine.SCROLL_RIGHT_TO_LEFT,
        )
        self.loading_label = label.Label(self.font, text="Loading", color=0x00B7FF, x=1, y=29)
        self.loading_dots = AnimatedText(
            self.font,
            0x00B7FF,
            character=".",
            start_x=33,
            end_x=45,
            line_y=29,
            direction=AnimatedText.DIRECTION_LEFT_TO_RIGHT,
            end_delay=0.3,
            character_spacing=4,
            step_interval_seconds=0.18,
            start_delay=0.0,
            character_count=3,
            restart=True,
        )
        self.arrows_label = label.Label(self.font, text="Inbound", color=0xFF6A00, x=1, y=41)
        self.arrows = AnimatedText(
            self.font,
            0xFF6A00,
            character="<",
            start_x=32,
            end_x=56,
            line_y=41,
            direction=AnimatedText.DIRECTION_RIGHT_TO_LEFT,
            end_delay=0.2,
            character_spacing=6,
            step_interval_seconds=0.12,
            start_delay=0.0,
            character_count=3,
            restart=True,
        )
        self.pulse_label = label.Label(self.font, text="Pulse", color=0x7CFF00, x=1, y=53)
        self.pulse = AnimatedText(
            self.font,
            0x7CFF00,
            character="=",
            start_x=24,
            end_x=54,
            line_y=53,
            direction=AnimatedText.DIRECTION_LEFT_TO_RIGHT,
            end_delay=0.4,
            character_spacing=5,
            step_interval_seconds=0.15,
            start_delay=0.1,
            character_count=2,
            restart=True,
        )

        self.group.append(self.title)
        self.scroll_line.add_to_group(self.group)
        self.group.append(self.loading_label)
        self.loading_dots.add_to_group(self.group)
        self.group.append(self.arrows_label)
        self.arrows.add_to_group(self.group)
        self.group.append(self.pulse_label)
        self.pulse.add_to_group(self.group)

        if hasattr(self.matrix.display, "root_group"):
            self.matrix.display.root_group = self.group
        else:
            self.matrix.display.show(self.group)

    def _load_font(self):
        try:
            font = bitmap_font.load_font("/assets/4by6.bdf")
            font.load_glyphs(
                b" !().:=?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>"
            )
            return font
        except Exception:
            return terminalio.FONT

    def run(self):
        now = time.monotonic()
        self.loading_dots.start(now)
        self.arrows.start(now)
        self.pulse.start(now)

        while True:
            now = time.monotonic()
            self.scroll_line.update(now)
            self.loading_dots.update(now)
            self.arrows.update(now)
            self.pulse.update(now)
            time.sleep(0.05)


UiComponentsDiagnostic().run()
