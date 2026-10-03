"""Schema for the two vision results the pipeline starts from:
page_states.json (parts, fasteners, tools and actions per manual page) and
diagram_analysis.json (diagram regions and part-list measurements per page).

These used to be produced by GPT-4o vision agents. The pipeline now runs
offline from hand-written fixtures in v2/tests/fixtures/, and the fixture
generators pass every page through these validators so the files have
exactly the schema (defaults, stable P/F/T/A uids) the later stages expect.
"""
import re
from typing import Any, Dict, List, Tuple


def norm(value: Any) -> str:
    return str(value or "").strip().lower()


def ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def ensure_dict_list(value: Any) -> List[Dict[str, Any]]:
    return [item for item in ensure_list(value) if isinstance(item, dict)]


def to_int(value: Any, default: int = 1) -> int:
    """Parse model-supplied counts such as 4, "4", "4x" or "x4"."""
    match = re.search(r"\d+", str(value or ""))
    return int(match.group()) if match else default


def make_aliases(item: Dict[str, Any], keys: List[str]) -> List[str]:
    aliases = []

    for key in keys:
        value = item.get(key)
        if value:
            aliases.append(norm(value))

    return list(set(a for a in aliases if a))


def remap_ref(ref: str, alias_map: Dict[str, str]) -> str:
    ref_n = norm(ref)

    if not ref_n:
        return ""

    return alias_map.get(ref_n, "")


