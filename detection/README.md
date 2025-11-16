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
Pick the entrypoint that matches your workflow:

```bash
# Live/demo pipeline with webcam or RTSP
python -m detection.processing.demo

# Offline evaluation against recorded videos
python -m detection.processing.video_test
```

Common environment variables:
- `MODEL_NAME`: Model filename (default: "yolo11.pt")
- `MODEL_URL`: URL to download the model from if not found locally
- `TEST_ENV`: Set to "true" to run in test mode (used by custom processors)

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
├── dto/                   # Unified detection dataclasses
├── model/                 # Detection service abstractions + implementations
│   ├── detection_service.py
│   ├── yolo/
│   ├── rf_detr/
│   └── cloud_model/
├── processing/            # Processor base class, adapters, utilities
│   ├── processors/
│   ├── adapters/
│   └── backoff_listener.py
├── tracking/              # TrackingDetectionService (ByteTrack + scoring)
├── main.py                # Sample wiring of local/cloud/tracking stack
└── requirements.txt
```

---

## 🧱 Data Contracts (`detection/dto`)

All detectors—local or remote—return `DetectionResult` objects composed of `Detection` entries defined in `detection/dto/detection_types.py`. Each detection carries:

- `class_id: Optional[int]` – numeric ID matched against the local model's class map
- `class_name: str` – lowercase label used when reconciling cloud and local outputs
- `confidence: float` – 0–1 confidence score from the model
- `bbox: List[float]` – `[x1, y1, x2, y2]` coordinates in pixels

By forcing every `DetectionService` subclass to emit these dataclasses, the rest of the pipeline (processors, trackers, visualization) can stay model-agnostic.

### Implementing a New Detection Model

1. **Subclass `DetectionService` (`detection/model/detection_service.py`)**
   - Implement `load_model()` to hydrate your weights and return the runtime model object.
   - Implement `detect(frame)` to run inference and return a `DetectionResult` populated with DTOs above.
   - Override `get_classes()` to return a `{class_name: id}` map. Processors rely on this to align remote detections to the local taxonomy. A missing or incomplete map will cause remote detections to be dropped because IDs cannot be reconciled.

2. **Optional: expose your detector through the cloud adapter**
   - If the model is remote-only, create a RabbitMQ consumer (see `rabbitMQ/cloud_consumer`) that loads your weights, runs inference, and responds with serialized DTOs (`{"detections": [...]}`) so the `CloudModelAdapter` can parse them.

---

## ⚙️ Processors (`detection/processing`)

Processors orchestrate the local model, optional cloud fallback, and tracking/scoring.

### Base Processor (`processors/processor.py`)

- Owns
  - `local_detection_service`: always available, guarantees `get_classes()` and `detect()`.
  - `cloud_detection_service`: typically a `CloudModelAdapter` backed by `CloudModelProducer`.
  - `tracking_service`: `TrackingDetectionService` for ByteTrack + suspicion scoring.
- Wraps cloud calls with a `pybreaker.CircuitBreaker` to degrade gracefully:
  - `fail_max=3`, `reset_timeout=5s` by default.
  - On each failure, `ExponentialBackoffListener` increases the reset timeout exponentially (base 5s → doubled per open up to 120s). Once the breaker closes, timeout resets to 5s.
- `_apply_processing(frame_bytes, resized_frame)` flow:
  1. Try cloud detection first through the circuit breaker.
  2. Map each remote detection's `class_name` to a `class_id` using the local class map returned by `get_classes()`.
  3. If mapping fails for an item, it is dropped—hence the need for 1:1 class definitions between local and cloud models.
  4. On breaker open, timeout, or general exception, fall back to the local detector.
  5. Forward the unified detections to the tracking service for suspicion scoring + track IDs.

### Backoff Listener (`processing/backoff_listener.py`)

Attaches to the breaker to implement exponential backoff:

- When the breaker transitions to `OPEN`, multiply `reset_timeout` by `factor` (default 2.0) but cap at `max_timeout`.
- When it returns to `CLOSED`, reset to `base_timeout`.
- This prevents hammering an unavailable cloud model while still allowing recovery once healthy.

### Provided Processor Implementations

1. **`DemoProcessor`** (`processors/demo_processor.py`)
   - Streams webcam frames, overlays bounding boxes + track IDs, and displays current FPS and suspicion score in real time.
   - Use it to manually validate that the local + cloud models and tracking stack are working end-to-end. Run `python detection/processing/processors/demo_processor.py` after wiring services similar to `detection/processing/main.py`.

2. **`VideoTestProcessor`** (`processors/test_processor.py`)
   - Offline evaluator for one or many video files.
   - Collects per-frame suspicion scores, class timelines, and bbox area ratios.
   - Generates three matplotlib charts: class appearance timelines, suspicion score over time, and area ratio vs. score—useful for regression testing model or tracker tweaks.

3. **Custom Processors**
   - Derive from `Processor` and implement `start_video_processing` with your own IO loop (e.g., RTSP pull, Kafka consumer, recorded dataset).
   - Call `_apply_processing(frame_bytes, resized_frame)` to reuse the cloud/local orchestration and tracking logic.

---

## ☁️ Cloud Model Integration (`rabbitMQ/cloud_consumer` + `CloudModelAdapter`)

### Producer Side (client)

- `CloudModelProducer` wraps RabbitMQ RPC semantics:
  1. Publishes JPEG-encoded frame bytes to `<model-name>-suspicion-task`.
  2. Listens on a private callback queue for the correlated response.
  3. Reconnects automatically when RabbitMQ drops and surfaces timeouts.
- `CloudModelAdapter` wraps the producer, sending frames and parsing JSON responses into DTOs.

### Consumer Side (cloud)

- `rabbitMQ/cloud_consumer/run_cloud_consumer.py` is the template for cloud workers.
- Responsibilities:
  - Subscribe to the same queue name the producer published to.
  - Deserialize the incoming frame, run the remote model, and serialize detections as JSON matching the DTO schema.
  - Ensure the `class_name` values align with those returned by the local model's `get_classes()` so ID reconciliation works.

### Why `get_classes()` Matters

- The local detector is the source of truth for class IDs.
- When the cloud model returns detections, the processor translates `class_name → class_id` using the local map.
- If the remote model emits a name missing from the map, that detection is ignored (no ID = no tracker alignment).
- Always implement `get_classes()` in your local model subclass and keep the cloud worker's label set in sync.

---

## 🔁 Tracking & Suspicion Scoring (`detection/tracking/tracking_service.py`)

`TrackingDetectionService` wraps ByteTrack to maintain `tracker_id`s across frames and computes a suspicion score:

1. Convert detection DTOs into `supervision.Detections` and update ByteTrack.
2. For each tracked instance:
   - Track first/last timestamps for persistence.
   - Compute `area_ratio` (bbox area ÷ frame area) as a %.
   - Apply class-specific weighting (`class_k`) that accelerates scoring for high-risk classes like `person` or `truck`.
   - Feed `area_ratio` and `duration` into logistic (sigmoid) curves to produce bounded subtotals (max 60 + 40 = 100).
3. Aggregate scores via a softmax-weighted average to emphasize larger scores but cap at `max_score` (100).
4. Return `(final_score, tracked_detections)` to the processor so downstream UIs/analytics can use both track metadata and the global threat score.

---

## 🔌 Putting It All Together

`detection/processing/main.py` shows a simple wiring:

1. Instantiate a local detector (YOLO).
2. Instantiate a `CloudModelProducer` (RF-DETR in RabbitMQ) and wrap it with `CloudModelAdapter`.
3. Build `TrackingDetectionService`.
4. Pass these into a processor implementation (e.g., Demo or Test) and call `start_video_processing()`.

This structure makes it easy to swap local models, add new cloud consumers, or build custom processors without rewriting the orchestration logic.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.