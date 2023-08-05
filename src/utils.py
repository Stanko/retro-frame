from re import search

def width_height_from_filename(filename: str):
    size = search("(\d\d)x(\d\d)", filename)
    if size:
        return int(size.group(1)), int(size.group(2))
    else:
        return None, None

def fps_from_filename(filename: str):
    # Check for "\d\dfps" pattern in the filename
    # If detected the number is used a fps value
    fps = search("(\d\d)fps", filename)
    if fps:
        return int(fps.group(1))
    else:
        return None

def width_height_from_bitmap(bitmap):
    # Detect sprite orientation
    # if there is no size in the filename, each frame is considered to be a square
    if (bitmap.height > bitmap.width):
        return bitmap.width, bitmap.width
    else:
        return bitmap.height, bitmap.height

def frame_count_from_bitmap(bitmap):
    # Detect sprite orientation
    # if there is no size in the filename, each frame is considered to be a square
    if (bitmap.height > bitmap.width):
        return int(bitmap.height / bitmap.width)
    else:
        return int(bitmap.width / bitmap.height)

def offset_from_width_height(width: int, height: int):
    x_offset = int((64 - width) / 2)
    y_offset = int((64 - height) / 2)
    return x_offset, y_offset

def compute_dimensions_and_offset(bitmap, filename: str):
    width, height = width_height_from_filename(filename)
    if width is None:
        width, height = width_height_from_bitmap(bitmap)
    x_offset, y_offset = offset_from_width_height(width, height)
    return width, height, x_offset, y_offset