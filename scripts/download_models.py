"""Download the YOLOv4-tiny model files into models/ and check their integrity.

Usage: python scripts/download_models.py
Source: https://github.com/AlexeyAB/darknet (YOLOv4-tiny, COCO-trained). Files are not
redistributed in this repo; check the Darknet license before commercial use.
"""
import hashlib
import urllib.request
from pathlib import Path

FILES = {
    "yolov4-tiny.cfg": (
        "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg",
        None,
    ),
    "yolov4-tiny.weights": (
        "https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights",
        "cf9fbfd0f6d4869b35762f56100f50ed05268084078805f0e7989efe5bb8ca87",
    ),
}
DEST = Path("models")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    DEST.mkdir(exist_ok=True)
    for name, (url, expected) in FILES.items():
        path = DEST / name
        if not path.exists():
            print(f"Downloading {name} ...")
            urllib.request.urlretrieve(url, path)
        if expected:
            actual = sha256(path)
            if actual != expected:
                path.unlink()
                raise SystemExit(
                    f"Checksum mismatch for {name}. Expected {expected}, got {actual}. "
                    "File deleted; try again."
                )
        print(f"OK: {path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
