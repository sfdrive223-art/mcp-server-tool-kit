from pathlib import Path

from dynamic_tool_mcp.loader import load_tools

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"


def test_load_tools_discovers_pairs() -> None:
    tools = load_tools(TOOLS_DIR)
    ids = [t.id for t in tools]
    assert "add_numbers" in ids


def test_loaded_tool_is_callable() -> None:
    tools = load_tools(TOOLS_DIR)
    add_numbers = next(t for t in tools if t.id == "add_numbers")
    assert add_numbers.func({"a": 2, "b": 3}) == {"sum": 5}


def test_missing_directory_raises() -> None:
    import pytest

    with pytest.raises(FileNotFoundError):
        load_tools(TOOLS_DIR / "does-not-exist")
