# MCP Tool Reference

Complete reference for all 8 MCP tools exposed by the server.

## remote_macos_get_screen

Capture a screenshot from the remote macOS machine.

**Parameters:** None (uses environment variables)

**Returns:** ImageContent (PNG) + TextContent with dimensions

**Example:**
```json
{}
```

---

## remote_macos_mouse_click

Perform a single mouse click with coordinate scaling.

**Parameters:**
- `x` (integer, required): X coordinate in source dimensions
- `y` (integer, required): Y coordinate in source dimensions
- `source_width` (integer, default: 1366): Reference width for scaling
- `source_height` (integer, default: 768): Reference height for scaling
- `button` (integer, default: 1): Mouse button (1=left, 2=middle, 3=right)

**Returns:** TextContent with click status and scaling info

---

## remote_macos_mouse_double_click

Perform a double-click with coordinate scaling.

**Parameters:** Same as `remote_macos_mouse_click`

**Returns:** TextContent with double-click status and scaling info

---

## remote_macos_mouse_move

Move mouse cursor to coordinates with scaling.

**Parameters:**
- `x` (integer, required): X coordinate in source dimensions
- `y` (integer, required): Y coordinate in source dimensions
- `source_width` (integer, default: 1366): Reference width
- `source_height` (integer, default: 768): Reference height

**Returns:** TextContent with move status and scaling info

---

## remote_macos_mouse_scroll

Scroll at specified coordinates using Page Up/Down keys.

**Parameters:**
- `x` (integer, required): X coordinate in source dimensions
- `y` (integer, required): Y coordinate in source dimensions
- `source_width` (integer, default: 1366): Reference width
- `source_height` (integer, default: 768): Reference height
- `direction` (string, default: "down"): "up" or "down"

**Returns:** TextContent with scroll status

**Implementation:** Moves cursor to position, then sends Page Up/Down key

---

## remote_macos_send_keys

Send keyboard input (text, special keys, or key combinations).

**Parameters:** (mutually exclusive - provide ONE of):
- `text` (string): Text to type
- `special_key` (string): Special key name (enter, tab, escape, backspace, delete, arrows, F1-F12, etc.)
- `key_combination` (string): Combo like "ctrl+c", "cmd+q", "cmd+shift+4"

**Returns:** TextContent with operation status

**Examples:**
```json
{"text": "Hello World"}
{"special_key": "enter"}
{"key_combination": "cmd+q"}
```

See [vnc-keycodes.md](vnc-keycodes.md) for complete key mappings.

---

## remote_macos_open_application

Launch or activate an application via Spotlight.

**Parameters:**
- `identifier` (string, required): App name, path, or bundle ID

**Returns:** TextContent with launch status

**Implementation:**
1. Send Cmd+Space to open Spotlight
2. Type the identifier
3. Press Enter

**Example:**
```json
{"identifier": "Safari"}
```

---

## remote_macos_mouse_drag_n_drop

Drag mouse from start point to end point with smooth motion.

**Parameters:**
- `start_x` (integer, required): Starting X in source dimensions
- `start_y` (integer, required): Starting Y in source dimensions
- `end_x` (integer, required): Ending X in source dimensions
- `end_y` (integer, required): Ending Y in source dimensions
- `source_width` (integer, default: 1366): Reference width
- `source_height` (integer, default: 768): Reference height
- `button` (integer, default: 1): Mouse button
- `steps` (integer, default: 10): Number of intermediate points
- `delay_ms` (integer, default: 10): Delay between steps

**Returns:** TextContent with drag operation details

**Implementation:**
1. Move to start position
2. Press mouse button
3. Move through intermediate steps with delays
4. Release button at end position
