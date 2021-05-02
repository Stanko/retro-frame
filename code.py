import time 
import gc

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
CLOCK_PADDING = 4
DIGIT_WIDTH = 12
DIGIT_MARGIN = 2
DIGIT_HEIGHT = 32
DIGIT_Y = (64 - DIGIT_HEIGHT) / 2

last_time_string = ""
last_update_in_ms = 0

digits_sprite = None

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

LOOP_TIME = 180  # in seconds

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
frame_duration_in_ms = 100
loop_started_time = time.time()

images_count = len(bmp_file_list)

# If there is no images switch to clock mode
if images_count == 0:
    display_mode_index = 2

# --------- Modes


def change_mode():
    global display_mode_index, DISPLAY_MODES, last_time_string, digits_sprite

    display_mode_index = (display_mode_index + 1) % len(DISPLAY_MODES)

    last_time_string = ""

    if DISPLAY_MODES[display_mode_index] != CLOCK:
        digits_sprite = None
        load_image()
        show_frame(None)
    else:
        digits_sprite = OnDiskBitmap(open('/clock/sprite.bmp', 'rb'))

# ---------- Clock


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

    time_data = network_connection.fetch_data(time_url, json_path=[['datetime'], ['dst']])

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
            hour_string = str(time_struct.tm_hour - 12)  # 13-23 -> 1-11 (pm)
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
    global current_image, images_count, current_frame, frame_count, sprite_group, frame_duration_in_ms

    # Empty sprite group
    while sprite_group:
        sprite_group.pop()

    gc.collect()

    filename = bmp_file_list[current_image]

    image_path = BMP_FOLDER + "/" + filename

    bitmap = OnDiskBitmap(open(image_path, "rb"))

    # Check for "\d\d-" pattern at the start of the filename
    # If detected number is used a frames per second value
    if filename[0].isdigit() and filename[1].isdigit() and filename[2] == '-':
        frame_duration_in_ms = 1.0 / int(filename[0:2]) * 1000
    else:
        frame_duration_in_ms = 100

    # Detect sprite orientation
    if (bitmap.height > bitmap.width):
        frame_count = int(bitmap.height / bitmap.width)
        tile_size = bitmap.width
    else:
        frame_count = int(bitmap.width / bitmap.height)
        tile_size = bitmap.height

    offset = int((matrix.display.height - bitmap.width) / 2)

    sprite = TileGrid(
        bitmap,
        pixel_shader=bitmap.pixel_shader,
        width=1,
        height=1,
        tile_width=tile_size,
        tile_height=tile_size,
        x=offset,
        y=offset,
    )

    sprite_group.append(sprite)
    current_frame = 0


def show_frame(delta_time):
    global current_frame, loop_started_time, sprite_group, frame_count, last_update_in_ms, frame_duration_in_ms

    if delta_time == None or delta_time < frame_duration_in_ms:
        return

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
    digits_sprite = OnDiskBitmap(open('/clock/sprite.bmp', 'rb'))


# ------- Main loop

while True:
    button_down.update()
    button_up.update()

    current_time_in_ms = time.monotonic() * 1000

    if current_time_in_ms == 0:
        delta_time = None
    else:
        delta_time = current_time_in_ms - last_update_in_ms

    # Handle button up
    if button_up.fell:
        change_mode()

    # Handle button down
    if button_down.fell:
        if DISPLAY_MODES[display_mode_index] != CLOCK:
            change_image()
        # Clock
        else:
            try_to_update_time()

    # Images
    if DISPLAY_MODES[display_mode_index] != CLOCK:
        show_frame(delta_time)
    # Clock
    else:
        now = time.localtime()
        time_string = hh_mm(now)

        if time_string != last_time_string:
            last_time_string = time_string

            # Empty group
            while sprite_group:
                sprite_group.pop()

            for index, digit in enumerate(time_string):
                x = index * DIGIT_WIDTH + index * DIGIT_MARGIN + CLOCK_PADDING
                if index > 1:
                    # Double space between hours and minutes
                    x += DIGIT_MARGIN

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
        
                digit_int = int(digit)

                sprite_group.append(digit_tilemap)

                # Skip hour leading zero
                if index == 0 and digit == '0':
                    sprite_group[index][0] = 40 # last frame in the sprite is just black
                else:
                    sprite_group[index][0] = digit_int + (index * 10) # sprite has 4 sets of digits

    now = time.time()  # Current epoch time in seconds

    # Sync with time server every 2 hours
    if now - last_sync > 7200:
        try_to_update_time()
