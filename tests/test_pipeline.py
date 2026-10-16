"""Integration test: run the whole pipeline on a tiny generated video with a fake detector."""
import cv2
import numpy as np
import pytest

from crowd_detection.config import Config
from crowd_detection.pipeline import resize_to_width, run


class FakeDetector:
    """Always finds 3 people, so the result is predictable."""

    def detect(self, frame):
        return [(10, 10, 30, 80), (100, 10, 30, 80), (200, 10, 30, 80)]


@pytest.fixture()
def tiny_video(tmp_path):
    path = tmp_path / "tiny.mp4"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for _ in range(12):
        writer.write(np.full((240, 320, 3), 90, dtype=np.uint8))
    writer.release()
    return path


def make_cfg(tiny_video, tmp_path, **kw):
    base = dict(source=str(tiny_video), frame_width=320, process_every_n_frames=2,
                medium_threshold=2, high_threshold=3, show_window=False,
                log_csv=str(tmp_path / "out" / "counts.csv"))
    base.update(kw)
    return Config(**base)


def test_run_counts_logs_and_alerts(tiny_video, tmp_path):
    cfg = make_cfg(tiny_video, tmp_path)
    stats = run(cfg, detector=FakeDetector())
    assert stats.frames_read == 12
    assert stats.frames_checked == 6          # every 2nd frame
    assert stats.peak_count == 3
    assert stats.level_checks["HIGH"] == 6
    assert stats.alerts == 1                  # cooldown stops repeated alerts
    rows = (tmp_path / "out" / "counts.csv").read_text().strip().splitlines()
    assert rows[0].startswith("timestamp")
    assert len(rows) == 7


def test_run_writes_output_video(tiny_video, tmp_path):
    out = tmp_path / "res" / "annotated.mp4"
    run(make_cfg(tiny_video, tmp_path, output_video=str(out)), detector=FakeDetector())
    assert out.exists() and out.stat().st_size > 0


def test_run_respects_roi(tiny_video, tmp_path):
    cfg = make_cfg(tiny_video, tmp_path, roi=[0.0, 0.0, 0.2, 1.0])  # only the left strip
    stats = run(cfg, detector=FakeDetector())
    assert stats.peak_count == 1


def test_run_raises_on_missing_source(tmp_path):
    with pytest.raises(RuntimeError):
        run(Config(source=str(tmp_path / "nope.mp4"), show_window=False, log_csv=None))


def test_resize_keeps_aspect_ratio():
    out = resize_to_width(np.zeros((480, 640, 3), dtype=np.uint8), 320)
    assert out.shape[:2] == (240, 320)


def test_run_without_model_files_raises_clear_error(tiny_video, tmp_path):
    from crowd_detection.detector import ModelNotFoundError

    cfg = make_cfg(tiny_video, tmp_path, detector="yolo", model_dir=str(tmp_path / "none"))
    with pytest.raises(ModelNotFoundError):
        run(cfg)


def test_build_detector_selects_hog():
    from crowd_detection.detector import PersonDetector, build_detector

    assert isinstance(build_detector(Config(detector="hog")), PersonDetector)
