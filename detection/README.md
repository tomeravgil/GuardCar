# Object Detection and Tracking Service

This project provides a flexible framework for object detection and tracking, supporting multiple models including [YOLO](https://docs.ultralytics.com/) and [RF-DETR](https://github.com/facebookresearch/rf-detr). It includes a custom scoring mechanism that evaluates detections based on multiple factors to determine their importance.

## 📌 Features

- **Multiple Model Support**:
  - YOLOv8 models for fast and accurate object detection
  - RF-DETR for advanced detection with transformer-based architecture
- **Stream Processing**:
  - Handles video files, RTSP streams, and webcam inputs
  - Configurable input sources via URL/path files
- **Advanced Object Tracking**:
  - Implements [ByteTrack](https://github.com/ifzhang/ByteTrack) for robust multi-object tracking
  - Tracks objects across frames with configurable parameters
- **Intelligent Scoring System**:
  - **Bounding Box Analysis**: Evaluates object size relative to frame
  - **Temporal Consistency**: Rewards persistent object tracks
  - **Class-based Weighting**: Adjusts scores based on object class importance
  - **Normalized Output**: Combines factors into a unified score (0-1 range)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PyTorch
- CUDA (for GPU acceleration)
- Other dependencies listed in `requirements.txt`

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download required model weights (YOLO weights are downloaded automatically if not present)

### Usage
```bash
python main.py
```

Environment variables:
- `MODEL_NAME`: Model filename (default: "yolo11.pt")
- `MODEL_URL`: URL to download the model from if not found locally
- `TEST_ENV`: Set to "true" to run in test mode

## ⚙️ How the Scoring Works

Each detection is evaluated using multiple factors to determine its importance:

1. **Bounding Box Analysis**
   - Measures the relative size of the object in the frame
   - Formula: 
     \[
     \text{box\_score} = \frac{\text{bbox area}}{\text{image area}}
     \]

2. **Temporal Consistency**
   - Rewards objects that persist in the frame over time
   - Tracks duration since first detection
   - Configurable time-based scoring

3. **Class-based Weighting**
   - Different weights for different object classes
   - Example configuration:
     ```python
     self.class_k = {
         0: 1.6,   # person → higher importance
         1: 0.6,   # bicycle → lower importance
         2: 1.0,   # car → standard importance
         3: 1.0,   # motorcycle
         5: 1.4,   # bus → higher importance
         7: 1.4    # truck → higher importance
     }
     ```

4. **Score Normalization**
   - Combines all factors into a unified score
   - Normalized to a 0-1 range for consistency
   - Configurable weighting between different factors

## 🏗️ Project Structure

```
detection/
├── model/                  # Model implementations
│   ├── yolo/              # YOLO model implementation
│   └── rf_detr/           # RF-DETR model implementation
├── processing/            # Data processing utilities
├── tracking/              # Object tracking implementation
├── main.py                # Main entry point
└── requirements.txt       # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.