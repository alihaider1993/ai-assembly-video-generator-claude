import json
from pathlib import Path

import pytest

from mcp_server import loader

FIXTURES = Path(__file__).parent / "fixtures"


def test_data_root_defaults_to_repo_root(monkeypatch):
    monkeypatch.delenv(loader.DATA_DIR_ENV, raising=False)
    assert loader.data_root() == Path(loader.__file__).resolve().parents[1]


def test_data_root_env_override(monkeypatch):
    monkeypatch.setenv(loader.DATA_DIR_ENV, str(FIXTURES))
    assert loader.data_root() == FIXTURES


def test_discover_only_folders_with_page_states():
    assert list(loader.discover_products(FIXTURES)) == ["broken_shelf", "good_table", "untitled_chair"]


def test_discover_missing_manuals_dir(tmp_path):
    assert loader.discover_products(tmp_path) == {}


def test_list_products_marks_bad_product_invalid():
    by_id = {p.id: p for p in loader.list_products(FIXTURES)}
    assert by_id["good_table"].status == "ok"
    assert by_id["good_table"].title == "Good Table"
    assert by_id["good_table"].pages_with_actions == 2
    assert by_id["untitled_chair"].title == "untitled chair"
    broken = by_id["broken_shelf"]
    assert broken.status == "invalid" and broken.reason and broken.pages_with_actions == 0


def test_schema_error_is_invalid(tmp_path):
    folder = tmp_path / "manuals" / "odd"
    folder.mkdir(parents=True)
    (folder / "page_states.json").write_text(json.dumps([{"observed_actions": "nope"}]))
    (product,) = loader.list_products(tmp_path)
    assert product.status == "invalid" and "schema" in product.reason


def test_steps_resolve_refs_and_skip_empty_pages():
    steps = loader.get_assembly_steps(FIXTURES, "good_table")
    assert [p.page_number for p in steps.pages] == [3, 4]
    action = steps.pages[0].actions[0]
    assert (action.moving_part.ref, action.moving_part.name) == ("P003_002", "leg")
    assert action.target_part.name == "table top"
    assert action.fastener.name == "bolt" and action.tool.name == "allen key"
    assert action.visual_evidence is None
    assert steps.pages[0].uncertainties == ["leg orientation unclear"]
    unresolved = steps.pages[1].actions[0]
    assert unresolved.target_part.ref == "P999_999" and unresolved.target_part.name is None
    assert unresolved.fastener is None


def test_steps_include_evidence():
    steps = loader.get_assembly_steps(FIXTURES, "good_table", include_evidence=True)
    assert steps.pages[0].actions[0].visual_evidence == "4x bolt through each leg"


@pytest.mark.parametrize("bad_id", ["nope", "../x", "..\\x", "manuals/good_table", "", "not_described"])
def test_unknown_or_traversal_id_rejected(bad_id):
    with pytest.raises(loader.LoaderError) as exc:
        loader.get_assembly_steps(FIXTURES, bad_id)
    assert exc.value.code == "unknown_product"
