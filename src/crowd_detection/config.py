"""Load and validate settings from a YAML file."""
from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path


class ConfigError(ValueError):
    """Raised when the config file has invalid values."""


@dataclass
class Config:
    source: int | str = 0                 # webcam index, video file path, or RTSP URL
    detector: str = "yolo"                # "yolo" (accurate, needs model download) or "hog"
    yolo_input_size: int = 608            # bigger sees smaller people, slower (multiple of 32)
    model_dir: str = "models"             # where scripts/download_models.py saves the YOLO files
    frame_width: int = 640                # frames are resized to this width before detection
    process_every_n_frames: int = 2       # skip frames to save CPU
    min_confidence: float | None = None   # ignore weaker detections (None = sensible default)
    hog_max_height_fraction: float = 0.45  # HOG only: drop boxes taller than this share of frame
    nms_threshold: float = 0.4            # overlap limit when merging boxes
    medium_threshold: int = 5             # people count where level becomes MEDIUM
    high_threshold: int = 10              # people count where level becomes HIGH
    alert_cooldown_seconds: float = 10.0  # minimum gap between two alerts
    grid_rows: int = 3                    # per-area count grid size
    grid_cols: int = 3
    roi: list[float] | None = None        # [x1, y1, x2, y2] as 0-1 fractions; count only inside
    show_window: bool = True
    output_video: str | None = None       # e.g. "output/result.mp4"
    log_csv: str | None = "output/counts.csv"

    def validate(self) -> None:
        if self.detector not in ("yolo", "hog"):
            raise ConfigError("detector must be 'yolo' or 'hog'")
        if self.yolo_input_size < 160 or self.yolo_input_size % 32 != 0:
            raise ConfigError("yolo_input_size must be a multiple of 32 and at least 160")
        if self.min_confidence is not None and not 0.0 <= self.min_confidence <= 1.0:
            raise ConfigError("min_confidence must be between 0 and 1")
        if self.frame_width < 100:
            raise ConfigError("frame_width must be at least 100")
        if self.process_every_n_frames < 1:
            raise ConfigError("process_every_n_frames must be at least 1")
        if not 0.0 <= self.nms_threshold <= 1.0:
            raise ConfigError("nms_threshold must be between 0 and 1")
        if self.medium_threshold >= self.high_threshold:
            raise ConfigError("medium_threshold must be lower than high_threshold")
        if self.grid_rows < 1 or self.grid_cols < 1:
            raise ConfigError("grid_rows and grid_cols must be at least 1")
        if self.alert_cooldown_seconds < 0:
            raise ConfigError("alert_cooldown_seconds cannot be negative")
        if self.roi is not None:
            if len(self.roi) != 4:
                raise ConfigError("roi must have 4 numbers: [x1, y1, x2, y2]")
            x1, y1, x2, y2 = self.roi
            if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
                raise ConfigError("roi values must satisfy 0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1")


def load_config(path: str | Path | None = None) -> Config:
    """Read a YAML file. With no path, return the defaults."""
    import yaml  # imported here so the rest of the package works without it

    if path is None:
        cfg = Config()
        cfg.validate()
        return cfg
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"Config file not found: {p}")
    data = yaml.safe_load(p.read_text()) or {}
    if not isinstance(data, dict):
        raise ConfigError("Config file must contain key: value pairs")
    unknown = set(data) - {f.name for f in fields(Config)}
    if unknown:
        raise ConfigError(f"Unknown config keys: {', '.join(sorted(unknown))}")
    cfg = Config(**data)
    cfg.validate()
    return cfg
