"""Main loop: read frames, detect people, draw results, log counts."""
from __future__ import annotations

import contextlib
import csv
import logging
import time
from pathlib import Path

import cv2
import numpy as np

from .alerts import AlertManager
from .config import Config
from .density import Level, classify, filter_by_roi, grid_counts
from .detector import build_detector
from .stats import RunStats

log = logging.getLogger("crowd_detection")

COLORS = {Level.LOW: (0, 200, 0), Level.MEDIUM: (0, 200, 255), Level.HIGH: (0, 0, 255)}


def resize_to_width(frame: np.ndarray, width: int) -> np.ndarray:
    h, w = frame.shape[:2]
    if w == width:
        return frame
    return cv2.resize(frame, (width, int(h * width / w)))


def draw_overlay(frame, boxes, level, count, grid, roi=None) -> np.ndarray:
    color = COLORS[level]
    H, W = frame.shape[:2]
    if roi is not None:
        p1 = (int(roi[0] * W), int(roi[1] * H))
        p2 = (int(roi[2] * W), int(roi[3] * H))
        cv2.rectangle(frame, p1, p2, (255, 200, 0), 1)
    for x, y, w, h in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    rows, cols = grid.shape
    for r in range(rows):
        for c in range(cols):
            if grid[r, c]:
                pos = (int((c + 0.5) * W / cols), int((r + 0.5) * H / rows))
                cv2.putText(frame, str(grid[r, c]), pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.rectangle(frame, (0, 0), (260, 36), (0, 0, 0), -1)
    cv2.putText(frame, f"People: {count}  Level: {level.value}", (8, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
    return frame


def run(cfg: Config, detector=None) -> RunStats:
    """Process the video source until it ends or the user quits. Returns run statistics."""
    cap = cv2.VideoCapture(cfg.source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {cfg.source!r}")

    try:
        detector = detector or build_detector(cfg)
    except Exception:
        cap.release()
        raise
    alerts = AlertManager(cfg.alert_cooldown_seconds)
    stats = RunStats()

    writer = None
    boxes: list = []
    count, level = 0, Level.LOW
    grid = np.zeros((cfg.grid_rows, cfg.grid_cols), dtype=int)
    start = time.monotonic()

    with contextlib.ExitStack() as stack:
        csv_writer = None
        if cfg.log_csv:
            Path(cfg.log_csv).parent.mkdir(parents=True, exist_ok=True)
            csv_file = stack.enter_context(open(cfg.log_csv, "w", newline=""))
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["timestamp", "frame", "count", "level"])

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    log.info("Video ended or stream lost.")
                    break
                frame = resize_to_width(frame, cfg.frame_width)
                H, W = frame.shape[:2]

                if stats.frames_read % cfg.process_every_n_frames == 0:
                    boxes = filter_by_roi(detector.detect(frame), cfg.roi, W, H)
                    count = len(boxes)
                    level = classify(count, cfg.medium_threshold, cfg.high_threshold)
                    grid = grid_counts(boxes, W, H, cfg.grid_rows, cfg.grid_cols)
                    alerted = alerts.check(level, count, time.monotonic())
                    stats.update(count, level, alerted)
                    if csv_writer:
                        csv_writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"),
                                             stats.frames_read, count, level.value])

                out = draw_overlay(frame, boxes, level, count, grid, cfg.roi)

                if cfg.output_video:
                    if writer is None:
                        Path(cfg.output_video).parent.mkdir(parents=True, exist_ok=True)
                        fps = cap.get(cv2.CAP_PROP_FPS) or 25
                        writer = cv2.VideoWriter(cfg.output_video,
                                                 cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
                    writer.write(out)

                if cfg.show_window:
                    cv2.imshow("Crowd Detection", out)
                    if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                        break
                stats.frames_read += 1
        except KeyboardInterrupt:
            log.info("Stopped by user.")
        finally:
            cap.release()
            if writer:
                writer.release()
            if cfg.show_window:
                cv2.destroyAllWindows()
            stats.seconds = time.monotonic() - start
    return stats
