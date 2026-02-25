# VNC Key Codes Reference

X11 keysym values used for keyboard operations in VNC protocol.

## Special Keys

| Key Name | Keysym | Hex Value |
|----------|--------|-----------|
| Enter / Return | 0xff0d | 65293 |
| Backspace | 0xff08 | 65288 |
| Tab | 0xff09 | 65289 |
| Escape / Esc | 0xff1b | 65307 |
| Delete / Del | 0xffff | 65535 |
| Space | 0x20 | 32 |
| Home | 0xff50 | 65360 |
| End | 0xff57 | 65367 |
| Page Up | 0xff55 | 65365 |
| Page Down | 0xff56 | 65366 |

## Arrow Keys

| Key | Keysym | Hex Value |
|-----|--------|-----------|
| Left | 0xff51 | 65361 |
| Up | 0xff52 | 65362 |
| Right | 0xff53 | 65363 |
| Down | 0xff54 | 65364 |

## Function Keys

| Key | Keysym | Hex Value |
|-----|--------|-----------|
| F1 | 0xffbe | 65470 |
| F2 | 0xffbf | 65471 |
| F3 | 0xffc0 | 65472 |
| F4 | 0xffc1 | 65473 |
| F5 | 0xffc2 | 65474 |
| F6 | 0xffc3 | 65475 |
| F7 | 0xffc4 | 65476 |
| F8 | 0xffc5 | 65477 |
| F9 | 0xffc6 | 65478 |
| F10 | 0xffc7 | 65479 |
| F11 | 0xffc8 | 65480 |
| F12 | 0xffc9 | 65481 |

## Modifier Keys

| Modifier | Keysym | Hex Value | Aliases |
|----------|--------|-----------|---------|
| Control | 0xffe3 | 65507 | ctrl, control |
| Shift | 0xffe1 | 65505 | shift |
| Alt | 0xffe9 | 65513 | alt, option |
| Command | 0xffeb | 65515 | cmd, command, win, super, meta |
| Function | 0xffed | 65517 | fn |

## Character Keys

- **Letters (a-z)**: Use ASCII ordinal values: `ord('a')` = 97, `ord('z')` = 122
- **Numbers (0-9)**: Use ASCII ordinal values: `ord('0')` = 48, `ord('9')` = 57
- **Other ASCII**: Use `ord(character)` for any single ASCII character

## Usage in Code

### Sending a Special Key

```python
enter_key = 0xff0d
vnc.send_key_event(enter_key, True)   # Press
vnc.send_key_event(enter_key, False)  # Release
```

### Sending a Key Combination

```python
# Cmd+Q (Quit application)
cmd_key = 0xffeb
q_key = ord('q')

# Press modifiers first
vnc.send_key_event(cmd_key, True)
vnc.send_key_event(q_key, True)

# Release in reverse order
vnc.send_key_event(q_key, False)
vnc.send_key_event(cmd_key, False)
```

### Parsing Key Combination String

The `handle_remote_macos_send_keys` function in [action_handlers.py](../src/action_handlers.py) automatically parses strings like:
- `"ctrl+c"` → Control + C
- `"cmd+shift+4"` → Command + Shift + 4
- `"alt+f4"` → Alt + F4

Modifiers and keys are separated by `+` and case-insensitive.
