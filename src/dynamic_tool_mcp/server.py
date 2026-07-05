"""Builds a FastMCP server from every tool discovered by the dynamic loader.

FastMCP infers each tool's JSON schema from its Python function signature, so
each loaded tool gets a small generated wrapper with one named parameter per
schema property (FastMCP rejects **kwargs-only functions for this reason).
"""

from __future__ import annotations

import inspect
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.tools.tool import Tool

from dynamic_tool_mcp.auth import StaticBearerTokenVerifier
from dynamic_tool_mcp.loader import ToolDefinition, load_tools

_TYPE_MAP = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool",
    "array": "list",
    "object": "dict",
}


def build_server(
    tools_dir: str | Path,
    *,
    name: str = "dynamic-tool-mcp",
    allowed_tokens: set[str] | None = None,
) -> FastMCP:
    auth = StaticBearerTokenVerifier(allowed_tokens) if allowed_tokens else None
    mcp = FastMCP(name=name, auth=auth)
    for tool_def in load_tools(tools_dir):
        mcp.add_tool(_to_fastmcp_tool(tool_def))
    return mcp


def _to_fastmcp_tool(tool_def: ToolDefinition) -> Tool:
    schema = tool_def.input_schema or {"type": "object", "properties": {}}
    properties: dict = schema.get("properties", {})
    required = set(schema.get("required", []))
    is_async = inspect.iscoroutinefunction(tool_def.func)

    sorted_names = sorted(properties, key=lambda name: 0 if name in required else 1)
    arg_defs = []
    for prop_name in sorted_names:
        py_type = _TYPE_MAP.get((properties[prop_name] or {}).get("type", "string"), "str")
        if prop_name in required:
            arg_defs.append(f"{prop_name}: {py_type}")
        else:
            arg_defs.append(f"{prop_name}: {py_type} = None")

    args_str = ", ".join(arg_defs)
    dict_str = ", ".join(f"'{name}': {name}" for name in properties)
    call_expr = "await _func(_input)" if is_async else "_func(_input)"
    code = (
        f"async def _run({args_str}):\n"
        f"    _input = {{k: v for k, v in {{{dict_str}}}.items() if v is not None}}\n"
        f"    return {call_expr}\n"
    )
    namespace: dict[str, object] = {"_func": tool_def.func}
    exec(code, namespace)
    fn = namespace["_run"]
    fn.__name__ = tool_def.id.replace("-", "_")

    return Tool.from_function(fn, name=tool_def.id, description=tool_def.description)
