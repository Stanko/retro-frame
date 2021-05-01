
# https://learn.adafruit.com/adafruit-matrixportal-m4/using-the-accelerometer

import time
import board
import busio
import adafruit_lis3dh

# Hardware I2C setup. Use the CircuitPlayground built-in accelerometer if available;
# otherwise check I2C pins.
# if hasattr(board, "ACCELEROMETER_SCL"):
#     i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
#     lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
# else:
#     i2c = board.I2C()  # uses board.SCL and board.SDA
#     lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)


# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# PyGamer OR MatrixPortal I2C Setup:
i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)


x, y, z = [
    value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
]
print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))