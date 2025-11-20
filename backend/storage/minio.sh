#!/bin/bash
#
# A script to launch a persistent MinIO server in Docker
# with pre-configured buckets, health checks, and auto-restart.

# --- Configuration ---
# Change these default credentials for any real use
readonly MINIO_ROOT_USER="minioadmin"
readonly MINIO_ROOT_PASSWORD="minio-secret-password" 

# --- Docker & MinIO Settings ---
readonly CONTAINER_NAME="minio-server"
readonly VOLUME_NAME="minio-data"
readonly API_PORT="9000"
readonly CONSOLE_PORT="9001"
readonly IMAGE_NAME="minio/minio:latest"

# --- Buckets to Create ---
readonly BUCKETS_TO_CREATE=("videos" "thumbnails")

# --- Script Safety ---
# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error.
set -u
# The return value of a pipeline is the status of the last command to exit non-zero.
set -o pipefail

# --- 1. Cleanup Old Container ---
# Stop and remove any existing container with the same name.
echo "Stopping and removing existing '$CONTAINER_NAME' container (if any)..."
docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

# --- 2. Ensure Persistent Volume Exists ---
echo "Ensuring Docker volume '$VOLUME_NAME' exists for persistent storage..."
docker volume create "$VOLUME_NAME" >/dev/null

# --- 3. Start the MinIO Container ---
echo "Starting new MinIO container '$CONTAINER_NAME'..."
docker run -d \
    -p "${API_PORT}:${API_PORT}" \
    -p "${CONSOLE_PORT}:${CONSOLE_PORT}" \
    --name "$CONTAINER_NAME" \
    -v "$VOLUME_NAME:/data" \
    -e "MINIO_ROOT_USER=${MINIO_ROOT_USER}" \
    -e "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}" \
    --restart unless-stopped \
    "$IMAGE_NAME" server /data --console-address ":${CONSOLE_PORT}"

# --- 4. Wait for MinIO to be Ready ---
echo "Waiting for MinIO to be ready (this may take a few seconds)..."
timeout=60
start_time=$(date +%s)

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    if [ $elapsed -ge $timeout ]; then
        echo "Error: MinIO failed to start after ${timeout} seconds."
        echo "--- Container Logs ---"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi

    # Check if MinIO is responding
    if curl -s http://localhost:${API_PORT}/minio/health/live > /dev/null 2>&1; then
        echo " MinIO is up and healthy!"
        break
    fi

    echo -n "."
    sleep 2
done

# --- 5. Configure MinIO Client (mc) ---
echo "Configuring MinIO client..."
docker exec "$CONTAINER_NAME" mc alias set local http://localhost:${API_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# --- 6. Create Buckets ---
echo "Creating buckets..."
for bucket in "${BUCKETS_TO_CREATE[@]}"; do
    if docker exec "$CONTAINER_NAME" mc ls "local/$bucket" >/dev/null 2>&1; then
        echo " - Bucket '$bucket' already exists. Skipping."
    else
        echo " - Creating bucket '$bucket'..."
        docker exec "$CONTAINER_NAME" mc mb "local/$bucket"
        echo " - Successfully created '$bucket'."
    fi
done

# --- 7. Final Summary ---
echo ""
echo "--------------------------------------------------"
echo "✅ MinIO Setup Complete!"
echo ""
echo "Access the MinIO Console at:"
echo "   http://localhost:${CONSOLE_PORT}"
echo ""
echo "Connect via API/SDK at:"
echo "   Endpoint: http://localhost:${API_PORT}"
echo "   Access Key: ${MINIO_ROOT_USER}"
echo "   Secret Key: ${MINIO_ROOT_PASSWORD}"
echo "--------------------------------------------------"