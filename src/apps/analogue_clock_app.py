import math
import time
from collections import namedtuple

import terminalio
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_text import label

from src.base_app import BaseApp

Angles = namedtuple("Angles", ("hour", "minute", "second"))
Point = namedtuple("Point", ("x", "y"))


class AnalogueClockApp(BaseApp):
    name = "AnalogueClock"

    def __init__(self, display, modules, settings):
        super().__init__(display, modules, settings)
        self.display = display
        self.real_time_clock = modules["real_time"]
        self.font = terminalio.FONT
        self.outline_color = 0xFFFFFF
        self.fill_color = 0x000000
        self.hour_hand_color = 0xE38E05
        self.minute_hand_color = 0xE38E05
        self.second_hand_color = 0xFF0000
        self.numbers_color = 0xFFFFFF
        self.origin_x = 32
        self.origin_y = 32
        self.radius = 30
        self.hour_hand_radius = self.radius * 0.60
        self.minute_hand_radius = self.radius * 0.90
        self.second_hand_radius = self.radius * 0.95

        self.twelve = label.Label(terminalio.FONT, text="12", color=self.numbers_color, x=28, y=8)
        self.three = label.Label(terminalio.FONT, text="3", color=self.numbers_color, x=55, y=32)
        self.six = label.Label(terminalio.FONT, text="6", color=self.numbers_color, x=30, y=56)
        self.nine = label.Label(terminalio.FONT, text="9", color=self.numbers_color, x=4, y=32)

        self.hours_hand = Line(self.origin_x, self.origin_y, 32, 32, color=self.hour_hand_color)
        self.minutes_hand = Line(self.origin_x, self.origin_y, 32, 32, color=self.minute_hand_color)
        self.seconds_hand = Line(self.origin_x, self.origin_y, 32, 32, color=self.second_hand_color)

        self.circle = Circle(32, 32, self.radius, fill=self.fill_color, outline=self.outline_color)
        self.display.draw(self.circle)
        self.display.draw(self.twelve)
        self.display.draw(self.three)
        self.display.draw(self.six)
        self.display.draw(self.nine)

        # Hands must be the last to be added so they can be popped off
        self.display.draw(self.hours_hand)
        self.display.draw(self.minutes_hand)
        self.display.draw(self.seconds_hand)

    def point_on_circle(self, angle, radius) -> Point:
        x = self.origin_x + radius * math.sin(math.radians(angle))
        y = self.origin_y - radius * math.cos(math.radians(angle))
        return Point(round(x), round(y))

    def compute_angles(self, now) -> Angles:
        hour_angle = (now.tm_hour * 30) % 360
        minute_angle = (now.tm_min * 6) % 360
        second_angle = (now.tm_sec * 6) % 360
        return Angles(hour_angle, minute_angle, second_angle)

    def draw_frame(self) -> float:
        now = time.localtime()

        angles = self.compute_angles(now)
        hours_coords = self.point_on_circle(angles.hour, self.hour_hand_radius)
        minutes_coords = self.point_on_circle(angles.minute, self.minute_hand_radius)
        seconds_coords = self.point_on_circle(angles.second, self.second_hand_radius)

        self.hours_hand = Line(self.origin_x, self.origin_y, hours_coords.x, hours_coords.y, color=self.hour_hand_color)
        self.minutes_hand = Line(
            self.origin_x, self.origin_y, minutes_coords.x, minutes_coords.y, color=self.minute_hand_color
        )
        self.seconds_hand = Line(
            self.origin_x, self.origin_y, seconds_coords.x, seconds_coords.y, color=self.second_hand_color
        )

        self.display.sprite_group[-3] = self.hours_hand
        self.display.sprite_group[-2] = self.minutes_hand
        self.display.sprite_group[-1] = self.seconds_hand

        return 0.1

    def handle_button_down(self) -> None:
        self.real_time_clock.sync_time_online()
