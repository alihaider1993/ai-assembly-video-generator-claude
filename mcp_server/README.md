# Assembly MCP server

## What it is

A local, read-only [MCP](https://modelcontextprotocol.io) server written in Python with the official MCP SDK (`FastMCP`, server name `assembly-video`). It talks over stdio.

It exposes the assembly pipeline's `page_states.json` output. The pipeline is a black box to the server: it never runs any pipeline stage, it only reads JSON from disk. A product is any folder `manuals/<id>/` under the data root that contains a `page_states.json`. The title comes from `manuals/<id>/product.json` (`"title"`), falling back to the folder name with underscores replaced by spaces.

## Tools

### `list_products()`

Returns `{"products": [...]}`. Each entry has:

- `id`: the folder name, used as `product_id`.
- `title`
- `pages_with_actions`: number of pages in `page_states.json` that have at least one observed action.
- `status`: `"ok"`, or `"invalid"` with a short `reason` when the file can't be read or doesn't match the expected schema.

### `get_assembly_steps(product_id, include_evidence=False)`

Returns `{"id", "title", "pages": [...]}`. Only pages with actions are included. Each page has:

- `page_number`
- `uncertainties`: the page's uncertainty notes from the vision stage.
- `actions`: a list where each action has
  - `action_uid`, `action_type`, `direction_hint`
  - `moving_part`, `target_part`, `fastener`, `tool`: each `{"ref", "name"}`. The raw ref is kept and `name` is resolved from the same page's visible parts, fasteners or tools. `name` is omitted when the ref isn't listed on that page.
  - `repeat`: the integer N from "repeat xN" in the action's evidence text, or `null` when there is no such phrase, when it is qualified ("total", "each", "per", "across") or when two "repeat x" counts disagree. It is always present, even as `null`.
  - `quantities_mentioned`: a list of `{"count", "text"}` for each `Nx <words>` in the evidence (for example `24x screw B`). Sizes such as `4x 35mm` are skipped.
  - `visual_evidence`: the raw evidence text, only when `include_evidence=True`.

`repeat` and `quantities_mentioned` are parsed from the evidence text whether or not `include_evidence` is set. Other fields that have no value are left out.

Errors come back as `{"error": {"code", "message"}}` with code `unknown_product`, `invalid_product` or `internal_error`.

## Known limits

- `pages_with_actions` counts the pages on which the vision stage observed actions. It is not the manual's step count or step numbering.
- `repeat` means "this action is repeated N times". It is not a parts count, so never add it up as a quantity.
- All counts are digit-only and parsed from vision text. Counts written as words ("two") are not captured, and nothing is checked against the manual.
- Part and fastener refs are page-local. The same ref on two pages doesn't necessarily mean the same part, so don't use refs to link actions across pages.

## Setup

From the repo root (Windows):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-mcp.txt
pytest mcp_server/tests
python -m mcp_server.server
```

`ASSEMBLY_DATA_DIR` sets the data root, the directory that contains `manuals/`. It defaults to the repo root (the parent of `mcp_server/`).

## Connecting a client

MCP Inspector, from the repo root with the venv active:

```bash
npx @modelcontextprotocol/inspector python -m mcp_server.server
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "assembly-video": {
      "command": "C:\\path\\to\\repo\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\path\\to\\repo",
      "env": {
        "ASSEMBLY_DATA_DIR": "C:\\path\\to\\repo",
        "PYTHONPATH": "C:\\path\\to\\repo"
      }
    }
  }
}
```

Claude Desktop ignored `cwd` on Windows, so `python -m mcp_server.server` could not find the package. `PYTHONPATH` is required.

## Safety notes

- `product_id` is checked against the products discovered on disk and is never joined into a path. Anything else, including path traversal such as `../x`, returns `unknown_product`.
- Nothing is ever written to stdout, which carries the JSON-RPC messages. Logs go to stderr.
- Both tools are annotated `readOnlyHint=True` (also `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`).
