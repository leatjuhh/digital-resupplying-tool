"""Unit-tests voor de login-rate-limiter (PR-013).

Deze tests gebruiken een geïnjecteerde, bestuurbare klok in plaats van echte
tijd, zodat het gedrag deterministisch is en er geen `sleep` nodig is. Ze zijn
de compenserende controle bij de R6.1-afwijking in backend/rate_limit.py.
"""
from __future__ import annotations

import pytest

from rate_limit import LoginRateLimiter


class _FakeClock:
    """Bestuurbare monotone klok voor deterministische tests."""

    def __init__(self, start: float = 1000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _make(max_attempts: int = 3, window: float = 60.0, lockout: float = 120.0,
          max_keys: int = 10_000):
    clock = _FakeClock()
    limiter = LoginRateLimiter(
        max_attempts=max_attempts,
        window_seconds=window,
        lockout_seconds=lockout,
        max_tracked_keys=max_keys,
        time_fn=clock,
    )
    return limiter, clock


def test_allows_attempts_below_threshold():
    limiter, _ = _make(max_attempts=3)
    assert limiter.check("ip") is None
    limiter.register_failure("ip")
    limiter.register_failure("ip")
    # Twee mislukte pogingen (< drempel 3): nog steeds toegestaan.
    assert limiter.check("ip") is None


def test_blocks_at_threshold_with_retry_after():
    limiter, _ = _make(max_attempts=3, lockout=120.0)
    for _ in range(3):
        limiter.register_failure("ip")
    retry_after = limiter.check("ip")
    assert retry_after is not None
    assert 1 <= retry_after <= 120


def test_lockout_expires_after_lockout_seconds():
    limiter, clock = _make(max_attempts=3, lockout=120.0)
    for _ in range(3):
        limiter.register_failure("ip")
    assert limiter.check("ip") is not None
    clock.advance(120.0)
    # Blokkade verlopen: weer toegestaan.
    assert limiter.check("ip") is None


def test_retry_after_decreases_over_time():
    limiter, clock = _make(max_attempts=1, lockout=100.0)
    limiter.register_failure("ip")
    first = limiter.check("ip")
    clock.advance(40.0)
    second = limiter.check("ip")
    assert first is not None and second is not None
    assert second < first


def test_reset_clears_lockout():
    limiter, _ = _make(max_attempts=3)
    for _ in range(3):
        limiter.register_failure("ip")
    assert limiter.check("ip") is not None
    limiter.reset("ip")
    assert limiter.check("ip") is None


def test_window_resets_failure_counter():
    limiter, clock = _make(max_attempts=3, window=60.0)
    limiter.register_failure("ip")
    limiter.register_failure("ip")
    # Venster verloopt vóór de derde poging: de teller begint opnieuw.
    clock.advance(61.0)
    limiter.register_failure("ip")
    assert limiter.check("ip") is None


def test_keys_are_independent():
    limiter, _ = _make(max_attempts=2)
    limiter.register_failure("a")
    limiter.register_failure("a")
    # 'a' is geblokkeerd, 'b' niet.
    assert limiter.check("a") is not None
    assert limiter.check("b") is None


def test_prune_removes_fully_expired_keys():
    limiter, clock = _make(max_attempts=3, window=60.0, lockout=60.0)
    limiter.register_failure("a")
    limiter.register_failure("b")
    assert limiter.tracked_key_count() == 2
    # Beide sleutels: venster én (niet-actieve) blokkade verlopen.
    clock.advance(61.0)
    limiter.register_failure("c")  # triggert prune
    assert limiter.tracked_key_count() == 1


def test_tracked_keys_are_bounded():
    limiter, _ = _make(max_attempts=5, max_keys=2)
    for key in ("a", "b", "c", "d"):
        limiter.register_failure(key)
    # Nooit meer dan de bovengrens, ongeacht het aantal unieke sleutels.
    assert limiter.tracked_key_count() <= 2


def test_invalid_configuration_raises():
    with pytest.raises(ValueError):
        LoginRateLimiter(max_attempts=0)
    with pytest.raises(ValueError):
        LoginRateLimiter(window_seconds=0)
    with pytest.raises(ValueError):
        LoginRateLimiter(lockout_seconds=-1)
