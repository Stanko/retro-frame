import math
import time

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from displayio import Bitmap, Group, Palette, TileGrid

from src.base_app import BaseApp
from src.apps.train_radar.animated_chevron_row import AnimatedChevronRow, AnimatedChevronRowConfig
from src.apps.train_radar.data_polling import DataPolling
from src.apps.train_radar.models import (
    RadarHalfPanelConfig,
    RadarPanelState,
    TrainRadarAnimationConfig,
    TrainRadarConfig,
    TrainRadarContentConfig,
    TrainRadarDisplayConfig,
    TrainRadarPanelLayoutConfig,
    TrainRadarStyleConfig,
)
from src.ui.scrolling_line import ScrollingLine


MOCK = None
SEPARATOR_Y = 31


TRAIN_RADAR_CONFIG = TrainRadarConfig(
    display=TrainRadarDisplayConfig(
        font_glyphs=b" '()&+,-./0123456789:;<>?=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz",
        font_path="/assets/4by6.bdf",
        frame_interval_seconds=0.05,
        layout_refresh_seconds=1.0,
        divider_color=0xffffff,
    ),
    panel_layout=TrainRadarPanelLayoutConfig(
        font_height=6,
        padding=1,
        line_gap=2,
        panel_width=64,
        badge_size=6,
        badge_gap=1,
        badge_hidden_x=-10,
        badge_y=0,
    ),
    animation=TrainRadarAnimationConfig(
        chevron_count=3,
        chevron_interval_seconds=0.25,
        chevron_spacing=6,
    ),
    style=TrainRadarStyleConfig(
        upcoming_line_colors=(
            0xFF3D00,
            0xFFFFFF,
            0xFFFFFF,
            0xFFFFFF,
        ),
        current_line_colors=(
            0xFFFFFF,
            0xFFFFFF,
            0xFF3D00,
            0xFFFFFF,
        ),
        company_icon_colors={
            "NS": (0xFFD400, 0x003082),
            "ICE": (0xFFFFFF, 0xDB0011),
            "NS_INT": (0xFFFFFF, 0x003082),
        },
    ),
    content=TrainRadarContentConfig(
        station_label_replacements={
            "Amsterdam Centraal": "Amsterdam",
            "Rotterdam Centraal": "Rotterdam",
            "Eindhoven Centraal": "Eindhoven",
            "Frankfurt (M) Hbf": "Frankfurt",
            "Driebergen-Zeist": "Driebergen-Z",
            "Utrecht Centraal": "Utrecht",
        },
        right_chevron_symbol="<",
        left_chevron_symbol=">",
        company_badge_pixels=(
            (0, 0, 1, 2, 0, 0),
            (0, 1, 1, 2, 2, 0),
            (1, 1, 1, 2, 2, 2),
            (1, 1, 1, 2, 2, 2),
            (0, 1, 1, 2, 2, 0),
            (0, 0, 1, 2, 0, 0),
        ),
    ),
)


