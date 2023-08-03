from adafruit_matrixportal.network import Network

try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

class NetworkModule:
    def __init__(self, skip_connection: bool = False):
        self.skip_connection = skip_connection
        self.network = Network(status_neopixel=None, debug=False)

    def is_connected(self) -> bool:
        return self.network.is_connected

    def connect(self) -> None:
        if not self.skip_connection:
            self.network.connect()
        else:
            print("Network connection skipped")