import gc

import adafruit_requests

try:
    import ipaddress
    import ssl
    import socketpool
    import wifi
except ImportError:
    ipaddress = None
    ssl = None
    socketpool = None
    wifi = None

try:
    import adafruit_connection_manager
except ImportError:
    adafruit_connection_manager = None

try:
    import board
    import busio
    from adafruit_esp32spi import adafruit_esp32spi
    from digitalio import DigitalInOut

    try:
        import adafruit_esp32spi.adafruit_esp32spi_socket as esp32spi_socket
    except ImportError:
        import adafruit_esp32spi.adafruit_esp32spi_socketpool as esp32spi_socket

    try:
        from adafruit_esp32spi.socketpool import SocketPool as ESP32SPISocketPool
    except ImportError:
        try:
            from adafruit_esp32spi.adafruit_esp32spi_socketpool import SocketPool as ESP32SPISocketPool
        except ImportError:
            ESP32SPISocketPool = None
except ImportError:
    board = None
    busio = None
    adafruit_esp32spi = None
    DigitalInOut = None
    esp32spi_socket = None
    ESP32SPISocketPool = None

from src.settings_utils import WifiSettings


class BaseNetworkModule:
    def __init__(self, wifi_settings: WifiSettings):
        self.wifi_settings = wifi_settings
        self.requests = None
        self.pool = None

    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

    def get_socketpool(self):
        raise NotImplementedError

    def run_connection_diagnostics(self) -> None:
        print("No additional network diagnostics available for this transport.")

    def _classify_request_error(self, error: Exception) -> str:
        message = str(error)
        message_lower = message.lower()

        if (
            "getaddrinfo" in message_lower
            or "name or service not known" in message_lower
            or "resolve" in message_lower
            or "dns" in message_lower
        ):
            return f"DNS failure while resolving host: {message}"

        if (
            "socket" in message_lower
            or "connection" in message_lower
            or "timeout" in message_lower
            or "ssl" in message_lower
        ):
            return f"Socket/session failure while sending request: {message}"

        return f"Request failed before a valid HTTP response was received: {message}"

    def get_json(self, url: str):
        if not self.is_connected():
            self.connect()

        try:
            response = self.requests.get(url)
        except Exception as error:
            raise RuntimeError(self._classify_request_error(error))

        try:
            status_code = getattr(response, "status_code", 200)
            if status_code >= 400:
                reason = getattr(response, "reason", "")
                raise RuntimeError(f"HTTP error {status_code} while requesting {url}. {reason}")
            return response.json()
        except RuntimeError:
            raise
        except Exception as error:
            raise RuntimeError(f"Received an HTTP response but could not parse JSON: {error}")
        finally:
            response.close()
            gc.collect()


class NativeNetworkModule(BaseNetworkModule):
    def is_connected(self) -> bool:
        return wifi.radio.connected

    def get_socketpool(self):
        if self.pool is None:
            self.pool = socketpool.SocketPool(wifi.radio)
        return self.pool

    def _build_requests_client(self) -> None:
        self.requests = adafruit_requests.Session(
            self.get_socketpool(),
            ssl.create_default_context(),
        )

    def connect(self) -> None:
        if self.wifi_settings.skip_connection:
            return

        if self.is_connected():
            if self.requests is None:
                self._build_requests_client()
            return

        retries = 3
        print("Connecting to WiFi...")

        while not wifi.radio.connected and retries > 0:
            try:
                wifi.radio.connect(self.wifi_settings.ssid, self.wifi_settings.password)
            except Exception as error:
                retries -= 1
                print(error)
                print(f"Could not connect to access point {self.wifi_settings.ssid}. Retries {retries}...")

        if not wifi.radio.connected:
            raise RuntimeError(f"Could not connect to access point {self.wifi_settings.ssid}.")

        print("Connected to", self.wifi_settings.ssid, "\tIP:", wifi.radio.ipv4_address)
        self._build_requests_client()
        gc.collect()

    def disconnect(self) -> None:
        if self.wifi_settings.skip_connection:
            return

        print("Disconnecting from WiFi...")

        if wifi.radio.connected:
            wifi.radio.stop_station()

        self.requests = None
        self.pool = None
        gc.collect()

    def run_connection_diagnostics(self) -> None:
        print("Running network diagnostics...")
        print("WiFi connected:", self.is_connected())
        print("IPv4 address:", wifi.radio.ipv4_address)

        if ipaddress is None:
            print("Ping test unavailable: ipaddress module not present.")
        else:
            try:
                ping_time = wifi.radio.ping(ipaddress.ip_address("8.8.8.8"))
                print("Ping 8.8.8.8:", ping_time)
            except Exception as error:
                print("Ping 8.8.8.8 failed:", error)

        try:
            response = self.requests.get("http://example.com/")
            print("HTTP probe http://example.com/ status:", getattr(response, "status_code", "unknown"))
        except Exception as error:
            print("HTTP probe http://example.com/ failed:", self._classify_request_error(error))
        else:
            response.close()
            gc.collect()


