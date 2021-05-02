import displayio


def get_digit(digit):
    # Create a bitmap with two colors
    digit_bitmap = displayio.Bitmap(12, 40, 2)

    for row in range(len(digit)):
        for col in range(0, len(digit[row])):
            if digit[row][col] == 'x':
                digit_bitmap[col, row] = 1

    return digit_bitmap


def create_palette(color):
    # Create a two color palette
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = color

    return palette


colors = [0xe74c3c, 0xf1c40f, 0x2ecc71, 0x3498db]

digit_palettes = [
    create_palette(colors[0]),
    create_palette(colors[1]),
    create_palette(colors[2]),
    create_palette(colors[3]),
]
