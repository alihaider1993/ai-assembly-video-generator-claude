import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

GRAPH_PATH = Path("v2/outputs/json/universal_assembly_graph.json")
MOTION_PATH = Path("v2/outputs/json/motion_plan.json")
GEOMETRY_PATH = Path("v2/outputs/json/geometry_spec.json")
# Written by part_shape_extractor_agent.py, which runs before this stage.
# Optional: without it the generic ring layout is used.
PART_SHAPES_PATH = Path("v2/output/part_shapes.json")
OUTPUT_PATH = Path("v2/outputs/json/scene_layout.json")


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_node_lookup(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    nodes = {}

    for part in graph.get("parts", []):
        uid = part.get("part_uid")
        if uid:
            item = dict(part)
            item["node_uid"] = uid
            item["node_type"] = "part"
            nodes[uid] = item

    for asm in graph.get("assemblies", []):
        uid = asm.get("assembly_uid")
        if uid:
            item = dict(asm)
            item["node_uid"] = uid
            item["node_type"] = "assembly"
            nodes[uid] = item

    for fastener in graph.get("fasteners", []):
        uid = fastener.get("fastener_uid")
        if uid:
            item = dict(fastener)
            item["node_uid"] = uid
            item["node_type"] = "fastener"
            item["canonical_name"] = fastener.get("name", uid)
            nodes[uid] = item

    return nodes


def geometry_lookup(geometry: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        obj["part_ref"]: obj
        for obj in geometry.get("objects", [])
        if obj.get("part_ref")
    }


def bounding_box_of(geom: Dict[str, Any]) -> Tuple[float, float, float]:
    """(width, depth, height) in meters, with a sane default for anything
    with no geometry entry (e.g. tools, or a node geometry_synthesizer
    didn't cover)."""
    if not geom:
        return (0.3, 0.1, 0.3)
    bb = geom.get("bounding_box", {})
    return (
        bb.get("width", 0.3),
        bb.get("depth", 0.1),
        bb.get("height", 0.3),
    )


def build_parent_map(graph: Dict[str, Any]) -> Dict[str, str]:
    """child_uid -> parent_uid, derived from real connections.

    In every connection, to_node_ref is the attachment TARGET (the thing
    that stays put) and from_node_ref plus any fasteners are the pieces
    that move to attach onto it. So for layout purposes, to_node_ref is
    the parent every other referenced node should be positioned near.

    The FIRST connection wins: that is the step in which motion_planner.py
    moves the node, so the node lands next to a parent that is already in
    place. (Later connections, e.g. a bracket also hooking a short rail,
    would point at a part that may still be in its exploded position.)
    """
    parent: Dict[str, str] = {}

    for conn in graph.get("connections", []):
        from_ref = conn.get("from_node_ref", "")
        to_ref = conn.get("to_node_ref", "")

        if from_ref and to_ref and from_ref != to_ref:
            parent.setdefault(from_ref, to_ref)

        for fastener in conn.get("fasteners", []):
            if fastener and to_ref and fastener != to_ref:
                parent.setdefault(fastener, to_ref)

    return parent


def build_kind_map(graph: Dict[str, Any]) -> Dict[str, str]:
    """node_uid -> kind, so instances of one part (4 legs, 2 rails) can be
    laid out as a symmetric group. Nodes without a kind are their own."""
    kinds: Dict[str, str] = {}

    for part in graph.get("parts", []):
        uid = part.get("part_uid")
        if uid:
            keys = part.get("identity_keys") or [part.get("base_name") or uid]
            kinds[uid] = keys[0]

    return kinds


# Clearance between a part and its parent, and the extra distance between
# successive rings when one parent has several kinds of children.
ATTACH_GAP = 0.12
RING_STEP = 0.3
# How far beyond its final position a moving part starts (and how high).
EXPLODE_DISTANCE = 1.6
EXPLODE_LIFT = 1.0


def footprint_half(geom: Dict[str, Any]) -> float:
    width, depth, _ = bounding_box_of(geom)
    return max(width, depth) / 2


def sibling_angles(count: int, ring_index: int, outward: float) -> List[float]:
    """Angles (radians) for `count` same-kind siblings around a parent:
    one goes outward, two sit on opposite sides, three or more spread
    evenly starting at a corner (so four legs land on four corners).
    Rings alternate axis so two pairs of different kinds don't collide."""
    if count == 1:
        return [outward + ring_index * math.pi / 2]

    if count == 2:
        base = outward if ring_index % 2 == 0 else outward + math.pi / 2
        return [base, base + math.pi]

    return [outward + math.pi / 4 + i * 2 * math.pi / count for i in range(count)]


def build_children_map(parent_map: Dict[str, str]) -> Dict[str, List[str]]:
    children_of: Dict[str, List[str]] = {}
    for child, par in parent_map.items():
        children_of.setdefault(par, []).append(child)
    return children_of


def find_components(parent_map: Dict[str, str]) -> List[set]:
    """Undirected connected components over the parent/child edges —
    doesn't assume everything reaches ASM0001, since a manual's
    connections can be entirely part-to-part rather than part-to-assembly."""
    adjacency: Dict[str, set] = {}
    for child, par in parent_map.items():
        adjacency.setdefault(child, set()).add(par)
        adjacency.setdefault(par, set()).add(child)

    seen: set = set()
    components: List[set] = []

    for node in adjacency:
        if node in seen:
            continue
        component = set()
        stack = [node]
        while stack:
            cur = stack.pop()
            if cur in component:
                continue
            component.add(cur)
            stack.extend(adjacency.get(cur, set()) - component)
        seen |= component
        components.append(component)

    return components


def choose_root(component: set, parent_map: Dict[str, str], primary_assembly: str) -> str:
    if primary_assembly in component:
        return primary_assembly
    # Prefer a node that attaches to nothing (the base part, e.g. the
    # tabletop); among those, the one most attached-to. A root that has a
    # parent would be pinned in place even though it should move.
    counts: Dict[str, int] = {}
    for child, par in parent_map.items():
        if par in component:
            counts[par] = counts.get(par, 0) + 1
    parentless = [uid for uid in counts if uid not in parent_map]
    if parentless:
        return max(parentless, key=counts.get)
    if counts:
        return max(counts, key=counts.get)
    return sorted(component)[0]


def compute_connected_positions(
    parent_map: Dict[str, str],
    geom_by_part: Dict[str, Dict[str, Any]],
    primary_assembly: str,
    kind_of: Dict[str, str],
) -> Tuple[Dict[str, List[float]], Dict[str, List[float]]]:
    """BFS out from a root in each connected component of the real
    attachment graph. Each parent's children are grouped by kind; each
    kind gets its own ring around the parent (sized from both parts'
    footprints) and its instances are spread symmetrically on it. Parts
    below the root are pushed outward, away from the root, so a part's
    children don't land on top of the root. Exploded positions continue
    outward and upward from the final position."""
    final_pos: Dict[str, List[float]] = {}
    exploded_pos: Dict[str, List[float]] = {}
    outward_of: Dict[str, float] = {}

    children_of = build_children_map(parent_map)
    components = find_components(parent_map)

    for comp_index, component in enumerate(components):
        root_uid = choose_root(component, parent_map, primary_assembly)
        # Space separate components (e.g. a branch that never links back
        # to the primary assembly) apart from each other.
        root_base = [comp_index * 4.0, 0.0, 1.0]
        final_pos[root_uid] = list(root_base)
        exploded_pos[root_uid] = list(root_base)
        outward_of[root_uid] = 0.0

        visited = {root_uid}
        queue = [root_uid]

        while queue:
            current = queue.pop(0)
            parent_final = final_pos[current]
            parent_half = footprint_half(geom_by_part.get(current, {}))

            groups: Dict[str, List[str]] = {}
            for child in children_of.get(current, []):
                if child in component and child not in visited:
                    groups.setdefault(kind_of.get(child, child), []).append(child)

            for ring_index, members in enumerate(groups.values()):
                child_half = footprint_half(geom_by_part.get(members[0], {}))
                radius = parent_half + child_half + ATTACH_GAP + ring_index * RING_STEP
                angles = sibling_angles(len(members), ring_index, outward_of[current])

                for child, angle in zip(members, angles):
                    visited.add(child)
                    dx, dy = math.cos(angle), math.sin(angle)

                    final_pos[child] = [
                        parent_final[0] + dx * radius,
                        parent_final[1] + dy * radius,
                        parent_final[2] + 0.1 * (ring_index + 1),
                    ]
                    exploded_pos[child] = [
                        final_pos[child][0] + dx * EXPLODE_DISTANCE,
                        final_pos[child][1] + dy * EXPLODE_DISTANCE,
                        final_pos[child][2] + EXPLODE_LIFT,
                    ]
                    outward_of[child] = angle
                    queue.append(child)

    return final_pos, exploded_pos


# Table layout: how far legs sit in from the top's edge, and where moving
# parts start relative to their final position (outward, then up).
LEG_INSET = 0.04
TABLE_EXPLODE_DISTANCE = 0.45
TABLE_EXPLODE_LIFT = 0.3
# Fasteners sit just under the top, nudged in from their host part so they
# aren't buried inside it; several at one host are spread sideways.
FASTENER_INSET = 0.05
FASTENER_SPREAD = 0.04
# A table's stretchers sit at this fraction of the leg height.
STRETCHER_HEIGHT = 0.3
# Inner frame rails are at most this share of half the frame's length.
INNER_RAIL_FIT = 0.8


def classify_rails(rails: List[str], shapes: Dict[str, Dict[str, Any]]) -> Tuple[List[str], List[str], List[str], List[str]]:
    """(side, end, cross, inner) rails of a table frame, by name: "long" or
    "side" rails run along the long edges, "end" or "short" rails along the
    short ones, "cross" rails across the inside, and other named rails
    (guides, runners) lengthways inside. When no rail is named that way,
    the two longest are the sides and the rest the ends."""
    by_length = sorted(rails, key=lambda uid: (-shapes[uid]["dimensions"][0], uid))

    def having(*words: str) -> List[str]:
        return [uid for uid in by_length if any(w in base_name(shapes[uid]).split() for w in words)]

    sides, ends, crosses = having("long", "side"), having("end", "short"), having("cross")
    named = set(sides) | set(ends) | set(crosses)
    if not named:
        return by_length[:2], by_length[2:], [], []
    return sides, [u for u in ends if u not in sides], [u for u in crosses if u not in sides + ends], [u for u in by_length if u not in named]


def load_part_shapes(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    data = load_json(path)
    return {p["part_uid"]: p for p in data.get("parts", []) if p.get("part_uid")}


def fastener_host_pairs(graph: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Every distinct (fastener_uid, host part) pair: the host is the part
    the fastener comes with in a connection (its from_node_ref). One
    fastener type used at four legs gives four pairs, i.e. four instances."""
    pairs: List[Tuple[str, str]] = []
    for conn in graph.get("connections", []):
        from_ref = conn.get("from_node_ref", "")
        for fastener in conn.get("fasteners", []):
            pair = (fastener, from_ref)
            if fastener and from_ref and fastener != from_ref and pair not in pairs:
                pairs.append(pair)
    return pairs


def outward_start(final: List[float], center: List[float]) -> List[float]:
    dx, dy = final[0] - center[0], final[1] - center[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        dx, dy, length = 1.0, 0.0, 1.0
    return [
        final[0] + dx / length * TABLE_EXPLODE_DISTANCE,
        final[1] + dy / length * TABLE_EXPLODE_DISTANCE,
        final[2] + TABLE_EXPLODE_LIFT,
    ]


def compute_table_positions(
    shapes: Dict[str, Dict[str, Any]],
    graph: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Lay out a top + legs (+ rails, brackets, fasteners) the way flat-pack
    tables are built: upside down, with the top lying face-down on the
    floor, to be turned over at the end. Legs stand at the top's corners,
    rails run along its edges between the legs, brackets sit inside the
    corners, and each fastener appears once per part it is used with.

    Positions are worked out for the upright table, then flipped 180
    degrees about the X axis through `pivot`; turning the assembly over
    by the same rotation about `pivot` gives back the upright table.

    Returns None when the parts don't form a table (no "top" or no "leg"
    role), so the generic layout is used. Otherwise a dict of per-node
    final/exploded/rotation/scale, instance_of (instance -> fastener uid)
    and the pivot."""
    by_role: Dict[str, List[str]] = {}
    for uid, shape in sorted(shapes.items()):
        if shape.get("role"):
            by_role.setdefault(shape["role"], []).append(uid)

    if not by_role.get("top") or not by_role.get("leg"):
        return None

    top_uid = by_role["top"][0]
    top_w, top_d, top_t = shapes[top_uid]["dimensions"]
    leg_h = max(shapes[uid]["dimensions"][2] for uid in by_role["leg"])
    leg_half = max(shapes[by_role["leg"][0]]["dimensions"][:2]) / 2
    leg_w = 2 * leg_half

    corner_x = top_w / 2 - LEG_INSET - leg_half
    corner_y = top_d / 2 - LEG_INSET - leg_half

    final = {top_uid: [0.0, 0.0, leg_h + top_t / 2]}
    rotation = {top_uid: [0.0, 0.0, 0.0]}
    scale: Dict[str, List[float]] = {}
    instance_of: Dict[str, str] = {}

    corners = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for i, uid in enumerate(by_role["leg"]):
        sx, sy = corners[i % 4]
        final[uid] = [sx * corner_x, sy * corner_y, leg_h / 2]
        rotation[uid] = [0.0, 0.0, 0.0]

    # Rails are stretched to fit between the legs. Side rails run along X
    # (the top's long side) and end rails along Y, each alternating between
    # opposite edges; cross rails span the frame along Y, evenly spaced
    # inside it; any other rails (guides, runners) lie along X inside the
    # frame. Names say which is which; without such names the two longest
    # rails are the sides and the rest the ends.
    span = {"x": 2 * corner_x - leg_w, "y": 2 * corner_y - leg_w}
    sides, ends, crosses, inner = classify_rails(by_role.get("rail", []), shapes)

    def place_rail(uid: str, x: float, y: float, axis: str, length: float = 0.0) -> None:
        rail_length, _, height = shapes[uid]["dimensions"]
        final[uid] = [x, y, leg_h - height / 2]
        rotation[uid] = [0.0, 0.0, 0.0 if axis == "x" else 90.0]
        if length:
            scale[uid] = [length / rail_length, 1.0, 1.0]

    for i, uid in enumerate(sides):
        place_rail(uid, 0.0, (1 if i % 2 == 0 else -1) * corner_y, "x", span["x"])
    for i, uid in enumerate(ends):
        place_rail(uid, (1 if i % 2 == 0 else -1) * corner_x, 0.0, "y", span["y"])
    for i, uid in enumerate(crosses):
        place_rail(uid, corner_x * (-1 + 2 * (i + 1) / (len(crosses) + 1)), 0.0, "y", span["y"])
    # Inner pieces: two columns, one in each half of the frame, rows spread
    # across Y; shortened if they wouldn't fit in their half.
    rows = max((len(inner) + 1) // 2, 1)
    for i, uid in enumerate(inner):
        row_y = corner_y * 0.6 * (-1 + 2 * (i // 2 + 0.5) / rows)
        fit = min(shapes[uid]["dimensions"][0], corner_x * INNER_RAIL_FIT)
        place_rail(uid, (1 if i % 2 == 0 else -1) * corner_x / 2, row_y, "x", fit)

    # Stretchers make a low H-frame: the shorter ones across each end
    # between the legs, the longest one down the middle between them.
    stretchers = sorted(by_role.get("stretcher", []), key=lambda uid: (-shapes[uid]["dimensions"][0], uid))
    long_stretchers = [uid for uid in stretchers if any(w in base_name(shapes[uid]) for w in ("long", "middle", "centre", "center"))]
    if not long_stretchers and len(stretchers) > 2:
        long_stretchers = stretchers[:1]
    stretcher_z = leg_h * STRETCHER_HEIGHT
    end_stretchers = [uid for uid in stretchers if uid not in long_stretchers]
    for i, uid in enumerate(end_stretchers):
        length, thickness, _ = shapes[uid]["dimensions"]
        final[uid] = [(1 if i % 2 == 0 else -1) * corner_x, 0.0, stretcher_z]
        rotation[uid] = [0.0, 0.0, 90.0]
        scale[uid] = [span["y"] / length, 1.0, 1.0]
    for uid in long_stretchers:
        length, thickness, _ = shapes[uid]["dimensions"]
        final[uid] = [0.0, 0.0, stretcher_z]
        rotation[uid] = [0.0, 0.0, 0.0]
        scale[uid] = [(2 * corner_x - thickness) / length, 1.0, 1.0]

    for i, uid in enumerate(by_role.get("bracket", [])):
        sx, sy = corners[i % 4]
        height = shapes[uid]["dimensions"][2]
        final[uid] = [sx * (corner_x - leg_w), sy * (corner_y - leg_w), leg_h - height / 2]
        rotation[uid] = [0.0, 0.0, 45.0 + 90.0 * (i % 4)]

    # One instance of a fastener per placed host part, nudged toward the
    # middle of the table and spread sideways when a host has several.
    # A fastener with no placed host keeps its own uid at a leg corner.
    per_host: Dict[str, int] = {}
    instance_count: Dict[str, int] = {}
    for fastener, host in fastener_host_pairs(graph):
        if host not in final or host == top_uid:
            continue
        hx, hy, _ = final[host]
        length = math.hypot(hx, hy) or 1.0
        ix, iy = -hx / length, -hy / length
        k = per_host.get(host, 0)
        per_host[host] = k + 1
        # 0, +1, -1, +2, -2 ... spacings either side of the host.
        offset = (k + 1) // 2 * FASTENER_SPREAD * (1 if k % 2 else -1)
        instance_count[fastener] = instance_count.get(fastener, 0) + 1
        uid = f"{fastener}_{instance_count[fastener]}"
        instance_of[uid] = fastener
        final[uid] = [
            hx + ix * FASTENER_INSET - iy * offset,
            hy + iy * FASTENER_INSET + ix * offset,
            leg_h - 0.03,
        ]
        rotation[uid] = [0.0, 0.0, 0.0]

    fastener_uids = [f.get("fastener_uid") for f in graph.get("fasteners", []) if f.get("fastener_uid")]
    for i, fastener in enumerate(f for f in fastener_uids if f not in instance_count):
        sx, sy = corners[i % 4]
        final[fastener] = [sx * corner_x, sy * corner_y, leg_h - 0.03]
        rotation[fastener] = [0.0, 0.0, 0.0]

    # Flip upside down: 180 degrees about X through the pivot maps
    # (x, y, z) to (x, -y, 2*pivot_z - z) and an object's Z rotation r to
    # an XYZ Euler of (180, 0, -r).
    height = leg_h + top_t
    pivot = [0.0, 0.0, height / 2]
    final = {uid: [x, -y, height - z] for uid, (x, y, z) in final.items()}
    rotation = {uid: [rx + 180.0, ry, -rz] for uid, (rx, ry, rz) in rotation.items()}

    center = [0.0, 0.0, top_t / 2]
    exploded = {
        uid: list(pos) if uid == top_uid else outward_start(pos, center)
        for uid, pos in final.items()
    }
    return {
        "final": final,
        "exploded": exploded,
        "rotation": rotation,
        "scale": scale,
        "instance_of": instance_of,
        "pivot": pivot,
    }


# Chairs and beds are built standing the way they end up, so there is no
# finale. Moving parts start outward and up from the middle by these
# fractions of the piece's longest side.
EXPLODE_FRACTION = 0.3
EXPLODE_LIFT_FRACTION = 0.25
# A slatted bed base sits this far below the top of its side rails.
SLAT_DROP = 0.03


def parts_by_role(shapes: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    by_role: Dict[str, List[str]] = {}
    for uid, shape in sorted(shapes.items()):
        if shape.get("role"):
            by_role.setdefault(shape["role"], []).append(uid)
    return by_role


def world_half_extents(dims: List[float], rotation: List[float], scale: List[float]) -> List[float]:
    """Half size along world X/Y/Z of a box turned a whole number of quarter
    turns about Z (the only turns the chair and bed layouts use)."""
    x, y, z = (d * s / 2 for d, s in zip(dims, scale))
    if round(rotation[2] / 90.0) % 2:
        x, y = y, x
    return [x, y, z]


def place_fastener_instances(
    shapes: Dict[str, Dict[str, Any]],
    graph: Dict[str, Any],
    final: Dict[str, List[float]],
    rotation: Dict[str, List[float]],
    scale: Dict[str, List[float]],
) -> Dict[str, str]:
    """One instance of a fastener per part it is used with (its host), at
    the point of the host nearest the part the host is joined to, or
    nearest the middle of the piece when the connection names no other
    part (a dowel pushed into a rail). Several at one host are spread
    along it. Adds the instances to final/rotation and returns instance
    uid -> fastener uid."""
    middle = [sum(p[i] for p in final.values()) / len(final) for i in range(3)]
    instance_of: Dict[str, str] = {}
    instance_count: Dict[str, int] = {}
    per_host: Dict[str, int] = {}
    hosted = set()

    for conn in graph.get("connections", []):
        from_ref, to_ref = conn.get("from_node_ref", ""), conn.get("to_node_ref", "")
        for fastener in conn.get("fasteners", []):
            host, other = (to_ref, "") if from_ref == fastener else (from_ref, to_ref)
            if (fastener, host) in hosted or host not in final or host not in shapes:
                continue
            hosted.add((fastener, host))

            center = final[host]
            half = world_half_extents(
                shapes[host]["dimensions"], rotation.get(host, [0.0, 0.0, 0.0]), scale.get(host, [1.0, 1.0, 1.0])
            )
            toward = final.get(other, middle)
            point = [min(max(t, c - h), c + h) for c, h, t in zip(center, half, toward)]

            # 0, +1, -1, +2, -2 ... spacings along the host's longer side.
            k = per_host.get(host, 0)
            per_host[host] = k + 1
            offset = (k + 1) // 2 * FASTENER_SPREAD * (1 if k % 2 else -1)
            axis = 0 if half[0] >= half[1] else 1
            point[axis] = min(max(point[axis] + offset, center[axis] - half[axis]), center[axis] + half[axis])

            instance_count[fastener] = instance_count.get(fastener, 0) + 1
            uid = f"{fastener}_{instance_count[fastener]}"
            instance_of[uid] = fastener
            final[uid] = point
            rotation[uid] = [0.0, 0.0, 0.0]

    return instance_of


def explode_outward(final: Dict[str, List[float]], center: List[float]) -> Dict[str, List[float]]:
    """Start positions for moving parts: outward from `center` and up, by a
    share of the piece's size."""
    xs = [p[0] for p in final.values()]
    ys = [p[1] for p in final.values()]
    zs = [p[2] for p in final.values()]
    size = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 0.5)
    distance, lift = size * EXPLODE_FRACTION, size * EXPLODE_LIFT_FRACTION

    exploded = {}
    for uid, pos in final.items():
        dx, dy = pos[0] - center[0], pos[1] - center[1]
        length = math.hypot(dx, dy)
        # Something over the middle (a seat) comes straight down.
        if length < 0.05:
            exploded[uid] = [pos[0], pos[1], pos[2] + distance]
            continue
        exploded[uid] = [pos[0] + dx / length * distance, pos[1] + dy / length * distance, pos[2] + lift]
    return exploded


def compute_chair_positions(
    shapes: Dict[str, Dict[str, Any]],
    graph: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Lay out a chair standing upright: the front leg frame at the front,
    the back (whose legs are the back legs) behind it, side rails between
    them along the inside of the legs, and the seat on top. None when the
    parts have no leg frame or no back."""
    by_role = parts_by_role(shapes)
    if not by_role.get("leg_frame") or not by_role.get("back"):
        return None

    frame_uid, back_uid = by_role["leg_frame"][0], by_role["back"][0]
    frame_w, frame_t, frame_h = shapes[frame_uid]["dimensions"]
    back_w, back_t, back_h = shapes[back_uid]["dimensions"]
    rails = by_role.get("rail", [])
    depth = shapes[rails[0]]["dimensions"][0] if rails else frame_w

    y_front = -(depth + frame_t) / 2
    y_back = (depth + back_t) / 2
    final = {frame_uid: [0.0, y_front, frame_h / 2], back_uid: [0.0, y_back, back_h / 2]}
    rotation = {frame_uid: [0.0, 0.0, 0.0], back_uid: [0.0, 0.0, 0.0]}
    scale: Dict[str, List[float]] = {}

    rail_x = min(frame_w, back_w) / 2 - frame_t / 2
    for i, uid in enumerate(rails):
        length, _, height = shapes[uid]["dimensions"]
        final[uid] = [rail_x * (1 if i % 2 == 0 else -1), (y_front + y_back) / 2, frame_h - height / 2]
        rotation[uid] = [0.0, 0.0, 90.0]
        scale[uid] = [depth / length, 1.0, 1.0]

    for uid in by_role.get("seat", []):
        _, seat_d, seat_t = shapes[uid]["dimensions"]
        final[uid] = [0.0, y_front - frame_t / 2 + seat_d / 2, frame_h + seat_t / 2]
        rotation[uid] = [0.0, 0.0, 0.0]

    instance_of = place_fastener_instances(shapes, graph, final, rotation, scale)
    return {
        "final": final,
        "exploded": explode_outward(final, [0.0, 0.0, frame_h / 2]),
        "rotation": rotation,
        "scale": scale,
        "instance_of": instance_of,
        "pivot": None,
    }


INSTANCE_SUFFIX_RE = re.compile(r"\s+\d+\s*/\s*\d+$")


def base_name(shape: Dict[str, Any]) -> str:
    """'right side rail 2/2' -> 'right side rail'."""
    return INSTANCE_SUFFIX_RE.sub("", shape.get("canonical_name", "")).lower()


def named(uids: List[str], shapes: Dict[str, Dict[str, Any]], word: str) -> List[str]:
    return [uid for uid in uids if word in base_name(shapes[uid])]


def side_of(shape: Dict[str, Any], index: int) -> int:
    """+1 (right, +X) or -1 (left) from the name, else alternating."""
    name = base_name(shape)
    if "left" in name:
        return -1
    if "right" in name:
        return 1
    return 1 if index % 2 == 0 else -1


def joined_to(uid: str, others: List[str], graph: Dict[str, Any]) -> bool:
    return any(
        uid in ends and ends & set(others)
        for ends in ({conn.get("from_node_ref"), conn.get("to_node_ref")} for conn in graph.get("connections", []))
    )


def compute_bed_positions(
    shapes: Dict[str, Dict[str, Any]],
    graph: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Lay out a bed standing upright, headboard at +Y: tall headboard posts
    with the headboard rails stacked between them, short footboard posts
    with a rail between them, side rails end to end down each side (with a
    centre leg where two meet) and slats across on top. None when there
    are no bed posts."""
    by_role = parts_by_role(shapes)
    posts = by_role.get("post", [])
    if not posts:
        return None

    rails = by_role.get("rail", [])
    head_posts, foot_posts = named(posts, shapes, "headboard"), named(posts, shapes, "footboard")
    side_rails = named(rails, shapes, "side")
    board_rails = [uid for uid in rails if uid not in side_rails]
    legs, slats = by_role.get("leg", []), by_role.get("slat", [])

    # Side rail kinds run from the headboard to the footboard: the kind
    # joined to the headboard posts first, then by name.
    kinds: Dict[str, List[str]] = {}
    for uid in side_rails:
        kinds.setdefault(base_name(shapes[uid]), []).append(uid)
    kind_order = sorted(kinds, key=lambda name: (not joined_to(kinds[name][0], head_posts, graph), name))
    kind_lengths = [shapes[kinds[name][0]]["dimensions"][0] for name in kind_order]

    post_w = shapes[posts[0]]["dimensions"][0]
    leg_w = shapes[legs[0]]["dimensions"][0] if legs else 0.0
    inner_w = max((shapes[uid]["dimensions"][0] for uid in board_rails), default=0.9)
    inner_len = sum(kind_lengths) + leg_w * max(len(kind_lengths) - 1, 0) or 1.9
    post_x = inner_w / 2 + post_w / 2
    post_y = inner_len / 2 + post_w / 2
    foot_h = max((shapes[uid]["dimensions"][2] for uid in foot_posts or legs), default=0.33)
    head_h = max((shapes[uid]["dimensions"][2] for uid in head_posts), default=0.9)

    final: Dict[str, List[float]] = {}
    rotation: Dict[str, List[float]] = {}

    def put(uid: str, pos: List[float], turn: float = 0.0) -> None:
        final[uid] = pos
        rotation[uid] = [0.0, 0.0, turn]

    for group, y in ((head_posts, post_y), (foot_posts, -post_y)):
        for i, uid in enumerate(group):
            put(uid, [side_of(shapes[uid], i) * post_x, y, shapes[uid]["dimensions"][2] / 2])

    # One board rail goes between the footboard posts: the one not joined
    # to the headboard, else the last of the widest.
    foot_rails: List[str] = []
    if foot_posts and board_rails:
        widest = max(shapes[uid]["dimensions"][2] for uid in board_rails)
        free = [uid for uid in board_rails if not joined_to(uid, head_posts, graph)]
        foot_rails = free[-1:] or [uid for uid in board_rails if shapes[uid]["dimensions"][2] == widest][-1:]
    for uid in foot_rails:
        put(uid, [0.0, -post_y, foot_h - shapes[uid]["dimensions"][2] / 2])

    # Headboard rails top to bottom: a widest one, the narrower ones, then
    # the other widest ones, with even gaps.
    head_rails = sorted(
        (uid for uid in board_rails if uid not in foot_rails),
        key=lambda uid: (-shapes[uid]["dimensions"][2], uid),
    )
    if head_rails:
        widest = shapes[head_rails[0]]["dimensions"][2]
        wide = [uid for uid in head_rails if shapes[uid]["dimensions"][2] == widest]
        order = wide[:1] + [uid for uid in head_rails if uid not in wide] + wide[1:]
        top, bottom = head_h - 0.03, foot_h + 0.06
        heights = [shapes[uid]["dimensions"][2] for uid in order]
        gap = max((top - bottom - sum(heights)) / max(len(order) - 1, 1), 0.01)
        z = top
        for uid, height in zip(order, heights):
            put(uid, [0.0, post_y, z - height / 2])
            z -= height + gap

    y = inner_len / 2
    leg_rows: List[float] = []
    for name, length in zip(kind_order, kind_lengths):
        for i, uid in enumerate(kinds[name]):
            height = shapes[uid]["dimensions"][2]
            put(uid, [(1 if i % 2 == 0 else -1) * post_x, y - length / 2, foot_h - height / 2], 90.0)
        y -= length
        if len(leg_rows) < len(kinds) - 1:
            leg_rows.append(y - leg_w / 2)
            y -= leg_w
    for i, uid in enumerate(legs):
        row = leg_rows[min(i // 2, len(leg_rows) - 1)] if leg_rows else 0.0
        put(uid, [(1 if i % 2 == 0 else -1) * post_x, row, shapes[uid]["dimensions"][2] / 2])

    # Slats evenly across the base, from the footboard to the headboard.
    if slats:
        slat_w = shapes[slats[0]]["dimensions"][1]
        pitch = (inner_len - slat_w) / max(len(slats) - 1, 1)
        for i, uid in enumerate(slats):
            thickness = shapes[uid]["dimensions"][2]
            put(uid, [0.0, -inner_len / 2 + slat_w / 2 + i * pitch, foot_h - SLAT_DROP - thickness / 2])

    instance_of = place_fastener_instances(shapes, graph, final, rotation, {})
    return {
        "final": final,
        "exploded": explode_outward(final, [0.0, 0.0, foot_h / 2]),
        "rotation": rotation,
        "scale": {},
        "instance_of": instance_of,
        "pivot": None,
    }


def fallback_grid_position(index: int, node_type: str) -> Tuple[List[float], List[float]]:
    """Genuine fallback for nodes with NO connection at all (e.g. an
    unused tool). Returns a real (final, exploded) pair — never
    exploded == final — so even fallback nodes visibly move if flagged
    as moving."""
    if node_type == "assembly":
        return [0.0, 0.0, 1.2], [0.0, 0.0, 1.2]

    row = index // 4
    col = index % 4
    final = [(col - 1.5) * 1.35, row * 0.85 + 3.0, 1.0]  # offset row so it doesn't collide with real clusters
    exploded = [final[0] * 2.2, final[1] * 2.2, final[2] + 2.0]
    return final, exploded


def moving_nodes_from_motion(motion: Dict[str, Any]) -> set:
    moving = set()
    for step in motion.get("steps", []):
        for uid in step.get("moving_nodes", []):
            moving.add(uid)
    return moving


def target_nodes_from_motion(motion: Dict[str, Any]) -> set:
    targets = set()
    for step in motion.get("steps", []):
        for uid in step.get("target_nodes", []):
            targets.add(uid)
    return targets


def first_motion_step(node_uid: str, motion: Dict[str, Any]) -> str:
    for step in motion.get("steps", []):
        if node_uid in step.get("moving_nodes", []) or node_uid in step.get("target_nodes", []):
            return step.get("step_uid", "")
    return ""


def primary_assembly_uid(graph: Dict[str, Any]) -> str:
    for asm in graph.get("assemblies", []):
        uid = asm.get("assembly_uid", "")
        if uid:
            return uid
    return "ASM0001"


def build_scene_layout(
    graph_path: Path = GRAPH_PATH,
    motion_path: Path = MOTION_PATH,
    geometry_path: Path = GEOMETRY_PATH,
    part_shapes_path: Path = PART_SHAPES_PATH,
    output_path: Path = OUTPUT_PATH,
) -> Dict[str, Any]:
    graph = load_json(graph_path)
    motion = load_json(motion_path)
    geometry = load_json(geometry_path)

    nodes = build_node_lookup(graph)
    geom_by_part = geometry_lookup(geometry)
    moving_nodes = moving_nodes_from_motion(motion)
    target_nodes = target_nodes_from_motion(motion)

    parent_map = build_parent_map(graph)
    primary_assembly = primary_assembly_uid(graph)

    connected_final, connected_exploded = compute_connected_positions(
        parent_map, geom_by_part, primary_assembly, build_kind_map(graph)
    )
    rotations: Dict[str, List[float]] = {}

    scales: Dict[str, List[float]] = {}
    finale: Dict[str, Any] = {}

    shapes = load_part_shapes(part_shapes_path)
    layout_mode = "generic"
    for mode, compute in (
        ("table", compute_table_positions),
        ("chair", compute_chair_positions),
        ("bed", compute_bed_positions),
    ):
        placed = compute(shapes, graph)
        if not placed:
            continue
        connected_final.update(placed["final"])
        connected_exploded.update(placed["exploded"])
        rotations = placed["rotation"]
        scales = placed["scale"]
        # Each instanced fastener replaces its single graph node.
        for instance_uid, base_uid in placed["instance_of"].items():
            if base_uid in nodes:
                nodes[instance_uid] = dict(nodes[base_uid], node_uid=instance_uid, instance_of=base_uid)
        for base_uid in set(placed["instance_of"].values()):
            nodes.pop(base_uid, None)
        # A table is built upside down and turned over at the end.
        if placed["pivot"] is not None:
            finale = {"type": "flip", "axis": "X", "angle": 180.0, "pivot": placed["pivot"]}
        layout_mode = mode
        break

    scene_objects = []
    warnings = []
    sorted_nodes = sorted(nodes.values(), key=lambda n: n["node_uid"])

    fallback_index = 0
    for node in sorted_nodes:
        uid = node["node_uid"]
        # A fastener instance shares its graph node's geometry, motion and parent.
        base_uid = node.get("instance_of", uid)
        node_type = node["node_type"]
        geom = geom_by_part.get(base_uid)
        geometry_uid = geom.get("geometry_uid") if geom else ""

        if uid in connected_final:
            final = connected_final[uid]
            exploded = connected_exploded.get(uid, final)
        else:
            final, exploded = fallback_grid_position(fallback_index, node_type)
            fallback_index += 1
            if node_type != "assembly":
                warnings.append(f"No connection found for node {uid} — used fallback grid position")

        is_moving = base_uid in moving_nodes
        start = exploded if is_moving else final

        parent = parent_map.get(base_uid, "")
        if not parent:
            for asm in graph.get("assemblies", []):
                if base_uid in asm.get("members", []):
                    parent = asm.get("assembly_uid", "")
                    break

        scene_object = {
            "node_uid": uid,
            "node_type": node_type,
            "name": node.get("canonical_name") or node.get("name") or uid,
            "geometry_uid": geometry_uid,
            "start_position": start,
            "final_position": final,
            "exploded_position": exploded,
            "rotation": rotations.get(uid, [0.0, 0.0, 0.0]),
            "scale": scales.get(uid, [1.0, 1.0, 1.0]),
            "parent": parent,
            "is_moving": is_moving,
            "is_target": base_uid in target_nodes,
            "first_motion_step": first_motion_step(base_uid, motion),
            "visible": True
        }
        if base_uid != uid:
            scene_object["instance_of"] = base_uid
        scene_objects.append(scene_object)

        if node_type == "part" and not geometry_uid:
            warnings.append(f"No geometry found for part node {uid}")

    layout = {
        "schema_version": "2.2",
        "scene_objects": scene_objects,
        # How the finished assembly is presented after the last step, e.g.
        # turned over from its upside-down build position. Empty: no finale.
        "finale": finale,
        "camera": {
            "position": [6.0, -8.0, 5.0],
            "target": [0.0, 0.0, 1.0],
            "lens": 35
        },
        "render": {
            "resolution_x": 1280,
            "resolution_y": 720,
            "fps": motion.get("fps", 24),
            "total_frames": motion.get("total_frames", 1)
        },
        "debug": {
            "moving_nodes": sorted(list(moving_nodes)),
            "target_nodes": sorted(list(target_nodes)),
            "primary_assembly": primary_assembly,
            "layout_mode": layout_mode,
            "connected_node_count": len(connected_final),
            "fallback_node_count": fallback_index,
        },
        "warnings": warnings
    }

    save_json(layout, output_path)

    print(f"Saved scene layout to {output_path}")
    print(f"Scene objects: {len(scene_objects)}")
    print(f"Connected via real structure: {len(connected_final)}")
    print(f"Fell back to grid: {fallback_index}")
    print(f"Moving objects: {sum(1 for o in scene_objects if o['is_moving'])}")
    print(f"Target objects: {sum(1 for o in scene_objects if o.get('is_target'))}")
    print(f"Warnings: {len(warnings)}")

    return layout


if __name__ == "__main__":
    result = build_scene_layout()

    if not any(obj["is_moving"] for obj in result["scene_objects"]):
        sys.exit(
            "ERROR: no scene object moves, so the video would show nothing being "
            "assembled. Check motion_plan.json."
        )