"""Dynamic .py + .yaml tool loading.

Each tool is a pair of files sharing a basename in a tools directory:
  add_numbers.yaml   — id, description, input_schema, function (default "run")
  add_numbers.py      — defines the callable named by `function`

Dropping a new pair into the directory and reloading picks it up — no
package publishing or restart-time registration required.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml


@dataclass(frozen=True)
class ToolDefinition:
    id: str
    description: str
    input_schema: dict[str, Any]
    func: Callable[..., Any]


def _load_module(py_path: Path):
    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {py_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tools(directory: str | Path) -> list[ToolDefinition]:
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Tools directory not found: {directory}")

    tools: list[ToolDefinition] = []
    for yaml_path in sorted(directory.glob("*.yaml")):
        meta = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        py_path = yaml_path.with_suffix(".py")
        if not py_path.exists():
            raise FileNotFoundError(f"Tool {yaml_path.name!r} has no matching {py_path.name}")

        module = _load_module(py_path)
        func_name = meta.get("function", "run")
        func = getattr(module, func_name, None)
        if func is None or not callable(func):
            raise AttributeError(f"{py_path} has no callable named {func_name!r}")

        tools.append(
            ToolDefinition(
                id=meta.get("id", yaml_path.stem),
                description=meta.get("description", ""),
                input_schema=meta.get("input_schema") or {"type": "object", "properties": {}},
                func=func,
            )
        )
    return tools
