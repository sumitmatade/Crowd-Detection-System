"""Alert logic with a cooldown, so one crowd does not trigger endless alerts."""
from __future__ import annotations

import logging

from .density import Level

log = logging.getLogger("crowd_detection")


class AlertManager:
    def __init__(self, cooldown_seconds: float = 10.0):
        self.cooldown = cooldown_seconds
        self._last_alert_time: float | None = None

    def check(self, level: Level, count: int, now: float) -> bool:
        """Return True (and log a warning) if an alert should fire at time `now`."""
        if level != Level.HIGH:
            return False
        if self._last_alert_time is not None and now - self._last_alert_time < self.cooldown:
            return False
        self._last_alert_time = now
        log.warning("HIGH crowd level: %d people detected", count)
        return True
