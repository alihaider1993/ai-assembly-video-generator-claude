"""MCP server (stdio) exposing the assembly pipeline's JSON output read-only.

Run from the repo root:  python -m mcp_server.server
stdout is the JSON-RPC channel: nothing here may print or log to it.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # allow `python mcp_server/server.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from mcp_server import loader

log = logging.getLogger("mcp_server")

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp = FastMCP("assembly-video")


def _error(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}


@mcp.tool(annotations=READ_ONLY)
def list_products() -> dict[str, Any]:
    """List the products whose assembly data is available.

    Each entry has id, title, pages_with_actions and status ("ok" or "invalid"
    with a short reason). pages_with_actions counts manual pages on which
    assembly actions were observed; it is not the manual's step numbering.
    """
    try:
        products = loader.list_products(loader.data_root())
    except Exception:
        log.exception("list_products failed")
        return _error("internal_error", "Could not list products.")
    return {"products": [p.model_dump(exclude_none=True) for p in products]}


@mcp.tool(annotations=READ_ONLY)
def get_assembly_steps(product_id: str, include_evidence: bool = False) -> dict[str, Any]:
    """Get the observed assembly actions for one product, page by page.

    Only pages with actions are returned. Part, fastener and tool refs are
    resolved to names from the same page (raw refs are kept). Page
    uncertainties are included. Set include_evidence=True to add each action's
    visual_evidence text. product_id must be an id from list_products.

    Each action also has repeat (int or null, from "repeat xN"; null when the
    phrase is qualified, e.g. "total", "each", or numbers disagree) and
    quantities_mentioned (list of {count, text} for each "Nx <words>"; sizes
    such as "4 x 35mm" are skipped). Both are filled even when evidence is off.
    Digit counts only; counts written as words (e.g. 'two') are not captured;
    parsed from vision text, not verified against the manual.
    """
    try:
        steps = loader.get_assembly_steps(loader.data_root(), product_id, include_evidence)
    except loader.LoaderError as exc:
        return _error(exc.code, exc.message)
    except Exception:
        log.exception("get_assembly_steps failed for %r", product_id)
        return _error("internal_error", "Could not load assembly steps.")
    return steps.model_dump(exclude_none=True)


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    log.info("data root: %s", loader.data_root())
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
