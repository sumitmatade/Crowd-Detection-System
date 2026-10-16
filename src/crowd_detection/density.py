"""Turn detections into a crowd level, a region-of-interest filter, and a grid count."""
from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

import numpy as np

Box = tuple[int, int, int, int]  # x, y, w, h


class Level(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def classify(count: int, medium: int, high: int) -> Level:
    """Map a people count to a crowd level."""
    if count < 0:
        raise ValueError("count cannot be negative")
    if count >= high:
        return Level.HIGH
    if count >= medium:
        return Level.MEDIUM
    return Level.LOW


def filter_by_roi(boxes: Sequence[Box], roi: Sequence[float] | None,
                  width: int, height: int) -> list[Box]:
    """Keep only boxes whose center is inside the region of interest.

    `roi` is [x1, y1, x2, y2] as fractions of the frame (0 to 1). None keeps everything.
    """
    if roi is None:
        return list(boxes)
    x1, y1, x2, y2 = roi[0] * width, roi[1] * height, roi[2] * width, roi[3] * height
    kept = []
    for x, y, w, h in boxes:
        cx, cy = x + w / 2, y + h / 2
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            kept.append((x, y, w, h))
    return kept


def grid_counts(boxes: Sequence[Box], width: int, height: int,
                rows: int, cols: int) -> np.ndarray:
    """Count people per grid cell, using the center of each box."""
    grid = np.zeros((rows, cols), dtype=int)
    for x, y, w, h in boxes:
        cx, cy = x + w / 2, y + h / 2
        if not (0 <= cx < width and 0 <= cy < height):
            continue
        r = min(int(cy / height * rows), rows - 1)
        c = min(int(cx / width * cols), cols - 1)
        grid[r, c] += 1
    return grid
