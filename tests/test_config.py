import pytest

from crowd_detection.config import ConfigError, load_config


def test_defaults_are_valid():
    assert load_config().process_every_n_frames >= 1


def test_load_valid_file(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("source: video.mp4\nhigh_threshold: 20\nmedium_threshold: 8\n")
    cfg = load_config(f)
    assert cfg.source == "video.mp4"
    assert cfg.high_threshold == 20


def test_missing_file():
    with pytest.raises(ConfigError):
        load_config("nope.yaml")


def test_unknown_key(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("sorce: 0\n")
    with pytest.raises(ConfigError):
        load_config(f)


def test_thresholds_must_be_ordered(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("medium_threshold: 10\nhigh_threshold: 5\n")
    with pytest.raises(ConfigError):
        load_config(f)


@pytest.mark.parametrize("roi", ["[0.5, 0.5]", "[0.6, 0.1, 0.4, 0.9]", "[0, 0, 1.5, 1]"])
def test_bad_roi_rejected(tmp_path, roi):
    f = tmp_path / "c.yaml"
    f.write_text(f"roi: {roi}\n")
    with pytest.raises(ConfigError):
        load_config(f)


def test_good_roi_accepted(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("roi: [0.1, 0.1, 0.9, 0.9]\n")
    assert load_config(f).roi == [0.1, 0.1, 0.9, 0.9]


def test_bad_detector_name(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("detector: magic\n")
    with pytest.raises(ConfigError):
        load_config(f)


@pytest.mark.parametrize("size", [100, 610])
def test_bad_yolo_input_size(tmp_path, size):
    f = tmp_path / "c.yaml"
    f.write_text(f"yolo_input_size: {size}\n")
    with pytest.raises(ConfigError):
        load_config(f)
