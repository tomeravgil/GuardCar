from pybreaker import CircuitBreakerListener

class ExponentialBackoffListener(CircuitBreakerListener):
    def __init__(self, base_timeout=5, factor=2.0, max_timeout=300):
        self.base_timeout = base_timeout
        self.factor = factor
        self.max_timeout = max_timeout

    def state_change(self, cb, old_state, new_state):
        if new_state.name == "open":
            # Circuit opened → backoff increases
            # (if current timeout too small, grow it)
            cb.reset_timeout = min(cb.reset_timeout * self.factor, self.max_timeout)

        elif new_state.name == "closed":
            # Circuit healed → reset backoff
            cb.reset_timeout = self.base_timeout
