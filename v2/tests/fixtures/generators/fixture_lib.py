"""Helpers for hand-authoring vision fixtures (page_states.json and
diagram_analysis.json) in the exact schema the vision agents write.

The raw dicts are what a vision model would plausibly return for each page;
they go through the agents' own validators."""
import copy
import json
import sys
from pathlib import Path


def part(label, name, desc, shape, material, qty, features=(), pos="center"):
    return {
        "part_uid": "", "manual_label": label, "name": name,
        "visual_description": desc, "shape_family": shape,
        "material_hint": material, "quantity_visible": qty,
        "connection_features": [
            {"feature_type": f, "count": c, "location_hint": loc} for f, c, loc in features
        ],
        "page_position": pos,
    }


def fastener(label, name, shape, qty):
    return {"fastener_uid": "", "manual_label": label, "name": name,
            "shape_family": shape, "quantity_visible": qty}


def tool(name):
    return {"tool_uid": "", "name": name}


def action(kind, moving, target, fast, tool_ref, direction, evidence):
    return {"action_uid": "", "action_type": kind, "moving_part_ref": moving,
            "target_part_ref": target, "fastener_ref": fast, "tool_ref": tool_ref,
            "direction_hint": direction, "visual_evidence": evidence}


def page(n, ptype, parts=(), fasteners=(), tools=(), actions=(), final="", unc=()):
    return copy.deepcopy({"page_number": n, "page_type": ptype, "visible_parts": list(parts),
                          "visible_fasteners": list(fasteners), "visible_tools": list(tools),
                          "observed_actions": list(actions), "final_visible_structure": final,
                          "uncertainties": list(unc)})


def diagram(dtype, desc, region, labels=(), parts=True, fast=False, tools=False,
            arrows=False, action_="none", complexity="medium", conf=0.8):
    x0, y0, x1, y1 = region
    return {"diagram_uid": "", "diagram_type": dtype, "description": desc,
            "page_region": {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1},
            "contains_parts": parts, "contains_fasteners": fast, "contains_tools": tools,
            "contains_arrows": arrows, "contains_labels": bool(labels),
            "visible_labels": list(labels), "likely_action": action_,
            "visual_complexity": complexity, "confidence": conf}


def write_fixture(repo: Path, out: Path, pages, diagrams) -> None:
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "v2" / "agents"))
    from page_state_agent import validate_page_state
    from diagram_analyzer_agent import DiagramAnalyzerAgent

    out.mkdir(parents=True, exist_ok=True)
    states = [validate_page_state(p)[0] for p in pages]
    (out / "page_states.json").write_text(json.dumps(states, indent=2) + "\n", encoding="utf-8")

    validator = DiagramAnalyzerAgent.__new__(DiagramAnalyzerAgent)  # no Azure client needed
    analyses = []
    for n, (ptype, items, unc) in diagrams.items():
        data = {"page_number": n, "page_type": ptype, "diagrams": items,
                "primary_assembly_diagram": "", "warnings": [], "uncertainties": unc}
        analyses.append(validator.validate(data, n))
    (out / "diagram_analysis.json").write_text(json.dumps(analyses, indent=2) + "\n", encoding="utf-8")

    for s in states:
        print(s["page_number"], s["page_type"], len(s["visible_parts"]),
              len(s["observed_actions"]), s["uncertainties"][-1:])
