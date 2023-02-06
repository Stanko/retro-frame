import time
import gc

from re import search

from os import listdir
from board import BUTTON_DOWN, BUTTON_UP, NEOPIXEL
from displayio import Group, OnDiskBitmap, TileGrid

from rtc import RTC

from digitalio import DigitalInOut, Pull
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

# ------- Button setup
pin_down = DigitalInOut(BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)

pin_up = DigitalInOut(BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

# ------- Display setup
matrix = Matrix(width=64, height=64, bit_depth=4)
sprite_group = Group()

matrix.display.show(sprite_group)

# ------- Clock setup

TWELVE_HOUR = False

last_time_string = ""
last_update_in_ms = 0

# ------- Splash

splash_bitmap = OnDiskBitmap(open('/splash.bmp', 'rb'))

splash_tilemap = TileGrid(
    splash_bitmap,
    pixel_shader=splash_bitmap.pixel_shader,
    width=1,
    height=1,
    tile_width=splash_bitmap.width,
    tile_height=splash_bitmap.height,
    x=0,
    y=0
)

sprite_group.append(splash_tilemap)

# ------- Network

network_connection = Network(status_neopixel=NEOPIXEL, debug=False)
network_connection.connect()

# ------- Display modes
SINGLE = "single"
LOOP = "loop"
CLOCK = "clock"

DISPLAY_MODES = [SINGLE, LOOP, CLOCK]

LOOP_TIME = 300  # in seconds

# ------- BMPs
BMP_FOLDER = "/bmp"

bmp_file_list = sorted(
    [
        f
        for f in listdir(BMP_FOLDER)
        if (f.endswith(".bmp") and not f.startswith("."))
    ]
)

# ------- Global state

display_mode_index = 1  # loop images
current_image = 0
current_frame = 0
frame_count = 0
frame_duration_in_s = 0.1
loop_started_time = time.time()

images_count = len(bmp_file_list)

# If there is no images switch to clock mode
if images_count == 0:
    display_mode_index = 2

# --------- Modes


def change_mode(index_to_set=None):
    global display_mode_index, DISPLAY_MODES, last_time_string

    if index_to_set == None:
        display_mode_index = (display_mode_index + 1) % len(DISPLAY_MODES)
    else:
        display_mode_index = index_to_set

    last_time_string = ""

    if DISPLAY_MODES[display_mode_index] != CLOCK:
        load_image()
        show_frame(None)
    else:
        create_clock_sprite()

# ---------- Clock


def create_clock_sprite():
    global sprite_group

    # Empty sprite group
    while sprite_group:
        sprite_group.pop()

    gc.collect()

    digits_sprite = OnDiskBitmap(open('/clock/sprite.bmp', 'rb'))

    # separator
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
    sprite_group.append(separator_tilemap)

    # Set time separator tile, it is 2px wide and all the way right
    sprite_group[0][0] = 246

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
        sprite_group.append(digit_tilemap)

    # Set digits to blank tiles
    # 41st tile is just black
    sprite_group[1][0] = 40
    sprite_group[2][0] = 40
    sprite_group[3][0] = 40
    sprite_group[4][0] = 40


def parse_time(timestring):
    # Separate into date and time
    # YYYY-MM-DD
    # HH:MM:SS.SS-HH:MM
    date_time = timestring.split('T')
    # Separate date into an array
    year_month_day = date_time[0].split('-')
    # Extract HH/MM/SS
    hour_minute_second = date_time[1].split('.')[0].split(':')

    return time.struct_time([int(year_month_day[0]),
                            int(year_month_day[1]),
                            int(year_month_day[2]),
                            int(hour_minute_second[0]),
                            int(hour_minute_second[1]),
                            int(hour_minute_second[2]),
                            -1, -1, -1])


def update_time():
    global network_connection

    time_url = 'http://worldtimeapi.org/api/ip'

    time_data = network_connection.fetch_data(
        time_url, json_path=[['datetime'], ['dst']])

    time_struct = parse_time(time_data[0])
    RTC().datetime = time_struct

    return time_struct


def try_to_update_time():
    global time_from_api, last_sync, last_time_string

    try:
        time_from_api = update_time()
        last_sync = time.mktime(time_from_api)
        last_time_string = hh_mm(time.localtime())
    except:
        # update_time() can throw an exception if time server doesn't
        # respond. That's OK, keep running with our current time, and
        # push sync time ahead to retry in 30 minutes (don't overwhelm
        # the server with repeated queries).
        last_sync += 1800  # 30 minutes in seconds


def hh_mm(time_struct):
    if TWELVE_HOUR:
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

# ---------- Images


def change_image():
    global current_image, images_count, current_frame, loop_started_time

    loop_started_time = time.time()

    current_image = (current_image + 1) % images_count
    current_frame = 0

    load_image()


def load_image():
    global current_image, images_count, current_frame, frame_count, sprite_group, frame_duration_in_s

    # Empty sprite group
    while sprite_group:
        sprite_group.pop()

    gc.collect()

    filename = bmp_file_list[current_image]

    image_path = BMP_FOLDER + "/" + filename

    bitmap = OnDiskBitmap(open(image_path, "rb"))

    # Check for "\d\dfps" pattern in the filename
    # If detected the number is used a fps value
    fps = search("(\d\d)fps", filename)

    if fps:
        frame_duration_in_s = 1.0 / float(fps.group(1))
    else:
        frame_duration_in_s = 0.1

    # Check for "(\d\d)x(\d\d)" pattern in the filename
    # If detected numbers are used as tile width and height
    size = search("(\d\d)x(\d\d)", filename)

    if size:
        tile_width = int(size.group(1))
        tile_height = int(size.group(2))

    # Detect sprite orientation
    # if there is no size in the filename, each frame is considered to be a square
    if (bitmap.height > bitmap.width):
        if not size:
            tile_width = bitmap.width
            tile_height = bitmap.width

        frame_count = int(bitmap.height / tile_height)
    else:
        if not size:
            tile_height = bitmap.height
            tile_width = bitmap.height

        frame_count = int(bitmap.width / tile_width)

    x_offset = int((64 - tile_width) / 2)
    y_offset = int((64 - tile_height) / 2)

    # print("**", filename)
    # print("size", tile_width, "x", tile_height)
    # print("frame count", frame_count)
    # print("frame duration", frame_duration_in_s, "s")

    sprite = TileGrid(
        bitmap,
        pixel_shader=bitmap.pixel_shader,
        width=1,
        height=1,
        tile_width=tile_width,
        tile_height=tile_height,
        x=x_offset,
        y=y_offset,
    )

    sprite_group.append(sprite)
    current_frame = 0


def show_frame():
    global current_frame, loop_started_time, sprite_group, frame_count, last_update_in_ms, frame_duration_in_s

    sprite_group[0][0] = current_frame

    last_update_in_ms = time.monotonic() * 1000

    current_frame = (current_frame + 1) % frame_count

    if current_frame == 0 and DISPLAY_MODES[display_mode_index] == LOOP:
        now = time.time()
        # Image has been looping for max time, switch to the next one
        if now - loop_started_time > LOOP_TIME:
            change_image()

# ------- Init


try:
    time_from_api = update_time()
except:
    time_from_api = time.localtime()

last_sync = time.mktime(time_from_api)

if DISPLAY_MODES[display_mode_index] != CLOCK:
    load_image()
else:
    create_clock_sprite()

# ------- Main loop

now = time.time()

while True:
    button_down.update()
    button_up.update()

    is_clock = DISPLAY_MODES[display_mode_index] == CLOCK

    now_struct = time.localtime()

    # At midnight change to clock
    if now_struct.tm_hour == 0 and now_struct.tm_min == 0 and now_struct.tm_sec == 0 and not is_clock:
        print("automatically change to clock")
        change_mode(2)  # clock
    # In morning switch to images
    elif now_struct.tm_hour == 9 and now_struct.tm_min == 0 and now_struct.tm_sec == 0 and is_clock:
        print("automatically change to images")
        change_mode(1)  # loop images

    # Handle button up
    if button_up.fell:
        change_mode()

    # Handle button down
    if button_down.fell:
        # Clock
        if is_clock:
            try_to_update_time()
        # Images
        else:
            change_image()

    # Clock logic
    if is_clock and len(sprite_group) > 1:
        time_string = hh_mm(now_struct)

        # Time needs to be updated
        if time_string != last_time_string:
            last_time_string = time_string

            # Go through the group and update tiles
            for index, digit in enumerate(time_string):
                digit_int = int(digit)

                # Skip hour leading zero
                if index == 0 and digit == '0':
                    # we use index + 1 because 0 is reserved for separator
                    # 41st tile is just black
                    sprite_group[index + 1][0] = 40
                else:
                    # we use index + 1 because 0 is reserved for separator
                    sprite_group[index + 1][0] = digit_int + \
                        (index * 10)  # sprite has 4 sets of digits

        # Sync with time server every 2 hours
        if now - last_sync > 7200:
            try_to_update_time()
    # Images logic
    else:
        show_frame()

    time.sleep(frame_duration_in_s)

    # Update time
    now = time.time()  # Current epoch time in seconds
