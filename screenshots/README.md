# Screenshots

`demo.png`, `high-alert.png` and `demo.gif` are real output of this project on OpenCV's sample video
(`videos/vtest.avi`), with the settings in `examples/demo.yaml`.

Regenerate them:

```bash
python scripts/download_models.py
python scripts/download_sample.py
python scripts/make_screenshots.py videos/vtest.avi
```

To use your own footage, run the same script with your video path. Only publish footage you have the right to share, and avoid identifiable faces of private people.
