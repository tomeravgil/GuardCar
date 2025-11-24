# 1. Use the 'bookworm' (Debian 12) version of the RPi-OS image.
#    Bookworm natively uses Python 3.11.
FROM ghcr.io/dtcooper/raspberrypi-os:python3.11-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    # This path is still needed for apt-installed packages
    PYTHONPATH=/usr/lib/python3/dist-packages

WORKDIR /app

# 2. Install the 'bookworm' versions of all packages from apt
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
      # System tools
      ca-certificates \
      # Python packages from APT (for stability)
      python3-picamera2 \
      python3-libcamera \
      python3-opencv \
      python3-numpy \
      # Runtime libraries
      libv4l-0 libjpeg62-turbo libatlas-base-dev ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 3. Copy requirements.txt, which must ONLY contain pip-specific packages
COPY requirements.txt .
# We use --break-system-packages because it's required on bookworm
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy only the Python script (certs will be mounted at runtime)
COPY sender.py .

# Create recordings directory
RUN mkdir -p /app/recordings

EXPOSE 8443 8080
# Use python3 to be explicit
CMD ["python3", "sender.py"]