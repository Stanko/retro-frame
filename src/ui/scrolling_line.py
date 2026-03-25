from adafruit_display_text import label
from displayio import Group


class ScrollingLine:
    ALIGN_LEFT = "left"
    ALIGN_RIGHT = "right"
    ALIGN_CENTER = "center"
    SCROLL_RIGHT_TO_LEFT = -1
    SCROLL_LEFT_TO_RIGHT = 1
    SCROLL_STEP_PX = 1
    SCROLL_INTERVAL_SECONDS = 0.12
    SCROLL_GAP_PX = 8

    def __init__(
        self,
        font,
        color,
        text="",
        x=0,
        y=0,
        align=ALIGN_LEFT,
        width=62,
        scroll_direction=SCROLL_RIGHT_TO_LEFT,
    ):
        self.label = label.Label(font, text=text, color=color, x=x, y=y)
        self.base_x = x
        self.align = align
        self.max_width = width
        self.scroll_direction = scroll_direction
        self.last_scroll_at = 0.0
        self.scroll_offset = 0

    def add_to_group(self, group: Group) -> None:
        group.append(self.label)

    def set_color(self, color: int) -> None:
        self.label.color = color

    def set_text(self, text: str) -> None:
        if self.label.text != text:
            self.label.text = text
            self.scroll_offset = 0
            self.last_scroll_at = 0.0
        self._apply_position(force=True)

    def update(self, now: float) -> None:
        text_width = self.width()
        if text_width <= self.max_width:
            self._apply_static_position()
            return

        if (now - self.last_scroll_at) < self.SCROLL_INTERVAL_SECONDS:
            return

        self.last_scroll_at = now
        cycle_width = text_width + self.max_width + self.SCROLL_GAP_PX
        self.scroll_offset = (self.scroll_offset + self.SCROLL_STEP_PX) % cycle_width
        self.label.x = self._scroll_x(text_width)

    def width(self) -> int:
        return self.label.bounding_box[2]

    def _apply_position(self, force: bool = False) -> None:
        if self.width() <= self.max_width:
            self._apply_static_position()
            return

        if force:
            self.label.x = self._scroll_x(self.width())

    def _apply_static_position(self) -> None:
        if self.align == self.ALIGN_RIGHT:
            self.label.x = self.base_x + self.max_width - self.width()
            return

        if self.align == self.ALIGN_CENTER:
            self.label.x = self.base_x + int((self.max_width - self.width()) / 2)
            return

        self.label.x = self.base_x

    def _scroll_x(self, text_width: int) -> int:
        if self.scroll_direction == self.SCROLL_LEFT_TO_RIGHT:
            return self.base_x - text_width + self.scroll_offset
        return self.base_x + self.max_width - self.scroll_offset
