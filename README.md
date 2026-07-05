# mcp-server-tool-kit

Minimal stand-in for the **Tools Framework** (package `dynamic-tool-mcp`) expected by
[agentic-assembly-framework](../AAFCodeBase). A FastMCP server that dynamically loads
tools from `.py`+`.yaml` pairs, plus a client satisfying AAF's `McpRuntimeAdapter`
contract (`get_session(server_url, bearer_token) -> session.call_tool(id, input)`).

## Run it

```bash
pip install -e .
dynamic-tool-mcp --tools-dir tools --host 127.0.0.1 --port 9100
```

## Adding a tool

Drop a matching pair into the tools directory — no restart-time registration:

```
tools/
├── add_numbers.yaml   # id, description, input_schema, function (default "run")
└── add_numbers.py     # def run(input: dict) -> object
```

## Auth

Set `MCP_BEARER_TOKENS` (comma-separated) to require a bearer token on every
request. Omit it to run with no auth, matching a `local-dev` assembly.

## Client

```python
from dynamic_tool_mcp.client import DynamicToolMcpClient

client = DynamicToolMcpClient()
session = await client.get_session("http://127.0.0.1:9100/sse")
result = await session.call_tool("add_numbers", {"a": 1, "b": 2})
```
