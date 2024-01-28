import gc

import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
import board
import busio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise


class NetworkModule:
    def __init__(self, skip_connection: bool = False):
        self.skip_connection = skip_connection
        # Reference: https://learn.adafruit.com/adafruit-matrixportal-m4/internet-connect
        self.esp = None
        self.esp32_cs = DigitalInOut(board.ESP_CS)
        self.esp32_ready = DigitalInOut(board.ESP_BUSY)
        self.esp32_reset = DigitalInOut(board.ESP_RESET)
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

    def is_connected(self) -> bool:
        if self.esp is None:
            return False
        return self.esp.is_connected

    def connect(self) -> None:
        if not self.skip_connection:
            retries = 3
            print("Connecting to WiFi...")
            self.esp = adafruit_esp32spi.ESP_SPIcontrol(self.spi, self.esp32_cs, self.esp32_ready, self.esp32_reset)
            while not self.esp.is_connected and retries > 0:
                try:
                    self.esp.connect_AP(secrets["ssid"], secrets["password"])
                except Exception as e:
                    retries -= 1
                    print(e)
                    print(f"Could not connect to access point {secrets['ssid']}. Retries {retries}...")
                    continue
            print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)
            socket.set_interface(self.esp)
            requests.set_socket(socket, self.esp)
            gc.collect()

    def disconnect(self) -> None:
        if not self.skip_connection:
            print("Disconnecting from WiFi...")
            self.esp.disconnect()
            self.esp = None
            gc.collect()

    def get_json(self, url: str):
        if not self.is_connected():
            self.connect()
        response = requests.get(url)
        gc.collect()
        return response.json()