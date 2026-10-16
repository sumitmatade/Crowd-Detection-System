# Architecture

## Flow

```
video source -> resize -> detector -> ROI filter -> level + grid -> overlay / CSV / alert
                  (every N-th frame)                                       |
                                                                  stats summary at exit
```

## Modules (`src/crowd_detection/`)

| File | Job |
|------|-----|
| `config.py` | Reads the YAML file and validates every value |
| `detector.py` | `YoloDetector`, `PersonDetector` (HOG), box merging, `build_detector` |
| `density.py` | Count to level, region-of-interest filter, per-area grid counts |
| `alerts.py` | Decides when to fire an alert (with a cooldown) |
| `stats.py` | Collects average, peak, level counts, alerts, speed |
| `pipeline.py` | The main loop that connects everything |
| `cli.py` | Command line options (`crowd-detection`) |

## Design choices

- **Detectors are swappable.** The pipeline only needs an object with `detect(frame)` returning `(x, y, w, h)` boxes. To add a new model, write one class and register it in `build_detector`.
- **Pure logic is easy to test.** `density.py`, `alerts.py`, `stats.py`, `config.py` and the YOLO output parser need no camera or model, so the tests run in under a second.
- **The pipeline is tested end to end.** Tests pass a fake detector and a tiny generated video, so CSV output, alerts, the ROI and video writing are checked without any model download.
- **Time is passed in.** `AlertManager.check` takes the current time as an argument, so tests do not need to wait.
- **Frame skipping.** Detection is the slow step. Running it every N-th frame keeps the video smooth. The last boxes stay on screen in between.
- **YOLO through OpenCV DNN.** No PyTorch or TensorFlow, so the install is small. The trade-off is a smaller choice of models.

## Known weak spots

- One thread. A slow detector slows the whole video.
- No tracking between frames, so counts are per frame, not unique people.
- Alert cooldown uses wall-clock time, not video time.
