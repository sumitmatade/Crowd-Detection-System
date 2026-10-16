"""Simple run statistics, printed when the program ends."""
from __future__ import annotations

from dataclasses import dataclass, field

from .density import Level


@dataclass
class RunStats:
    frames_read: int = 0
    frames_checked: int = 0
    peak_count: int = 0
    total_count: int = 0
    alerts: int = 0
    seconds: float = 0.0
    level_checks: dict[str, int] = field(default_factory=lambda: {lv.value: 0 for lv in Level})

    def update(self, count: int, level: Level, alerted: bool) -> None:
        self.frames_checked += 1
        self.total_count += count
        self.peak_count = max(self.peak_count, count)
        self.level_checks[level.value] += 1
        if alerted:
            self.alerts += 1

    @property
    def average_count(self) -> float:
        return self.total_count / self.frames_checked if self.frames_checked else 0.0

    @property
    def fps(self) -> float:
        return self.frames_read / self.seconds if self.seconds > 0 else 0.0

    def summary(self) -> str:
        levels = ", ".join(f"{k}: {v}" for k, v in self.level_checks.items())
        return (
            f"Frames read: {self.frames_read} | checked: {self.frames_checked}\n"
            f"People per checked frame: average {self.average_count:.2f}, peak {self.peak_count}\n"
            f"Level counts -> {levels}\n"
            f"Alerts fired: {self.alerts} | speed: {self.fps:.1f} frames/sec"
        )
