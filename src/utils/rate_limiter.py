import asyncio
import time
from collections import deque
from typing import Deque, Optional, Type, Any

class AsyncRateLimiter:
    """
    An asynchronous rate limiter to manage API call frequency,
    usable as an async context manager.
    """
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.timestamps: Deque[float] = deque()
        self._lock = asyncio.Lock()

    def can_make_request(self) -> bool:
        """Checks if a request can be made without waiting."""
        self._prune_timestamps()
        return len(self.timestamps) < self.max_calls

    async def force_wait(self):
        """Forces the limiter to be in a 'waiting' state for a short duration."""
        async with self._lock:
            # Add a timestamp to effectively block this limiter for a bit
            self.timestamps.append(time.time())

    def _prune_timestamps(self):
        """Removes timestamps that are outside the current time window."""
        current_time = time.time()
        while self.timestamps and current_time - self.timestamps[0] > self.period:
            self.timestamps.popleft()

    async def __aenter__(self):
        """Async context manager entry."""
        async with self._lock:
            while not self.can_make_request():
                time_since_oldest = time.time() - self.timestamps[0]
                wait_time = self.period - time_since_oldest
                await asyncio.sleep(wait_time)
            self.timestamps.append(time.time())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ):
        """Async context manager exit."""
        pass
