# Changelog

All notable changes are listed here. Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Planned
- Tracking, so unique people can be counted over time
- Video-time based alert cooldown for file input
- Move to OpenCV 5 with an ONNX model
- Optional larger models (YOLOv4, YOLOv8 via ONNX) for dense crowds
- Formal accuracy numbers on a labeled dataset (see `docs/evaluation.md`)
- Email or webhook alerts

## [1.1.0] - 2026-10-14

### Added
- YOLOv4-tiny detector through OpenCV DNN (now the default), with `scripts/download_models.py` and a pinned checksum
- Region of interest (`roi`) setting
- Run summary (average, peak, level counts, alerts, speed) printed at exit
- `pyproject.toml`: install with `pip install -e .`, command `crowd-detection`
- `scripts/` for model and sample download, benchmark, and screenshot generation
- Real screenshots and a demo GIF, plus `docs/evaluation.md`
- Integration tests for the full pipeline; 38 tests in total
- Ruff linting, issue and pull request templates, Dependabot, SECURITY.md, CODE_OF_CONDUCT.md, Makefile

### Changed
- HOG detector now drops oversized boxes (`hog_max_height_fraction`)
- `min_confidence` defaults per detector instead of one shared value
- CI runs lint and tests on Python 3.10, 3.11 and 3.12

### Fixed
- Pinned `opencv-python<5`: OpenCV 5 removed `HOGDescriptor` and `readNetFromDarknet`, which broke fresh installs
- Webcam and video capture is now released if the detector fails to load

## [1.0.0] - 2026-10-14

### Added
- People counting from webcam, video file, or RTSP stream (HOG detector)
- LOW / MEDIUM / HIGH crowd levels with configurable thresholds
- Per-area grid counts drawn on the video
- Alerts with a cooldown
- CSV logging and optional annotated video output
- YAML configuration with validation
