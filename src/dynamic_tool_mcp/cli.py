"""dynamic-tool-mcp — console entrypoint for the standalone Tools Framework server."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dynamic_tool_mcp.server import build_server

DEFAULT_TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools"


def main() -> None:
    parser = argparse.ArgumentParser(prog="dynamic-tool-mcp")
    parser.add_argument("--tools-dir", type=Path, default=None)
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    tools_dir = args.tools_dir or Path(os.environ.get("MCP_TOOLS_DIR", str(DEFAULT_TOOLS_DIR)))
    host = args.host or os.environ.get("MCP_HOST", "0.0.0.0")
    port = args.port or int(os.environ.get("MCP_PORT", "9100"))

    allowed = os.environ.get("MCP_BEARER_TOKENS", "")
    allowed_tokens = {t.strip() for t in allowed.split(",") if t.strip()} or None

    server = build_server(tools_dir, allowed_tokens=allowed_tokens)
    server.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    main()
