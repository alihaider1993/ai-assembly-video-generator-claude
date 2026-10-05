"""
Part Shape Extractor — v2

Fixes vs. the original version:
1. Parts are now keyed by canonical IDs (OBJ0001, FAST0001, ...) from
   universal_assembly_graph.json, instead of page/diagram IDs
   (e.g. "P_PAGE3_D003_001") that never matched anything downstream.
   This was the root cause of proxy geometry never being found by
   blender_builder_v3.py.
2. Shape family comes directly from the graph's already-correct
   "shape_family" field, instead of re-guessing from diagram description
   text (which was misclassifying wooden side rails as cylinders).
3. Hole counts come from the graph's structured "connection_features"
   (count field), instead of a broken "4x" in labels string check that
   never matched the real "x4" label format.
4. Real millimeter dimensions are parsed from diagram_analysis.json
   part-list descriptions (e.g. "(310 x 60mm)") and from fastener names
   (e.g. "M6x50mm Bolt"), instead of using fixed per-shape-type buckets.

Assembly nodes (ASM0001) are intentionally NOT given proxy geometry here;
blender_builder_v3.py already has a sensible built-in fallback box for
node_type == "assembly", and this stage has no reliable size data for
"the whole product" as a single shape.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    UNIVERSAL_GRAPH_JSON,
    DIAGRAM_ANALYSIS_JSON,
    DIAGRAM_ANALYSIS_COPY_JSON,
    PAGE_STATES_JSON,
    PART_SHAPES_JSON,
)


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def norm(value: Any) -> str:
    return str(value or "").strip().lower()


def to_int(value: Any, default: int = 1) -> int:
    """Parse counts that may arrive as 4, "4", "4x" or "x4"."""
    match = re.search(r"\d+", str(value or ""))
    return int(match.group()) if match else default


# ---------------------------------------------------------------------
# Real dimensions from the manual, instead of hardcoded buckets
# ---------------------------------------------------------------------

MM_PAIR_RE = re.compile(r"\((\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*mm\)", re.IGNORECASE)
FASTENER_M_RE = re.compile(r"m(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*mm", re.IGNORECASE)
FASTENER_LEN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mm", re.IGNORECASE)

# [diameter, diameter, length] in metres for small hardware with no size in
# its name, by shape family.
SMALL_FASTENER_SIZES = {
    "cam": [0.015, 0.015, 0.012],
    "plug": [0.008, 0.008, 0.025],
    "nail": [0.002, 0.002, 0.03],
    "other": [0.008, 0.008, 0.03],
    "unknown": [0.008, 0.008, 0.03],
}


def load_diagram_analysis() -> List[Dict[str, Any]]:
    """Prefer the authoritative outputs/json copy; fall back to the
    legacy v2/output/ mirror if that's the only one present."""
    if DIAGRAM_ANALYSIS_JSON.exists():
        return load_json(DIAGRAM_ANALYSIS_JSON)
    if DIAGRAM_ANALYSIS_COPY_JSON.exists():
        return load_json(DIAGRAM_ANALYSIS_COPY_JSON)
    return []


INSTANCE_SUFFIX_RE = re.compile(r"\s+\d+\s*/\s*\d+$")


def described_shapes() -> Dict[str, Dict[str, Any]]:
    """Part name -> the estimated size, lean and outline describe.py gave
    it (size_mm, tilt_deg, profile), from the copied page_states.json; the
    last page that gives a field wins."""
    if not PAGE_STATES_JSON.exists():
        return {}
    shapes: Dict[str, Dict[str, Any]] = {}
    for page in load_json(PAGE_STATES_JSON):
        for part in page.get("visible_parts", []):
            fields = {k: part[k] for k in ("size_mm", "tilt_deg", "profile") if part.get(k)}
            if fields:
                shapes.setdefault(norm(part.get("name", "")), {}).update(fields)
    return shapes


# For an outline traced in each view: the axes (of x, y, z) its two figures
# run along, and the axis it is extruded along.
PROFILE_AXES = {"side": (1, 2, 0), "front": (0, 2, 1), "top": (0, 1, 2)}


