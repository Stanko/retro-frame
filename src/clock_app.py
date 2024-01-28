import time

from displayio import OnDiskBitmap, TileGrid

from src.base_app import BaseApp


class ClockApp(BaseApp):
    name = "Clock"

    def __init__(self, display, real_time_clock):
        super().__init__()
        self.display = display
        self.real_time_clock = real_time_clock
        self.separator_tile_index = 246
        self.twelve_hour: bool = False
        self.last_time_string: str = ""
        self.create_clock_sprite()

    def create_clock_sprite(self):
        self.display.clear()

        digits_sprite = OnDiskBitmap(open('/clock/sprite.bmp', 'rb'))

        separator_tilemap = TileGrid(
            digits_sprite,
            pixel_shader=digits_sprite.pixel_shader,
            width=1,
            height=1,
            tile_width=2,
            tile_height=40,
            x=31,
            y=12,
        )
        self.display.draw(separator_tilemap)
        # Set time separator tile, it is 2px wide and all the way right
        self.display.sprite_group[0][0] = self.separator_tile_index

        # digits
        digit_x_positions = [3, 17, 35, 49]

        for x in digit_x_positions:
            digit_tilemap = TileGrid(
                digits_sprite,
                pixel_shader=digits_sprite.pixel_shader,
                width=1,
                height=1,
                tile_width=12,
                tile_height=40,
                x=x,
                y=12,
            )
            self.display.draw(digit_tilemap)

        # Set digits to blank tiles
        # 41st tile is just black
        self.display.sprite_group[1][0] = 40
        self.display.sprite_group[2][0] = 40
        self.display.sprite_group[3][0] = 40
        self.display.sprite_group[4][0] = 40

    def hh_mm(self, time_struct):
        if self.twelve_hour:
            if time_struct.tm_hour > 12:
                # 13-23 -> 1-11 (pm)
                hour_string = str(time_struct.tm_hour - 12)
            elif time_struct.tm_hour > 0:
                hour_string = str(time_struct.tm_hour)  # 1-12
            else:
                hour_string = '12'  # 0 -> 12 (am)
        else:
            hour_string = time_struct.tm_hour

        return '{0:0>2}'.format(hour_string) + '{0:0>2}'.format(time_struct.tm_min)

    def handle_button_down(self):
        self.real_time_clock.sync_time_online()

    def draw_frame(self) -> float:
        now_struct = time.localtime()
        time_string = self.hh_mm(now_struct)

        # Time needs to be updated
        if time_string != self.last_time_string:
            self.last_time_string = time_string
            self.display.sprite_group[0][0] = self.separator_tile_index

            # Go through the group and update tiles
            for index, digit in enumerate(time_string):
                digit_int = int(digit)

                # Skip hour leading zero
                if index == 0 and digit == '0':
                    # we use index + 1 because 0 is reserved for separator
                    # 41st tile is just black
                    self.display.sprite_group[index + 1][0] = 40
                else:
                    # we use index + 1 because 0 is reserved for separator
                    # sprite has 4 sets of digits
                    self.display.sprite_group[index + 1][0] = digit_int + (index * 10)
        return 0.1
