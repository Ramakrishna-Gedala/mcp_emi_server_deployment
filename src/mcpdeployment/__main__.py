"""
CLI entrypoint for starting the EMI MCP server.

Supports both `python -m emiserver` (package execution) and direct script
execution `python src/emiserver/__main__.py` by falling back to adding the
repository's `src` directory to `sys.path` when the package context is missing.
"""

if __package__:
    from .emi_calculator import mcp
else:  # pragma: no cover - convenience for direct script execution
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from emiserver.emi_calculator import mcp  # type: ignore


def main() -> None:
    """Start the FastMCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
