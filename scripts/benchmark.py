"""Measure detector speed and counts on a video. Results depend on your machine.

Usage: python scripts/benchmark.py videos/vtest.avi --detector yolo --every 3 --max-frames 300
"""
import argparse
import statistics
import time

import cv2

from crowd_detection.config import Config
from crowd_detection.detector import build_detector
from crowd_detection.pipeline import resize_to_width


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--detector", choices=["yolo", "hog"], default="yolo")
    p.add_argument("--input-size", type=int, default=608, help="YOLO input size")
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--every", type=int, default=3, help="check every N-th frame")
    p.add_argument("--max-frames", type=int, default=300)
    args = p.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open {args.video}")
    detector = build_detector(Config(detector=args.detector, yolo_input_size=args.input_size))
    counts, times, n = [], [], 0
    while n < args.max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if n % args.every == 0:
            frame = resize_to_width(frame, args.width)
            t = time.perf_counter()
            counts.append(len(detector.detect(frame)))
            times.append(time.perf_counter() - t)
        n += 1
    if not counts:
        raise SystemExit("No frames were checked.")
    print(f"detector: {args.detector}")
    print(f"frames read: {n}, checked: {len(counts)} (every {args.every}), width: {args.width}")
    print(f"detector time per checked frame: mean {statistics.mean(times) * 1000:.0f} ms, "
          f"median {statistics.median(times) * 1000:.0f} ms")
    print(f"people per checked frame: mean {statistics.mean(counts):.2f}, "
          f"median {statistics.median(counts)}, max {max(counts)}")


if __name__ == "__main__":
    main()
