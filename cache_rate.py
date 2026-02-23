import time
from functools import lru_cache
from threading import Lock

class RateLimiter:
    def __init__(self, max_calls: int = 10, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = Lock()

    def allow(self) -> bool:
        with self.lock:
            now = time.time()
            self.calls = [c for c in self.calls if now - c < self.period]

            if len(self.calls) >= self.max_calls:
                return False

            self.calls.append(now)
            return True