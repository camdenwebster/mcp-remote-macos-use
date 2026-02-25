import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
import base64
import socket
import time
import io
from PIL import Image
import asyncio
import pyDes
import json
import os
from base64 import b64encode
from datetime import datetime
import sys

# Import MCP server libraries
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Import VNC client functionality from the src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vnc_client import VNCClient, capture_vnc_screen

# Import action handlers from the src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from action_handlers import (
    handle_remote_macos_get_screen,
    handle_remote_macos_mouse_scroll,
    handle_remote_macos_send_keys,
    handle_remote_macos_mouse_move,
    handle_remote_macos_mouse_click,
    handle_remote_macos_mouse_double_click,
    handle_remote_macos_open_application,
    handle_remote_macos_mouse_drag_n_drop,
    handle_remote_macos_send_ssh_command,
    handle_remote_macos_send_file_scp,
    handle_remote_macos_save_screenshot,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_remote_macos_use')
logger.setLevel(logging.DEBUG)

# Load environment variables for VNC connection
MACOS_HOST = os.environ.get('MACOS_HOST', '')
MACOS_VNC_PORT = int(os.environ.get('MACOS_VNC_PORT', '5900'))
MACOS_USERNAME = os.environ.get('MACOS_USERNAME', '')
MACOS_PASSWORD = os.environ.get('MACOS_PASSWORD', '')
VNC_ENCRYPTION = os.environ.get('VNC_ENCRYPTION', 'prefer_on')

# Log environment variable status (without exposing actual values)
logger.info(f"MACOS_HOST from environment: {'Set' if MACOS_HOST else 'Not set'}")
logger.info(f"MACOS_VNC_PORT from environment: {MACOS_VNC_PORT}")
logger.info(f"MACOS_USERNAME from environment: {'Set' if MACOS_USERNAME else 'Not set'}")
logger.info(f"MACOS_PASSWORD from environment: {'Set' if MACOS_PASSWORD else 'Not set (Required)'}")
logger.info(f"VNC_ENCRYPTION from environment: {VNC_ENCRYPTION}")

# Validate required environment variables
if not MACOS_HOST:
    logger.error("MACOS_HOST environment variable is required but not set")
    raise ValueError("MACOS_HOST environment variable is required but not set")

if not MACOS_PASSWORD:
    logger.error("MACOS_PASSWORD environment variable is required but not set")
    raise ValueError("MACOS_PASSWORD environment variable is required but not set")


async def main():
    """Run the Remote MacOS MCP server."""
    logger.info("Remote MacOS computer use server starting")

    # Validate required environment variables
    if not MACOS_HOST:
        logger.error("MACOS_HOST environment variable is required but not set")
        raise ValueError("MACOS_HOST environment variable is required but not set")

    if not MACOS_PASSWORD:
        logger.error("MACOS_PASSWORD environment variable is required but not set")
        raise ValueError("MACOS_PASSWORD environment variable is required but not set")

    server = Server("remote-macos-client")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        return []

    @server.read_resource()
    async def handle_read_resource(uri: types.AnyUrl) -> str:
        return ""

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="remote_macos_get_screen",
                description="Connect to a remote MacOs machine and get a screenshot of the remote desktop. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
            ),
            types.Tool(
                name="remote_macos_mouse_scroll",
                description="Perform a mouse scroll at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "direction": {
                            "type": "string",
                            "description": "Scroll direction",
                            "enum": ["up", "down"],
                            "default": "down"
                        }
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_send_keys",
                description="Send keyboard input to a remote MacOs machine. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to send as keystrokes"},
                        "special_key": {"type": "string", "description": "Special key to send (e.g., 'enter', 'backspace', 'tab', 'escape', etc.)"},
                        "key_combination": {"type": "string", "description": "Key combination to send (e.g., 'ctrl+c', 'cmd+q', 'ctrl+alt+delete', etc.)"}
                    },
                    "required": []
                },
            ),
            types.Tool(
                name="remote_macos_mouse_move",
                description="Move the mouse cursor to specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_click",
                description="Perform a mouse click at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_double_click",
                description="Perform a mouse double-click at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_open_application",
                description="Opens/activates an application and returns its PID for further interactions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "REQUIRED. App name, path, or bundle ID."
                        }
                    },
                    "required": ["identifier"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_drag_n_drop",
                description="Perform a mouse drag operation from start point and drop to end point on a remote MacOs machine, with automatic coordinate scaling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_x": {"type": "integer", "description": "Starting X coordinate (in source dimensions)"},
                        "start_y": {"type": "integer", "description": "Starting Y coordinate (in source dimensions)"},
                        "end_x": {"type": "integer", "description": "Ending X coordinate (in source dimensions)"},
                        "end_y": {"type": "integer", "description": "Ending Y coordinate (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling. Use 0 for 1:1 mapping with actual VM resolution.", "default": 0},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1},
                        "steps": {"type": "integer", "description": "Number of intermediate points for smooth dragging", "default": 10},
                        "delay_ms": {"type": "integer", "description": "Delay between steps in milliseconds", "default": 10}
                    },
                    "required": ["start_x", "start_y", "end_x", "end_y"]
                },
            ),
            types.Tool(
                name="remote_macos_send_ssh_command",
                description="Execute a shell command on the remote macOS machine via SSH. If the command contains sudo, the password is injected automatically via stdin.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute on the remote machine"}
                    },
                    "required": ["command"]
                },
            ),
            types.Tool(
                name="remote_macos_send_file_scp",
                description="Copy a local file to the /tmp directory on the remote macOS machine via SCP.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "local_path": {"type": "string", "description": "Absolute path to the local file to upload"}
                    },
                    "required": ["local_path"]
                },
            ),
            types.Tool(
                name="remote_macos_save_screenshot",
                description="Capture a screenshot of the remote macOS desktop and save it as a PNG to a local file path. Use paths under /mcp-output/ (e.g. /mcp-output/screenshot-1.png) — this directory is mounted to the host and is suitable for logging and diagnostic reports.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "File path where the PNG will be saved. Use /mcp-output/<filename>.png to persist to the host machine."}
                    },
                    "required": ["file_path"]
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if not arguments:
                arguments = {}

            if name == "remote_macos_get_screen":
                return await handle_remote_macos_get_screen(arguments)

            elif name == "remote_macos_mouse_scroll":
                return handle_remote_macos_mouse_scroll(arguments)

            elif name == "remote_macos_send_keys":
                return handle_remote_macos_send_keys(arguments)

            elif name == "remote_macos_mouse_move":
                return handle_remote_macos_mouse_move(arguments)

            elif name == "remote_macos_mouse_click":
                return handle_remote_macos_mouse_click(arguments)

            elif name == "remote_macos_mouse_double_click":
                return handle_remote_macos_mouse_double_click(arguments)

            elif name == "remote_macos_open_application":
                return handle_remote_macos_open_application(arguments)

            elif name == "remote_macos_mouse_drag_n_drop":
                return handle_remote_macos_mouse_drag_n_drop(arguments)

            elif name == "remote_macos_send_ssh_command":
                return await handle_remote_macos_send_ssh_command(arguments)

            elif name == "remote_macos_send_file_scp":
                return await handle_remote_macos_send_file_scp(arguments)

            elif name == "remote_macos_save_screenshot":
                return await handle_remote_macos_save_screenshot(arguments)

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Error in handle_call_tool: {str(e)}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vnc-client",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    load_dotenv()

    try:
        # Run the server
        asyncio.run(main())
    except ValueError as e:
        logger.error(f"Initialization failed: {str(e)}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"ERROR: Unexpected error occurred: {str(e)}")
        sys.exit(1)