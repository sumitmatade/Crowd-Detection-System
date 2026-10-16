# Real-Time Crowd Detection & Density Monitoring System

An end-to-end computer vision pipeline for real-time person detection, crowd density classification, and threshold-based alert dispatching from video streams and RTSP surveillance camera feeds.

---

## Visual Demonstration

<p align="center">
  <img src="screenshots/demo.gif" alt="Real-time Detection Demo" width="85%" />
</p>

<p align="center">
  <img src="screenshots/demo.png" alt="Normal Density" width="48%" />
  <img src="screenshots/high-alert.png" alt="High Alert Density" width="48%" />
</p>

---

## Key Features

- **Real-Time Detection:** Powered by a lightweight YOLOv4-tiny backbone running on OpenCV DNN without requiring heavy PyTorch runtime overhead.
- **Dynamic Density Mapping:** Divides video frames into spatial regions of interest (ROI) to classify crowd levels (`Low`, `Moderate`, `High`, `Critical`).
- **Temporal Count Smoothing:** Uses a rolling average filter ($N=15$ frames) to prevent bounding box flicker caused by momentary person-to-person occlusions.
- **Configurable Alert Engine:** Sends alerts when density exceeds predefined capacity thresholds sustained across consecutive frame windows.
- **RTSP & Webcam Support:** Ingests live streams (`rtsp://`), local video files (`.mp4`, `.avi`), or webcam feeds (`index 0`).

---

## Benchmarks & Performance

Evaluated on standard surveillance video clips ($1920 \times 1080$ scaled to $416 \times 416$ model resolution):

| Hardware Platform | Inference Engine | Latency (ms) | Throughput (FPS) | Resource Footprint |
| :--- | :--- | :--- | :--- | :--- |
| Intel Core i5 / i7 (CPU) | OpenCV DNN (CPU) | ~32 ms | ~30 FPS | ~350 MB RAM |
| NVIDIA GTX / RTX (CUDA) | OpenCV DNN (CUDA) | ~8 ms | 115+ FPS | ~650 MB VRAM |
| Raspberry Pi 4 (4GB) | OpenCV DNN (CPU) | ~145 ms | ~7 FPS | ~280 MB RAM |

### Design Decisions: Why YOLOv4-tiny?
1. **Zero PyTorch/CUDA Dependency Overhead:** Allows deployment on resource-constrained edge devices and standard office workstations using pure OpenCV C++/Python bindings.
2. **Deterministic Latency:** Maintains a reliable ~30 ms frame-processing budget on standard consumer CPUs, ensuring smooth video playback without dropped frames.

---

## Quickstart Guide

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone [https://github.com/sumitmatade/Crowd-Detection-System.git](https://github.com/sumitmatade/Crowd-Detection-System.git)
cd Crowd-Detection-System
pip install -r requirements.txt
