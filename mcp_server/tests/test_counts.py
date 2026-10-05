import json

import pytest

from mcp_server import counts, loader, server

ALHULT_P4 = "Attach two corner brackets 102646 onto left side frame seat rail using screws 109598; Repeat x4 total across both frames"

CASES = [
    # (evidence, repeat, quantities_mentioned)
    ("Repeat x4", 4, []),
    ("wooden dowel A pushed into both ends of wide headboard rail 6, repeat x4", 4, []),
    (ALHULT_P4, None, []),
    ("screwed down with 24x screw B", None, [(24, "screw B")]),
    ("screwed down with 4 x 35mm screw B", None, []),
    ("wooden dowel 10 x 40mm", None, []),
    ("2x bracket fixed to the rail with 4x screw", None, [(2, "bracket fixed to the rail with"), (4, "screw")]),
    ("shelf slides in", None, []),
    ("repeat x2, then repeat x4", None, []),
]


@pytest.mark.parametrize("evidence, repeat, quantities", CASES)
def test_parsers(evidence, repeat, quantities):
    assert counts.parse_repeat(evidence) == repeat
    assert counts.parse_quantities(evidence) == quantities


@pytest.mark.parametrize("evidence", ["2x 35mm screw", "2x 1/4 in bolt", "M6x 20 bolt", "1.5x wide"])
def test_sizes_are_not_quantities(evidence):
    assert counts.parse_quantities(evidence) == []


def test_text_stops_at_clause_and_is_short():
    assert counts.parse_quantities("8x cam lock and 8x bolt; then turn") == [(8, "cam lock"), (8, "bolt")]
    ((_, text),) = counts.parse_quantities("1x " + "long words " * 10)
    assert len(text) <= counts.MAX_TEXT


def test_same_repeat_twice_is_kept():
    assert counts.parse_repeat("repeat x2 on the left; repeat x2 on the right") == 2


@pytest.fixture
def counted(tmp_path, monkeypatch):
    folder = tmp_path / "manuals" / "counted"
    folder.mkdir(parents=True)
    actions = [{"action_uid": f"A001_{i:03}", "visual_evidence": ev} for i, (ev, _, _) in enumerate(CASES, 1)]
    (folder / "page_states.json").write_text(json.dumps([{"page_number": 1, "observed_actions": actions}]))
    monkeypatch.setenv(loader.DATA_DIR_ENV, str(tmp_path))
    return tmp_path


def test_tool_output_has_counts_without_evidence(counted):
    actions = server.get_assembly_steps("counted")["pages"][0]["actions"]
    for action, (_, repeat, quantities) in zip(actions, CASES):
        assert "visual_evidence" not in action
        assert action["repeat"] == repeat  # present as null, not dropped
        assert action["quantities_mentioned"] == [{"count": n, "text": t} for n, t in quantities]


def test_counts_unchanged_with_evidence(counted):
    action = server.get_assembly_steps("counted", include_evidence=True)["pages"][0]["actions"][0]
    assert (action["repeat"], action["visual_evidence"]) == (4, "Repeat x4")
