#!/bin/bash
set -e

echo "===================================================="
echo " Updating system"
echo "===================================================="
sudo apt-get update
sudo apt-get upgrade -y

echo "===================================================="
echo " Installing prerequisites"
echo "===================================================="
sudo apt-get install -y \
  ca-certificates curl wget gnupg2 lsb-release software-properties-common

echo "===================================================="
echo " Adding Docker's official GPG key"
echo "===================================================="
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "===================================================="
echo " Adding Docker APT repository"
echo "===================================================="
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "===================================================="
echo " Installing Docker Engine + Docker Compose"
echo "===================================================="
sudo apt-get update
sudo apt-get install -y \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

echo "===================================================="
echo " Adding your user to Docker group (no sudo needed)"
echo "===================================================="
sudo usermod -aG docker $USER

echo "===================================================="
echo " Installing NVIDIA Container Toolkit (Ubuntu 24.04 safe)"
echo "===================================================="

# Step 1 — Add the GPG key from the official NVIDIA docs
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Step 2 — Add the generic DEB repo (works for Ubuntu 22.04+, including 24.04)
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

echo "===================================================="
echo " Installing NVIDIA Container Toolkit"
echo "===================================================="
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

echo "===================================================="
echo " Configuring Docker to use NVIDIA runtime"
echo "===================================================="
sudo nvidia-ctk runtime configure --runtime=docker

echo "===================================================="
echo " Restarting Docker (WSL-safe)"
echo "===================================================="
sudo service docker restart || true

echo "===================================================="
echo " 🎉 INSTALL COMPLETE! 🎉"
echo "===================================================="
echo "Next steps:"
echo " 1. Close this terminal completely"
echo " 2. Run in PowerShell:  wsl --shutdown"
echo " 3. Reopen Ubuntu (to apply Docker permissions)"
echo ""
echo "Then test GPU with:"
echo "  docker run --rm --gpus all nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04 nvidia-smi"

