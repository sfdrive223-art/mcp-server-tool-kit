"""Client satisfying AAF's McpRuntimeAdapter contract:

    session = await mcp_client.get_session(server_url, bearer_token)
    raw = await session.call_tool(tool_id, input)

Wraps fastmcp.Client, which already speaks the MCP protocol over SSE/HTTP.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Client


class DynamicToolMcpSession:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def call_tool(self, tool_id: str, input: dict[str, Any]) -> Any:
        return await self._client.call_tool(tool_id, input)

    async def close(self) -> None:
        await self._client.__aexit__(None, None, None)


class DynamicToolMcpClient:
    """Minimal client facade — one session per call, matching AAF's usage pattern."""

    async def get_session(
        self, server_url: str, bearer_token: str | None = None
    ) -> DynamicToolMcpSession:
        client = Client(server_url, auth=bearer_token) if bearer_token else Client(server_url)
        await client.__aenter__()
        return DynamicToolMcpSession(client)
