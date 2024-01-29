# https://learn.adafruit.com/adafruit-matrixportal-m4/using-the-accelerometer
import time

import adafruit_lis3dh
import board
import busio
import digitalio


class Axis:
    X = 0
    Y = 1
    Z = 2


class AccelerometerModule:

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
        self.lis3dh = adafruit_lis3dh.LIS3DH_I2C(self.i2c, address=0x19, int1=self.int1)
        # Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
        self.lis3dh.range = adafruit_lis3dh.RANGE_2_G

        self.deadzone = 0.08
        self.wait_for_reset = False
        self.rotation_threshold = 0.3

    def read(self, debug=False):
        x, y, z = [
           value / adafruit_lis3dh.STANDARD_GRAVITY for value in self.lis3dh.acceleration
        ]
        if self.wait_for_reset and (abs(x) < self.deadzone and abs(z) < self.deadzone):
            self.wait_for_reset = False
        if debug:
            print(f"wait_for_reset={self.wait_for_reset} x={x:.3f}G, y={y:.3f}G, z={z:.3f}G")
        return x, y, z

    def check_next_by_axis(self, axis: int):
        axes = self.read()
        if self.wait_for_reset:
            return False
        value = axes[axis]
        if value > self.rotation_threshold:
            self.wait_for_reset = True
            return True
        return False

    def check_previous_by_axis(self, axis: int):
        axes = self.read()
        if self.wait_for_reset:
            return False
        value = axes[axis]
        if value < -self.rotation_threshold:
            self.wait_for_reset = True
            return True
        return False
