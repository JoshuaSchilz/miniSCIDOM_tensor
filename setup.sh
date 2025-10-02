#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

module load apptainer
# --- Configuration ---
CONTAINER_IMAGE="apptainer/miniscidom_image.sif"
DOCKER_IMAGE="continuumio/miniconda3"
CONDA_ENV_FILE="environment.yaml"
ZROK_DIR="/opt/zrok"

echo "--- Starting Environment Setup ---"

if [ ! -f "$CONDA_ENV_FILE" ]; then
    echo "Error: Conda environment file not found at '$CONDA_ENV_FILE'."
    exit 1
fi

# --- Step 1: Build the Apptainer Container ---
if [ ! -d "$CONTAINER_IMAGE" ]; then
    echo "Container sandbox '$CONTAINER_IMAGE' not found. Building from '$DOCKER_IMAGE'..."
    apptainer build --sandbox "$CONTAINER_IMAGE" "docker://$DOCKER_IMAGE"
    echo "Container built successfully."
else
    echo "Container sandbox '$CONTAINER_IMAGE' already exists. Skipping build."
fi

# --- Step 2: Set up software INSIDE the container ---
echo "Configuring software inside the container..."
apptainer exec \
    --writable \
    --no-home \
    --bind "$(pwd)/$CONDA_ENV_FILE:/tmp/environment.yaml:ro" \
    --pwd  "/home" \
    "$CONTAINER_IMAGE" /bin/bash -c '
set -e

mkdir -p ~
touch ~/.bashrc

# --- Step 2a: Install zrok ---
if [ ! -f "'"$ZROK_DIR"'/zrok" ]; then
    echo "zrok not found inside the container. Installing..."
    mkdir -p "'"$ZROK_DIR"'"
    wget -O /tmp/zrok.tar.gz "https://github.com/openziti/zrok/releases/download/v1.0.8/zrok_1.0.8_linux_amd64.tar.gz"
    tar -xzf /tmp/zrok.tar.gz -C "'"$ZROK_DIR"'"
    rm /tmp/zrok.tar.gz
    echo "export PATH=\$PATH:'"$ZROK_DIR"'" >> ~/.bashrc
    echo "zrok installed."
else
    echo "zrok is already installed in the container. Skipping."
fi

# Activate the path for the current session
export PATH=$PATH:'"$ZROK_DIR"'/

# --- Step 2b: Create Conda Environment ---
source /opt/conda/etc/profile.d/conda.sh
CONDA_ENV_NAME=$(grep "name:" /tmp/environment.yaml | cut -d':' -f2 | xargs)
if ! conda env list | grep -q "$CONDA_ENV_NAME"; then
    echo "Conda environment '$CONDA_ENV_NAME' not found. Creating from file..."
    conda env create -f /tmp/environment.yaml
    echo "Conda environment created successfully."
else
    echo "Conda environment '$CONDA_ENV_NAME' already exists. Skipping creation."
    echo "To update it, use the run_app.sh script."
fi
'

echo "--- Environment Setup Complete ---"
echo "Setup is fully automated. You can now use './run_app.sh' to start your application."