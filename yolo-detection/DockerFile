FROM python:3.13.7

WORKDIR /app

# Set up build args and env defaults
ARG TEST_ENV=false
ENV MODEL_NAME="yolo11.pt"
ENV MODEL_URL="https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"

# Copy base files
COPY main.py .
COPY detection.py .
COPY requirements.txt .

# Conditionally copy test files if TEST_ENV is true
RUN if [ "$TEST_ENV" = "true" ]; then \
      echo "Including test files..."; \
      mkdir -p /app/tests && \
      echo "test data" > /app/tests/test_files.txt; \
    else \
      echo "Skipping test files."; \
    fi

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
 && rm -rf /var/lib/apt/lists/*


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
