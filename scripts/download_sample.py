"""Download OpenCV's public sample pedestrian video (Apache-2.0) into videos/.

Usage: python scripts/download_sample.py
"""
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/vtest.avi"
DEST = Path("videos/vtest.avi")


def main() -> None:
    DEST.parent.mkdir(exist_ok=True)
    if DEST.exists():
        print(f"{DEST} already exists.")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST} ({DEST.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
