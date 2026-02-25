#!/bin/bash
set -e

# Ensure Homebrew-installed tools (like tart) are on PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# MCP Remote macOS Use - Tart VM Integration
# Automatically detects Tart VM IP and starts the MCP server container

# Configuration (override with environment variables)
VM_NAME="${TART_VM_NAME:-26-edit_1024x768}"
MACOS_VNC_PORT="${MACOS_VNC_PORT:-5900}"
MACOS_USERNAME="${MACOS_USERNAME:-admin}"
MACOS_PASSWORD="${MACOS_PASSWORD:-admin}"
VNC_ENCRYPTION="${VNC_ENCRYPTION:-prefer_on}"
CONTAINER_RUNTIME="${CONTAINER_RUNTIME:-podman}"
CONTAINER_IMAGE="${CONTAINER_IMAGE:-mcp-remote-macos-use:latest}"

# SSH Tunnel Configuration (optional)
USE_SSH_TUNNEL="${USE_SSH_TUNNEL:-false}"
MACOS_SSH_PORT="${MACOS_SSH_PORT:-22}"
MACOS_SSH_KEY_PATH="${MACOS_SSH_KEY_PATH:-}"

# Output directory for screenshots and reports (mounted into container at /mcp-output)
MCP_OUTPUT_DIR="${MCP_OUTPUT_DIR:-$PWD/mcp-output}"

# Timeout configuration
TIMEOUT="${TART_TIMEOUT:-20}"
INTERVAL=2
ELAPSED=0

# Get script directory for building image
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup Functions
setup_podman() {
    echo "Setting up Podman..." >&2

    # Check if podman is installed
    if ! command -v podman &> /dev/null; then
        echo "Podman not found. Installing via Homebrew..." >&2
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew is not installed. Please install Homebrew first: https://brew.sh" >&2
            exit 1
        fi
        brew install podman
    else
        echo "Podman is already installed." >&2
    fi

    # Check if podman machine is initialized
    if ! podman machine list 2>/dev/null | grep -q "podman-machine-default"; then
        echo "Initializing Podman machine..." >&2
        podman machine init --cpus 4 --memory 4096
    else
        echo "Podman machine already initialized." >&2
    fi

    # Check if podman machine is running
    if ! podman machine list 2>/dev/null | grep "podman-machine-default" | grep -iq "running"; then
        echo "Starting Podman machine..." >&2
        podman machine start
        # Give it a moment to fully start
        sleep 3
    else
        echo "Podman machine is already running." >&2
    fi

    # Verify podman is working
    if ! podman ps &> /dev/null; then
        echo "Error: Podman is not responding. Try running 'podman machine start' manually." >&2
        exit 1
    fi

    echo "Podman setup complete." >&2
}

build_image() {
    echo "Checking for container image..." >&2

    # Check if image exists
    if podman images | grep -q "mcp-remote-macos-use"; then
        echo "Container image 'mcp-remote-macos-use:latest' already exists." >&2
        return 0
    fi

    echo "Building container image 'mcp-remote-macos-use:latest'..." >&2
    echo "This may take several minutes on first run..." >&2

    if [[ ! -f "$SCRIPT_DIR/Dockerfile" ]]; then
        echo "Error: Dockerfile not found in $SCRIPT_DIR" >&2
        exit 1
    fi

    cd "$SCRIPT_DIR"
    podman build -t mcp-remote-macos-use:latest .

    echo "Image build complete." >&2
}

# Only run setup if using podman
if [[ "$CONTAINER_RUNTIME" == "podman" ]]; then
    setup_podman
    build_image
fi

echo "Waiting for Tart VM '$VM_NAME' to boot..." >&2

# Wait for VM to be ready and get IP
while true; do
    VM_IP=$(tart ip "$VM_NAME" 2>/dev/null) || true

    if [[ -n "$VM_IP" ]]; then
        echo "VM ready at $VM_IP" >&2
        break
    fi

    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        echo "Error: timed out after ${TIMEOUT}s waiting for '$VM_NAME'" >&2
        exit 1
    fi

    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
done

# Ensure output directory exists on host
mkdir -p "$MCP_OUTPUT_DIR"

# Build container command with required parameters
CONTAINER_ARGS=(
    "--rm"
    "-i"
    "-e" "MACOS_HOST=$VM_IP"
    "-e" "MACOS_VNC_PORT=$MACOS_VNC_PORT"
    "-e" "MACOS_USERNAME=$MACOS_USERNAME"
    "-e" "MACOS_PASSWORD=$MACOS_PASSWORD"
    "-e" "VNC_ENCRYPTION=$VNC_ENCRYPTION"
    "-v" "$MCP_OUTPUT_DIR:/mcp-output"
)

# Add SSH tunnel parameters if configured
if [[ "$USE_SSH_TUNNEL" == "true" ]]; then
    CONTAINER_ARGS+=("-e" "USE_SSH_TUNNEL=true")
    CONTAINER_ARGS+=("-e" "MACOS_SSH_PORT=$MACOS_SSH_PORT")

    if [[ -n "$MACOS_SSH_KEY_PATH" ]]; then
        CONTAINER_ARGS+=("-e" "MACOS_SSH_KEY_PATH=/root/.ssh/id_rsa")
        CONTAINER_ARGS+=("-v" "$MACOS_SSH_KEY_PATH:/root/.ssh/id_rsa:ro")
    fi
fi

# Execute container
exec "$CONTAINER_RUNTIME" run "${CONTAINER_ARGS[@]}" "$CONTAINER_IMAGE"
