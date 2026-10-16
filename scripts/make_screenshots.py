"""Create the README screenshots and demo GIF from a real video, using real detector output.

Usage: python scripts/make_screenshots.py videos/vtest.avi
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from crowd_detection.config import Config
from crowd_detection.density import Level, classify, grid_counts
from crowd_detection.detector import build_detector
from crowd_detection.pipeline import draw_overlay, resize_to_width

MEDIUM, HIGH = 4, 6   # set for the sample clip, which has about 5 to 8 people in view
EVERY = 3
GIF_FRAMES = 24
OUT = Path("screenshots")


def main(video: str) -> None:
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open {video}")
    detector = build_detector(Config(detector="yolo"))
    annotated, counts, n = [], [], 0
    while n < 450:
        ok, frame = cap.read()
        if not ok:
            break
        if n % EVERY == 0:
            frame = resize_to_width(frame, 640)
            H, W = frame.shape[:2]
            boxes = detector.detect(frame)
            level = classify(len(boxes), MEDIUM, HIGH)
            grid = grid_counts(boxes, W, H, 3, 3)
            annotated.append(draw_overlay(frame.copy(), boxes, level, len(boxes), grid))
            counts.append(len(boxes))
        n += 1

    OUT.mkdir(exist_ok=True)
    peak = int(np.argmax(counts))
    mid = next((i for i, c in enumerate(counts) if MEDIUM <= c < HIGH and i > 10), len(counts) // 2)
    cv2.imwrite(str(OUT / "demo.png"), annotated[mid])
    cv2.imwrite(str(OUT / "high-alert.png"), annotated[peak])

    start = max(0, min(peak - GIF_FRAMES // 2, len(annotated) - GIF_FRAMES))
    frames = []
    for f in annotated[start:start + GIF_FRAMES]:
        small = cv2.resize(f, (400, int(f.shape[0] * 400 / f.shape[1])))
        frames.append(Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)))
    frames = [f.quantize(colors=64) for f in frames]
    frames[0].save(OUT / "demo.gif", save_all=True, append_images=frames[1:],
                   duration=250, loop=0, optimize=True)
    levels = [classify(c, MEDIUM, HIGH) for c in counts]
    print(f"checked {len(counts)} frames; peak {max(counts)}; "
          f"HIGH frames: {levels.count(Level.HIGH)}; saved demo.png, high-alert.png, demo.gif")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "videos/vtest.avi")
