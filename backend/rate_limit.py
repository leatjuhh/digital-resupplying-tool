"""In-memory login-rate-limiter (audit-bevinding PR-013).

Begrenst brute-force / credential-stuffing op het login-endpoint door mislukte
pogingen per client-sleutel (IP) te tellen en na een drempel een tijdelijke
blokkade op te leggen. Dit implementeert Power of Ten-regel 2 (begrensde
herhaling van een operatie) voor het loginpad.

AFWIJKING: R6.1 — deze module houdt bewust gedeelde, muteerbare state
(mislukte-login-tellers) op procesniveau bij. Dat valt onder de in de standaard
(hoofdstuk 3, Regel 6) toegestane uitzondering voor een cache met een expliciete
invalidatiestrategie: elke registratie vervalt automatisch na `window_seconds`
en een blokkade na `lockout_seconds`, en verlopen sleutels worden opgeruimd.
Toegang tot de state loopt via een `threading.Lock`, en de limiter wordt via
dependency injection (`get_login_rate_limiter`) aan de handler aangeboden in
plaats van als vrije globale.

Compenserende controle: `backend/test_rate_limit.py` (unit) en een
integratietest in `backend/test_security_hardening.py`.

Beperking: de state is per proces. Bij meerdere workers telt elke worker zijn
eigen pogingen; een gedistribueerde opzet vereist een gedeelde store (bv.
Redis) — bewust buiten scope gehouden conform de audit (PR-013).
"""
from __future__ import annotations

import logging
import math
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Standaardwaarden zijn bewust constanten (geen env-vlaggen) om het
# configuratieoppervlak klein te houden (R8.4); tests construeren de limiter met
# eigen, kleine waarden.
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_WINDOW_SECONDS = 300.0    # telvenster voor mislukte pogingen (5 min)
DEFAULT_LOCKOUT_SECONDS = 300.0   # blokkadeduur na te veel pogingen (5 min)
MAX_TRACKED_KEYS = 10_000         # bovengrens op geheugengebruik (R2/R3)


@dataclass
class _Entry:
    """Telstatus voor één client-sleutel."""
    fails: int = 0
    window_start: float = 0.0
    locked_until: float = 0.0


class LoginRateLimiter:
    """Telt mislukte inlogpogingen per sleutel en blokkeert tijdelijk.

    Gebruik:
        retry_after = limiter.check(key)   # None = toegestaan, anders seconden
        limiter.register_failure(key)      # na een mislukte poging
        limiter.reset(key)                 # na een geslaagde poging
    """

    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        window_seconds: float = DEFAULT_WINDOW_SECONDS,
        lockout_seconds: float = DEFAULT_LOCKOUT_SECONDS,
        max_tracked_keys: int = MAX_TRACKED_KEYS,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts moet >= 1 zijn")
        if window_seconds <= 0 or lockout_seconds <= 0:
            raise ValueError("window_seconds en lockout_seconds moeten > 0 zijn")
        self._max_attempts = max_attempts
        self._window = float(window_seconds)
        self._lockout = float(lockout_seconds)
        self._max_keys = max_tracked_keys
        self._now = time_fn
        self._entries: Dict[str, _Entry] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> Optional[int]:
        """Geef ``None`` als een poging is toegestaan, anders het aantal seconden
        (>= 1) tot de blokkade afloopt."""
        now = self._now()
        with self._lock:
            entry = self._entries.get(key)
            if entry is not None and entry.locked_until > now:
                return max(1, math.ceil(entry.locked_until - now))
            return None

    def register_failure(self, key: str) -> None:
        """Registreer een mislukte inlogpoging; blokkeer bij het bereiken van de
        drempel."""
        now = self._now()
        with self._lock:
            self._prune(now)
            entry = self._entries.get(key)
            if entry is None:
                if len(self._entries) >= self._max_keys:
                    self._evict_oldest()
                entry = _Entry(window_start=now)
                self._entries[key] = entry
            # Start een nieuw telvenster wanneer het vorige is verlopen.
            if now - entry.window_start > self._window:
                entry.fails = 0
                entry.window_start = now
            entry.fails += 1
            if entry.fails >= self._max_attempts:
                entry.locked_until = now + self._lockout
                logger.warning(
                    "Login rate limit: sleutel %s geblokkeerd na %d mislukte pogingen",
                    key,
                    entry.fails,
                )

    def reset(self, key: str) -> None:
        """Wis de telstatus na een geslaagde inlog."""
        with self._lock:
            self._entries.pop(key, None)

    def tracked_key_count(self) -> int:
        """Aantal sleutels dat momenteel in het geheugen wordt bijgehouden
        (voor observability/tests; de bovengrens is `max_tracked_keys`)."""
        with self._lock:
            return len(self._entries)

    # -- interne helpers; aangeroepen terwijl self._lock is vastgehouden --

    def _prune(self, now: float) -> None:
        """Verwijder sleutels waarvan zowel het telvenster is verlopen als de
        blokkade voorbij is, zodat het geheugen begrensd blijft."""
        expired = [
            k
            for k, e in self._entries.items()
            if e.locked_until <= now and now - e.window_start > self._window
        ]
        for k in expired:
            del self._entries[k]

    def _evict_oldest(self) -> None:
        """Bovengrens bereikt: verwijder de oudste registratie (R3). Dit is een
        zeldzaam pad (bv. een gedistribueerde aanval met veel IP's); log het."""
        oldest = min(self._entries, key=lambda k: self._entries[k].window_start)
        del self._entries[oldest]
        logger.warning(
            "Login rate limit: bovengrens van %d sleutels bereikt; oudste verwijderd",
            self._max_keys,
        )


# Eén procesbrede instantie. AFWIJKING: R6.1 — bewuste, gedocumenteerde
# module-level singleton (cache met invalidatie); toegang loopt via de
# dependency hieronder, niet als vrije globale in de handler.
_login_rate_limiter = LoginRateLimiter()


def get_login_rate_limiter() -> LoginRateLimiter:
    """FastAPI-dependency die de procesbrede limiter teruggeeft."""
    return _login_rate_limiter
