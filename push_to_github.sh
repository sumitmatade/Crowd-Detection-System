#!/usr/bin/env bash
# Usage: ./push_to_github.sh <your-github-username>
# Before running: create an EMPTY repo named "crowd-detection-system" on github.com
# (no README, no .gitignore, no license - this folder already has them).
set -e
USER_NAME="${1:?Give your GitHub username: ./push_to_github.sh <username>}"
sed -i.bak "s/YOUR-USERNAME/${USER_NAME}/g" README.md CONTRIBUTING.md && rm -f README.md.bak CONTRIBUTING.md.bak
git init -b main
git add .
git commit -m "Release v1.1.0: crowd detection with YOLO and HOG detectors"
git remote add origin "https://github.com/${USER_NAME}/crowd-detection-system.git"
git push -u origin main
git tag v1.1.0 && git push origin v1.1.0
