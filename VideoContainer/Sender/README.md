# Sender

Dual-camera Raspberry Pi video streamer with on-demand recording and MinIO upload.

## Features
- Streams dual camera feed via TLS (port 8443)
- REST API control for recording (port 8080)
- Automatic upload to backend API
- Mock mode for testing without hardware

---

## Quick Start

### ⚠️ Prerequisites (REQUIRED)
1. Generate TLS certificates:
   ```bash
   cd VideoContainer/Sender
   openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
     -keyout key.pem \
     -out cert.pem \
     -subj "/CN=guardcar-sender"
   ```
   **Note:** Certificates are git-ignored and must be generated for each deployment.

2. Configure environment (see [Environment Variables](#environment-variables) below)


### Setup MinIO and Backend API:
The sender requires a running backend API with MinIO storage.
**Start MinIO:**
```bash
cd backend/storage
bash minio.sh
```

### Install Dependencies and Run Backend API:
```bash
cd backend/app
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
MINIO CONSOLE URL: http://localhost:9001

### Test the Control API:
```bash
Invoke-WebRequest -Method POST -Uri http://localhost:8080/start
curl http://localhost:8080/status
Invoke-WebRequest -Method POST -Uri http://localhost:8080/stop
```

### 🍓 Deploy on Raspberry Pi (Docker - Recommended)
```bash
cd VideoContainer/Sender
# Ensure .env and certificates exist (see prerequisites)
docker-compose up -d
```

### 🍓 Deploy on Raspberry Pi (Manual)
```bash
cd VideoContainer/Sender
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install -y python3-opencv python3-numpy python3-picamera2
python sender.py
```

---

## Configuration
### Environment Variables
Create `VideoContainer/Sender/.env`:

```env
# Streaming Configuration
HOST=0.0.0.0
SERVER_PORT=8443
FPS=30
JPEG_QUALITY=90
CERT_FILE=cert.pem
KEY_FILE=key.pem

# Recording Configuration
MINIO_API_URL=http://192.168.1.100:8000  # Backend API endpoint
CAMERA_ID=CAM001
LOCATION=Right Mirror
RECORDING_DIR=/app/recordings # Local storage need to be changed to file location if local
CONTROL_API_PORT=8080
```

Create `backend/app/core/services/minio/.env`
```bash
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=YourAccessKey
MINIO_SECRET_KEY=YourSecretKey
MINIO_BUCKET_NAME=videos
```
---

## Control API Endpoints

### Health Check
```bash
GET http://<pi-ip>:8080/health
```

### Get Recording Status
```bash
GET http://<pi-ip>:8080/status
```

### Start Recording
```bash
POST http://<pi-ip>:8080/start
```

### Stop Recording
```bash
POST http://<pi-ip>:8080/stop
```

## Recording Workflow
1. Call `/start` to begin recording
2. Frames are saved locally to `RECORDING_DIR`
3. Call `/stop` to end recording
4. Video is automatically uploaded to `MINIO_API_URL/api/videos/upload`
5. Local file is deleted after successful upload

## Camera Configuration
- **Camera 0** (left): `/dev/video0`
- **Camera 1** (right): `/dev/video1`
- Combined output: 1280x480 (640x480 per camera, side-by-side)
- Fixed resolution (hardcoded in code)

## Architecture
```
┌──────────────────┐
│  Sender (Pi)     │
│  Port 8443       │──TLS Stream──▶ Receiver/YOLO
│  Port 8080       │──HTTP API────▶ Control
└──────────────────┘
         │
         │ Upload on /stop
         ▼
┌──────────────────┐
│  Backend API     │
│  Port 8000       │
│  /api/videos/    │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  MinIO Storage   │
└──────────────────┘
```

## Troubleshooting

**Camera not detected**
```bash
ls /dev/video*  # Check camera devices
sudo usermod -aG video $USER  # Add user to video group
```

**TLS connection fails**
- Verify `cert.pem` and `key.pem` exist
- Check firewall allows port 8443

**Upload fails**
- Verify `MINIO_API_URL` is correct
- Check backend is running and accessible
- Review backend logs for errors

**Mock mode fails to encode**
- Ensure OpenCV is installed: `pip install opencv-python`