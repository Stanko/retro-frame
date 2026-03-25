class TrainRadarDisplayConfig:
    def __init__(self, font_glyphs, font_path, frame_interval_seconds, layout_refresh_seconds, divider_color):
        self.font_glyphs = font_glyphs
        self.font_path = font_path
        self.frame_interval_seconds = frame_interval_seconds
        self.layout_refresh_seconds = layout_refresh_seconds
        self.divider_color = divider_color


class TrainRadarPanelLayoutConfig:
    def __init__(self, font_height, padding, line_gap, panel_width, badge_size, badge_gap, badge_hidden_x, badge_y):
        self.font_height = font_height
        self.padding = padding
        self.line_gap = line_gap
        self.panel_width = panel_width
        self.badge_size = badge_size
        self.badge_gap = badge_gap
        self.badge_hidden_x = badge_hidden_x
        self.badge_y = badge_y

    @property
    def content_width(self):
        return self.panel_width - (self.padding * 2)


class TrainRadarAnimationConfig:
    def __init__(self, chevron_count, chevron_interval_seconds, chevron_spacing):
        self.chevron_count = chevron_count
        self.chevron_interval_seconds = chevron_interval_seconds
        self.chevron_spacing = chevron_spacing


class TrainRadarStyleConfig:
    def __init__(self, upcoming_line_colors, current_line_colors, company_icon_colors):
        self.upcoming_line_colors = upcoming_line_colors
        self.current_line_colors = current_line_colors
        self.company_icon_colors = company_icon_colors


class TrainRadarContentConfig:
    def __init__(self, station_label_replacements, right_chevron_symbol, left_chevron_symbol, company_badge_pixels):
        self.station_label_replacements = station_label_replacements
        self.right_chevron_symbol = right_chevron_symbol
        self.left_chevron_symbol = left_chevron_symbol
        self.company_badge_pixels = company_badge_pixels


class TrainRadarConfig:
    def __init__(self, display, panel_layout, animation, style, content):
        self.display = display
        self.panel_layout = panel_layout
        self.animation = animation
        self.style = style
        self.content = content


class RadarHalfPanelConfig:
    def __init__(
        self,
        top_y,
        align,
        scroll_direction,
        chevron_symbol,
        initial_line_colors,
        layout,
        animation,
        content,
    ):
        self.top_y = top_y
        self.align = align
        self.scroll_direction = scroll_direction
        self.chevron_symbol = chevron_symbol
        self.initial_line_colors = initial_line_colors
        self.layout = layout
        self.animation = animation
        self.content = content


class AnimatedChevronRowConfig:
    def __init__(
        self,
        line_y,
        content_x,
        content_width,
        align,
        chevron_symbol,
        initial_text_color,
        initial_chevron_color,
        chevron_count=3,
        step_interval_seconds=0.25,
        character_spacing=6,
        reserved_middle_text="-60s",
    ):
        self.line_y = line_y
        self.content_x = content_x
        self.content_width = content_width
        self.align = align
        self.chevron_symbol = chevron_symbol
        self.initial_text_color = initial_text_color
        self.initial_chevron_color = initial_chevron_color
        self.chevron_count = chevron_count
        self.step_interval_seconds = step_interval_seconds
        self.character_spacing = character_spacing
        self.reserved_middle_text = reserved_middle_text


class RadarPanelState:
    def __init__(
        self,
        header_text="",
        origin_text="",
        destination_text="",
        middle_text="",
        line_colors=(0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF),
        show_chevron=False,
        animate_chevrons=False,
        company_badge_colors=None,
    ):
        self.header_text = header_text
        self.origin_text = origin_text
        self.destination_text = destination_text
        self.middle_text = middle_text
        self.line_colors = line_colors
        self.show_chevron = show_chevron
        self.animate_chevrons = animate_chevrons
        self.company_badge_colors = company_badge_colors

    def key(self):
        return (
            self.header_text,
            self.origin_text,
            self.destination_text,
            self.middle_text,
            self.line_colors,
            self.show_chevron,
            self.animate_chevrons,
            self.company_badge_colors,
        )
