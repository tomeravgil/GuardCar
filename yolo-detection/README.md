# YOLO Tracking Detection Service with Weighted Normalization Scoring

This project extends the [Ultralytics YOLO](https://docs.ultralytics.com/) object detection framework by adding a **custom scoring mechanism**.  
It uses **bounding box area**, **tracking time**, and **class-based weights** to produce a **normalized score between 0 and 1**, representing the "importance" of each detection.

---

## 📌 Features

- **YOLO Model Loading** – load YOLOv8 models from a given path.
- **Stream Input** – read input sources (video files, RTSP, or webcam streams) from a file containing URLs/paths.
- **Object Tracking** – tracks objects across frames using [ByteTrack](https://github.com/ifzhang/ByteTrack).
- **Weighted Normalization Score**:
  - **Box Score** → relative bounding box area (object size in frame).
  - **Time Score** → how long an object has been tracked.
  - **Class Score** → class-specific weight adjusted by detection confidence.
- **Final Score** → all three normalized and combined into a single score between **0 and 1**.

---

## ⚙️ How the Scoring Works

Each detection is evaluated using **three factors**:

1. **Box Score**  
   - Measures how much space the object occupies relative to the frame.  
   - Formula:  
     \[
     \text{box\_score} = \frac{\text{bbox area}}{\text{image area}}
     \]

2. **Time Score**  
   - Rewards objects that persist longer in the frame.  
   - Computed as elapsed time since the object’s first detection.

3. **Class Score**  
   - Uses predefined weights per class (e.g., person = 0.05, car = 0.04).  
   - Multiplied by detection confidence.  
   - Example:  
     ```python
     self.class_to_score = {
         0: 0.05,  # person
         1: 0.01,  # bicycle
         2: 0.04,  # car
         3: 0.02,  # motorcycle
         5: 0.04,  # bus
         7: 0.04   # truck
     }
     ```

4. **Normalization**  
   - Each score is first **min–max normalized** to the range `[0, 1]`.  
   - Then combined with weights:  
     \[
     \text{final score} = w_1 \cdot \text{box} + w_2 \cdot \text{time} + w_3 \cdot \text{class}
     \]  
   - Default weights:  
     - Box = `1/6` (≈17%)  
     - Time = `0.5` (50%)  
     - Class = `1/3` (≈33%)