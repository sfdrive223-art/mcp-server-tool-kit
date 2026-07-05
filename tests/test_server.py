from pathlib import Path

from fastmcp import Client

from dynamic_tool_mcp.server import build_server

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"


async def test_add_numbers_tool_via_in_memory_client() -> None:
    server = build_server(TOOLS_DIR)
    async with Client(server) as client:
        tools = await client.list_tools()
        assert any(t.name == "add_numbers" for t in tools)

        result = await client.call_tool("add_numbers", {"a": 2, "b": 3})
        assert result.data == {"sum": 5.0}
