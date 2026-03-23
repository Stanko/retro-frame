import gc
import ipaddress
import ssl

import adafruit_requests
import socketpool
import wifi

from src.settings_utils import WifiSettings


class NetworkModule:
    def __init__(self, wifi_settings: WifiSettings):
        self.wifi_settings = wifi_settings
        self.requests = None
        self.pool = None

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
