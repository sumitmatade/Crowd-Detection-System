import numpy as np

from crowd_detection.detector import PersonDetector, merge_boxes


def test_merge_boxes_removes_heavy_overlap():
    boxes = [(10, 10, 50, 100), (12, 12, 50, 100), (200, 10, 50, 100)]
    merged = merge_boxes(boxes, [0.9, 0.5, 0.8], 0.4)
    assert len(merged) == 2


def test_merge_boxes_empty():
    assert merge_boxes([], [], 0.4) == []


def test_detector_returns_zero_on_blank_frame():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    assert PersonDetector().detect(frame) == []


def _yolo_row(box, objectness, cls, cls_score):
    """Build one fake YOLO output row: [cx, cy, w, h, objectness, 80 class scores]."""
    row = np.zeros(85)
    row[:4] = box
    row[4] = objectness
    row[5 + cls] = cls_score
    return row


def test_parse_yolo_output_keeps_only_confident_people():
    from crowd_detection.detector import parse_yolo_output

    person = _yolo_row([0.5, 0.5, 0.2, 0.4], 0.9, 0, 0.9)
    car = _yolo_row([0.2, 0.2, 0.2, 0.2], 0.9, 2, 0.9)
    weak = _yolo_row([0.8, 0.8, 0.1, 0.2], 0.3, 0, 0.5)   # confidence 0.15
    boxes, scores = parse_yolo_output([np.array([person, car, weak])], 100, 100, 0.25)
    assert boxes == [(40, 30, 20, 40)]
    assert scores[0] > 0.8


def test_parse_yolo_output_clips_to_frame():
    from crowd_detection.detector import parse_yolo_output

    row = _yolo_row([0.99, 0.5, 0.2, 0.4], 1.0, 0, 1.0)
    boxes, _ = parse_yolo_output([np.array([row])], 100, 100, 0.25)
    x, _y, w, _h = boxes[0]
    assert x + w <= 100


def test_yolo_missing_model_gives_clear_error(tmp_path):
    import pytest

    from crowd_detection.detector import ModelNotFoundError, YoloDetector

    with pytest.raises(ModelNotFoundError, match="download_models"):
        YoloDetector(model_dir=tmp_path)


def test_hog_drops_oversized_boxes():
    from crowd_detection.detector import PersonDetector

    det = PersonDetector(min_confidence=0.0, max_height_fraction=0.0001)
    assert det.detect(np.zeros((480, 640, 3), dtype=np.uint8)) == []
