# Evaluation

## What was measured

Data: `vtest.avi` (OpenCV samples), 768x576, 795 frames, about 5 to 8 pedestrians in view, small in the frame.
Settings: first 300 frames, every 3rd checked, frame width 640, YOLO input 608, single-core cloud CPU.

| Detector | Mean people per checked frame | Median | Max | Detector time per frame |
|----------|------------------------------|--------|-----|------------------------|
| HOG | 0.97 | 1 | 3 | 140 ms |
| YOLOv4-tiny | 5.97 | 6 | 8 | 236 ms |

Full-clip run with `examples/demo.yaml`: 265 checked frames, average 5.62 people, peak 8, about 11.6 frames/sec.

## What was NOT measured

- **No ground truth.** The clip has no labeled people count, so there is no precision, recall, or counting error (MAE).
- Frames were also compared by eye on a small sample. That supports "HOG misses most people here" but is not a statistic.
- Only one clip, one camera angle, one lighting condition.

## How to add a real accuracy number

1. Pick a labeled dataset with people counts or boxes, for example MOT17/MOT20 or CrowdHuman.
2. Run the detector on each frame and compare the predicted count with the true count.
3. Report mean absolute error (MAE) of the count, and precision/recall if you have boxes.
4. Report results per scene type (sparse, medium, dense). Expect worse results as density rises.
5. Add the table here and update the README.
