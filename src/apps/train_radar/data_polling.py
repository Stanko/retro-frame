import time


class DataPolling:
    def __init__(self, network, url: str, poll_interval_seconds: float, mock=None):
        self.network = network
        self.url = url
        self.poll_interval_seconds = poll_interval_seconds
        self.mock = mock
        self.data = None
        self.data_fetched_at = None
        self.last_error = None
        self.last_poll_at = -poll_interval_seconds

        if self.mock is None and self.network.wifi_settings.skip_connection:
            raise ValueError("WiFi connection is disabled, cannot poll data")

    def refresh(self, force: bool = False) -> float:
        now = time.monotonic()
        if not force and not self._poll_due(now):
            return now

        self.last_poll_at = now

        try:
            self.data = self._fetch_data()
            self.data_fetched_at = time.monotonic()
            self.last_error = None
        except Exception as error:
            self.last_error = str(error)

        return now

    def _fetch_data(self):
        if self.mock is not None:
            return self.mock
        return self.network.get_json(self.url)

    def _poll_due(self, now: float) -> bool:
        return (now - self.last_poll_at) >= self.poll_interval_seconds
