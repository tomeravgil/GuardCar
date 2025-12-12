# GuardCar 2.0

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

GuardCar is an advanced vehicle monitoring and security system that provides real-time surveillance and threat detection for vehicles. The system combines computer vision, machine learning, and IoT technologies to create a comprehensive security solution.

## 🚀 Features

- **Real-time Video Streaming**: Stream live video from vehicle-mounted cameras
- **Suspicious Activity Detection**: AI-powered detection of potential security threats
- **Cloud Integration**: Securely store and access footage with MinIO/S3 compatible storage
- **Web Dashboard**: Intuitive interface for monitoring and managing vehicle security
- **Alert System**: Instant notifications for security events
- **Distributed Architecture**: Scalable backend using FastAPI and RabbitMQ

## 🏗️ System Architecture

GuardCar is built with a microservices architecture:

- **Frontend**: React-based web application for monitoring and control
- **Backend**: FastAPI server handling API requests and business logic
- **Video Processing**: Real-time video analysis and threat detection
- **Message Broker**: RabbitMQ for inter-service communication
- **Storage**: MinIO for secure video and data storage

![Architecture](GuardCar%20Architecture.png)

## 🛠️ Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 16+ and npm 8+
- RabbitMQ server
- MinIO server (or compatible S3 storage)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GuardCar.git
   cd GuardCar
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env` and update with your configuration

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MinIO Console: http://localhost:9001

## 📂 Project Structure

```
GuardCar/
├── backend/             # FastAPI backend server
├── frontend/            # React frontend application
├── detection/           # Computer vision and ML models
├── VideoContainer/      # Video streaming components
├── gRPC/                # gRPC service definitions
├── rabbitMQ/            # Message broker configuration
└── config/              # Configuration files
```

## 🔧 Development

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend/webapplication
npm install
npm start
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For any questions or feedback, please open an issue on GitHub.