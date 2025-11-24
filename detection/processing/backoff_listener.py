from aiobreaker import CircuitBreakerListener
import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncExponentialBackoffListener(CircuitBreakerListener):
    def __init__(self, base_timeout=5, factor=2.0, max_timeout=120):
        self.base_timeout = base_timeout
        self.factor = factor
        self.max_timeout = max_timeout
        self.current_timeout = base_timeout

    async def state_change(self, breaker, old_state, new_state):
        if new_state.name == "open":
            logger.warning(f"Circuit opened. Backing off {self.current_timeout}s")
            await asyncio.sleep(self.current_timeout)
            self.current_timeout = min(self.current_timeout * self.factor, self.max_timeout)
        elif new_state.name == "half-open":
            logger.info("Circuit half-open: testing...")
        elif new_state.name == "closed":
            logger.info("Circuit closed: reset backoff")
            self.current_timeout = self.base_timeout
