# Use Python base image
FROM python:3.10-slim

# Install system dependencies required by livekit and aiortc
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    libopus-dev \
    libvpx-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Copy the entire project
COPY . .

# Install the package
RUN pip install -e .

# Run the server
CMD ["python", "-m", "mcp_remote_macos_use.server"] 