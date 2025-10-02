#!/bin/bash
set -e
module load apptainer

# --- Configuration ---
CONTAINER_IMAGE="apptainer/miniscidom_image.sif"
CONDA_ENV_FILE="environment.yaml"
ZROK_DIR="/opt/zrok"
STREAMLIT_APP_PATH="run_ui.py"
PORT=8501
ZROK_ENV_FILE="zrok.env"

# --- Pre-run Check ---
if [ ! -d "$CONTAINER_IMAGE" ]; then
    echo "Error: Container '$CONTAINER_IMAGE' not found. Please run ./setup.sh first."
    # exit 1
fi
if [ ! -f "$CONDA_ENV_FILE" ]; then
    echo "Error: '$CONDA_ENV_FILE' not found."
    # exit 1
fi

if [ ! -f "$ZROK_ENV_FILE" ]; then
    echo "Error: zrok token file not found at '$ZROK_ENV_FILE'."
    echo "Please create it with your token: ZROK_TOKEN=\"your-token\""
    exit 1
fi
source "$ZROK_ENV_FILE"
if [ -z "$ZROK_TOKEN" ]; then
    echo "Error: ZROK_TOKEN is not set in '$ZROK_ENV_FILE'."
    exit 1
fi

CONDA_ENV_NAME=$(grep "name:" "$CONDA_ENV_FILE" | cut -d':' -f2 | xargs)

echo "--- Launching Application in Apptainer Container ---"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# SCRIPT_DIR="/home/dahiya61/codes/miniSCIDOM/miniscidom/"
echo "Script directory: $SCRIPT_DIR"

# Use the script directory instead of current working directory
env ZROK_TOKEN="$ZROK_TOKEN" apptainer exec \
    --writable \
    --bind "$SCRIPT_DIR/../../:/home" \
    --pwd  "/home/Software/miniscidom_new/" \
    "$CONTAINER_IMAGE" \
    /bin/bash -c '
set -e

echo "--- Inside Container ---"

# --- Step 1: Activate Environment ---
echo "Activating Conda environment: '"'"$CONDA_ENV_NAME"'"'..."
source /opt/conda/etc/profile.d/conda.sh
conda activate "'"$CONDA_ENV_NAME"'"

# --- Step 2: Check and Install Dependencies ---
echo "Syncing environment with '"'"$CONDA_ENV_FILE"'"'..."
conda env update --name "'"$CONDA_ENV_NAME"'" --file "'"$CONDA_ENV_FILE"'" --prune

# --- Step 3: Run Streamlit and zrok ---
echo "Starting Streamlit app in the background..."
streamlit run "'"$STREAMLIT_APP_PATH"'" --server.port "'"$PORT"'" --server.headless=true &
STREAMLIT_PID=$!

sleep 5

# Function to cleanup processes
cleanup() {
    echo "Shutting down services..."
    kill $STREAMLIT_PID 2>/dev/null || true
    zrok disable 2>/dev/null || true
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "Starting zrok public share..."
# Export PATH for current session (not just add to bashrc)
export PATH=$PATH:'"$ZROK_DIR"'

zrok enable $ZROK_TOKEN
echo "zrok enabled successfully."
zrok share public http://localhost:"'"$PORT"'"

echo
echo "zrok has been terminated. Performing cleanup..."
cleanup
'