class LegacyNetworkModule(BaseNetworkModule):
    def __init__(self, wifi_settings: WifiSettings):
        super().__init__(wifi_settings)
        self.esp = None
        self.esp32_cs = DigitalInOut(board.ESP_CS)
        self.esp32_ready = DigitalInOut(board.ESP_BUSY)
        self.esp32_reset = DigitalInOut(board.ESP_RESET)
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

    def is_connected(self) -> bool:
        if self.esp is None:
            return False
        return self.esp.is_connected

    def get_socketpool(self):
        if self.pool is not None:
            return self.pool

        if adafruit_connection_manager is not None:
            self.pool = adafruit_connection_manager.get_radio_socketpool(self.esp)
            return self.pool

        if ESP32SPISocketPool is None:
            raise RuntimeError("No ESP32SPI socket pool implementation is available.")

        self.pool = ESP32SPISocketPool(self.esp)
        return self.pool

    def _build_requests_client(self) -> None:
        if adafruit_connection_manager is not None:
            self.requests = adafruit_requests.Session(
                self.get_socketpool(),
                adafruit_connection_manager.get_radio_ssl_context(self.esp),
            )
            return

        esp32spi_socket.set_interface(self.esp)
        adafruit_requests.set_socket(esp32spi_socket, self.esp)
        self.requests = adafruit_requests

    def connect(self) -> None:
        if self.wifi_settings.skip_connection:
            return

        if self.is_connected():
            if self.requests is None:
                self._build_requests_client()
            return

        retries = 3
        print("Connecting to WiFi...")
        self.esp = adafruit_esp32spi.ESP_SPIcontrol(
            self.spi,
            self.esp32_cs,
            self.esp32_ready,
            self.esp32_reset,
        )

        while not self.esp.is_connected and retries > 0:
            try:
                self.esp.connect_AP(self.wifi_settings.ssid, self.wifi_settings.password)
            except Exception as error:
                retries -= 1
                print(error)
                print(f"Could not connect to access point {self.wifi_settings.ssid}. Retries {retries}...")

        if not self.esp.is_connected:
            raise RuntimeError(f"Could not connect to access point {self.wifi_settings.ssid}.")

        if hasattr(self.esp, "ap_info") and self.esp.ap_info is not None:
            print("Connected to", self.esp.ap_info.ssid, "\tRSSI:", self.esp.ap_info.rssi)
        else:
            print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)

        self._build_requests_client()
        gc.collect()

    def disconnect(self) -> None:
        if self.wifi_settings.skip_connection:
            return

        print("Disconnecting from WiFi...")

        if self.esp is not None:
            self.esp.disconnect()
            self.esp = None

        self.requests = None
        self.pool = None
        gc.collect()


def create_network_module(wifi_settings: WifiSettings):
    if wifi is not None and socketpool is not None and ssl is not None:
        return NativeNetworkModule(wifi_settings)

    if (
        adafruit_esp32spi is not None
        and board is not None
        and busio is not None
        and DigitalInOut is not None
        and hasattr(board, "ESP_CS")
        and hasattr(board, "ESP_BUSY")
        and hasattr(board, "ESP_RESET")
    ):
        return LegacyNetworkModule(wifi_settings)

    raise RuntimeError("No supported WiFi transport found for this board.")