def profile_dimensions(profile: Dict[str, Any], dimensions: List[float]) -> List[float]:
    """[x, y, z] in metres of a traced outline: its extent (plus the strip
    thickness for an open path) in its view, and the part's own size
    along the axis it is extruded."""
    u_axis, v_axis, w_axis = PROFILE_AXES.get(profile.get("plane", "side"), PROFILE_AXES["side"])
    points = profile.get("path", [])
    pad = 0.0 if profile.get("closed") else float(profile.get("thickness", 30)) / 1000.0
    us = [p[0] / 1000.0 for p in points]
    vs = [p[1] / 1000.0 for p in points]
    out = [0.0, 0.0, 0.0]
    out[u_axis] = max(us) - min(us) + pad
    out[v_axis] = max(vs) - min(vs) + pad
    out[w_axis] = dimensions[w_axis]
    return out


def build_label_dimensions_mm(diagram_analysis: List[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
    """Map a manual numeric label (e.g. "1") to (dim1_mm, dim2_mm)
    parsed from part-list diagram descriptions like
    "Left/Right Side Rail (310 x 60mm) x4"."""
    label_dims: Dict[str, Tuple[float, float]] = {}

    for page in diagram_analysis:
        for diagram in page.get("diagrams", []):
            if not diagram.get("contains_parts"):
                continue

            description = diagram.get("description", "")
            match = MM_PAIR_RE.search(description)
            if not match:
                continue

            labels = diagram.get("visible_labels", [])
            numeric_label = next((l for l in labels if str(l).strip().isdigit()), None)
            if not numeric_label:
                continue

            label_dims[str(numeric_label).strip()] = (
                float(match.group(1)),
                float(match.group(2)),
            )

    return label_dims


def parse_fastener_dimensions_m(name: str) -> Tuple[float, float]:
    """Return (diameter_m, length_m) for a fastener, parsed from its name."""
    m = FASTENER_M_RE.search(name)
    if m:
        diameter_mm = float(m.group(1))
        length_mm = float(m.group(2))
        return diameter_mm / 1000.0, length_mm / 1000.0

    m2 = FASTENER_LEN_RE.search(name)
    length_mm = float(m2.group(1)) if m2 else 30.0

    name_l = name.lower()
    if "dowel" in name_l:
        diameter_mm = 8.0
    elif "screw" in name_l:
        diameter_mm = 4.0
    elif "washer" in name_l or "nut" in name_l:
        diameter_mm = 16.0
        length_mm = 3.0  # washers are effectively flat discs
    else:
        diameter_mm = 6.0

    return diameter_mm / 1000.0, length_mm / 1000.0


# ---------------------------------------------------------------------
# Shape family -> primitive the Blender builder actually understands
# (blender_builder_v3.py only special-cases "cylinder" and
# "rounded_box"/shape_type "rounded_panel"; everything else falls
# through to a plain box, so we target those three deliberately)
# ---------------------------------------------------------------------

def primitive_and_shape_type(shape_family: str, material_hint: str) -> Tuple[str, str]:
    shape = norm(shape_family)
    material = norm(material_hint)

    if shape in {"cylinder", "dowel", "bolt", "screw"}:
        return "cylinder", "cylinder"

    if shape in {"washer", "nut"}:
        return "cylinder", "washer"

    if shape == "panel" and material == "fabric":
        return "rounded_box", "rounded_panel"

    if shape in {"frame", "beam"}:
        return "box", "rectangular_beam"

    if shape == "panel":
        return "box", "thin_plate"

    if shape == "curved":
        return "box", "curved_frame"  # true curve primitive not yet supported by the renderer

    if shape == "bracket":
        return "box", "bracket"

    return "box", "proxy_block"


# Generic furniture vocabulary -> the part's role, which fixes how it sits in
# the finished piece, a plausible [x, y, z] size in meters (z is up) for
# when the manual gives no measurement, and how a measured pair of figures
# is turned (ROLE_ORIENTATION). The first match wins, so a "seat rail" is a
# rail, not a seat, and a "drawer front" is not a front panel.
PART_ROLES = [
    ("top", re.compile(r"\b(table ?top|top panels?|worktop|desktop|top boards?|top shelf)\b"), [1.2, 0.75, 0.025]),
    # A bed's corner posts, which the headboard/footboard rails run between.
    ("post", re.compile(r"\b(head|foot)board (foot|feet|posts?|legs?)\b"), [0.045, 0.045, 0.9]),
    # On chairs a "leg frame" is a wide U-shaped frame, not a post.
    ("leg_frame", re.compile(r"\blegs? frame\b"), [0.42, 0.04, 0.45]),
    # A chair side: front leg, tall back leg and the rails between them,
    # standing in the Y/Z plane (depth along Y).
    ("side_frame", re.compile(r"\bside frames?\b"), [0.04, 0.42, 0.95]),
    # Hardware named after what it is fitted to ("door hinge", "drawer
    # handle") is still hardware, so it is matched before doors and drawers.
    ("handle", re.compile(r"\b(handles?|knobs?|pulls?)\b"), [0.12, 0.025, 0.03]),
    ("hinge", re.compile(r"\bhinges?\b"), [0.035, 0.05, 0.012]),
    # Drawers: each drawer is a front, two sides, a back and a bottom.
    ("drawer_front", re.compile(r"\bdrawer fronts?\b"), [0.76, 0.018, 0.16]),
    ("drawer_side", re.compile(r"\bdrawer sides?\b"), [0.012, 0.4, 0.12]),
    ("drawer_back", re.compile(r"\bdrawer backs?\b"), [0.7, 0.012, 0.12]),
    ("drawer_bottom", re.compile(r"\bdrawer (bottom|base)s?\b"), [0.7, 0.4, 0.004]),
    ("runner", re.compile(r"\bdrawer (runners?|slides?)\b"), [0.4, 0.012, 0.035]),
    # Upholstery: cushions and the sofa or chair body they sit on.
    ("back_cushion", re.compile(r"\b(back cushions?|backrest cushions?|back pillows?)\b"), [0.8, 0.2, 0.45]),
    ("cushion", re.compile(r"\b(seat cushions?|cushions?|mattress(es)?)\b"), [0.8, 0.8, 0.12]),
    ("body", re.compile(r"\b(sofa|couch|settee|chaise|armchair|ottoman|footstool|pouffe?)\b"), [1.0, 0.9, 0.45]),
    # A bed's head or foot end as one board (not its rails or posts).
    ("end_board", re.compile(r"\b(head|foot)boards?\b(?!\s+(rails?|foot|feet|posts?|legs?))"), [0.95, 0.04, 0.9]),
    # Cabinet carcass panels.
    ("side_panel", re.compile(r"\b(side panels?|end panels?|gables?|side boards?)\b"), [0.018, 0.4, 0.8]),
    ("divider", re.compile(r"\b(dividers?|partitions?|middle panels?|cent(re|er) panels?|vertical panels?|mullions?)\b"),
     [0.018, 0.38, 0.7]),
    ("back_panel", re.compile(r"\b(back panels?|back boards?|backboards?|rear panels?|hardboard)\b"), [0.8, 0.005, 0.8]),
    ("front_panel", re.compile(r"\bfront panels?\b"), [0.9, 0.018, 0.4]),
    ("door", re.compile(r"\bdoors?\b"), [0.4, 0.018, 0.7]),
    ("lid", re.compile(r"\blids?\b"), [0.9, 0.45, 0.018]),
    ("plinth", re.compile(r"\b(plinths?|kick ?boards?|toe ?kicks?|base rails?|skirting)\b"), [0.76, 0.018, 0.08]),
    ("shelf", re.compile(r"\b(shelf|shelves|bottom panels?|base panels?|bottom boards?)\b"), [0.76, 0.38, 0.018]),
    ("leg", re.compile(r"\blegs?\b"), [0.05, 0.05, 0.72]),
    # Short feet under a sofa, cabinet or bed base.
    ("foot", re.compile(r"\b(foot|feet)\b"), [0.06, 0.06, 0.1]),
    ("back", re.compile(r"\b(chair back|backrest|back rest|seat back)\b"), [0.42, 0.04, 0.9]),
    ("slat", re.compile(r"\bslats?\b"), [0.9, 0.07, 0.018]),
    # Low bars between a table's legs (an H-frame), below the top rails.
    ("stretcher", re.compile(r"\bstretchers?\b"), [0.9, 0.03, 0.07]),
    ("rail", re.compile(r"\b(rails?|aprons?)\b"), [0.9, 0.03, 0.07]),
    ("seat", re.compile(r"\bseat\b"), [0.45, 0.42, 0.05]),
    ("bracket", re.compile(r"\bbrackets?\b"), [0.08, 0.08, 0.04]),
]

# How a measured (A x B mm) pair is turned, by role: "flat" lies down
# (larger along X, smaller along Y), "bar" stands up, "tall"/"wide" stand
# facing the front (XZ) or the side ("side_tall"/"side_wide", YZ) with the
# larger figure as height or width; "fixed" keeps the default (a bracket's
# figures don't say which faces they cover). Others are beams along X.
ROLE_ORIENTATION = {
    "top": "flat", "seat": "flat", "slat": "flat", "shelf": "flat", "lid": "flat", "cushion": "flat",
    "drawer_bottom": "flat", "body": "flat",
    "leg": "bar", "post": "bar", "foot": "bar",
    "leg_frame": "tall", "back": "tall", "door": "tall", "back_panel": "tall",
    "drawer_front": "wide", "drawer_back": "wide", "front_panel": "wide", "end_board": "wide", "back_cushion": "wide",
    "side_frame": "side_tall", "side_panel": "side_tall", "divider": "side_tall",
    "drawer_side": "side_wide",
    "bracket": "fixed", "handle": "fixed", "hinge": "fixed",
}

# Roles whose part is several pieces joined together; blender_builder_v3.py
# builds these primitives from boxes. Upholstery gets rounded corners.
ROLE_PRIMITIVES = {"leg_frame": "u_frame", "back": "slatted_back", "side_frame": "side_frame",
                   "cushion": "rounded_box", "back_cushion": "rounded_box", "body": "rounded_box"}


def part_role(name: str) -> str:
    name_n = norm(name)
    for role, pattern, _ in PART_ROLES:
        if pattern.search(name_n):
            return role
    return ""


def role_dimensions(role: str, dims_mm: Optional[Tuple[float, float]]) -> List[float]:
    """[x, y, z] in meters for a part with a known role: the default, or a
    measured pair turned the way the role sits (ROLE_ORIENTATION), with
    the default for the third side."""
    default = next(dims for r, _, dims in PART_ROLES if r == role)
    orientation = ROLE_ORIENTATION.get(role, "beam")
    if not dims_mm or orientation == "fixed":
        return list(default)

    larger = max(dims_mm) / 1000.0
    smaller = min(dims_mm) / 1000.0
    return {
        "flat": [larger, smaller, default[2]],
        "bar": [smaller, smaller, larger],
        "tall": [smaller, default[1], larger],
        "wide": [larger, default[1], smaller],
        "side_tall": [default[0], smaller, larger],
        "side_wide": [default[0], larger, smaller],
    }.get(orientation, [larger, default[1], smaller])


DEFAULT_THICKNESS_M = {
    "thin_plate": 0.018,     # side-rail-style flat panel, typical board thickness
    "rectangular_beam": 0.09,
    "curved_frame": 0.09,
    "bracket": 0.05,
    "rounded_panel": 0.06,
    "proxy_block": 0.08,
}


def dimensions_for_part(
    shape_family: str,
    material_hint: str,
    dims_mm: Optional[Tuple[float, float]],
) -> List[float]:
    """
    Returns [x, y, z] in meters. Axis assignment is a heuristic:
    manuals mix side-view, front-view, and top-view dimension pairs
    with no explicit axis labels, so this maps the larger figure to
    "height" for upright parts (frames/curved/panels) and to "width"
    for flat parts (fabric panels), and uses a shape-based default
    thickness for the un-stated third axis. This is a proxy, not a
    CAD-accurate reconstruction — flagged as a known limitation.
    """
    _, shape_type = primitive_and_shape_type(shape_family, material_hint)
    thickness = DEFAULT_THICKNESS_M.get(shape_type, 0.08)

    if not dims_mm:
        # No manual measurement found — reasonable generic fallback per type
        fallback = {
            "thin_plate": [0.31, thickness, 0.06],
            "rectangular_beam": [0.42, thickness, 0.43],
            "curved_frame": [0.40, thickness, 0.90],
            "bracket": [0.05, 0.03, 0.04],
            "rounded_panel": [0.45, thickness, 0.36],
            "cylinder": [0.02, 0.02, 0.10],
            "washer": [0.02, 0.02, 0.004],
            "proxy_block": [0.5, thickness, 0.3],
        }
        return fallback.get(shape_type, [0.5, thickness, 0.3])

    a_m, b_m = dims_mm[0] / 1000.0, dims_mm[1] / 1000.0
    larger, smaller = max(a_m, b_m), min(a_m, b_m)

    if shape_type == "rounded_panel":
        # Flat cushion/seat: larger figure is width, smaller is depth
        return [larger, thickness, smaller]

    # Upright structural parts: larger figure is height
    return [smaller, thickness, larger]


# Four holes described as being at the corners sit just in from each corner.
CORNER_HOLE_POSITIONS = [(0.06, 0.08), (0.94, 0.08), (0.06, 0.92), (0.94, 0.92)]


def edge_position(i: int, count: int) -> List[float]:
    """i-th of `count` points spread evenly around the corner-hole inset
    rectangle, so a top's holes follow its edges where the frame sits."""
    (x0, y0), (x1, y1) = CORNER_HOLE_POSITIONS[0], CORNER_HOLE_POSITIONS[3]
    w, h = x1 - x0, y1 - y0
    d = (i + 0.5) / count * 2 * (w + h)
    if d < w:
        return [round(x0 + d, 4), y0]
    d -= w
    if d < h:
        return [x1, round(y0 + d, 4)]
    d -= h
    if d < w:
        return [round(x1 - d, 4), y1]
    return [x0, round(y1 - (d - w), 4)]


def build_holes_from_features(
    connection_features: List[Dict[str, Any]],
    around_edge: bool = False,
) -> List[Dict[str, Any]]:
    """Use the graph's already-correct structured hole/slot counts,
    instead of re-deriving (incorrectly) from label text."""
    holes = []
    hole_index = 1

    for feature in connection_features or []:
        if not isinstance(feature, dict) or norm(feature.get("feature_type")) != "hole":
            continue

        count = to_int(feature.get("count"))
        at_corners = count == 4 and "corner" in norm(feature.get("location_hint"))

        for i in range(count):
            if at_corners:
                position = [CORNER_HOLE_POSITIONS[i][0], CORNER_HOLE_POSITIONS[i][1]]
            elif around_edge:
                position = edge_position(i, count)
            else:
                # Spread evenly along the part so positions stay inside 0..1
                # for any count (the old 2-column grid overflowed past 4 holes).
                position = [round((i + 0.5) / count, 4), 0.5]
            holes.append({
                "hole_uid": f"H{hole_index}",
                "type": "round",
                "relative_position": position,
                "radius_hint": 0.006,
                "location_hint": feature.get("location_hint", ""),
            })
            hole_index += 1

    return holes


def aspect_ratio(dimensions: List[float]) -> float:
    """Longest side over shortest side of the proxy box."""
    shortest = min(dimensions)
    return round(max(dimensions) / shortest, 3) if shortest > 0 else 1.0


# ---------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------

def extract_part_shapes():
    graph = load_json(UNIVERSAL_GRAPH_JSON)
    diagram_analysis = load_diagram_analysis()

    label_dims_mm = build_label_dimensions_mm(diagram_analysis)

    part_shapes = {
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "universal_assembly_graph.json + diagram_analysis.json",
            "note": "Canonical-ID-keyed proxy shape extraction for MVP rendering",
        },
        "parts": [],
    }

    # --- Real parts (OBJ*) ---
    described_by_name = described_shapes()
    for part in graph.get("parts", []):
        part_uid = part.get("part_uid")
        if not part_uid:
            continue

        shape_family = part.get("shape_family", "unknown")
        material_hint = part.get("material_hint", "unknown")

        manual_label = ""
        labels = part.get("manual_labels", [])
        if labels:
            manual_label = str(labels[0]).strip()

        dims_mm = label_dims_mm.get(manual_label)
        primitive, shape_type = primitive_and_shape_type(shape_family, material_hint)
        role = part_role(part.get("base_name") or part.get("canonical_name", ""))
        primitive = ROLE_PRIMITIVES.get(role, primitive)
        if role:
            dimensions = role_dimensions(role, dims_mm)
        else:
            dimensions = dimensions_for_part(shape_family, material_hint, dims_mm)

        if dims_mm:
            dims_source = "manual_measurement"
        elif role:
            dims_source = "name_hint_default"
        else:
            dims_source = "fallback_default"

        # Estimated size and outline from describe.py, when it gave them.
        described = described_by_name.get(norm(INSTANCE_SUFFIX_RE.sub("", part.get("canonical_name", "")))) or {}
        profile = described.get("profile")
        if described.get("size_mm"):
            dimensions = [v / 1000.0 for v in described["size_mm"]]
            if not dims_mm:
                dims_source = "estimated"
        if profile:
            dimensions = profile_dimensions(profile, dimensions)
            primitive = "profile"

        part_shapes["parts"].append({
            "part_uid": part_uid,  # canonical: OBJ0001, etc.
            "canonical_name": part.get("canonical_name", part_uid),
            "shape_family": shape_family,
            "material_hint": material_hint,
            "shape_type": shape_type,
            "primitive": primitive,
            "role": role,
            "dimensions": dimensions,
            "dims_source": dims_source,
            "aspect_ratio": aspect_ratio(dimensions),
            "source_page": part.get("first_seen_page"),
            "source_diagram_uid": "",
            "has_rounded_corners": shape_type == "rounded_panel",
            "holes": build_holes_from_features(part.get("connection_features", []), around_edge=role == "top"),
            "anchor_points": [
                {"anchor_uid": "A_TOP", "relative_position": [0.5, 0.0]},
                {"anchor_uid": "A_CENTER", "relative_position": [0.5, 0.5]},
                {"anchor_uid": "A_BOTTOM", "relative_position": [0.5, 1.0]},
            ],
            "labels": labels,
            "tilt_deg": described.get("tilt_deg", 0.0),
            "profile": profile,
            "confidence": part.get("confidence", 0.7),
        })

    # --- Fasteners (FAST*) ---
    for fastener in graph.get("fasteners", []):
        fastener_uid = fastener.get("fastener_uid")
        if not fastener_uid:
            continue

        name = fastener.get("name", "")
        shape_family = fastener.get("shape_family", "cylinder")

        if shape_family in {"irregular"}:
            # e.g. Allen key — small tool, not a fastener geometry
            dimensions = [0.01, 0.01, 0.15]
            primitive, shape_type = "cylinder", "cylinder"
            dims_source = "fallback_default"
        elif shape_family in SMALL_FASTENER_SIZES:
            # Cam locks, plugs, nails and other small hardware: a few
            # centimetres at most, never a furniture part's default size.
            diameter_m, length_m = parse_fastener_dimensions_m(name) if FASTENER_LEN_RE.search(name) else (0.0, 0.0)
            default = SMALL_FASTENER_SIZES[shape_family]
            dimensions = [diameter_m or default[0], diameter_m or default[1], length_m or default[2]]
            primitive, shape_type = "cylinder", "cylinder"
            dims_source = "parsed_from_name" if length_m else "fallback_default"
        else:
            primitive, shape_type = primitive_and_shape_type(shape_family, "metal")

            if primitive == "cylinder":
                diameter_m, length_m = parse_fastener_dimensions_m(name)
                dimensions = [diameter_m, diameter_m, length_m]
                dims_source = "parsed_from_name"
            elif FASTENER_LEN_RE.search(name):
                # e.g. a "70mm spacer": a small block that long.
                length_m = float(FASTENER_LEN_RE.search(name).group(1)) / 1000.0
                dimensions = [0.02, 0.02, length_m]
                dims_source = "parsed_from_name"
            else:
                # e.g. a bracket listed with the hardware: a thin rod is wrong.
                dimensions = dimensions_for_part(shape_family, "metal", None)
                dims_source = "fallback_default"

        part_shapes["parts"].append({
            "part_uid": fastener_uid,  # canonical: FAST0001, etc.
            "canonical_name": name,
            "shape_family": shape_family,
            "material_hint": "metal",
            "shape_type": shape_type,
            "primitive": primitive,
            "dimensions": dimensions,
            "dims_source": dims_source,
            "aspect_ratio": aspect_ratio(dimensions),
            "source_page": fastener.get("first_seen_page"),
            "source_diagram_uid": "",
            "has_rounded_corners": False,
            "holes": [],
            "anchor_points": [],
            "labels": fastener.get("manual_labels", []),
            "confidence": 0.8,
        })

    PART_SHAPES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(PART_SHAPES_JSON, "w", encoding="utf-8") as f:
        json.dump(part_shapes, f, indent=2)

    if not part_shapes["parts"]:
        print(
            f"[FATAL] No parts or fasteners in {UNIVERSAL_GRAPH_JSON}; "
            "nothing to build shapes for. Check the earlier stages' output.",
            file=sys.stderr,
        )
        sys.exit(2)

    print("[SUCCESS] Part Shape Extractor complete")
    print(f"Parts extracted: {len(part_shapes['parts'])}")
    print(f"Output: {PART_SHAPES_JSON}")


if __name__ == "__main__":
    extract_part_shapes()