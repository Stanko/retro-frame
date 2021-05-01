import time
import os
import board
import displayio

from digitalio import DigitalInOut, Pull
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

# ------- TODO
# Scale, for smaller images (16x16, 32x32) detect scale
# maybe I could use file size to detect it


# ------- Button setup
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)

pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

# ------- Display setup
# 4 bit - 16 colors
# 6 bit - 64 colors
# 8 bit - 256 colors
# 16 bit - 65K colors
matrix = Matrix(width=64, height=64, bit_depth=6)
sprite_group = displayio.Group()
matrix.display.show(sprite_group)

# ------- Display modes
SINGLE = "single"
LOOP = "loop"
CLOCK = "clock"

DISPLAY_MODES = [SINGLE, LOOP, CLOCK]

LOOP_TIME = 60

# ------- BMPs
BMP_FOLDER = "/bmp"

bmp_file_list = sorted(
    [
        f
        for f in os.listdir(BMP_FOLDER)
        if (f.endswith(".bmp") and not f.startswith("."))
    ]
)

# ------- Global state
display_mode_index = 0
current_image = 0
current_frame = 0
frame_count = 0
frame_duration = 0.1
loop_started = time.time()_time

images_count = len(bmp_file_list)

# If there is no images switch to clock mode
if images_count == 0:
    display_mode_index = 2

def change_mode():
  global display_mode_index, DISPLAY_MODES

  display_mode_index = display_mode_index++ % len(DISPLAY_MODES)

def change_image():
  global current_image, images_count, current_frame, loop_started_time

  loop_started = time.time()_time

  current_image = current_image++ % images_count
  current_frame = 0

  load_image()


def load_image():
    global current_image, images_count, current_frame, frame_count

    # Empty sprite group
    while sprite_group:
        sprite_group.pop()

    bitmap = displayio.OnDiskBitmap(
        open(BMP_FOLDER + "/" + bmp_file_list[current_image], "rb")
    )

    frame_count = int(bitmap.height / matrix.display.height)
    # frame_duration = DEFAULT_FRAME_DURATION
    # if bmp_file_list[current_image] in FRAME_DURATION_OVERRIDES:
    #     frame_duration = FRAME_DURATION_OVERRIDES[bmp_file_list[current_image]]

    sprite = displayio.TileGrid(
        bitmap,
        pixel_shader=displayio.ColorConverter(),
        width=1,
        height=1,
        tile_width=bitmap.width,
        tile_height=matrix.display.height,
    )

    sprite_group.append(sprite)
    current_frame = 0
    current_loop = 0

def show_frame():
    global current_frame, current_loop, loop_started_time, sprite_group, frame_count
    
    sprite_group[0][0] = current_frame

    current_frame = (current_frame + 1) % frame_count

    if current_frame == 0 and DISPLAY_MODES[display_mode_index] == LOOP:
        now = time.time()
        # Image has been looping for max time, switch to the next one
        if now - loop_started_time > LOOP_TIME:
            change_image()

# ------- Init

load_image()

# ------- Main loop
while True:
    button_down.update()
    button_up.update()

    # Handle button up
    if button_up.fell:
        change_mode()

    # Handle button down
    if button_down.fell:
        if DISPLAY_MODES[display_mode_index] != CLOCK:
          change_image()

    if DISPLAY_MODES[display_mode_index] != CLOCK:
        show_frame()

    time.sleep(frame_duration)
