import time

from adafruit_display_text import label
from displayio import Group

from src.apps.train_radar.models import AnimatedChevronRowConfig
from src.ui.animated_text import AnimatedText


class AnimatedChevronRow:
    ALIGN_LEFT = "left"
    ALIGN_RIGHT = "right"
    CENTER_GAP_SLOT_PADDING = 1

    def __init__(self, font, config):
        self.font = font
        self.config = config
        self.text_color = config.initial_text_color
        self.chevron_color = config.initial_chevron_color
        self.line_y = config.line_y
        self.content_x = config.content_x
        self.content_width = config.content_width
        self.align = config.align
        self.chevron_symbol = config.chevron_symbol
        self.chevron_count = config.chevron_count
        self.step_interval_seconds = config.step_interval_seconds
        self.character_spacing = config.character_spacing
        self.reserved_middle_text = config.reserved_middle_text

        self.group = Group()
        self.render_state = ("", False, False)

        self.middle_label = label.Label(font, text="", color=self.text_color, x=self.content_x, y=self.line_y)
        self.static_chevron_label = label.Label(font, text="", color=self.chevron_color, x=self.content_x, y=self.line_y)
        self.chevron_width = label.Label(
            font,
            text=self.chevron_symbol,
            color=self.chevron_color,
            x=self.content_x,
            y=self.line_y,
        ).bounding_box[2]
        self.hidden_slot_count = self._hidden_slot_count_for_text(self.reserved_middle_text)
        left_start_x, left_end_x, right_start_x, right_end_x = self._chevron_track()

        self.left_chevron_animation = self._build_animation(left_start_x, left_end_x, self.chevron_color, 0.0)
        self.right_chevron_animation = self._build_animation(right_start_x, right_end_x, self.chevron_color, 0.0)

        self.left_chevron_animation.add_to_group(self.group)
        self.group.append(self.static_chevron_label)
        self.group.append(self.middle_label)
        self.right_chevron_animation.add_to_group(self.group)

    def add_to_group(self, group: Group) -> None:
        group.append(self.group)

    def set_colors(self, text_color: int, chevron_color: int) -> None:
        self.text_color = text_color
        self.chevron_color = chevron_color
        self.middle_label.color = text_color
        self.static_chevron_label.color = chevron_color
        self.left_chevron_animation.set_color(chevron_color)
        self.right_chevron_animation.set_color(chevron_color)

    def render(self, text: str, show_chevron: bool, animate_chevrons: bool) -> None:
        previous_text, previous_show_chevron, previous_animate_chevrons = self.render_state
        mode_changed = show_chevron != previous_show_chevron or animate_chevrons != previous_animate_chevrons

        self.render_state = (text, show_chevron, animate_chevrons)
        self.middle_label.text = text
        self._align_middle_text()

        if animate_chevrons and text:
            self.static_chevron_label.text = ""
            if mode_changed or not previous_text:
                self._start_sequence(time.monotonic())
            return

        self._hide_current_chevrons()
        if show_chevron:
            self._show_static_chevron()
            return

        self.static_chevron_label.text = ""

    def update(self, now: float) -> None:
        left_finished = self.left_chevron_animation.update(now)
        right_finished = self.right_chevron_animation.update(now)

        if left_finished:
            self.right_chevron_animation.start(now)

        if right_finished:
            self.left_chevron_animation.start(now)

    def _align_middle_text(self) -> None:
        text_width = self.middle_label.bounding_box[2]
        self.middle_label.x = self.content_x + int((self.content_width - text_width) / 2)

    def _chevron_track(self):
        center_gap_slot_count = self.hidden_slot_count + self.CENTER_GAP_SLOT_PADDING
        # Lay out the row as: left chevrons, center timer gap, right chevrons.
        chevron_block_span = (self.chevron_count - 1) * self.character_spacing
        center_gap_span = (center_gap_slot_count + 1) * self.character_spacing
        track_width = self.chevron_width + (chevron_block_span * 2) + center_gap_span
        track_start_x = self.content_x + int((self.content_width - track_width) / 2)

        left_start_x = track_start_x
        left_end_x = left_start_x + chevron_block_span
        right_start_x = left_end_x + center_gap_span
        right_end_x = right_start_x + chevron_block_span
        return left_start_x, left_end_x, right_start_x, right_end_x

    def _hidden_slot_count_for_text(self, text: str) -> int:
        middle_width = label.Label(self.font, text=text, color=self.text_color, x=0, y=self.line_y).bounding_box[2]
        middle_width = max(middle_width, self.chevron_width)
        return max(1, int((middle_width + self.character_spacing - 1) / self.character_spacing))

    def _current_chevron_direction(self) -> int:
        if self.align == self.ALIGN_RIGHT:
            return AnimatedText.DIRECTION_RIGHT_TO_LEFT
        return AnimatedText.DIRECTION_LEFT_TO_RIGHT

    def _hide_current_chevrons(self) -> None:
        self.left_chevron_animation.stop()
        self.right_chevron_animation.stop()

    def _show_static_chevron(self) -> None:
        self.static_chevron_label.text = self.chevron_symbol
        self.static_chevron_label.x = self.content_x + int((self.content_width - self.chevron_width) / 2)

    def _start_sequence(self, now: float) -> None:
        self.left_chevron_animation.stop()
        self.right_chevron_animation.stop()
        if self.align == self.ALIGN_RIGHT:
            self.right_chevron_animation.start(now)
            return
        self.left_chevron_animation.start(now)

    def _build_animation(self, start_x: int, end_x: int, color: int, end_delay: float, direction=None) -> AnimatedText:
        if direction is None:
            direction = self._current_chevron_direction()
        return AnimatedText(
            self.font,
            color,
            character=self.chevron_symbol,
            start_x=start_x,
            end_x=end_x,
            line_y=self.line_y,
            direction=direction,
            end_delay=end_delay,
            character_spacing=self.character_spacing,
            step_interval_seconds=self.step_interval_seconds,
            start_delay=0.0,
            character_count=self.chevron_count,
            restart=False,
        )