class RadarHalfPanel:
    ALIGN_LEFT = "left"
    ALIGN_RIGHT = "right"

    def __init__(self, font, config):
        self.font = font
        self.config = config
        self.top_y = config.top_y
        self.scroll_direction = config.scroll_direction
        self.layout = config.layout
        self.animation = config.animation
        self.content = config.content

        self.render_state = RadarPanelState(line_colors=config.initial_line_colors)

        self.company_badge_palette = Palette(3)
        self.company_badge_palette[0] = 0x000000
        self.company_badge_palette[1] = 0x000000
        self.company_badge_palette[2] = 0x000000
        self.company_badge_palette.make_transparent(0)

        self.company_badge = TileGrid(
            self._build_company_badge_bitmap(),
            pixel_shader=self.company_badge_palette,
            x=self.layout.badge_hidden_x,
            y=self.top_y + self.layout.padding + self.layout.badge_y,
        )
        self.header_label = label.Label(
            font,
            text="",
            color=config.initial_line_colors[0],
            x=0,
            y=self.y_pos_by_line_index(0),
        )
        self.origin_line = ScrollingLine(
            font,
            config.initial_line_colors[1],
            text="",
            x=self.layout.padding,
            y=self.y_pos_by_line_index(1),
            align=ScrollingLine.ALIGN_CENTER,
            width=self.layout.content_width,
            scroll_direction=self.scroll_direction,
        )
        self.middle_row = AnimatedChevronRow(
            font,
            AnimatedChevronRowConfig(
                line_y=self.y_pos_by_line_index(2),
                content_x=self.layout.padding,
                content_width=self.layout.content_width,
                align=config.align,
                chevron_symbol=config.chevron_symbol,
                initial_text_color=config.initial_line_colors[0],
                initial_chevron_color=config.initial_line_colors[2],
                chevron_count=self.animation.chevron_count,
                step_interval_seconds=self.animation.chevron_interval_seconds,
                character_spacing=self.animation.chevron_spacing,
                reserved_middle_text="-60s",
            ),
        )
        self.destination_line = ScrollingLine(
            font,
            config.initial_line_colors[3],
            text="",
            x=self.layout.padding,
            y=self.y_pos_by_line_index(3),
            align=ScrollingLine.ALIGN_CENTER,
            width=self.layout.content_width,
            scroll_direction=self.scroll_direction,
        )

    def add_to_group(self, group: Group) -> None:
        group.append(self.company_badge)
        group.append(self.header_label)
        self.origin_line.add_to_group(group)
        self.middle_row.add_to_group(group)
        self.destination_line.add_to_group(group)

    def render(self, state: RadarPanelState) -> None:
        self.render_state = state

        self._apply_line_colors(state.line_colors)
        self._apply_company_badge_colors(state.company_badge_colors)
        self.header_label.text = state.header_text
        self._align_header()
        self.origin_line.set_text(state.origin_text)
        self.middle_row.render(state.middle_text, state.show_chevron, state.animate_chevrons)
        self.destination_line.set_text(state.destination_text)

    def update(self, now: float) -> None:
        self.origin_line.update(now)
        self.destination_line.update(now)
        self.middle_row.update(now)

    def y_pos_by_line_index(self, line_index: int) -> int:
        half_font_height = int(self.layout.font_height / 2)
        if line_index == 0:
            return self.top_y + self.layout.padding + half_font_height

        line_height = self.layout.font_height + self.layout.line_gap
        return self.top_y + self.layout.padding + half_font_height + (line_height * line_index)

    def _align_header(self) -> None:
        text_width = self.header_label.bounding_box[2]
        badge_colors = self.render_state.company_badge_colors
        if badge_colors is None:
            self.company_badge.x = self.layout.badge_hidden_x
            self.header_label.x = self.layout.padding + int((self.layout.panel_width - text_width) / 2)
            return

        block_width = self.layout.badge_size + self.layout.badge_gap + text_width
        block_x = self.layout.padding + int((self.layout.panel_width - block_width) / 2)
        self.company_badge.x = block_x
        self.header_label.x = block_x + self.layout.badge_size + self.layout.badge_gap

    def _apply_line_colors(self, line_colors) -> None:
        self.header_label.color = line_colors[0]
        self.origin_line.set_color(line_colors[1])
        self.middle_row.set_colors(line_colors[0], line_colors[2])
        self.destination_line.set_color(line_colors[3])

    def _apply_company_badge_colors(self, badge_colors) -> None:
        if badge_colors is None:
            self.company_badge.x = self.layout.badge_hidden_x
            return

        self.company_badge_palette[1] = badge_colors[0]
        self.company_badge_palette[2] = badge_colors[1]

    def _build_company_badge_bitmap(self):
        bitmap = Bitmap(self.layout.badge_size, self.layout.badge_size, 3)
        for y, row in enumerate(self.content.company_badge_pixels):
            for x, color_index in enumerate(row):
                bitmap[x, y] = color_index
        return bitmap


