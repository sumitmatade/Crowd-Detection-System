# Crowd Detection System

[![CI](https://github.com/YOUR-USERNAME/crowd-detection-system/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/crowd-detection-system/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Counts people in a webcam, video file, or RTSP stream and labels the scene **LOW**, **MEDIUM**, or **HIGH**. It draws boxes, shows per-area counts, logs everything to CSV, and fires an alert (with a cooldown) when the crowd gets too big.

![Demo](screenshots/demo.gif)

<p>
  <img src="screenshots/demo.png" width="49%" alt="Medium crowd level">
  <img src="screenshots/high-alert.png" width="49%" alt="High crowd level with alert">
</p>

*Real output on OpenCV's public sample video (details in [Evaluation](#evaluation)).*

## Features

- Input: webcam, video file, or RTSP camera
- Two detectors you can switch in one line: **YOLOv4-tiny** (accurate) or **HOG** (no download)
- LOW / MEDIUM / HIGH levels with thresholds you set
- Region of interest: count only inside an area you choose
- Per-area grid counts on the video
- Alerts with a cooldown
- CSV log, optional annotated output video, and a summary when the run ends
- All settings in one validated YAML file
- 38 unit and integration tests, linted with ruff, CI on Python 3.10 to 3.12

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/crowd-detection-system.git
cd crowd-detection-system

python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -e .

python scripts/download_models.py      # one-time, about 24 MB
python scripts/download_sample.py      # optional sample video, about 8 MB

crowd-detection --config examples/demo.yaml     # run on the sample video
```

Use your own source:

```bash
cp config.example.yaml config.yaml     # then edit it
crowd-detection --config config.yaml
crowd-detection --source 0                       # webcam
crowd-detection --source rtsp://user:pass@host/stream --no-window
```

Press `q` or `Esc` to quit. When the run ends you get a summary:

```
Frames read: 795 | checked: 265
People per checked frame: average 5.62, peak 8
Alerts fired: 6 | speed: 11.6 frames/sec
```

No model download wanted? Set `detector: hog` in the config. It works out of the box but is much weaker (see below).

## Evaluation

I compared both detectors on `vtest.avi`, OpenCV's public pedestrian sample (768x576, 795 frames, about 5 to 8 people in view, small and far from the camera).

| Detector | Mean people per checked frame | Detector time per frame |
|----------|-------------------------------|-------------------------|
| HOG | 0.97 | 140 ms |
| YOLOv4-tiny (input 608) | 5.97 | 236 ms |

How this was measured: first 300 frames, every 3rd frame checked, width 640, a single-core cloud CPU. Your speed will differ. Reproduce with:

```bash
python scripts/benchmark.py videos/vtest.avi --detector yolo
python scripts/benchmark.py videos/vtest.avi --detector hog
```

**What this does and does not show.** I checked a handful of frames by eye: about 6 to 8 people are visible, so YOLO is close and HOG misses most of them. HOG needs people about 128 px tall, and here they are 30 to 50 px. This is **not** a formal accuracy score. There is no labeled ground truth here, so there is no precision/recall number. See [docs/evaluation.md](docs/evaluation.md) for the method and how to add one.

## How it works

```
video -> resize -> detector -> region filter -> level + grid -> alert / overlay / CSV
```

Detection runs on every N-th frame to keep video smooth. See [docs/architecture.md](docs/architecture.md).

## Project layout

```
src/crowd_detection/   package: detector, density, alerts, stats, pipeline, cli
tests/                 pytest tests (unit + end-to-end with a fake detector)
scripts/               download models/sample, benchmark, make screenshots
examples/              ready-to-run demo config
docs/                  architecture, usage, evaluation
screenshots/           images used in this README
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Known limits

- It counts people **per frame**. It does not track individuals, so it cannot tell how many *different* people passed by.
- YOLOv4-tiny is small and fast, not state of the art. It can miss people who are tiny, partly hidden, or in dense crowds, and the count is an estimate.
- Needs OpenCV 4.x. OpenCV 5 removed the HOG and Darknet loaders this project uses, so `pyproject.toml` pins `opencv-python<5`. Moving to OpenCV 5 would need an ONNX model.
- Alert cooldown uses wall-clock time. When you process a video file faster or slower than real time, alerts follow processing time, not video time.
- CPU only. At 608 input this runs at roughly 12 frames/sec on a single core with frame skipping.
- Not safety-grade. Do not use it alone for real crowd-safety decisions.

Planned improvements are listed in [CHANGELOG.md](CHANGELOG.md).

## Credits

- Sample video: `vtest.avi` from the [OpenCV](https://github.com/opencv/opencv) samples (Apache-2.0).
- Model: YOLOv4-tiny trained on COCO, from [AlexeyAB/darknet](https://github.com/AlexeyAB/darknet). Weights are downloaded by the script, not stored in this repo.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md). Licensed under the MIT License ([LICENSE](LICENSE)).
