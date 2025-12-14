# Backend

FastAPI-based backend server for the GuardCar vehicle monitoring system.

## Prerequisites
- Python 3.8+
- RabbitMQ server
- MinIO server (or compatible S3 storage)

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the backend directory:

```env
# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_SECURE=False

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# App
DEBUG=True
SECRET_KEY=your-secret-key-here
```

## Running

Start the development server:
```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

## API Docs
- Interactive: `http://localhost:8000/docs`
- Alternative: `http://localhost:8000/redoc`

## Testing
Run tests with:
```bash
pytest app/tests/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Secret key for encryption | - |
| `MINIO_ENDPOINT` | MinIO server endpoint | - |
| `MINIO_ACCESS_KEY` | MinIO access key | - |
| `MINIO_SECRET_KEY` | MinIO secret key | - |
| `RABBITMQ_URL` | RabbitMQ connection URL | - |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Specify your license here]