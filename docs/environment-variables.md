# Environment Variables Reference

Complete configuration reference for the MCP Remote macOS Use server.

## Required Variables

### MACOS_HOST
- **Type:** String
- **Required:** Yes
- **Description:** Remote macOS machine hostname or IP address
- **Example:** `192.168.1.100`, `macos-vm.local`
- **Validation:** Server exits with error if not set

### MACOS_PASSWORD
- **Type:** String
- **Required:** Yes
- **Description:** VNC password for authentication
- **Example:** `mypassword`
- **Validation:** Server exits with error if not set
- **Security:** Never commit actual passwords. Use environment-specific config.

## VNC Connection Variables

### MACOS_VNC_PORT
- **Type:** Integer
- **Required:** No
- **Default:** `5900`
- **Description:** VNC server port on remote machine
- **Example:** `5900`, `5901`
- **Note:** macOS Screen Sharing uses port 5900 by default

### MACOS_USERNAME
- **Type:** String
- **Required:** Recommended (required for SSH tunnel)
- **Default:** Empty string
- **Description:** VNC and SSH username (used for both when SSH tunnel is enabled)
- **Example:** `admin`
- **Note:** When `USE_SSH_TUNNEL=true`, this username is used for both SSH and VNC authentication

### VNC_ENCRYPTION
- **Type:** String
- **Required:** No
- **Default:** `prefer_on`
- **Description:** VNC encryption preference
- **Options:** `prefer_on`, `prefer_off`, `required`, `none`
- **Recommendation:** Use `prefer_on` or `required` for security

## SSH Tunnel Variables (Recommended)

When `USE_SSH_TUNNEL=true`, all VNC traffic routes through an encrypted SSH tunnel using the same credentials as VNC.

### USE_SSH_TUNNEL
- **Type:** Boolean
- **Required:** No
- **Default:** `false`
- **Description:** Enable SSH tunnel for VNC traffic
- **Example:** `true`, `false`
- **Effect:** When `true`, VNC connects via encrypted SSH tunnel using `MACOS_USERNAME` and `MACOS_PASSWORD`

### MACOS_SSH_PORT
- **Type:** Integer
- **Required:** No
- **Default:** `22`
- **Description:** SSH server port on remote host
- **Example:** `22`, `2222`

### MACOS_SSH_KEY_PATH
- **Type:** String (file path)
- **Required:** No (for key-based SSH auth)
- **Description:** Path to SSH private key file
- **Example:** `/Users/you/.ssh/id_rsa`, `/root/.ssh/id_rsa`
- **Note:** When set, overrides password authentication for SSH (still uses `MACOS_USERNAME`)
- **Container:** Mount key as read-only volume: `-v ~/.ssh/id_rsa:/root/.ssh/id_rsa:ro`

## LiveKit Variables (Optional)

Optional real-time streaming support. All three must be set to enable LiveKit.

### LIVEKIT_URL
- **Type:** String (URL)
- **Required:** No
- **Description:** LiveKit server URL
- **Example:** `wss://livekit.example.com`

### LIVEKIT_API_KEY
- **Type:** String
- **Required:** No
- **Description:** LiveKit API key
- **Example:** `APIxxxxxxxxx`

### LIVEKIT_API_SECRET
- **Type:** String
- **Required:** No
- **Description:** LiveKit API secret
- **Example:** `secretxxxxxxxxx`

## Tart VM Integration Variables

Used by [mcp-macos-use.sh](../mcp-macos-use.sh) wrapper script.

### TART_VM_NAME
- **Type:** String
- **Required:** No (for Tart VMs)
- **Default:** `26-edit_1024x768`
- **Description:** Name of Tart VM to connect to
- **Example:** `macos-sonoma`, `test-vm`
- **Usage:** Script runs `tart ip TART_VM_NAME` to get IP

### TART_TIMEOUT
- **Type:** Integer (seconds)
- **Required:** No
- **Default:** `30`
- **Description:** Seconds to wait for Tart VM to boot
- **Example:** `30`, `60`

### CONTAINER_RUNTIME
- **Type:** String
- **Required:** No
- **Default:** `podman`
- **Description:** Container runtime to use
- **Options:** `podman`, `docker`
- **Note:** Script auto-installs/configures Podman if selected

### CONTAINER_IMAGE
- **Type:** String
- **Required:** No
- **Default:** `mcp-remote-macos-use:latest`
- **Description:** Container image name to use
- **Example:** `mcp-remote-macos-use:latest`, `buryhuang/mcp-remote-macos-use:latest`

## Configuration Examples

### Direct VNC Connection
```bash
export MACOS_HOST="192.168.1.100"
export MACOS_VNC_PORT="5900"
export MACOS_PASSWORD="password"
export VNC_ENCRYPTION="prefer_on"
```

### VNC via SSH Tunnel (Key-Based)
```bash
export MACOS_HOST="macos-vm.example.com"
export MACOS_USERNAME="admin"
export MACOS_PASSWORD="shared_password"
export USE_SSH_TUNNEL="true"
export MACOS_SSH_KEY_PATH="/Users/you/.ssh/id_rsa"
```

### VNC via SSH Tunnel (Password-Based)
```bash
export MACOS_HOST="macos-vm.example.com"
export MACOS_USERNAME="admin"
export MACOS_PASSWORD="shared_password"
export USE_SSH_TUNNEL="true"
```

### Tart VM Integration
```bash
export TART_VM_NAME="macos-sonoma"
export MACOS_USERNAME="admin"
export MACOS_PASSWORD="admin"
export CONTAINER_RUNTIME="podman"
```

## Loading from .env File

Create a `.env` file in the project root:
```bash
MACOS_HOST=192.168.1.100
MACOS_PASSWORD=password
VNC_ENCRYPTION=prefer_on
```

The server automatically loads `.env` via python-dotenv when run directly:
```bash
python -m mcp_remote_macos_use.server
```

**Security Warning:** Never commit `.env` files with real credentials to version control.
