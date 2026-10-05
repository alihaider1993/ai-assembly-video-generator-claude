import asyncio
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from mcp_server import loader, server

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def fixture_data(monkeypatch):
    monkeypatch.setenv(loader.DATA_DIR_ENV, str(FIXTURES))


def test_list_products_tool():
    products = {p["id"]: p for p in server.list_products()["products"]}
    assert products["good_table"] == {"id": "good_table", "title": "Good Table", "pages_with_actions": 2, "status": "ok"}
    assert products["broken_shelf"]["status"] == "invalid"


def test_get_assembly_steps_tool():
    result = server.get_assembly_steps("good_table")
    action = result["pages"][0]["actions"][0]
    assert action["moving_part"] == {"ref": "P003_002", "name": "leg"}
    assert "visual_evidence" not in action
    with_evidence = server.get_assembly_steps("good_table", include_evidence=True)
    assert with_evidence["pages"][0]["actions"][0]["visual_evidence"] == "4x bolt through each leg"


@pytest.mark.parametrize("bad_id", ["nope", "../x"])
def test_unknown_product_is_structured_error(bad_id):
    result = server.get_assembly_steps(bad_id)
    assert result["error"]["code"] == "unknown_product"
    assert "Traceback" not in json.dumps(result)


def test_invalid_product_is_structured_error():
    assert server.get_assembly_steps("broken_shelf")["error"]["code"] == "invalid_product"


def test_tools_are_read_only():
    tools = asyncio.run(server.mcp.list_tools())
    assert {t.name for t in tools} == {"list_products", "get_assembly_steps"}
    assert all(t.annotations.readOnlyHint for t in tools)


def _rpc(msg_id, method, params=None):
    msg = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    if msg_id is not None:
        msg["id"] = msg_id
    return json.dumps(msg) + "\n"


def test_stdio_smoke_every_stdout_line_is_jsonrpc():
    requests = [
        _rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                               "clientInfo": {"name": "smoke", "version": "0"}}),
        _rpc(None, "notifications/initialized"),
        _rpc(2, "tools/list"),
        _rpc(3, "tools/call", {"name": "list_products", "arguments": {}}),
        _rpc(4, "tools/call", {"name": "get_assembly_steps", "arguments": {"product_id": "good_table"}}),
        _rpc(5, "tools/call", {"name": "get_assembly_steps", "arguments": {"product_id": "../x"}}),
    ]
    env = {**os.environ, loader.DATA_DIR_ENV: str(FIXTURES)}
    proc = subprocess.Popen([sys.executable, "-m", "mcp_server.server"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                            cwd=REPO_ROOT, env=env)
    watchdog = threading.Timer(60, proc.kill)
    watchdog.start()
    lines = []
    try:
        # Send one request at a time and wait for its reply: closing stdin early stops the server.
        for request in requests:
            proc.stdin.write(request)
            proc.stdin.flush()
            if '"id"' in request:
                lines.append(proc.stdout.readline())
        proc.stdin.close()
        lines += proc.stdout.readlines()
        proc.wait(timeout=30)
    finally:
        watchdog.cancel()
        proc.kill()
        stderr = proc.stderr.read()
    stdout = "".join(lines)
    messages = [json.loads(line) for line in lines if line.strip()]
    assert all(m.get("jsonrpc") == "2.0" for m in messages)
    by_id = {m["id"]: m for m in messages if "id" in m}
    assert set(by_id) == {1, 2, 3, 4, 5}, stderr
    assert not any("error" in m for m in by_id.values())
    assert "SECRET" not in stdout
    assert "unknown_product" in json.dumps(by_id[5]["result"])