class TrainRadarApp(BaseApp):
    name = "TrainRadar"

    def __init__(self, display, modules, settings):
        super().__init__(display, modules, settings)
        self.config = TRAIN_RADAR_CONFIG
        self.display = display
        self.network = modules["network"]
        self.font = self.load_font(self.config.display.font_path, self.config.display.font_glyphs)
        self.polling = DataPolling(
            self.network,
            self.settings["url"],
            self.settings["poll_interval_seconds"],
            mock=MOCK,
        )

        self.root_group = Group()
        self.display.draw(self.root_group)
        self.root_group.append(self._build_separator())

        self.top_panel = RadarHalfPanel(
            self.font,
            RadarHalfPanelConfig(
                top_y=0,
                align=RadarHalfPanel.ALIGN_RIGHT,
                scroll_direction=ScrollingLine.SCROLL_RIGHT_TO_LEFT,
                chevron_symbol=self.config.content.right_chevron_symbol,
                initial_line_colors=self.config.style.upcoming_line_colors,
                layout=self.config.panel_layout,
                animation=self.config.animation,
                content=self.config.content,
            ),
        )
        self.bottom_panel = RadarHalfPanel(
            self.font,
            RadarHalfPanelConfig(
                top_y=32,
                align=RadarHalfPanel.ALIGN_LEFT,
                scroll_direction=ScrollingLine.SCROLL_LEFT_TO_RIGHT,
                chevron_symbol=self.config.content.left_chevron_symbol,
                initial_line_colors=self.config.style.upcoming_line_colors,
                layout=self.config.panel_layout,
                animation=self.config.animation,
                content=self.config.content,
            ),
        )
        self.top_panel.add_to_group(self.root_group)
        self.bottom_panel.add_to_group(self.root_group)

        self.last_layout_update_at = None
        self.last_rendered_data_fetched_at = None

        self.polling.refresh(force=True)
        self._render_layout(time.monotonic())
        self.last_layout_update_at = time.monotonic()
        self.last_rendered_data_fetched_at = self.polling.data_fetched_at

    def draw_frame(self) -> float:
        now = time.monotonic()
        now = self.polling.refresh(force=self._should_force_data_refresh(now))
        if self._should_render_layout(now):
            self._render_layout(now)
            self.last_layout_update_at = now
            self.last_rendered_data_fetched_at = self.polling.data_fetched_at

        self.top_panel.update(now)
        self.bottom_panel.update(now)
        return self.config.display.frame_interval_seconds

    def handle_button_down(self) -> None:
        self.polling.refresh(force=True)

    def handle_accelerometer_z_next(self) -> None:
        self.polling.refresh(force=True)

    def handle_accelerometer_z_previous(self) -> None:
        self.polling.refresh(force=True)

    def load_font(self, font_path: str, font_glyphs: bytes):
        font = bitmap_font.load_font(font_path)
        font.load_glyphs(font_glyphs)
        return font

    def _build_separator(self):
        bitmap = Bitmap(self.config.panel_layout.panel_width, 1, 1)
        palette = Palette(1)
        palette[0] = self.config.display.divider_color
        return TileGrid(bitmap, pixel_shader=palette, x=0, y=SEPARATOR_Y)

    def _should_render_layout(self, now: float) -> bool:
        if self.last_layout_update_at is None:
            return True

        if self.polling.data_fetched_at != self.last_rendered_data_fetched_at:
            return True

        return (now - self.last_layout_update_at) >= self.config.display.layout_refresh_seconds

    def _should_force_data_refresh(self, now: float) -> bool:
        if self.polling.data is None or self.polling.data_fetched_at is None:
            return False

        elapsed = self._elapsed_since_last_fetch(now)
        current = self.polling.data.get("current") or {}
        upcoming = self.polling.data.get("upcoming") or {}

        return self._upcoming_timer_expired(current.get("right"), upcoming.get("right"), elapsed) or self._upcoming_timer_expired(
            current.get("left"),
            upcoming.get("left"),
            elapsed,
        )

    def _render_layout(self, now: float) -> None:
        if self.polling.data is None:
            self._render_empty_layout()
            return

        elapsed = self._elapsed_since_last_fetch(now)
        current = self.polling.data.get("current") or {}
        upcoming = self.polling.data.get("upcoming") or {}

        self.top_panel.render(
            self._build_panel_state(
                current.get("right"),
                upcoming.get("right"),
                elapsed,
            )
        )
        self.bottom_panel.render(
            self._build_panel_state(
                current.get("left"),
                upcoming.get("left"),
                elapsed,
            )
        )

    def _render_empty_layout(self) -> None:
        if self.polling.last_error is None:
            top_state = RadarPanelState(
                header_text="Loading",
                line_colors=self.config.style.upcoming_line_colors,
            )
            bottom_state = RadarPanelState(
                header_text="Polling {}".format(self.format_seconds(int(self.polling.poll_interval_seconds))),
                line_colors=self.config.style.upcoming_line_colors,
            )
        else:
            top_state = RadarPanelState(
                header_text="API error",
                line_colors=self.config.style.upcoming_line_colors,
            )
            bottom_state = RadarPanelState(
                header_text=self.fit_text_to_width(
                    self.sanitize_text(self.polling.last_error),
                    self.config.panel_layout.content_width,
                ),
                line_colors=self.config.style.upcoming_line_colors,
            )

        self.top_panel.render(top_state)
        self.bottom_panel.render(bottom_state)

    def _build_panel_state(self, current_train, upcoming_train, elapsed_seconds: float) -> RadarPanelState:
        active_train = current_train or upcoming_train
        is_current = current_train is not None

        if active_train is None:
            return RadarPanelState(
                header_text="No train",
                line_colors=self.config.style.upcoming_line_colors,
            )

        badge_colors = self.company_icon_colors(active_train) if is_current else None
        line_colors = self.config.style.current_line_colors if is_current else self.config.style.upcoming_line_colors
        header_max_width = self.config.panel_layout.panel_width
        if badge_colors is not None:
            header_max_width -= self.config.panel_layout.badge_size + self.config.panel_layout.badge_gap

        return RadarPanelState(
            header_text=self.fit_text_to_width(
                self._header_text_for_train(active_train, is_current, elapsed_seconds),
                header_max_width,
            ),
            origin_text=self.sanitize_text(self._train_value(active_train, "origin") or ""),
            destination_text=self.sanitize_text(self._train_value(active_train, "destination") or ""),
            middle_text=self._current_middle_text(active_train, elapsed_seconds) if is_current else "",
            line_colors=line_colors,
            show_chevron=True,
            animate_chevrons=is_current,
            company_badge_colors=badge_colors,
        )

    def _upcoming_timer_expired(self, current_train, upcoming_train, elapsed_seconds: float) -> bool:
        if current_train is not None or upcoming_train is None:
            return False

        remaining = self.remaining_seconds(upcoming_train.get("seconds_until_range"), elapsed_seconds)
        if remaining is None:
            return False
        return remaining <= 0

    def _header_text_for_train(self, train_data, is_current: bool, elapsed_seconds: float) -> str:
        if is_current:
            return self._current_header_text(train_data)
        return self._upcoming_header_text(train_data, elapsed_seconds)

    def _current_header_text(self, train_data) -> str:
        company = self._train_value(train_data, "company", default="--")
        train_type = self._train_value(train_data, "train_type", default="--")
        if company.lower() == "ice":
            return company
        if company.lower() == "ns_int":
            return "NS Internatio"
        else:
            return f"{company} {train_type}".strip()

    def _upcoming_header_text(self, train_data, elapsed_seconds: float) -> str:
        seconds = self.remaining_seconds(train_data.get("seconds_until_range"), elapsed_seconds)
        if seconds is None:
            return "Next --"
        return "Next {}".format(self.format_seconds(seconds))

    def _current_middle_text(self, train_data, elapsed_seconds: float) -> str:
        seconds = self.signed_remaining_seconds(train_data.get("seconds_until_target"), elapsed_seconds)
        if seconds is None:
            return "--s"
        return "{}s".format(seconds)

    def fit_text_to_width(self, text: str, max_width: int) -> str:
        text = self.sanitize_text(text)
        if self.measure_text_width(text) <= max_width:
            return text

        shortened = text
        while len(shortened) > 1 and self.measure_text_width(shortened + "..") > max_width:
            shortened = shortened[:-1]
        return shortened + ".."

    def measure_text_width(self, text: str) -> int:
        temp_label = label.Label(self.font, text=text, color=self.config.style.upcoming_line_colors[0], x=0, y=0)
        return temp_label.bounding_box[2]

    def _elapsed_since_last_fetch(self, now: float) -> float:
        if self.polling.data_fetched_at is None:
            return 0
        return max(0, now - self.polling.data_fetched_at)

    def company_icon_colors(self, train_data):
        if train_data is None:
            return None
        company = str(train_data.get("company") or "").strip().upper()
        return self.config.style.company_icon_colors.get(company)

    def _train_value(self, train_data, key, default="?"):
        if train_data is None:
            return None
        value = train_data.get(key) or default
        return self.sanitize_text(self._normalize_station_label(value))

    def _normalize_station_label(self, value: str) -> str:
        value = str(value).strip()
        return self.config.content.station_label_replacements.get(value, value)

    def sanitize_text(self, text: str) -> str:
        text = text.replace("ü", "u").replace("ä", "a").replace("ö", "o")
        allowed = self.config.display.font_glyphs.decode("ascii")
        return "".join(char if char in allowed else "?" for char in str(text))

    @staticmethod
    def remaining_seconds(initial_seconds, elapsed_seconds: float):
        if initial_seconds is None:
            return None
        return max(0, int(initial_seconds - elapsed_seconds))

    @staticmethod
    def signed_remaining_seconds(initial_seconds, elapsed_seconds: float):
        if initial_seconds is None:
            return None
        return math.floor(initial_seconds - elapsed_seconds)

    @staticmethod
    def format_seconds(seconds: int) -> str:
        if seconds < 100:
            return f"{seconds}s"
        minutes = seconds // 60
        remainder = seconds % 60
        return "{}:{:02d}".format(minutes, remainder)