def generate_stable_ids(state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    page_number = int(state.get("page_number", 0))

    visible_parts = ensure_dict_list(state.get("visible_parts"))
    visible_fasteners = ensure_dict_list(state.get("visible_fasteners"))
    visible_tools = ensure_dict_list(state.get("visible_tools"))
    observed_actions = ensure_dict_list(state.get("observed_actions"))

    part_alias_map: Dict[str, str] = {}
    fastener_alias_map: Dict[str, str] = {}
    tool_alias_map: Dict[str, str] = {}

    for index, part in enumerate(visible_parts, start=1):
        old_uid = part.get("part_uid", "")
        stable_uid = f"P{page_number:03d}_{index:03d}"

        for alias in make_aliases(
            part,
            ["part_uid", "manual_label", "name", "visual_description"]
        ):
            part_alias_map[alias] = stable_uid

        if old_uid:
            part_alias_map[norm(old_uid)] = stable_uid

        part["part_uid"] = stable_uid
        part["quantity_visible"] = to_int(part.get("quantity_visible"))
        part["connection_features"] = ensure_dict_list(part.get("connection_features"))

        for feature in part["connection_features"]:
            feature["count"] = to_int(feature.get("count"))

        part.setdefault("manual_label", "")
        part.setdefault("name", "")
        part.setdefault("visual_description", "")
        part.setdefault("shape_family", "unknown")
        part.setdefault("material_hint", "unknown")
        part.setdefault("page_position", "unknown")

    for index, fastener in enumerate(visible_fasteners, start=1):
        old_uid = fastener.get("fastener_uid", "")
        stable_uid = f"F{page_number:03d}_{index:03d}"

        for alias in make_aliases(
            fastener,
            ["fastener_uid", "manual_label", "name"]
        ):
            fastener_alias_map[alias] = stable_uid

        if old_uid:
            fastener_alias_map[norm(old_uid)] = stable_uid

        fastener["fastener_uid"] = stable_uid
        fastener["quantity_visible"] = to_int(fastener.get("quantity_visible"))
        fastener.setdefault("manual_label", "")
        fastener.setdefault("name", "")
        fastener.setdefault("shape_family", "unknown")

    for index, tool in enumerate(visible_tools, start=1):
        old_uid = tool.get("tool_uid", "")
        stable_uid = f"T{page_number:03d}_{index:03d}"

        for alias in make_aliases(tool, ["tool_uid", "name"]):
            tool_alias_map[alias] = stable_uid

        if old_uid:
            tool_alias_map[norm(old_uid)] = stable_uid

        tool["tool_uid"] = stable_uid
        tool.setdefault("name", "")

    unresolved_refs = 0

    for index, action in enumerate(observed_actions, start=1):
        action["action_uid"] = f"A{page_number:03d}_{index:03d}"
        action.setdefault("action_type", "unknown")
        action.setdefault("direction_hint", "unknown")
        action.setdefault("visual_evidence", "")

        moving = action.get("moving_part_ref", "")
        target = action.get("target_part_ref", "")
        fastener = action.get("fastener_ref", "")
        tool = action.get("tool_ref", "")

        action["moving_part_ref"] = remap_ref(moving, part_alias_map)
        action["target_part_ref"] = remap_ref(target, part_alias_map)
        action["fastener_ref"] = remap_ref(fastener, fastener_alias_map)
        action["tool_ref"] = remap_ref(tool, tool_alias_map)

        if moving and not action["moving_part_ref"]:
            unresolved_refs += 1

        if target and not action["target_part_ref"]:
            unresolved_refs += 1

        if fastener and not action["fastener_ref"]:
            unresolved_refs += 1

        if tool and not action["tool_ref"]:
            unresolved_refs += 1

    state["visible_parts"] = visible_parts
    state["visible_fasteners"] = visible_fasteners
    state["visible_tools"] = visible_tools
    state["observed_actions"] = observed_actions

    stats = {
        "unresolved_refs": unresolved_refs
    }

    return state, stats


def validate_page_state(state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    required_keys = [
        "page_number",
        "page_type",
        "visible_parts",
        "visible_fasteners",
        "visible_tools",
        "observed_actions",
        "final_visible_structure",
        "uncertainties",
    ]

    for key in required_keys:
        if key not in state:
            if key in [
                "visible_parts",
                "visible_fasteners",
                "visible_tools",
                "observed_actions",
                "uncertainties",
            ]:
                state[key] = []
            elif key == "final_visible_structure":
                state[key] = ""
            else:
                state[key] = "unknown"

    state["visible_parts"] = ensure_dict_list(state.get("visible_parts"))
    state["visible_fasteners"] = ensure_dict_list(state.get("visible_fasteners"))
    state["visible_tools"] = ensure_dict_list(state.get("visible_tools"))
    state["observed_actions"] = ensure_dict_list(state.get("observed_actions"))
    state["uncertainties"] = ensure_list(state.get("uncertainties"))

    # Downstream stages compare page_type with ==, so store the normalised value.
    page_type = norm(state.get("page_type")) or "unknown"
    state["page_type"] = page_type

    if page_type == "cover":
        state["visible_parts"] = []
        state["visible_fasteners"] = []
        state["visible_tools"] = []
        state["observed_actions"] = []

    if page_type == "warning":
        state["visible_parts"] = []
        state["visible_fasteners"] = []
        state["observed_actions"] = []

    if page_type == "parts_list":
        state["observed_actions"] = []

    state, stats = generate_stable_ids(state)

    if page_type == "assembly_step" and len(state.get("observed_actions", [])) == 0:
        state["uncertainties"].append(
            "Assembly step page has no observed_actions. Re-check page analysis."
        )

    if stats["unresolved_refs"] > 0:
        state["uncertainties"].append(
            f"{stats['unresolved_refs']} action reference(s) could not be resolved to visible objects on this page."
        )

    return state, stats


def validate_diagram_analysis(data: Dict[str, Any], page_number: int) -> Dict[str, Any]:
    """Fill defaults and stable diagram uids (D<page>_<n>) in one page's
    diagram analysis, as diagram_analysis.json stores it."""
    data.setdefault("page_number", page_number)
    data.setdefault("page_type", "unknown")
    data.setdefault("diagrams", [])
    data.setdefault("primary_assembly_diagram", "")
    data.setdefault("warnings", [])
    data.setdefault("uncertainties", [])

    validated_diagrams = []
    diagrams = data.get("diagrams")
    diagrams = [d for d in diagrams if isinstance(d, dict)] if isinstance(diagrams, list) else []

    for idx, diagram in enumerate(diagrams, start=1):
        diagram.setdefault("diagram_uid", "")
        diagram["diagram_uid"] = f"D{page_number:03d}_{idx:03d}"

        diagram.setdefault("diagram_type", "unknown")
        diagram.setdefault("description", "")
        diagram.setdefault("page_region", {
            "x_min": 0.0,
            "y_min": 0.0,
            "x_max": 1.0,
            "y_max": 1.0
        })

        region = diagram["page_region"]

        if not isinstance(region, dict):
            region = {}

        for key, default in [("x_min", 0.0), ("y_min", 0.0), ("x_max", 1.0), ("y_max", 1.0)]:
            try:
                region[key] = max(0.0, min(1.0, float(region.get(key, default))))
            except (TypeError, ValueError):
                region[key] = default

        diagram["page_region"] = region

        diagram.setdefault("contains_parts", False)
        diagram.setdefault("contains_fasteners", False)
        diagram.setdefault("contains_tools", False)
        diagram.setdefault("contains_arrows", False)
        diagram.setdefault("contains_labels", False)
        if not isinstance(diagram.get("visible_labels"), list):
            diagram["visible_labels"] = []
        diagram.setdefault("likely_action", "unknown")
        diagram.setdefault("visual_complexity", "medium")
        diagram.setdefault("confidence", 0.5)

        validated_diagrams.append(diagram)

    data["diagrams"] = validated_diagrams

    if not data["primary_assembly_diagram"]:
        for diagram in data["diagrams"]:
            if diagram.get("diagram_type") in ["assembly_view", "exploded_view"]:
                data["primary_assembly_diagram"] = diagram["diagram_uid"]
                break

    return data
