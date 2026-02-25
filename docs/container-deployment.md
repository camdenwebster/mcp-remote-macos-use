# Container Deployment

Guide for deploying the MCP Remote macOS Use server in Docker or Podman containers.

## Building the Container

### Docker
```bash
docker build -t mcp-remote-macos-use .
```

### Podman
```bash
podman build -t mcp-remote-macos-use .
```

### Multi-Platform Build (Docker)
```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourusername/mcp-remote-macos-use:latest --push .
```

## Running the Container

### Basic Docker Run
```bash
docker run -i \
  -e MACOS_HOST=192.168.1.100 \
  -e MACOS_USERNAME=admin \
  -e MACOS_PASSWORD=password \
  --rm \
  mcp-remote-macos-use:latest
```

### Basic Podman Run
```bash
podman run -i \
  -e MACOS_HOST=192.168.1.100 \
  -e MACOS_USERNAME=admin \
  -e MACOS_PASSWORD=password \
  --rm \
  mcp-remote-macos-use:latest
```

### With SSH Tunnel (Key-Based)
```bash
docker run -i \
  -e MACOS_HOST=macos-vm.example.com \
  -e MACOS_USERNAME=admin \
  -e MACOS_PASSWORD=shared_password \
  -e USE_SSH_TUNNEL=true \
  -e MACOS_SSH_KEY_PATH=/root/.ssh/id_rsa \
  -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:ro \
  --rm \
  mcp-remote-macos-use:latest
```

### With SSH Tunnel (Password-Based)
```bash
docker run -i \
  -e MACOS_HOST=macos-vm.example.com \
  -e MACOS_USERNAME=admin \
  -e MACOS_PASSWORD=shared_password \
  -e USE_SSH_TUNNEL=true \
  --rm \
  mcp-remote-macos-use:latest
```

## Claude Desktop Configuration

### Direct VNC
```json
{
  "mcpServers": {
    "macos-test-vm": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e", "MACOS_HOST=192.168.1.100",
        "-e", "MACOS_VNC_PORT=5900",
        "-e", "MACOS_USERNAME=testuser",
        "-e", "MACOS_PASSWORD=your_vnc_password",
        "-e", "VNC_ENCRYPTION=prefer_on",
        "--rm",
        "buryhuang/mcp-remote-macos-use:latest"
      ]
    }
  }
}
```

### SSH Tunnel
```json
{
  "mcpServers": {
    "macos-test-vm-ssh": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e", "MACOS_HOST=vm-host.example.com",
        "-e", "MACOS_USERNAME=testuser",
        "-e", "MACOS_PASSWORD=shared_password",
        "-e", "USE_SSH_TUNNEL=true",
        "-e", "MACOS_SSH_PORT=22",
        "-v", "/Users/you/.ssh/id_rsa:/root/.ssh/id_rsa:ro",
        "-e", "MACOS_SSH_KEY_PATH=/root/.ssh/id_rsa",
        "--rm",
        "buryhuang/mcp-remote-macos-use:latest"
      ]
    }
  }
}
```

### Tart VM Integration (Recommended)
```json
{
  "mcpServers": {
    "macos-tart-vm": {
      "command": "/path/to/mcp-remote-macos-use/mcp-macos-use.sh",
      "env": {
        "TART_VM_NAME": "your-vm-name",
        "MACOS_USERNAME": "admin",
        "MACOS_PASSWORD": "admin",
        "CONTAINER_RUNTIME": "podman"
      }
    }
  }
}
```

## Tart VM Wrapper Script

The [mcp-macos-use.sh](../mcp-macos-use.sh) script provides automatic Tart VM integration.

### First-Run Automatic Setup

On first run, the script automatically:
1. Installs Podman via Homebrew (if not present)
2. Initializes Podman machine (4 CPUs, 4GB RAM)
3. Starts Podman machine
4. Builds `mcp-remote-macos-use:latest` image

### Script Environment Variables

All standard environment variables plus:
- `TART_VM_NAME`: Tart VM name (default: `26-edit_1024x768`)
- `TART_TIMEOUT`: Seconds to wait for VM boot (default: `30`)
- `CONTAINER_RUNTIME`: `podman` or `docker` (default: `podman`)
- `CONTAINER_IMAGE`: Image name (default: `mcp-remote-macos-use:latest`)

### Manual Script Execution
```bash
chmod +x mcp-macos-use.sh
./mcp-macos-use.sh
```

### Script Workflow
1. Setup Podman (if needed)
2. Build image (if not found)
3. Wait for Tart VM to boot (detect via `tart ip`)
4. Launch container with detected VM IP
5. Pass through SSH tunnel variables if configured

## Container Implementation Details

### Dockerfile Structure
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "mcp_remote_macos_use.server"]
```

### What's Installed
- Python 3.10 base image
- All dependencies from pyproject.toml
- Project code in `/app`
- Entry point runs the MCP server

### Container Requirements
- Interactive mode (`-i` flag) for stdio communication
- Environment variables passed at runtime
- Volume mount for SSH keys (if using key-based auth)
- Removal on exit (`--rm` flag recommended)

## Security Best Practices

1. **Never build credentials into images** - Always pass via environment variables
2. **Mount SSH keys read-only** - Use `:ro` flag
3. **Use SSH tunnels** - Set `USE_SSH_TUNNEL=true` for encrypted VNC traffic
4. **Prefer key-based SSH** - More secure than password-based (set `MACOS_SSH_KEY_PATH`)
5. **Use VNC encryption** - Set `VNC_ENCRYPTION=prefer_on` or `required`
6. **Rotate credentials** - Update passwords periodically
7. **Network isolation** - Run test VMs on isolated network segments

## Troubleshooting

### Container won't start
- Check required env vars: `MACOS_HOST`, `MACOS_PASSWORD`
- Verify container runtime is installed and running
- Check logs: `docker logs <container_id>`

### Podman machine issues
- Verify machine status: `podman machine list`
- Start manually: `podman machine start`
- Recreate if needed: `podman machine rm`, then `podman machine init`

### SSH tunnel connection fails
- Verify SSH credentials
- Test SSH manually: `ssh user@host`
- Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- Verify SSH server is running on remote host

### VNC connection fails
- Verify Screen Sharing is enabled on remote macOS
- Test VNC manually: macOS Screen Sharing app
- Check firewall rules on remote host
- Verify VNC port (default: 5900)
