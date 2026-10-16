# Usage guide

## Settings

All settings live in `config.yaml` (copy it from `config.example.yaml`). Unknown keys and bad values are rejected with a clear message, so typos are caught early.

| Setting | Meaning |
|---------|---------|
| `source` | `0` for webcam, a file path, or an RTSP URL |
| `detector` | `yolo` (accurate, needs `scripts/download_models.py`) or `hog` (no download, weak) |
| `yolo_input_size` | YOLO input size. Bigger sees smaller people, slower. Multiple of 32 |
| `model_dir` | Folder with the YOLO files |
| `min_confidence` | Ignore weaker detections. Leave unset for a good default |
| `hog_max_height_fraction` | HOG only: drop boxes taller than this share of the frame |
| `frame_width` | Frames are resized to this width. Smaller is faster |
| `process_every_n_frames` | Run detection on every N-th frame |
| `nms_threshold` | Overlap allowed before boxes are merged (0 to 1) |
| `medium_threshold`, `high_threshold` | People counts for MEDIUM and HIGH. Medium must be lower |
| `alert_cooldown_seconds` | Minimum time between two alerts |
| `grid_rows`, `grid_cols` | Size of the per-area count grid |
| `roi` | `[left, top, right, bottom]` as 0 to 1 fractions. Only people inside are counted |
| `show_window` | Show the live video window |
| `output_video` | Path to save the annotated video, or `null` |
| `log_csv` | Path for the CSV log, or `null` |

## Tuning tips

- Missing people: raise `yolo_input_size` (608 to 800) or `frame_width`.
- False boxes: raise `min_confidence`.
- Video lags: raise `process_every_n_frames`, lower `yolo_input_size`, or lower `frame_width`.
- Double boxes on one person: lower `nms_threshold`.
- Only one part of the scene matters (a door, a platform): set `roi`.
- Choose thresholds from your own scene. Run once, read the summary, then set `medium_threshold` and `high_threshold` above the usual average.

## CSV log

Columns: `timestamp`, `frame`, `count`, `level`. One row per checked frame.

## RTSP cameras

Put the stream URL in `source`. Camera URLs often contain a password. Keep them in `config.yaml`, which is already in `.gitignore`. Never put a real URL in `config.example.yaml`.

## Using a different detector

Write a class with a `detect(frame)` method that returns a list of `(x, y, w, h)` boxes, then pass it to `crowd_detection.pipeline.run(cfg, detector=MyDetector())`.
