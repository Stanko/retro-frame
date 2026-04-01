import gc
import time


class GarbageCollectorModule:
    def __init__(self, collection_interval_seconds: float = 30):
        self.collection_interval_seconds = collection_interval_seconds
        self.last_collection_at = time.monotonic()

    def run_if_due(self, now: float = None) -> bool:
        if now is None:
            now = time.monotonic()

        if (now - self.last_collection_at) < self.collection_interval_seconds:
            return False

        gc.collect()
        self.last_collection_at = now
        return True
