import time

from adafruit_display_text import label
from displayio import Group


class AnimatedText:
    DIRECTION_LEFT_TO_RIGHT = 1
    DIRECTION_RIGHT_TO_LEFT = -1
    STATE_IDLE = "idle"
    STATE_WAITING_START = "waiting_start"
    STATE_RUNNING = "running"
    STATE_WAITING_END = "waiting_end"

    def __init__(
        self,
        font,
        color,
        character=">",
        start_x=0,
        end_x=0,
        line_y=0,
        direction=DIRECTION_LEFT_TO_RIGHT,
        end_delay=0.0,
        character_spacing=6,
        step_interval_seconds=0.25,
        start_delay=0.0,
        character_count=1,
        restart=True,
    ):
        self.font = font
        self.character = character
        self.start_x = start_x
        self.end_x = end_x
        self.line_y = line_y
        self.direction = direction
        self.end_delay = end_delay
        self.character_spacing = character_spacing
        self.step_interval_seconds = step_interval_seconds
        self.start_delay = start_delay
        self.character_count = character_count
        self.restart = restart

        self.labels = []
        for _ in range(character_count):
            self.labels.append(label.Label(font, text="", color=color, x=start_x, y=line_y))

        self.slot_count = 1
        self.step_index = 0
        self.state = self.STATE_IDLE
        self.wait_until = 0.0
        self.next_step_at = None
        self._recalculate_slot_count()
        self.stop()

    def add_to_group(self, group: Group) -> None:
        for animated_label in self.labels:
            group.append(animated_label)

    def set_color(self, color: int) -> None:
        for animated_label in self.labels:
            animated_label.color = color

    def start(self, now=None) -> None:
        if now is None:
            now = time.monotonic()
        self.step_index = 0
        self.wait_until = now + self.start_delay
        self.next_step_at = None
        self.state = self.STATE_WAITING_START
        self._hide()

    def stop(self) -> None:
        self.step_index = 0
        self.state = self.STATE_IDLE
        self.wait_until = 0.0
        self.next_step_at = None
        self._hide()

    def reset(self, now=None) -> None:
        if now is None:
            now = time.monotonic()
        self.start(now)

    def update(self, now: float) -> bool:
        if self.step_interval_seconds <= 0:
            self.step_index = 0
            self._apply_step()
            return False

        if self.state == self.STATE_IDLE:
            return False

        if self.state == self.STATE_WAITING_START:
            if now < self.wait_until:
                return False

            self.state = self.STATE_RUNNING
            self.step_index = 0
            self._apply_step()
            self.next_step_at = now + self.step_interval_seconds
            return False

        if self.state == self.STATE_WAITING_END:
            if now < self.wait_until:
                return False

            if self.restart:
                self.start(now)
                return False

            self.stop()
            return True

        if now < self.next_step_at:
            return False

        self.step_index += 1
        if self.step_index >= self.total_steps():
            self.state = self.STATE_WAITING_END
            self.wait_until = now + self.end_delay
            self.next_step_at = None
            self._hide()
            if self.end_delay <= 0:
                if self.restart:
                    self.start(now)
                    return False
                self.stop()
                return True
            return False

        self._apply_step()
        self.next_step_at = now + self.step_interval_seconds
        return False

    def total_steps(self) -> int:
        return self.slot_count + self.character_count - 1

    def active_duration_seconds(self) -> float:
        return self.total_steps() * self.step_interval_seconds

    def animation_duration_seconds(self) -> float:
        return self.start_delay + self.active_duration_seconds() + self.end_delay

    def _apply_step(self) -> None:
        for index, animated_label in enumerate(self.labels):
            if self.direction == self.DIRECTION_RIGHT_TO_LEFT:
                slot_index = (self.slot_count - 1 - self.step_index) + index
            else:
                slot_index = self.step_index - index

            if 0 <= slot_index < self.slot_count:
                animated_label.text = self.character
                animated_label.x = self.start_x + (slot_index * self.character_spacing)
                continue

            animated_label.text = ""

    def _hide(self) -> None:
        for animated_label in self.labels:
            animated_label.text = ""

    def _recalculate_slot_count(self) -> None:
        width = abs(self.end_x - self.start_x)
        self.slot_count = max(1, int(width / self.character_spacing) + 1)
