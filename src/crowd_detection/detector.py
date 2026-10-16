"""People detectors.

Two options, chosen with `detector:` in the config:
  - "yolo": YOLOv4-tiny through OpenCV's DNN module. Much better, needs a model download.
  - "hog":  OpenCV's built-in HOG people detector. No download, but weak on small people.

Any class with a `detect(frame) -> list[(x, y, w, h)]` method can be used as a detector.
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import cv2
import numpy as np

Box = tuple[int, int, int, int]  # x, y, w, h

YOLO_CFG = "yolov4-tiny.cfg"
YOLO_WEIGHTS = "yolov4-tiny.weights"


class ModelNotFoundError(RuntimeError):
    """Raised when the YOLO model files are missing."""


def merge_boxes(boxes: list[Box], scores: list[float], nms_threshold: float,
                score_threshold: float = 0.0) -> list[Box]:
    """Remove overlapping boxes (non-maximum suppression). Higher scores win."""
    if not boxes:
        return []
    idx = cv2.dnn.NMSBoxes([list(map(int, b)) for b in boxes],
                           [float(s) for s in scores], score_threshold, nms_threshold)
    idx = np.array(idx).flatten()
    return [tuple(int(v) for v in boxes[i]) for i in idx]


def parse_yolo_output(outputs: Sequence[np.ndarray], width: int, height: int,
                      min_confidence: float) -> tuple[list[Box], list[float]]:
    """Pick 'person' detections (class 0) out of raw YOLO output arrays.

    Each row is [cx, cy, w, h, objectness, class scores...], with positions as fractions.
    """
    boxes: list[Box] = []
    scores: list[float] = []
    for out in outputs:
        for row in out:
            class_scores = row[5:]
            if int(np.argmax(class_scores)) != 0:
                continue
            conf = float(row[4] * class_scores[0])
            if conf < min_confidence:
                continue
            w, h = row[2] * width, row[3] * height
            x, y = row[0] * width - w / 2, row[1] * height - h / 2
            x1, y1 = max(0, int(x)), max(0, int(y))
            x2, y2 = min(width, int(x + w)), min(height, int(y + h))
            if x2 - x1 < 2 or y2 - y1 < 2:
                continue
            boxes.append((x1, y1, x2 - x1, y2 - y1))
            scores.append(conf)
    return boxes, scores


class YoloDetector:
    """YOLOv4-tiny person detector running on the CPU via OpenCV."""

    def __init__(self, model_dir: str | Path = "models", input_size: int = 608,
                 min_confidence: float = 0.25, nms_threshold: float = 0.4):
        model_dir = Path(model_dir)
        cfg, weights = model_dir / YOLO_CFG, model_dir / YOLO_WEIGHTS
        if not cfg.is_file() or not weights.is_file():
            raise ModelNotFoundError(
                f"YOLO model files not found in '{model_dir}'. "
                "Run: python scripts/download_models.py   (or set detector: hog in your config)"
            )
        self.input_size = input_size
        self.min_confidence = min_confidence
        self.nms_threshold = nms_threshold
        self._net = cv2.dnn.readNetFromDarknet(str(cfg), str(weights))
        self._out_names = self._net.getUnconnectedOutLayersNames()

    def detect(self, frame: np.ndarray) -> list[Box]:
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (self.input_size, self.input_size),
                                     swapRB=True, crop=False)
        self._net.setInput(blob)
        outputs = self._net.forward(self._out_names)
        boxes, scores = parse_yolo_output(outputs, w, h, self.min_confidence)
        return merge_boxes(boxes, scores, self.nms_threshold, self.min_confidence)


class PersonDetector:
    """HOG + SVM detector. Needs people to be fairly large in the frame (about 128 px tall).

    Boxes taller than `max_height_fraction` of the frame are dropped, because the HOG detector
    often draws oversized false boxes around groups.
    """

    def __init__(self, min_confidence: float = 0.3, nms_threshold: float = 0.4,
                 max_height_fraction: float = 0.45):
        self.min_confidence = min_confidence
        self.nms_threshold = nms_threshold
        self.max_height_fraction = max_height_fraction
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame: np.ndarray) -> list[Box]:
        """Return a list of (x, y, w, h) boxes, one per detected person."""
        max_h = self.max_height_fraction * frame.shape[0]
        rects, weights = self._hog.detectMultiScale(
            frame, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        boxes, scores = [], []
        for rect, weight in zip(rects, np.array(weights).flatten(), strict=False):
            if weight >= self.min_confidence and rect[3] <= max_h:
                boxes.append(tuple(int(v) for v in rect))
                scores.append(float(weight))
        return merge_boxes(boxes, scores, self.nms_threshold)


def build_detector(cfg):
    """Create the detector chosen in the config."""
    if cfg.detector == "yolo":
        conf = 0.25 if cfg.min_confidence is None else cfg.min_confidence
        return YoloDetector(cfg.model_dir, cfg.yolo_input_size, conf, cfg.nms_threshold)
    conf = 0.3 if cfg.min_confidence is None else cfg.min_confidence
    return PersonDetector(conf, cfg.nms_threshold, cfg.hog_max_height_fraction)
