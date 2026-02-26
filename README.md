# MCP Remote macOS Use - Jamf Testing Fork

**AI-powered E2E and exploratory testing for Mac applications on macOS VMs.**

MCP server enabling Claude to control remote macOS systems via VNC for automated testing. Uses vision-based interaction to test applications exactly as users experience them.

## Use Cases

* **E2E Testing**: Automate complete user workflows across Jamf applications
* **Exploratory Testing**: AI-driven investigation of app behavior and edge cases
* **Regression Testing**: Validate functionality across macOS versions
* **Visual Validation**: Screenshot-based UI verification
* **Cross-Version Testing**: Test against multiple macOS releases simultaneously

## Features

* **No Installation**: Uses native macOS Screen Sharing (VNC)
* **Vision-Based**: AI interprets screenshots to understand app state
* **Natural Language**: Describe test scenarios in plain English
* **SSH Tunneling**: Secure encrypted VNC connections
* **Version Agnostic**: Works with all macOS versions

## Setup

**Prerequisites:**

* macOS VM with Screen Sharing enabled
* [Homebrew](https://brew.sh) installed
* Claude Code/Desktop
* (Optional) [Tart](https://tart.run/) for local macOS VMs

The script automatically handles Podman installation, configuration, and image building on first run.

**Enable Screen Sharing on VMs:**
System Settings → General → Sharing → Enable "Screen Sharing" (default port: 5900)

**Configure Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

See [`example-config.json`](example-config.json) for complete configuration examples.

### Tart VM Integration (Recommended)

For local [Tart VMs](https://tart.run/) (macOS virtualization), use the included script to automatically detect VM IP:

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

**Running Tart VMs with Shared Directories:**

For file transfer between host and VM (e.g., installing packages), launch your Tart VM with shared directory support:

```bash
tart run your-vm-name --net-host --vnc --dir="host-downloads:~/Downloads/"
```

Flags:

* `--net-host`: Uses host networking for easy connectivity
* `--vnc`: Enables VNC access for the MCP server
* `--dir="host-downloads:~/Downloads/"`: Mounts your Downloads folder at `/Volumes/My Shared Files/host-downloads/` in the VM

This allows you to place files in `~/Downloads/` on your host and access them from the VM without needing SCP.

**First-Run Setup:**

The script automatically handles:

1. **Podman Installation**: Installs via Homebrew if not present
2. **Machine Initialization**: Creates Podman machine with 4 CPUs, 4GB RAM
3. **Machine Start**: Ensures Podman machine is running
4. **Image Build**: Builds `mcp-remote-macos-use:latest` if not found

**Script Environment Variables:**

* `TART_VM_NAME`: Name of your Tart VM (default: `26-edit_1024x768`)
* `MACOS_USERNAME`: VNC and SSH username (default: `admin`)
* `MACOS_PASSWORD`: VNC and SSH password (default: `admin`)
* `CONTAINER_RUNTIME`: `podman` or `docker` (default: `podman`)
* `CONTAINER_IMAGE`: Container image name (default: `mcp-remote-macos-use:latest`)
* `TART_TIMEOUT`: Seconds to wait for VM boot (default: `30`)
* `USE_SSH_TUNNEL`: Enable SSH tunnel (`true` or `false`, default: `false`)
* `MACOS_SSH_PORT`: SSH port (default: `22`)
* `MACOS_SSH_KEY_PATH`: Path to SSH private key (optional, overrides password auth)

### Direct VNC Configuration

For VMs with known IP addresses:

```json
{
  "mcpServers": {
    "macos-test-vm": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "-e",
        "MACOS_HOST=192.168.1.100",
        "-e",
        "MACOS_VNC_PORT=5900",
        "-e",
        "MACOS_USERNAME=testuser",
        "-e",
        "MACOS_PASSWORD=your_vnc_password",
        "-e",
        "VNC_ENCRYPTION=prefer_on",
        "--rm",
        "mcp-remote-macos-use:latest"
      ]
    }
  }
}
```

**Note:** Replace `podman` with `docker` in the command field if you prefer Docker.

### SSH Tunnel Configuration (Recommended)

For enhanced security or when VMs are behind firewalls, route VNC traffic through an encrypted SSH tunnel. Uses the same credentials as VNC:

```json
{
  "mcpServers": {
    "macos-test-vm-ssh": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "-e",
        "MACOS_HOST=vm-host.jamf.example.com",
        "-e",
        "MACOS_USERNAME=testuser",
        "-e",
        "MACOS_PASSWORD=shared_password",
        "-e",
        "USE_SSH_TUNNEL=true",
        "-e",
        "MACOS_SSH_PORT=22",
        "-v",
        "/Users/you/.ssh/id_rsa:/root/.ssh/id_rsa:ro",
        "-e",
        "MACOS_SSH_KEY_PATH=/root/.ssh/id_rsa",
        "--rm",
        "mcp-remote-macos-use:latest"
      ]
    }
  }
}
```

**Note**: SSH uses `MACOS_USERNAME` and `MACOS_PASSWORD` for authentication. For SSH key auth, mount your key and set `MACOS_SSH_KEY_PATH=/root/.ssh/id_rsa` (overrides password auth).

### Configuration Parameters

**Required:** `MACOS_HOST`, `MACOS_USERNAME`, `MACOS_PASSWORD`

**Optional:** `MACOS_VNC_PORT` (default: 5900), `VNC_ENCRYPTION` (default: `prefer_on`)

**SSH Tunnel (Recommended):** When `USE_SSH_TUNNEL=true`, VNC traffic routes through an encrypted SSH tunnel using the same credentials.

* `USE_SSH_TUNNEL`: Enable SSH tunnel (`true` to enable)
* `MACOS_SSH_PORT`: SSH port (default: 22)
* `MACOS_SSH_KEY_PATH`: Path to private key (overrides password auth)

## Usage

Interact with test VMs through natural language in Claude Code:

```text
Open Self Service and verify it launches successfully.
Navigate to Categories → Productivity, find Microsoft Office, and click Install.
Monitor the installation and verify completion.
```

```text
Explore Jamf Connect Settings. Try changing network configuration
and document any unexpected behavior.
```

**Tips:**

* Specify VM targets: "On the macOS 14.5 VM..."
* Define success criteria clearly
* Request screenshots for verification
* Ask Claude to summarize findings

## Available Tools

Claude uses these tools automatically (all use configured environment variables and handle VNC/SSH authentication):

* **remote_macos_get_screen**: Captures screenshots for visual verification
* **remote_macos_mouse_click/double_click**: Clicks UI elements with coordinate scaling
* **remote_macos_mouse_move**: Moves cursor for hover states and positioning
* **remote_macos_mouse_scroll**: Scrolls through lists and content
* **remote_macos_mouse_drag_n_drop**: Drag-and-drop interactions
* **remote_macos_send_keys**: Sends text, special keys, and key combinations
* **remote_macos_open_application**: Launches/activates apps by name

## Best Practices

**Environment:**

* Use dedicated test VMs with snapshots
* Maintain consistent base images for reproducibility
* Isolate test VMs on separate network segments

**Security:**

* Enable SSH tunneling for all connections
* Use key-based SSH authentication
* Store credentials securely; use synthetic test data only

**Testing Strategy:**

* Document observations and request screenshots for evidence
* Specify VM/OS version for each test
* Reset VMs to known-good states between test runs

## Development

```bash
# Clone and build
git clone https://github.com/yourusername/mcp-remote-macos-use.git
cd mcp-remote-macos-use
podman build -t mcp-remote-macos-use .
# or: docker build -t mcp-remote-macos-use .

# Make script executable
chmod +x mcp-macos-use.sh

# Test with Tart VM
./mcp-macos-use.sh

# Multi-platform publish (using Docker buildx)
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourusername/mcp-remote-macos-use:latest --push .
```

## Limitations

* Supports Apple Authentication (VNC protocol 30) only
* Vision-based interaction slower than native automation
* Each instance connects to one VM at a time
* Best with consistent screen resolutions

## Security Notes

Uses VNC protocol 30 (Diffie-Hellman key agreement). **Recommended:** Enable `VNC_ENCRYPTION=prefer_on` + SSH tunneling (`MACOS_SSH_USER`) + key-based SSH auth for defense-in-depth.

[Apple Remote Desktop Encryption](https://support.apple.com/guide/remote-desktop/encrypt-network-data-apdfe8e386b/mac)

## About

Jamf-optimized fork of [baryhuang/mcp-remote-macos-use](https://github.com/baryhuang/mcp-remote-macos-use) with:

* **Unified Credentials**: SSH and VNC use the same `MACOS_USERNAME` and `MACOS_PASSWORD` for simplified configuration
* **SSH Tunnel Support**: VNC traffic routes through encrypted SSH when `USE_SSH_TUNNEL=true`
* **Tart VM Integration**: `mcp-macos-use.sh` automatically detects Tart VM IPs via `tart ip` command
* **Podman/Docker Support**: Works with either container runtime
* **QE-Focused Documentation**: Best practices for E2E and exploratory testing workflows

## License

MIT License - Built on [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
