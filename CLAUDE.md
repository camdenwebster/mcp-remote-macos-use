# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP server enabling Claude to control remote macOS systems via VNC for automated testing. Uses vision-based interaction for E2E and exploratory testing of Mac applications on VMs.

## Essential Commands

```bash
# Setup (uses uv for dependency management)
uv sync                         # Install dependencies
uv sync --dev                   # Install with dev dependencies

# Run tests
uv run pytest                   # All tests
uv run pytest tests/test_server.py  # Specific test file
uv run pytest -v                # Verbose output

# Development
uv run python -m mcp_remote_macos_use.server  # Run server directly
# Or use pip: pip install -e .

# Container
docker build -t mcp-remote-macos-use .  # Build image
./mcp-macos-use.sh             # Run with Tart VM auto-detection

# Type checking
uv run pyright src/
```

## Architecture

### Three-Layer Design

1. **MCP Server** ([server.py](src/mcp_remote_macos_use/server.py)) - Implements MCP protocol, registers 8 tools, routes calls to handlers
2. **VNC Client** ([vnc_client.py](src/vnc_client.py)) - VNC protocol implementation with SSH tunnel support
3. **Action Handlers** ([action_handlers.py](src/action_handlers.py)) - Converts tool calls to VNC operations with coordinate scaling

### Connection Pattern

**Critical**: Each tool operation creates a NEW connection (not persistent):

```python
vnc = VNCClient(host, port, password, ...)
success, error = vnc.connect()
try:
    # Execute operation
finally:
    vnc.close()  # Always close
```

### Coordinate Scaling

All mouse operations accept `source_width`/`source_height` (default 1366x768) and scale to actual remote screen dimensions:

```python
scaled_x = int((x / source_width) * vnc.width)
scaled_y = int((y / source_height) * vnc.height)
```

### SSH Tunnel Support

When `USE_SSH_TUNNEL=true`, VNC traffic routes through encrypted SSH tunnel automatically using the same credentials as VNC.

## Environment Variables

**Required:**

- `MACOS_HOST` - Remote macOS hostname/IP
- `MACOS_USERNAME` - VNC and SSH username
- `MACOS_PASSWORD` - VNC and SSH password

**Important:**

- `MACOS_VNC_PORT` - VNC port (default: 5900)
- `VNC_ENCRYPTION` - Encryption preference (default: "prefer_on")

**SSH Tunnel (Recommended):**

- `USE_SSH_TUNNEL` - Enable SSH tunnel (`true` to enable)
- `MACOS_SSH_PORT` - SSH port (default: 22)
- `MACOS_SSH_KEY_PATH` - Path to SSH private key (overrides password auth)

See [docs/environment-variables.md](docs/environment-variables.md) for complete reference.

## Adding a New Tool

1. Create handler in [action_handlers.py](src/action_handlers.py) following the connection pattern
2. Import handler in [server.py](src/mcp_remote_macos_use/server.py)
3. Register in `handle_list_tools()` with input schema
4. Add routing in `handle_call_tool()`

**Reference existing tools as examples** - All 8 tools follow the same consistent pattern.

## Key Files

```text
src/mcp_remote_macos_use/server.py    - MCP server, tool registration
src/vnc_client.py                     - VNC protocol + SSH tunneling
src/action_handlers.py                - Tool implementations
tests/                                - pytest tests with async support
mcp-macos-use.sh                      - Tart VM integration wrapper
```

## Reference Documentation

- [Tool Reference](docs/tool-reference.md) - All 8 MCP tools with schemas
- [VNC Key Codes](docs/vnc-keycodes.md) - X11 keysym mappings for keyboard input
- [Environment Variables](docs/environment-variables.md) - Complete configuration reference
- [Container Deployment](docs/container-deployment.md) - Docker/Podman deployment patterns

## Testing Notes

- Tests use pytest with pytest-asyncio
- Mock environment variables and MCP server/stdio in fixtures
- Tests verify tool registration and routing, not actual VNC operations
- See [tests/conftest.py](tests/conftest.py) for shared fixtures
