"""Command line entry point."""
from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .config import ConfigError, load_config
from .pipeline import run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crowd-detection",
                                description="Count people in video and flag crowded scenes.")
    p.add_argument("-c", "--config", help="Path to a YAML config file")
    p.add_argument("-s", "--source", help="Override source: webcam index, video file, or RTSP URL")
    p.add_argument("--no-window", action="store_true", help="Run without opening a window")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        cfg = load_config(args.config)
        if args.source is not None:
            cfg.source = int(args.source) if args.source.isdigit() else args.source
        if args.no_window:
            cfg.show_window = False
        cfg.validate()
        stats = run(cfg)
    except (ConfigError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("\n--- Run summary ---")
    print(stats.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
