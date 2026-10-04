"""One layout for any piece of furniture.

Flat-pack furniture is a box frame: parts stand on the floor (legs, posts,
side frames, a chair back), long parts run along the frame's edges or across
it (rails, stretchers, slats), flat parts lie on top or across it (a table
top, a seat), and small parts sit in its corners (brackets). Each part gets a
place in that frame from:

- its kind, from its role or, without one, its proportions (part_kind):
  upright, wall, beam, plate or block;
- the parts it is joined to in the assembly graph, which say which edge a
  rail runs along and how high it sits;
- words in its name, only to break ties: front/back/head/foot, left/right,
  side/long, end/short, cross, top, bottom.

The frame's size comes from the measured parts (the manual's printed sizes)
before the role defaults. Rails and other beams are stretched or shortened to
fill the gap between the parts at their ends. A piece built from a part that
ends up on top (a table top lying face down) is laid out upside down and
turned over at the end.

Axes: X is the width (left -X, right +X), Y the depth (front -Y, back or head
+Y), Z up. Rotations are XYZ Euler angles in degrees, as Blender uses them.
"""
import math
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

Vec = List[float]

# A part at least this many times longer than its next-longest side is a
# bar (an upright or a beam).
ELONGATED = 2.5
# A part whose middle side is this many times its thickness is a board (a
# panel), unless its longest side is more than PLANK_RATIO times the middle.
PANEL_RATIO = 4
PLANK_RATIO = 6
# Legs stand this far in from a table top's edge.
LEG_INSET = 0.04
# Stretchers sit at this share of the frame's height.
STRETCHER_HEIGHT = 0.3
# A slatted base sits this far below the top of the rails it rests on.
SLAT_DROP = 0.03
# Beams stacked between two tall posts (a headboard) keep this far from the
# posts' tops and from the frame's lower rails.
STACK_TOP_MARGIN = 0.03
STACK_BOTTOM_MARGIN = 0.06
# Interior beams joined to nothing but a plate (runners under a top) spread
# over this share of the frame's half depth.
INTERIOR_SPREAD = 0.6
# Gaps smaller than this count as touching, not overlapping.
TOUCH = 1e-4
# Brackets slide toward the middle in steps of this size until they are clear
# of the parts at the corner.
PUSH_STEP = 0.005
PUSH_LIMIT = 400
# Fasteners at one host part are spread this far apart.
FASTENER_SPREAD = 0.04
# Moving parts start outward from the middle and up by these shares of the
# piece's longest side.
EXPLODE_FRACTION = 0.3
EXPLODE_LIFT_FRACTION = 0.25

# Doors and drawer fronts leave this gap around them; drawer boxes stand
# this far in from the carcass sides (room for the runners) and off the
# drawer's slot bottom.
FRONT_GAP = 0.004
RUNNER_GAP = 0.0125
DRAWER_LIFT = 0.02
# Joining hardware between two upholstered bodies starts this far up from
# the floor; brackets along the joint are this far apart.
HARDWARE_LIFT = 0.05
HARDWARE_SPREAD = 0.15

# Rungs between two uprights start this far up them.
RUNG_START = 0.35

# Seat height as a share of a side frame's height; blender_builder_v3.py
# draws the side frame's seat rail at the same height.
SIDE_FRAME_SEAT_FRACTION = 0.48

ROLE_KINDS = {
    "top": "plate", "seat": "plate",
    "leg": "upright", "post": "upright", "foot": "upright",
    "side_frame": "wall", "back": "wall", "leg_frame": "wall",
    "rail": "beam", "stretcher": "beam", "slat": "beam",
    "bracket": "block",
    # Cabinets.
    "side_panel": "wall", "divider": "wall", "back_panel": "wall", "front_panel": "wall", "end_board": "wall",
    "shelf": "plate", "lid": "plate", "plinth": "beam",
    # Placed onto a carcass or body after it is built.
    "door": "fitting", "drawer_front": "fitting", "drawer_side": "fitting", "drawer_back": "fitting",
    "drawer_bottom": "fitting", "runner": "fitting", "handle": "fitting", "hinge": "fitting",
    "back_cushion": "fitting",
    # Upholstery.
    "body": "body", "cushion": "plate",
}
VERTICAL_KINDS = ("upright", "wall")
# Quarter turns that can lay a standing panel flat.
FLAT_TURNS = [[0.0, 0.0, 0.0], [90.0, 0.0, 0.0], [0.0, 90.0, 0.0], [0.0, 0.0, 90.0],
              [90.0, 0.0, 90.0], [0.0, 90.0, 90.0], [90.0, 90.0, 0.0]]

# Words that put a part at the back (+Y) or front (-Y), checked in this
# order so a "headboard foot" is at the head, not the foot.
Y_WORDS = [("headboard", 1), ("footboard", -1), ("back", 1), ("rear", 1), ("head", 1), ("front", -1), ("foot", -1)]
X_WORDS = [("left", -1), ("right", 1)]
LONG_WORDS = {"side", "long"}
SHORT_WORDS = {"end", "short"}
CROSS_WORDS = {"cross"}
MIDDLE_WORDS = {"central", "centre", "center", "middle"}
TOP_WORDS = {"top", "upper"}
BOTTOM_WORDS = {"bottom", "lower", "base"}

INSTANCE_SUFFIX_RE = re.compile(r"\s+\d+\s*/\s*\d+$")
WORD_RE = re.compile(r"[a-z]+")


# --- names -------------------------------------------------------------------

def base_name(shape: Dict[str, Any]) -> str:
    """'right side rail 2/2' -> 'right side rail'."""
    return INSTANCE_SUFFIX_RE.sub("", shape.get("canonical_name", "")).lower()


def name_words(shape: Dict[str, Any]) -> Set[str]:
    return set(WORD_RE.findall(base_name(shape)))


def word_side(words: Set[str], table: List[Tuple[str, int]]) -> int:
    for word, side in table:
        if word in words:
            return side
    return 0


def family_name(shape: Dict[str, Any]) -> str:
    """The name without left/right: a left and a right headboard foot are
    one family of two."""
    return " ".join(w for w in base_name(shape).split() if w not in ("left", "right"))


# --- geometry ----------------------------------------------------------------

def rotation_matrix(rotation: Sequence[float]) -> List[List[float]]:
    """XYZ Euler in degrees (X applied first) -> 3x3 matrix Rz.Ry.Rx."""
    ax, ay, az = (math.radians(a) for a in rotation)
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    return [
        [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
        [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
        [-sy, cy * sx, cy * cx],
    ]


def matmul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def euler_from_matrix(m: List[List[float]]) -> Vec:
    """Inverse of rotation_matrix, rounded to 1e-6 degrees."""
    sy = -m[2][0]
    if abs(sy) < 1 - 1e-9:
        ay = math.asin(sy)
        ax = math.atan2(m[2][1], m[2][2])
        az = math.atan2(m[1][0], m[0][0])
    else:
        ay = math.copysign(math.pi / 2, sy)
        ax = 0.0
        az = math.atan2(-m[0][1], m[1][1])
    return [round(math.degrees(a), 6) + 0.0 for a in (ax, ay, az)]


def world_half_extents(dims: Sequence[float], rotation: Sequence[float], scale: Sequence[float]) -> Vec:
    """Half size along world X/Y/Z of a scaled, rotated box."""
    half = [d * s / 2 for d, s in zip(dims, scale)]
    m = rotation_matrix(rotation)
    return [sum(abs(m[i][j]) * half[j] for j in range(3)) for i in range(3)]


def part_kind(shape: Dict[str, Any]) -> str:
    """upright (leg, post), wall (a frame or panel standing up), beam (rail,
    slat), plate (top, seat) or block (bracket): from the role, else from
    the part's proportions (its dimensions are as it is fitted, Z up)."""
    kind = ROLE_KINDS.get(shape.get("role") or "")
    if kind:
        return kind
    x, y, z = shape["dimensions"]
    thin, middle, longest = sorted((x, y, z))
    # A board: much wider than thick, and not so long it is a plank.
    if middle >= PANEL_RATIO * thin and longest <= PLANK_RATIO * middle:
        return "plate" if z == thin else "wall"
    if longest >= ELONGATED * middle:
        return "upright" if z == longest else "beam"
    return "block"


def is_measured(shape: Dict[str, Any]) -> bool:
    """A size from the manual, or estimated from its drawings: kept as
    given instead of stretched to fit."""
    return shape.get("dims_source") in ("manual_measurement", "estimated")


class Frame:
    """Placed parts: centre, rotation and scale per uid, with box queries."""

    def __init__(self, shapes: Dict[str, Dict[str, Any]]):
        self.shapes = shapes
        # How a part is turned before the layout moves it (a panel laid flat).
        self.base_rotation: Dict[str, Vec] = {}
        self.final: Dict[str, Vec] = {}
        self.rotation: Dict[str, Vec] = {}
        self.scale: Dict[str, Vec] = {}

    def put(self, uid: str, center: Sequence[float], rotation: Optional[Sequence[float]] = None,
            scale: Optional[Sequence[float]] = None) -> None:
        if rotation is None:
            rotation = self.base_rotation.get(uid, [0.0, 0.0, 0.0])
        self.final[uid] = [float(c) for c in center]
        self.rotation[uid] = [float(r) for r in rotation]
        if scale is not None and any(abs(s - 1.0) > 1e-9 for s in scale):
            self.scale[uid] = [float(s) for s in scale]
        else:
            self.scale.pop(uid, None)

    def half(self, uid: str) -> Vec:
        return world_half_extents(self.shapes[uid]["dimensions"], self.rotation.get(uid, [0.0, 0.0, 0.0]),
                                  self.scale.get(uid, [1.0, 1.0, 1.0]))

    def box(self, uid: str) -> Tuple[Vec, Vec]:
        center, half = self.final[uid], self.half(uid)
        return [c - h for c, h in zip(center, half)], [c + h for c, h in zip(center, half)]

    def top(self, uid: str) -> float:
        return self.box(uid)[1][2]

    def colliders(self, lo: Sequence[float], hi: Sequence[float], ignore: Iterable[str] = ()) -> List[str]:
        skip = set(ignore)
        hits = []
        for uid in self.final:
            if uid in skip:
                continue
            olo, ohi = self.box(uid)
            if all(lo[i] < ohi[i] - TOUCH and olo[i] < hi[i] - TOUCH for i in range(3)):
                hits.append(uid)
        return hits

    def free_run(self, axis: int, center: Sequence[float], half: Sequence[float], limit: Tuple[float, float],
                 ignore: Iterable[str] = ()) -> Tuple[float, float]:
        """The gap along `axis` through `center` between the nearest placed
        parts on either side of it, within `limit`, for a part whose cross
        section is `half` wide on the other two axes."""
        low, high = limit
        skip = set(ignore)
        others = [i for i in range(3) if i != axis]
        for uid in self.final:
            if uid in skip:
                continue
            olo, ohi = self.box(uid)
            if not all(center[i] - half[i] < ohi[i] - TOUCH and olo[i] < center[i] + half[i] - TOUCH for i in others):
                continue
            if ohi[axis] <= center[axis] + TOUCH:
                low = max(low, ohi[axis])
            elif olo[axis] >= center[axis] - TOUCH:
                high = min(high, olo[axis])
        return low, high


# --- the graph ---------------------------------------------------------------

def part_links(graph: Dict[str, Any], parts: Dict[str, Dict[str, Any]]) -> Dict[str, Set[str]]:
    """Part-to-part joins, both ways. Copying an action to every copy of a
    part joins each of n copies to each of n others ("right side rail" 1/2
    and 2/2 each to both headboard feet); where two families of the same
    size are joined all-to-all like that, copy i keeps only partner i."""
    links: Dict[str, Set[str]] = {uid: set() for uid in parts}
    for conn in graph.get("connections", []):
        a, b = conn.get("from_node_ref", ""), conn.get("to_node_ref", "")
        if a in parts and b in parts and a != b:
            links[a].add(b)
            links[b].add(a)

    families: Dict[str, List[str]] = {}
    for uid in sorted(parts):
        families.setdefault(family_name(parts[uid]), []).append(uid)
    groups = [sorted(g, key=lambda u: (word_side(name_words(parts[u]), X_WORDS), u)) for g in families.values() if len(g) > 1]
    for i, ga in enumerate(groups):
        for gb in groups[i + 1:]:
            if len(ga) == len(gb) and all(b in links[a] for a in ga for b in gb):
                for k, a in enumerate(ga):
                    for m, b in enumerate(gb):
                        if k != m:
                            links[a].discard(b)
                            links[b].discard(a)
    return links


def sibling_groups(uids: Iterable[str], shapes: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """Copies of one part (same name without the n/N suffix), in uid order."""
    groups: Dict[str, List[str]] = {}
    for uid in sorted(uids):
        groups.setdefault(base_name(shapes[uid]), []).append(uid)
    return list(groups.values())


def base_part(motion: Dict[str, Any], parts: Dict[str, Any]) -> str:
    """The part the build starts from: never moved, and the target of the
    most steps (the first such on a tie)."""
    moving = {uid for step in motion.get("steps", []) for uid in step.get("moving_nodes", [])}
    counts: Dict[str, int] = {}
    order: List[str] = []
    for step in motion.get("steps", []):
        for uid in step.get("target_nodes", []):
            if uid in parts and uid not in moving:
                if uid not in counts:
                    order.append(uid)
                counts[uid] = counts.get(uid, 0) + 1
    return max(order, key=lambda uid: (counts[uid], -order.index(uid))) if order else ""


# --- the layout ----------------------------------------------------------------

class GeneralLayout:
    def __init__(self, shapes: Dict[str, Dict[str, Any]], graph: Dict[str, Any], motion: Dict[str, Any]):
        part_uids = {p.get("part_uid") for p in graph.get("parts", [])}
        self.parts = {uid: s for uid, s in shapes.items() if uid in part_uids and s.get("dimensions")}
        self.graph = graph
        self.motion = motion
        self.frame = Frame(shapes)
        self.kind = {uid: part_kind(s) for uid, s in self.parts.items()}
        self.words = {uid: name_words(s) for uid, s in self.parts.items()}
        self.links = part_links(graph, self.parts)
        self.orient_panels()
        self.groups = sibling_groups(self.parts, self.parts)
        self.group_of = {uid: g for g in self.groups for uid in g}
        self.corner_side: Dict[str, Tuple[int, int]] = {}
        self.junctions: List[str] = []
        # Height the carcass or bodies stand at: the legs or feet under them.
        self.floor = 0.0
        # Set by footprint(): the carcass's height, and the width figure of
        # each measured front or back panel.
        self.carcass_height = 0.0
        self.panel_width: Dict[str, float] = {}

    # -- helpers --

    def of_kind(self, kind: str, unplaced: bool = False) -> List[str]:
        return sorted(uid for uid, k in self.kind.items() if k == kind and not (unplaced and self.placed(uid)))

    def role(self, uid: str) -> str:
        return self.parts[uid].get("role") or ""

    def with_role(self, *roles: str) -> List[str]:
        return sorted(uid for uid in self.parts if self.role(uid) in roles)

    def dims(self, uid: str) -> List[float]:
        """Size along X/Y/Z as fitted, after any base rotation."""
        rotation = self.frame.base_rotation.get(uid)
        if rotation:
            return [2 * h for h in world_half_extents(self.parts[uid]["dimensions"], rotation, [1.0, 1.0, 1.0])]
        return self.parts[uid]["dimensions"]

    def orient_panels(self) -> None:
        """Panels with no role are sized standing up and facing the front.
        Those named as sides (side, left, right) turn to face sideways;
        those joined between two sides and not named front or back (shelves,
        a bottom) lie flat, their longer side across between the sides."""
        walls = [u for u in self.of_kind("wall") if not self.parts[u].get("role")]
        sides = set()
        for uid in walls:
            if "side" in self.words[uid] or word_side(self.words[uid], X_WORDS):
                sides.add(uid)
                x, y, _ = self.dims(uid)
                if x > y:
                    self.frame.base_rotation[uid] = [0.0, 0.0, 90.0]
        sides |= {u for u in self.of_kind("wall") if self.dims(u)[0] < self.dims(u)[1]}
        for uid in walls:
            if uid in sides or word_side(self.words[uid], Y_WORDS) or len(self.links[uid] & sides) < 2:
                continue
            thin, middle, longest = sorted(self.parts[uid]["dimensions"])
            for rotation in FLAT_TURNS:
                x, y, z = (2 * h for h in world_half_extents(self.parts[uid]["dimensions"], rotation, [1.0, 1.0, 1.0]))
                if abs(x - longest) < 1e-9 and abs(y - middle) < 1e-9 and abs(z - thin) < 1e-9:
                    self.frame.base_rotation[uid] = rotation
                    self.kind[uid] = "plate"
                    break

    def structural(self) -> Dict[str, Dict[str, Any]]:
        """Parts the piece is built on: not doors, drawers or their hardware,
        which are often put together lying on a front."""
        return {u: s for u, s in self.parts.items() if self.kind[u] != "fitting"}

    def placed(self, uid: str) -> bool:
        return uid in self.frame.final

    def linked(self, uid: str, kinds: Sequence[str] = ()) -> List[str]:
        return sorted(o for o in self.links.get(uid, ()) if self.placed(o) and (not kinds or self.kind[o] in kinds))

    def attach_level(self, uid: str) -> float:
        """Height at which other parts join a vertical part: a side frame's
        seat rail, else its top."""
        if self.role(uid) == "side_frame" or self.parts[uid].get("primitive") == "side_frame":
            lo, hi = self.frame.box(uid)
            return lo[2] + (hi[2] - lo[2]) * SIDE_FRAME_SEAT_FRACTION
        return self.frame.top(uid)

    def tall_end(self, uid: str) -> int:
        """Which Y end of a wall reaches its full height: a side frame's back
        leg is at +Y. 0 when the wall is the same height all along."""
        return 1 if self.role(uid) == "side_frame" or self.parts[uid].get("primitive") == "side_frame" else 0

    # -- 1. walls and the frame's footprint --

    def walls(self) -> Tuple[List[str], List[str]]:
        """(side walls standing in the Y/Z plane, front/back walls in X/Z)."""
        walls = [u for u in self.of_kind("wall") if self.role(u) != "divider"]
        side = [u for u in walls if self.dims(u)[0] < self.dims(u)[1]]
        return side, [u for u in walls if u not in side]

    def footprint(self) -> Tuple[float, float, Optional[str]]:
        """(width, depth, the plate that sets them or None). Measured sizes
        win over role defaults; without measurements a plate wins over
        walls, and walls over the beams between them."""
        # Cushions are soft and sized by default; they don't set the frame.
        plates = sorted((u for u in self.of_kind("plate") if self.role(u) != "cushion"),
                        key=lambda u: (-self.dims(u)[0] * self.dims(u)[1], u))
        plate = plates[0] if plates else None
        side_walls, end_walls = self.walls()
        width: List[Tuple[float, bool, int]] = []
        depth: List[Tuple[float, bool, int]] = []
        # In a carcass the walls set the size before a plate's role default
        # (a default "top panel" is a table top's size).
        plate_rank = 2 if side_walls else 0
        if plate:
            width.append((self.dims(plate)[0], is_measured(self.parts[plate]), plate_rank))
            depth.append((self.dims(plate)[1], is_measured(self.parts[plate]), plate_rank))

        # The carcass height: measured side walls, else a measured front or
        # back panel's other figure, else the side walls' default.
        measured_sides = [self.dims(u)[2] for u in side_walls if is_measured(self.parts[u])]
        heights = list(measured_sides)
        self.panel_width = {}
        for uid in end_walls:
            x, _, z = self.dims(uid)
            if side_walls and is_measured(self.parts[uid]):
                # Which figure is the width: the one unlike the sides'
                # measured height, else the larger.
                if measured_sides:
                    across = x if abs(x - measured_sides[0]) >= abs(z - measured_sides[0]) else z
                else:
                    across = max(x, z)
                self.panel_width[uid] = across
                if not measured_sides:
                    heights.append(z if across == x else x)
                x = across
            width.append((x, is_measured(self.parts[uid]), 1))
        self.carcass_height = max(heights) if heights else max((self.dims(u)[2] for u in side_walls), default=0.0)
        for uid in side_walls:
            depth.append((self.dims(uid)[1], is_measured(self.parts[uid]), 1))
        for uid in self.of_kind("beam"):
            joined = self.links[uid]
            for walls, out, t_axis in ((side_walls, width, 0), (end_walls, depth, 1)):
                # Only a beam spanning between two of the walls (joined to
                # both) says how far apart they are.
                if len(joined & set(walls)) >= 2:
                    thickness = 2 * min(self.dims(w)[t_axis] for w in walls)
                    out.append((self.dims(uid)[0] + thickness, is_measured(self.parts[uid]), 3))

        def pick(cands: List[Tuple[float, bool, int]]) -> float:
            measured = [v for v, m, _ in cands if m]
            if measured:
                return max(measured)
            if not cands:
                return 0.0
            best = min(p for _, _, p in cands)
            return max(v for v, _, p in cands if p == best)

        return pick(width), pick(depth), plate

    def place_walls(self, width: float, depth: float) -> None:
        side_walls, end_walls = self.walls()
        # With more than one pair of side pieces, those named for the back or
        # front (a chair's back uprights) stand inside the outer pair, at
        # that end.
        inner = [u for u in side_walls if word_side(self.words[u], Y_WORDS)] if len(side_walls) > 2 else []
        outer_t = max((self.dims(u)[0] for u in side_walls if u not in inner), default=0.0)
        for i, uid in enumerate(side_walls):
            if self.placed(uid):
                continue
            t, d, h = self.dims(uid)
            side = word_side(self.words[uid], X_WORDS) or (1 if i % 2 == 0 else -1)
            if uid in inner:
                end = word_side(self.words[uid], Y_WORDS)
                self.frame.put(uid, [side * (width / 2 - outer_t - t / 2), end * (depth / 2 - d / 2), self.floor + h / 2])
                continue
            # Unmeasured sides take the carcass height a measured panel gives.
            scale = None
            if not is_measured(self.parts[uid]) and self.carcass_height and abs(h - self.carcass_height) > 1e-6 \
                    and self.role(uid) != "side_frame":
                scale = [1.0, 1.0, self.carcass_height / h]
                h = self.carcass_height
            self.frame.put(uid, [side * (width / 2 - t / 2), 0.0, self.floor + h / 2], scale=scale)
        height = self.carcass_height
        # Front and back walls stand between the corners of the frame, or
        # just outside the side walls when there are some (a back panel).
        outside = 1 if side_walls else -1
        # Copies of one panel on the same face share its width (a back made
        # of two halves).
        share: Dict[str, Tuple[int, int]] = {}
        for group in sibling_groups(end_walls, self.parts):
            for k, uid in enumerate(group):
                share[uid] = (k, len(group))
        for i, uid in enumerate(end_walls):
            if self.placed(uid):
                continue
            scale = None
            if side_walls:
                # A panel across a carcass: turned so its longer side runs the
                # way the carcass is longer, and sized to cover it unless
                # measured.
                x, _, z = self.dims(uid)
                across = self.panel_width.get(uid)
                if (across is not None and abs(z - across) < abs(x - across)) or \
                        (across is None and (x - z) * (width - height) < 0):
                    self.frame.base_rotation[uid] = [0.0, 90.0, 0.0]
                if not is_measured(self.parts[uid]):
                    x, _, z = self.dims(uid)
                    # Scale is along the part's own axes: swapped when turned.
                    scale = [height / x, 1.0, width / z] if uid in self.frame.base_rotation else [width / x, 1.0, height / z]
            _, t, h = self.dims(uid)
            if scale:
                h = height
            side = word_side(self.words[uid], Y_WORDS) or {
                "back": 1, "leg_frame": -1, "back_panel": 1, "front_panel": -1}.get(self.role(uid), 0) \
                or (-1 if i % 2 == 0 else 1)
            k, n = share.get(uid, (0, 1))
            x = 0.0
            if n > 1 and side_walls:
                x = -width / 2 + width * (k + 0.5) / n
                if scale:
                    axis = 2 if uid in self.frame.base_rotation else 0
                    scale[axis] /= n
            self.frame.put(uid, [x, side * (depth / 2 + outside * t / 2), self.floor + h / 2], scale=scale)

    # -- 2. uprights --

    def assign_corners(self) -> None:
        """Which corner each upright stands at: (x side, y side). Uprights
        named central/middle, or beyond the fourth, are junctions along the
        sides instead. Taller uprights go to the back."""
        uprights = self.of_kind("upright", unplaced=True)
        self.junctions = [u for u in uprights if self.words[u] & MIDDLE_WORDS]
        corners = [u for u in uprights if u not in self.junctions]
        self.junctions += corners[4:]
        corners = corners[:4]
        heights = {round(self.dims(u)[2], 3) for u in corners}
        tallest = max(heights) if heights else 0.0

        wanted = {}
        for uid in corners:
            ys = word_side(self.words[uid], Y_WORDS)
            if not ys and len(heights) > 1:
                ys = 1 if round(self.dims(uid)[2], 3) == tallest else -1
            wanted[uid] = (word_side(self.words[uid], X_WORDS), ys)

        free = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        # Fully named uprights first, then half-named, then the rest.
        for uid in sorted(corners, key=lambda u: (-sum(1 for s in wanted[u] if s), u)):
            xs, ys = wanted[uid]
            choice = next((c for c in free if (not xs or c[0] == xs) and (not ys or c[1] == ys)), free[0])
            free.remove(choice)
            self.corner_side[uid] = choice

    # -- 3. beams: which line each one runs along --

    def long_axis(self, width: float, depth: float, plate: Optional[str]) -> int:
        """The axis "side" and "long" beams run along: a plate's longer side
        when only the plate sets the frame (a table top), else Y (the sides
        of a chair or bed are at -X and +X)."""
        return 0 if plate and not any(self.walls()) and width >= depth else 1

    def beam_axis(self, uid: str, long_axis: int) -> Tuple[int, str]:
        """(axis, why): 0 = along X, 1 = along Y."""
        words = self.words[uid]
        if words & LONG_WORDS:
            return long_axis, "long"
        if words & SHORT_WORDS:
            return 1 - long_axis, "short"
        if words & CROSS_WORDS:
            return 1 - long_axis, "cross"
        if word_side(words, Y_WORDS):
            return 0, "face"
        sides = [self.corner_side[o] for o in self.links[uid] if o in self.corner_side]
        if any(o in self.junctions for o in self.links[uid]):
            return 1, "corners"
        if len({s[0] for s in sides}) > 1 and len({s[1] for s in sides}) == 1:
            return 0, "corners"
        if len({s[1] for s in sides}) > 1 and len({s[0] for s in sides}) == 1:
            return 1, "corners"
        side_walls, end_walls = self.walls()
        if self.links[uid] & set(side_walls):
            return 0, "walls"
        if self.links[uid] & set(end_walls):
            return 1, "walls"
        return long_axis, "interior"

    def beam_side(self, uid: str, axis: int) -> int:
        """Which edge (+1/-1) a beam runs along, from the corner uprights it
        is joined to, then its name; 0 when nothing says."""
        cross = 1 - axis
        sides = {self.corner_side[o][cross] for o in self.links[uid] if o in self.corner_side}
        if len(sides) == 1:
            return sides.pop()
        if axis == 0:
            return word_side(self.words[uid], Y_WORDS)
        return 0

    # -- placement --

    def compute(self) -> Dict[str, Any]:
        self.place_bodies()
        self.floor = max(self.floor, self.carcass_floor())
        width, depth, plate = self.footprint()
        self.place_walls(width, depth)
        self.assign_corners()
        long_axis = self.long_axis(width, depth, plate)

        plan, ladders = self.plan_beams(long_axis)
        corners = list(self.corner_side)
        up_half = [max((self.dims(u)[i] for u in corners + self.junctions), default=0.0) / 2 for i in range(2)]

        # Frame size from the beams when no plate or wall sets it (a bed):
        # beams across the frame give its inner width, beams along each side
        # (end to end, with a junction post between) its inner length.
        chains = self.side_chains(plan, corners)
        if corners and not plate and not any(self.walls()):
            across = [self.dims(u)[0] for u, p in plan.items() if p.get("side") and p["axis"] == 0]
            inner_w = max(across, default=width or 0.9)
            inner_l = max((sum(self.dims(g[0])[0] for g in chain) + up_half[1] * 2 * (len(chain) - 1)
                           for chain in chains.values()), default=depth or 1.9)
            cx, cy = inner_w / 2 + up_half[0], inner_l / 2 + up_half[1]
            width, depth = 2 * cx + 2 * up_half[0], 2 * cy + 2 * up_half[1]
        else:
            cx, cy = width / 2 - LEG_INSET - up_half[0], depth / 2 - LEG_INSET - up_half[1]

        for uid, (xs, ys) in self.corner_side.items():
            self.frame.put(uid, [xs * cx, ys * cy, self.dims(uid)[2] / 2])
        self.panels_between_legs(cx, cy, up_half)

        frame_top = max((self.frame.top(u) for u in self.frame.final), default=0.75)
        corner_top = max((self.frame.top(u) for u in corners), default=frame_top)

        # A plate on corner posts (a table top) goes on before the beams.
        if plate and corners and not any(self.walls()):
            self.frame.put(plate, [0.0, 0.0, corner_top + self.dims(plate)[2] / 2])

        self.place_junctions(chains, plan, cx, cy, up_half)
        self.place_frame_beams(plan, chains, cx, cy, width, depth, frame_top, corner_top)
        for group in sorted(ladders, key=lambda g: -len(g)):
            self.place_ladder(group, frame_top)
        self.place_blocks()
        self.place_shelves()
        self.place_fittings()
        for uid in self.of_kind("plate"):
            if not self.placed(uid):
                self.place_plate(uid, frame_top)
        for uid in sorted(self.parts):
            if not self.placed(uid):
                self.place_leftover(uid)

        return self.finish()

    def plan_beams(self, long_axis: int) -> Tuple[Dict[str, Dict[str, Any]], List[List[str]]]:
        """Which line each frame beam runs along: {uid: axis, and an edge
        side (+1/-1) or its place among interior beams}; and the sets of
        slats, placed after the frame."""
        beams = self.of_kind("beam", unplaced=True)
        ladder_groups = [g for g in sibling_groups(beams, self.parts)
                         if self.parts[g[0]].get("role") == "slat"
                         or (len(g) >= 3 and all(self.kind[o] == "beam" for u in g for o in self.links[u]))]
        # Slats of one size are one set, whatever their names ("slat with
        # stamp" and "slat" 1/13...).
        sets: Dict[Tuple[Any, ...], List[str]] = {}
        for group in ladder_groups:
            key = (self.parts[group[0]].get("role"), tuple(self.dims(group[0])))
            sets.setdefault(key, []).extend(group)
        ladders = list(sets.values())
        ladder_uids = {u for g in ladders for u in g}
        frame_groups = [g for g in sibling_groups(beams, self.parts) if g[0] not in ladder_uids]

        # Each frame beam: axis, edge side (+1/-1), or interior.
        plan: Dict[str, Dict[str, Any]] = {}
        for group in frame_groups:
            axis, why = self.beam_axis(group[0], long_axis)
            sides = [self.beam_side(u, axis) for u in group]
            # A lone beam that nothing puts on an edge runs down the middle
            # (the long stretcher of an H-frame).
            interior = why in ("cross", "interior") or (
                len(group) == 1 and not sides[0] and not (self.words[group[0]] & TOP_WORDS))
            if interior:
                for i, uid in enumerate(group):
                    plan[uid] = {"axis": axis, "interior": (i, len(group)), "why": why}
                continue
            # Copies nothing places spread over the two edges, + first.
            taken = [s for s in sides if s]
            for i, uid in enumerate(group):
                if not sides[i]:
                    plus, minus = taken.count(1), taken.count(-1)
                    sides[i] = 1 if plus <= minus else -1
                    taken.append(sides[i])
                plan[uid] = {"axis": axis, "side": sides[i], "why": why}
        # A beam joined only to slats takes the line of the other beam
        # those slats are joined to (a top rail over a back's slats).
        for uid, p in plan.items():
            if p["why"] != "interior" or not self.links[uid] or not self.links[uid] <= ladder_uids:
                continue
            partner = next((o for o in sorted(plan) if o != uid and plan[o]["why"] != "interior"
                            and self.links[o] & self.links[uid]), None)
            if partner:
                plan[uid] = {"axis": plan[partner]["axis"], "side": plan[partner].get("side", 1) or 1, "why": "partner"}
        # "top" beams on walls with a tall end go to that end.
        for uid, p in plan.items():
            if self.words[uid] & TOP_WORDS and not p.get("side") and "interior" not in p:
                walls = [w for w in self.links[uid] if self.kind.get(w) == "wall"]
                p["side"] = next((self.tall_end(w) for w in walls if self.tall_end(w)), 1)

        corners = list(self.corner_side)
        # Edges between two corner posts with no beam take a spare copy
        # from a group that has two or more on one edge (a footboard rail
        # listed with the headboard rails).
        if corners:
            for axis in (0, 1):
                for side in (1, -1):
                    if any(p["axis"] == axis and p.get("side") == side for p in plan.values()):
                        continue
                    ends = [u for u in corners if self.corner_side[u][1 - axis] == side]
                    if len(ends) < 2:
                        continue
                    crowded = [u for u in plan if plan[u]["axis"] == axis and plan[u].get("side") == -side]
                    if len(crowded) < 2:
                        continue
                    spare = min(reversed(crowded), key=lambda u: len(self.links[u] & set(corners)))
                    plan[spare]["side"] = side
        return plan, ladders

    def panels_between_legs(self, cx: float, cy: float, up_half: List[float]) -> None:
        """Legs at the corners and side panels too (a frame-and-panel
        dresser): each side panel sits between the front and back legs on
        its side, in line with them, filling the gap unless measured."""
        if not self.corner_side:
            return
        side_walls = [w for w in self.walls()[0] if self.placed(w) and self.role(w) != "side_frame"]
        # Only legs as tall as the panels frame them; short feet just raise
        # a carcass.
        tallest_leg = max(self.dims(u)[2] for u in self.corner_side)
        side_walls = [w for w in side_walls if tallest_leg >= 0.6 * self.dims(w)[2]]
        for uid in side_walls:
            c = self.frame.final[uid]
            side = 1 if c[0] > 0 else -1
            t, d, h = self.dims(uid)
            gap = 2 * cy - 2 * up_half[1]
            scale = list(self.frame.scale.get(uid, [1.0, 1.0, 1.0]))
            if not is_measured(self.parts[uid]):
                scale[1] = gap / d
            # Flush with the tops of the legs, which the top rests on.
            leg_top = max(self.frame.top(u) for u in self.corner_side if self.corner_side[u][0] == side)
            self.frame.put(uid, [side * cx, 0.0, leg_top - h * scale[2] / 2], scale=scale)
        if not side_walls:
            return
        # A back (or front) panel then goes on the back of that frame, as
        # high as the side panels.
        boxes = [self.frame.box(u) for u in side_walls + list(self.corner_side)]
        z0 = min(self.frame.box(w)[0][2] for w in side_walls)
        z1 = max(self.frame.box(w)[1][2] for w in side_walls)
        for uid in self.walls()[1]:
            if not self.placed(uid) or self.role(uid) in ("back", "leg_frame"):
                continue
            c = self.frame.final[uid]
            half = self.frame.half(uid)
            y = max(b[1][1] for b in boxes) + half[1] if c[1] > 0 else min(b[0][1] for b in boxes) - half[1]
            scale = list(self.frame.scale.get(uid, [1.0, 1.0, 1.0]))
            if not is_measured(self.parts[uid]):
                axis = 0 if uid in self.frame.base_rotation else 2
                scale[axis] *= (z1 - z0) / (2 * half[2])
            self.frame.put(uid, [c[0], y, (z0 + z1) / 2], self.frame.rotation.get(uid), scale)

    def side_chains(self, plan: Dict[str, Dict[str, Any]], corners: List[str]) -> Dict[Tuple[int, int], List[List[str]]]:
        """Beams along each side edge, as (axis, side) -> groups end to end
        from +Y/+X: when junction posts stand on the frame, the beams of
        different names along one edge are laid end to end, the group
        joined to the back corners first."""
        chains: Dict[Tuple[int, int], List[List[str]]] = {}
        if not self.junctions:
            return chains
        for (axis, side) in ((1, 1), (1, -1), (0, 1), (0, -1)):
            members = [u for u, p in plan.items() if p["axis"] == axis and p.get("side") == side
                       and self.links[u] & set(self.junctions)]
            groups: Dict[str, List[str]] = {}
            for uid in members:
                groups.setdefault(base_name(self.parts[uid]), []).append(uid)
            if len(groups) < 2:
                continue
            back = [u for u in corners if self.corner_side[u][axis] == 1]
            ordered = sorted(groups.values(), key=lambda g: (not (self.links[g[0]] & set(back)), base_name(self.parts[g[0]])))
            chains[(axis, side)] = ordered
        return chains

    def place_junctions(self, chains: Dict[Tuple[int, int], List[List[str]]], plan: Dict[str, Dict[str, Any]],
                        cx: float, cy: float, up_half: List[float]) -> None:
        """Junction posts between the beams laid end to end along a side,
        each on the side of the beams it joins; any others along the sides'
        middles."""
        spots: List[Vec] = []
        for (axis, side), chain in chains.items():
            far = cy if axis == 1 else cx
            pos = far - up_half[axis]
            for group in chain[:-1]:
                pos -= self.dims(group[0])[0]
                spot = [0.0, 0.0]
                spot[axis] = pos - up_half[axis]
                spot[1 - axis] = side * (cx if axis == 1 else cy)
                spots.append(spot)
                pos -= 2 * up_half[axis]
        for i, uid in enumerate(self.junctions):
            if spots:
                sides = {(plan[b]["axis"], plan[b].get("side")) for b in self.links[uid] if b in plan}
                spot = next((s for s in spots if any(s[1 - a] * (sd or 0) > 0 for a, sd in sides)), spots[0])
                spots.remove(spot)
            else:
                spot = [(1 if i % 2 == 0 else -1) * cx, 0.0]
            self.frame.put(uid, [spot[0], spot[1], self.dims(uid)[2] / 2])

    def line_verticals(self, axis: int, offset: float) -> List[str]:
        """Uprights and walls standing on the line along `axis` at `offset`."""
        cross = 1 - axis
        found = []
        for uid in self.frame.final:
            if self.kind.get(uid) not in VERTICAL_KINDS:
                continue
            lo, hi = self.frame.box(uid)
            if lo[cross] - TOUCH <= offset <= hi[cross] + TOUCH:
                found.append(uid)
        return found

    def place_frame_beams(self, plan: Dict[str, Dict[str, Any]], chains: Dict[Tuple[int, int], List[List[str]]],
                          cx: float, cy: float, width: float, depth: float, frame_top: float, corner_top: float) -> None:
        side_walls, end_walls = self.walls()
        corners = list(self.corner_side)

        def edge(axis: int, thickness: float) -> float:
            """Distance from the middle to the edge line a beam along `axis`
            runs on."""
            if corners:
                return cy if axis == 0 else cx
            if axis == 0:
                if side_walls:
                    return depth / 2 - min(self.dims(w)[0] for w in side_walls) / 2
                return depth / 2 - LEG_INSET - thickness / 2
            if end_walls:
                return min(self.dims(w)[0] for w in end_walls) / 2 - min(self.dims(w)[1] for w in end_walls) / 2
            if side_walls:
                return width / 2 - min(self.dims(w)[0] for w in side_walls) - thickness / 2
            return width / 2 - LEG_INSET - thickness / 2

        chain_pos: Dict[str, float] = {}
        for (axis, side), chain in chains.items():
            far = (cy if axis == 1 else cx)
            pos = far - max(self.dims(u)[axis] for u in corners) / 2 if corners else far
            for group in chain:
                length = self.dims(group[0])[0]
                for uid in group:
                    chain_pos[uid] = pos - length / 2
                junction = next((j for j in self.junctions), None)
                pos -= length + (self.dims(junction)[axis] if junction else 0.0)

        # Group the beams by line, so several on one edge can be stacked.
        lines: Dict[Tuple[int, float, float], List[str]] = {}
        order = sorted(plan, key=lambda u: (bool(self.words[u] & TOP_WORDS), plan[u]["why"] == "interior", u))
        for uid in order:
            p = plan[uid]
            axis = p["axis"]
            length, thickness, height = self.dims(uid)
            if "interior" in p:
                i, n = p["interior"]
                reach = edge(axis, thickness)
                if p["why"] == "cross":
                    offset = reach * (-1 + 2 * (i + 1) / (n + 1))
                else:
                    offset = reach * INTERIOR_SPREAD * (-1 + 2 * (i + 0.5) / n) if n > 1 else 0.0
            else:
                offset = p["side"] * edge(axis, thickness)
            along = chain_pos.get(uid, 0.0)
            lines.setdefault((axis, round(offset, 6), round(along, 6)), []).append(uid)

        for (axis, offset, along), members in lines.items():
            verticals = self.line_verticals(axis, offset)
            ends = [v for v in verticals if self.kind[v] == "upright"] or verticals
            stack = self.stack_order(members)
            heights = [self.dims(u)[2] for u in stack]
            line_top = max((self.frame.top(v) for v in ends), default=corner_top)
            line_low = min((self.attach_level(v) for v in ends), default=corner_top)
            lowest_corner = min((self.frame.top(u) for u in corners), default=self.floor)
            plain = [u for u in stack if not (self.words[u] & (TOP_WORDS | BOTTOM_WORDS))
                     and self.role(u) not in ("stretcher", "plinth")]

            # Several beams on one edge between tall posts: stacked with even
            # gaps from just under the posts' tops down to the lower rails.
            stacked: Dict[str, float] = {}
            equal_posts = line_top <= lowest_corner + sum(heights)
            if len(plain) > 1 and (not equal_posts or self.walls()[0]):
                # Between taller posts: from just under their tops down to
                # the lower rails. Between equal posts with panels (the
                # front rails of a dresser): evenly from the bottom to the top.
                top = line_top - (STACK_TOP_MARGIN if not equal_posts else 0.0)
                bottom = (lowest_corner if not equal_posts else self.floor + STACK_BOTTOM_MARGIN) + STACK_BOTTOM_MARGIN
                plain_h = [self.dims(u)[2] for u in plain]
                gap = max((top - bottom - sum(plain_h)) / max(len(plain) - 1, 1), 0.01)
                z = top
                for uid, h in zip(plain, plain_h):
                    stacked[uid] = z
                    z -= h + gap

            for uid in stack:
                length, thickness, height = self.dims(uid)
                words = self.words[uid]
                if self.role(uid) == "plinth":
                    z_top = height
                elif uid in stacked:
                    z_top = stacked[uid]
                elif words & TOP_WORDS:
                    z_top = line_top + height
                elif words & BOTTOM_WORDS or self.parts[uid].get("role") == "stretcher":
                    z_top = frame_top * STRETCHER_HEIGHT + height / 2
                else:
                    # Inside the walls it is joined to (a seat's side rail):
                    # at their joining height.
                    walls = [w for w in self.links[uid] if self.placed(w) and self.kind.get(w) == "wall"]
                    z_top = line_low if verticals else (min(self.attach_level(w) for w in walls) if walls else corner_top)
                center = [0.0, 0.0, z_top - height / 2]
                center[1 - axis] = offset
                center[axis] = along
                rotation = [0.0, 0.0, 0.0 if axis == 0 else 90.0]
                half = [0.0, 0.0, height / 2]
                half[1 - axis] = thickness / 2
                reach = (width if axis == 0 else depth) / 2
                if words & TOP_WORDS:
                    low, high = -reach, reach
                else:
                    low, high = self.frame.free_run(axis, center, half, (along - reach, along + reach) if along else (-reach, reach))
                    if high - low < 0.02:
                        low, high = along - length / 2, along + length / 2
                center[axis] = (low + high) / 2
                self.frame.put(uid, center, rotation, [(high - low) / length, 1.0, 1.0])

    def stack_order(self, members: List[str]) -> List[str]:
        """Beams on one edge from the top down: one of the tallest, the
        narrower ones, then the other tallest ones (a frame's outer rails
        are its widest)."""
        if len(members) < 2:
            return list(members)
        ordered = sorted(members, key=lambda u: (-self.dims(u)[2], u))
        tallest = self.dims(ordered[0])[2]
        wide = [u for u in ordered if self.dims(u)[2] == tallest]
        return wide[:1] + [u for u in ordered if u not in wide] + wide[1:]

    def place_rungs(self, group: List[str]) -> bool:
        """Slats joined between two upright side pieces (a back's uprights):
        across between them, spread up the height they share, at their
        depth. False when they aren't joined to two such pieces."""
        walls = sorted({o for u in group for o in self.links[u] if self.placed(o) and self.kind[o] in VERTICAL_KINDS})
        sides = {1 if self.frame.final[w][0] > 0 else -1 for w in walls}
        if len(walls) < 2 or sides != {1, -1}:
            return False
        boxes = [self.frame.box(w) for w in walls]
        x0 = max(b[1][0] for b in boxes if b[0][0] < 0)
        x1 = min(b[0][0] for b in boxes if b[1][0] > 0)
        z0, z1 = max(b[0][2] for b in boxes), min(b[1][2] for b in boxes)
        y = sum(self.frame.final[w][1] for w in walls) / len(walls)
        length, slat_w, thickness = self.dims(group[0])
        n = len(group)
        # Rungs over the upper share of the uprights, top one near the top.
        low, high = z0 + (z1 - z0) * RUNG_START, z1 - slat_w
        for k, uid in enumerate(group):
            z = high - (high - low) * k / max(n - 1, 1)
            # Wide face to the front: the slat's width runs up, its thickness
            # front to back.
            if self.parts[uid].get("primitive") == "profile":
                # A traced slat is already drawn as it sits: span the gap.
                self.frame.put(uid, [(x0 + x1) / 2, y, z], [0.0, 0.0, 0.0], [(x1 - x0) / self.dims(uid)[0], 1.0, 1.0])
            else:
                self.frame.put(uid, [(x0 + x1) / 2, y, z], [90.0, 0.0, 0.0], [(x1 - x0) / length, 1.0, 1.0])
        return True

    def place_ladder(self, group: List[str], frame_top: float) -> None:
        """Slats: across between two parallel beams they rest on (a bed
        base), or standing between a lower and an upper beam on one face (a
        chair back)."""
        joined = sorted({o for u in group for o in self.links[u] if self.placed(o) and self.kind[o] == "beam"})
        joined = [b for b in joined if b not in group]
        by_line: Dict[Tuple[int, float], List[str]] = {}
        for b in joined:
            axis = 0 if self.frame.half(b)[0] >= self.frame.half(b)[1] else 1
            by_line.setdefault((axis, round(self.frame.final[b][1 - axis], 3)), []).append(b)
        n = len(group)
        length, slat_w, thickness = self.dims(group[0])

        lines = list(by_line)
        if not lines and self.place_rungs(group):
            return
        if not lines:
            return
        axes = {a for a, _ in lines}
        if len(axes) == 1 and len({off for _, off in lines}) > 1:
            # Across between parallel beams, spread along them.
            axis = lines[0][0]
            boxes = [self.frame.box(b) for b in joined]
            lo = min(b[0][axis] for b in boxes)
            hi = max(b[1][axis] for b in boxes)
            z = min(b[1][2] for b in boxes) - SLAT_DROP - thickness / 2
            cross = 1 - axis
            pitch = (hi - lo - slat_w) / max(n - 1, 1)
            for i, uid in enumerate(group):
                center = [0.0, 0.0, z]
                center[axis] = lo + slat_w / 2 + i * pitch if n > 1 else (lo + hi) / 2
                half = [0.0, 0.0, thickness / 2]
                half[axis] = slat_w / 2
                reach = max(abs(off) for _, off in lines) + 0.1
                low, high = self.frame.free_run(cross, center, half, (-reach, reach))
                center[cross] = (low + high) / 2
                self.frame.put(uid, center, [0.0, 0.0, 0.0 if cross == 0 else 90.0], [(high - low) / length, 1.0, 1.0])
            return

        # Standing between the lowest and highest beams on one face.
        beams = sorted(joined, key=lambda b: self.frame.box(b)[1][2])
        lower = beams[0]
        upper = beams[-1] if len(beams) > 1 else None
        lo_box = self.frame.box(lower)
        axis = 0 if self.frame.half(lower)[0] >= self.frame.half(lower)[1] else 1
        bottom = lo_box[1][2]
        top = self.frame.box(upper)[0][2] if upper and self.frame.box(upper)[0][2] > bottom else frame_top
        run_lo, run_hi = lo_box[0][axis], lo_box[1][axis]
        inner = run_hi - run_lo
        rotation = [0.0, 90.0, 90.0] if axis == 0 else [0.0, 90.0, 0.0]
        for i, uid in enumerate(group):
            center = list(self.frame.final[lower])
            center[axis] = run_lo + inner * (i + 1) / (n + 1)
            center[2] = (bottom + top) / 2
            self.frame.put(uid, center, rotation, [(top - bottom) / length, min(1.0, inner / (2 * n + 1) / slat_w), 1.0])

    def frame_lines(self) -> List[Tuple[int, str]]:
        """(axis, uid) of every placed beam, and of every wall as a line along
        its plane (a side frame runs along Y)."""
        lines = []
        for uid in self.frame.final:
            if self.kind.get(uid) in ("beam", "wall"):
                half = self.frame.half(uid)
                lines.append((0 if half[0] >= half[1] else 1, uid))
        return lines

    def corner_slots(self) -> List[Dict[str, Any]]:
        """Inside corners where a part along X meets a part along Y: the
        point just inside both, at the lower of their joining heights."""
        lines = self.frame_lines()
        slots: List[Dict[str, Any]] = []
        seen = set()
        for ax, a in lines:
            if ax != 0:
                continue
            alo, ahi = self.frame.box(a)
            for bx_axis, b in lines:
                if bx_axis != 1:
                    continue
                blo, bhi = self.frame.box(b)
                # They must meet in plan (touching or overlapping in X and Y)
                # and share some height.
                if not all(alo[i] <= bhi[i] + 0.02 and blo[i] <= ahi[i] + 0.02 for i in range(3)):
                    continue
                x, y = self.frame.final[b][0], self.frame.final[a][1]
                level = min(self.attach_level(o) if self.kind[o] == "wall" else self.frame.top(o) for o in (a, b))
                key = (round(x, 3), round(y, 3), round(level, 3))
                if key in seen:
                    continue
                seen.add(key)
                slots.append({"x": x, "y": y, "level": level, "parts": {a, b},
                              "beams": all(self.kind[o] == "beam" for o in (a, b)),
                              "inset": (self.frame.half(b)[0], self.frame.half(a)[1])})
        return sorted(slots, key=lambda s: (round(s["y"], 3), round(s["x"], 3), round(s["level"], 3)))

    def place_blocks(self) -> None:
        """Brackets: each in a different inside corner, the corners that
        touch the most of the parts it is joined to first, slid toward the
        middle until clear of the parts there."""
        blocks = [u for u in self.of_kind("block", unplaced=True) if self.linked(u, ("beam", "upright", "wall"))]
        slots = self.corner_slots()

        uprights = [u for u in self.frame.final if self.kind.get(u) == "upright"]

        def near(o: str, slot: Dict[str, Any]) -> bool:
            lo, hi = self.frame.box(o)
            return lo[0] - 0.06 <= slot["x"] <= hi[0] + 0.06 and lo[1] - 0.06 <= slot["y"] <= hi[1] + 0.06

        def touches(uid: str, slot: Dict[str, Any]) -> int:
            # A corner with a leg or post in it is a real corner of the frame.
            count = 1 if any(near(u, slot) for u in uprights) else 0
            for o in self.linked(uid, ("beam", "upright", "wall")):
                if o in slot["parts"]:
                    count += 2
                    continue
                if near(o, slot):
                    count += 1
            return count

        choices = sorted(((touches(u, s), -i, u) for u in blocks for i, s in enumerate(slots)), key=lambda c: (-c[0], c[2], -c[1]))
        taken: Dict[str, int] = {}
        used = set()
        for score, neg_i, uid in choices:
            if score <= 1 or uid in taken or -neg_i in used:
                continue
            taken[uid] = -neg_i
            used.add(-neg_i)
        for uid in blocks:
            if uid in taken:
                self.place_in_slot(uid, slots[taken[uid]])
            else:
                self.place_block(uid)

    def place_in_slot(self, uid: str, slot: Dict[str, Any]) -> None:
        sx = 1 if slot["x"] >= 0 else -1
        sy = 1 if slot["y"] >= 0 else -1
        # Two rails meeting at a corner: the bracket lies across it.
        turn = math.degrees(math.atan2(sy, sx)) if slot["beams"] else 0.0
        self.frame.put(uid, [0.0, 0.0, 0.0], [0.0, 0.0, round(turn, 6)])
        hx, hy, hz = self.frame.half(uid)
        inset_x, inset_y = slot["inset"]
        self.frame.final[uid] = [slot["x"] - sx * (inset_x + hx), slot["y"] - sy * (inset_y + hy), slot["level"] - hz]
        self.push_clear(uid, [-sx, -sy])

    def place_block(self, uid: str) -> None:
        """A bracket with no corner: at the inner face of the part it is
        joined to, the copies at its two ends; joined to several, where
        they meet."""
        joined = self.linked(uid, ("beam", "upright", "wall"))
        if not joined:
            return
        bx, by, bz = self.dims(uid)
        if len(joined) == 1:
            host = joined[0]
            lo, hi = self.frame.box(host)
            center = self.frame.final[host]
            thin = 0 if hi[0] - lo[0] <= hi[1] - lo[1] else 1
            along = 1 - thin
            siblings = [u for u in self.group_of[uid] if self.linked(u, ("beam", "upright", "wall")) == joined]
            k = siblings.index(uid) if uid in siblings else 0
            inward = -1 if center[thin] > 0 else 1
            pos = [0.0, 0.0, 0.0]
            pos[thin] = (lo[thin] if inward < 0 else hi[thin]) + inward * [bx, by][thin] / 2
            end = -1 if k % 2 == 0 else 1
            pos[along] = center[along] + end * ((hi[along] - lo[along]) / 2 - [bx, by][along] / 2)
            pos[2] = self.attach_level(host) - bz / 2
            self.frame.put(uid, pos)
            self.push_clear(uid, [0.0 if a == thin else -end for a in range(2)])
            return

        boxes = [self.frame.box(o) for o in joined]
        point = [(max(b[0][axis] for b in boxes) + min(b[1][axis] for b in boxes)) / 2 for axis in range(3)]
        beams = [o for o in joined if self.kind[o] == "beam"]
        point[2] = min((self.frame.top(b) for b in beams), default=point[2] + bz / 2) - bz / 2
        self.frame.put(uid, point)
        self.push_clear(uid, [-point[0], -point[1]])

    def push_clear(self, uid: str, direction: Sequence[float], ignore: Iterable[str] = ()) -> None:
        """Slide a part along `direction` (horizontal) until it overlaps
        nothing placed."""
        dx, dy = direction[0], direction[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            return
        dx, dy = dx / length, dy / length
        for _ in range(PUSH_LIMIT):
            lo, hi = self.frame.box(uid)
            if not self.frame.colliders(lo, hi, ignore=[uid, *ignore]):
                return
            c = self.frame.final[uid]
            self.frame.final[uid] = [c[0] + dx * PUSH_STEP, c[1] + dy * PUSH_STEP, c[2]]

    def carcass_floor(self) -> float:
        """The height of the legs or feet a carcass stands on: uprights
        joined straight to its walls or its bottom (not a table's legs,
        which hold up a top), when they are shorter than the walls."""
        walls = [u for u in self.parts if self.kind[u] == "wall"]
        if not walls:
            return 0.0
        carcass = set(walls) | set(self.with_role("shelf"))
        feet = [u for u in self.of_kind("upright", unplaced=True) if self.links[u] & carcass]
        tallest = max(self.dims(u)[2] for u in walls)
        return max((self.dims(u)[2] for u in feet if self.dims(u)[2] < tallest / 2), default=0.0)

    def place_shelves(self) -> None:
        """A carcass's flat panels: a top (or lid) on the side walls, a bottom
        at their foot (on the plinth if there is one), dividers standing on
        the bottom, evenly spaced across, and the other shelves evenly
        spaced up each compartment between two of those walls."""
        side_walls = [w for w in self.walls()[0] if self.placed(w)]
        if len(side_walls) < 2:
            return
        dividers = self.with_role("divider")
        uprights = set(side_walls) | set(dividers)
        spanning = [u for u in self.of_kind("plate", unplaced=True)
                    if len(self.links[u] & uprights) >= 2 or self.role(u) in ("shelf", "top", "lid")]
        wall_top = min(self.frame.top(w) for w in side_walls)
        y = sum(self.frame.final[w][1] for w in side_walls) / len(side_walls)
        left = min(self.frame.box(w)[1][0] for w in side_walls)
        right = max(self.frame.box(w)[0][0] for w in side_walls)
        tops = [u for u in spanning if self.role(u) in ("top", "lid") or self.words[u] & TOP_WORDS]
        bottoms = [u for u in spanning if u not in tops and self.words[u] & BOTTOM_WORDS]
        middles = [u for u in spanning if u not in tops and u not in bottoms]
        boxes = [self.frame.box(w) for w in side_walls]
        outer = max(b[1][0] for b in boxes) - min(b[0][0] for b in boxes)
        deep = max(b[1][1] for b in boxes) - min(b[0][1] for b in boxes)

        def fitted(uid: str, w: float, d: float) -> Optional[List[float]]:
            """Scale for an unmeasured panel to cover w x d."""
            if is_measured(self.parts[uid]):
                return None
            x, yy, _ = self.dims(uid)
            return [w / x, d / yy, 1.0]

        for uid in tops:
            self.frame.put(uid, [0.0, y, wall_top + self.dims(uid)[2] / 2], scale=fitted(uid, outer, deep))
        plinths = [u for u in self.with_role("plinth") if self.placed(u)]
        low = max([self.frame.top(u) for u in plinths] or [self.floor if self.floor else STACK_BOTTOM_MARGIN])
        for uid in bottoms:
            self.frame.put(uid, [0.0, y, low + self.dims(uid)[2] / 2], scale=fitted(uid, right - left, deep))
        low = max([low] + [self.frame.top(u) for u in bottoms])

        # Dividers: from the bottom up to the top of the sides.
        for k, uid in enumerate(dividers):
            if self.placed(uid):
                continue
            h = self.dims(uid)[2]
            x = left + (right - left) * (k + 1) / (len(dividers) + 1)
            self.frame.put(uid, [x, y, (low + wall_top) / 2], scale=[1.0, 1.0, (wall_top - low) / h])

        # Compartments between neighbouring upright panels; each shelf goes to
        # one both of whose walls it is joined to, else to the emptiest.
        walls = sorted(side_walls + [d for d in dividers if self.placed(d)], key=lambda w: self.frame.final[w][0])
        bays = [(walls[i], walls[i + 1]) for i in range(len(walls) - 1)]
        shelves_in: Dict[int, List[str]] = {i: [] for i in range(len(bays))}
        for uid in middles:
            fits = [i for i, (a, b) in enumerate(bays) if {a, b} <= self.links[uid]]
            bay = min(fits or range(len(bays)), key=lambda i: (len(shelves_in[i]), i))
            shelves_in[bay].append(uid)
        high = wall_top - (0.0 if tops else max((self.dims(u)[2] for u in middles), default=0.0))
        for i, (a, b) in enumerate(bays):
            x0, x1 = self.frame.box(a)[1][0], self.frame.box(b)[0][0]
            for k, uid in enumerate(shelves_in[i]):
                z = low + (high - low) * (k + 1) / (len(shelves_in[i]) + 1)
                w = self.dims(uid)[0]
                scale = None if is_measured(self.parts[uid]) else [(x1 - x0) / w, 1.0, 1.0]
                self.frame.put(uid, [(x0 + x1) / 2, y, z], scale=scale)

    # -- doors, drawers and their hardware --

    def opening(self) -> Optional[Tuple[float, float, float, float, float, float]]:
        """The carcass's front opening: (x0, x1, z0, z1, front y, back y)
        between the side walls, above the bottom and below the top."""
        side_walls = [w for w in self.walls()[0] if self.placed(w)]
        if len(side_walls) < 2:
            return None
        boxes = [self.frame.box(w) for w in side_walls]
        x0 = min(b[1][0] for b in boxes)
        x1 = max(b[0][0] for b in boxes)
        # The front edge of the frame: the side walls, or the legs in front
        # of them (a frame-and-panel dresser).
        front = min([b[0][1] for b in boxes] + [self.frame.box(u)[0][1] for u in self.corner_side if self.placed(u)])
        back = max(b[1][1] for b in boxes)
        z1 = min(b[1][2] for b in boxes)
        bottoms = [u for u in self.of_kind("plate") if self.placed(u) and self.words[u] & BOTTOM_WORDS]
        plinths = [u for u in self.with_role("plinth") if self.placed(u)]
        z0 = max([self.frame.top(u) for u in bottoms + plinths] or [min(b[0][2] for b in boxes)])
        return x0, x1, z0, z1, front, back

    def place_fittings(self) -> None:
        """Doors and drawers fill the carcass's front opening: drawers in
        rows from the top (in a band above the doors when there are both),
        doors side by side below. Each drawer's sides, back, bottom and
        runners go behind its front; handles on the fronts; hinges at each
        door's hinge edge, or along a lid's back edge."""
        opening = self.opening()
        drawers = [u for u in self.with_role("drawer_front") if not self.placed(u)]
        doors = [u for u in self.with_role("door") if not self.placed(u)]
        fronts: List[str] = []
        if opening and (drawers or doors):
            x0, x1, z0, z1, front, back = opening
            band = z0
            if drawers:
                slots = self.pack_drawers(drawers, x0, x1, z0, z1, bool(doors))
                band = min(s[2] for s in slots.values())
                runners_each = max(2, len(self.with_role("runner")) // len(drawers))
                for uid in sorted(drawers, key=lambda u: (-slots[u][3], slots[u][0])):
                    self.place_front(uid, slots[uid], front)
                    self.place_drawer_box(slots[uid], front, back, runners_each)
                    fronts.append(uid)
            if doors:
                top = band if drawers else z1
                for uid, (bx0, bx1) in zip(doors, self.door_bays(len(doors), x0, x1)):
                    self.place_front(uid, (bx0, bx1, z0, top), front)
                    fronts.append(uid)
        self.place_hinges([u for u in fronts if self.role(u) == "door"])
        self.place_handles(fronts)
        self.place_back_cushions()

    def pack_drawers(self, drawers: List[str], x0: float, x1: float, z0: float, z1: float,
                     band: bool) -> Dict[str, Tuple[float, float, float, float]]:
        """Each drawer's slot (x0, x1, z0, z1). Drawers go into the bays
        between the sides and dividers (one column per bay, or by their
        measured widths), the shallowest first from the top; drawers narrow
        enough share a row. Rows are then stretched to fill the opening (or
        a band above the doors)."""
        dividers = sorted(self.frame.final[d][0] for d in self.with_role("divider") if self.placed(d))
        edges = [x0] + dividers + [x1]
        bays = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
        if len(bays) == 1:
            cols, _ = self.drawer_grid(drawers, x1 - x0)
            bays = [(x0 + (x1 - x0) * c / cols, x0 + (x1 - x0) * (c + 1) / cols) for c in range(cols)]
        order = sorted(drawers, key=lambda u: (self.dims(u)[2], self.dims(u)[0], u))
        # Deal the drawers to the bays in turn, keeping each bay in order.
        in_bay: List[List[str]] = [[] for _ in bays]
        for k, uid in enumerate(order):
            in_bay[k % len(bays)].append(uid)
        slots: Dict[str, Tuple[float, float, float, float]] = {}
        for (bx0, bx1), members in zip(bays, in_bay):
            width = bx1 - bx0
            rows: List[List[str]] = []
            used = 0.0
            for uid in members:
                w = min(self.dims(uid)[0], width) if is_measured(self.parts[uid]) else width
                if rows and used + w <= width * 1.05:
                    rows[-1].append(uid)
                    used += w
                else:
                    rows.append([uid])
                    used = w
            heights = [max(self.dims(u)[2] for u in row) for row in rows]
            bottom = z1 - min(0.5 * (z1 - z0), sum(heights)) if band else z0
            stretch = (z1 - bottom) / sum(heights)
            top = z1
            for row, h in zip(rows, heights):
                h *= stretch
                for k, uid in enumerate(row):
                    slots[uid] = (bx0 + width * k / len(row), bx0 + width * (k + 1) / len(row), top - h, top)
                top -= h
        return slots

    def drawer_grid(self, drawers: List[str], inner: float) -> Tuple[int, int]:
        """(columns, rows) of drawers: side by side when their measured
        fronts are narrow enough, or one column per compartment."""
        width = self.dims(drawers[0])[0]
        cols = 1
        if is_measured(self.parts[drawers[0]]) and width < 0.75 * inner:
            cols = max(1, round(inner / width))
        elif self.with_role("divider") and not self.with_role("door"):
            cols = len(self.with_role("divider")) + 1
        cols = min(cols, len(drawers))
        return cols, -(-len(drawers) // cols)

    def door_bays(self, n: int, x0: float, x1: float) -> List[Tuple[float, float]]:
        """Door widths: one per compartment when the counts match, else equal."""
        dividers = sorted(self.frame.final[d][0] for d in self.with_role("divider") if self.placed(d))
        if len(dividers) + 1 == n:
            edges = [x0] + dividers + [x1]
            return [(edges[i], edges[i + 1]) for i in range(n)]
        return [(x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n) for i in range(n)]

    def place_front(self, uid: str, slot: Tuple[float, float, float, float], front: float) -> None:
        """A door or drawer front over its slot, on the carcass's front edge."""
        sx0, sx1, sz0, sz1 = slot
        w, t, h = self.dims(uid)
        self.frame.put(uid, [(sx0 + sx1) / 2, front - t / 2, (sz0 + sz1) / 2],
                       scale=[(sx1 - sx0 - FRONT_GAP) / w, 1.0, (sz1 - sz0 - FRONT_GAP) / h])

    def place_drawer_box(self, slot: Tuple[float, float, float, float], front: float, back: float,
                         runners_each: int = 2) -> None:
        """The next drawer's sides, back, bottom and runners, behind its front:
        the first two runner pieces on the carcass either side, any next two
        on the drawer's sides."""
        sx0, sx1, sz0, sz1 = slot
        sides = [u for u in self.with_role("drawer_side") if not self.placed(u)][:2]
        backs = [u for u in self.with_role("drawer_back") if not self.placed(u)][:1]
        bottoms = [u for u in self.with_role("drawer_bottom") if not self.placed(u)][:1]
        runners = [u for u in self.with_role("runner") if not self.placed(u)][:runners_each]
        bx0, bx1 = sx0 + RUNNER_GAP, sx1 - RUNNER_GAP
        y0, y1 = front, back - DRAWER_LIFT
        zb = sz0 + DRAWER_LIFT
        bh = min(max(sz1 - sz0 - 2 * DRAWER_LIFT, 0.02), max((self.dims(u)[2] for u in sides + backs), default=0.12))
        for i, uid in enumerate(sides):
            t, d, h = self.dims(uid)
            x = bx0 + t / 2 if i == 0 else bx1 - t / 2
            self.frame.put(uid, [x, (y0 + y1) / 2, zb + bh / 2], scale=[1.0, (y1 - y0) / d, bh / h])
        side_t = max((self.dims(u)[0] for u in sides), default=0.0)
        for uid in backs:
            w, t, h = self.dims(uid)
            self.frame.put(uid, [(bx0 + bx1) / 2, y1 - t / 2, zb + bh / 2],
                           scale=[(bx1 - bx0 - 2 * side_t) / w, 1.0, bh / h])
        for uid in bottoms:
            w, d, t = self.dims(uid)
            self.frame.put(uid, [(bx0 + bx1) / 2, (y0 + y1) / 2, zb + t / 2],
                           scale=[(bx1 - bx0 - 2 * side_t) / w, (y1 - y0) / d, 1.0])
        for i, uid in enumerate(runners):
            length, t, h = self.dims(uid)
            # Carcass runners at the slot edges; drawer runners on the
            # drawer sides, just inside them.
            inset = 0.0 if i < 2 else side_t + t
            x = sx0 + t / 2 + inset if i % 2 == 0 else sx1 - t / 2 - inset
            self.frame.put(uid, [x, (y0 + y1) / 2, zb + bh * 0.4], [0.0, 0.0, 90.0], [(y1 - y0) / length, 1.0, 1.0])

    def place_hinges(self, doors: List[str]) -> None:
        """Two hinges per door just inside its hinge edge (the outer edge),
        near its top and bottom; with no doors, spread along the underside
        of a lid's back edge."""
        hinges = [u for u in self.with_role("hinge") if not self.placed(u)]
        if not hinges:
            return
        if doors:
            for i, uid in enumerate(hinges):
                door = doors[min(i // 2, len(doors) - 1)]
                lo, hi = self.frame.box(door)
                c = self.frame.final[door]
                hx, hy, hz = self.dims(uid)
                x = lo[0] + hx / 2 if c[0] <= 0 else hi[0] - hx / 2
                z = lo[2] + (hi[2] - lo[2]) * (0.1 if i % 2 == 0 else 0.9)
                self.frame.put(uid, [x, hi[1] + hy / 2, z])
            return
        lids = [u for u in self.with_role("lid", "top") if self.placed(u)]
        if lids:
            lo, hi = self.frame.box(lids[0])
            for i, uid in enumerate(hinges):
                hx, hy, hz = self.dims(uid)
                x = lo[0] + (hi[0] - lo[0]) * (i + 1) / (len(hinges) + 1)
                self.frame.put(uid, [x, hi[1] - hy / 2, lo[2] - hz / 2])

    def place_handles(self, fronts: List[str]) -> None:
        """A handle on each door and drawer front: the one it is joined to,
        else the next without one. Centred on a drawer; upright on a door,
        at the edge away from its hinges. Two on each front when there are
        twice as many handles as fronts."""
        handles = [u for u in self.with_role("handle") if not self.placed(u)]
        if not fronts or not handles:
            return
        # One per front; spare handles go to the widest fronts (two knobs on
        # a wide drawer, one on a small one).
        widest = sorted(fronts, key=lambda f: -(self.frame.box(f)[1][0] - self.frame.box(f)[0][0]))
        extra = set(widest[:max(0, len(handles) - len(fronts))])
        allowed = {f: 2 if f in extra else 1 for f in fronts}
        count: Dict[str, int] = {}
        for uid in handles:
            free = [f for f in fronts if count.get(f, 0) < allowed[f]]
            if not free:
                break
            front = next((f for f in free if f in self.links[uid]), free[0])
            k = count.get(front, 0)
            count[front] = k + 1
            lo, hi = self.frame.box(front)
            c = self.frame.final[front]
            _, hy, _ = self.dims(uid)
            if self.role(front) == "door":
                x = hi[0] - 0.05 if c[0] <= 0 else lo[0] + 0.05
                self.frame.put(uid, [x, lo[1] - hy / 2, c[2]], [0.0, 90.0, 0.0])
            else:
                x = c[0] if allowed[front] == 1 else c[0] + (hi[0] - lo[0]) * (-0.25 if k == 0 else 0.25)
                self.frame.put(uid, [x, lo[1] - hy / 2, c[2]])

    # -- upholstered bodies (sofas, chairs, ottomans) --

    def place_bodies(self) -> None:
        """Upholstered bodies stand side by side in a row along X, backs in
        line, from the base part outward (a body named "left" goes to the
        left). Feet go under the corners of the body they are joined to,
        seat cushions side by side on top of it, and the joining hardware in
        the joint between two bodies."""
        bodies = self.of_kind("body")
        if not bodies:
            return
        feet = [u for u in self.of_kind("upright") if self.links[u] & set(bodies)]
        self.floor = max((self.dims(u)[2] for u in feet), default=0.0)
        base = base_part(self.motion, self.structural())
        order = [base] if base in bodies else [bodies[0]]
        while len(order) < len(bodies):
            nxt = next((b for b in bodies if b not in order and self.links[b] & set(order)), None)
            order.append(nxt or next(b for b in bodies if b not in order))
        back = self.dims(order[0])[1] / 2
        left = right = 0.0
        for i, uid in enumerate(order):
            w, d, h = self.dims(uid)
            if i == 0:
                x, left, right = 0.0, -w / 2, w / 2
            elif word_side(self.words[uid], X_WORDS) < 0:
                x, left = left - w / 2, left - w
            else:
                x, right = right + w / 2, right + w
            # On its own feet; a body the manual shows no feet for (a sofa
            # the new section is fitted to) reaches down to the floor, its
            # top level with the bodies on feet.
            lift = max((self.dims(f)[2] for f in feet if uid in self.links[f]), default=0.0)
            if lift or not self.floor:
                self.frame.put(uid, [x, back - d / 2, lift + h / 2])
            else:
                self.frame.put(uid, [x, back - d / 2, (self.floor + h) / 2], scale=[1.0, 1.0, (self.floor + h) / h])

        corners = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        for body in order:
            lo, hi = self.frame.box(body)
            for i, uid in enumerate(f for f in feet if body in self.links[f] and not self.placed(f)):
                fx, fy, fh = self.dims(uid)
                sx, sy = corners[i % 4]
                self.frame.put(uid, [(lo[0] + hi[0]) / 2 + sx * ((hi[0] - lo[0]) / 2 - LEG_INSET - fx / 2),
                                     (lo[1] + hi[1]) / 2 + sy * ((hi[1] - lo[1]) / 2 - LEG_INSET - fy / 2), fh / 2])
            seat_z, rest_y = self.body_seat(body)
            backs = [u for u in self.with_role("back_cushion") if body in self.links[u]]
            back_d = max((self.dims(u)[1] for u in backs), default=0.0)
            seats = [u for u in self.of_kind("plate", unplaced=True) if body in self.links[u]]
            for k, uid in enumerate(seats):
                w, d, t = self.dims(uid)
                span = (hi[0] - lo[0]) / len(seats)
                front_y, back_y = lo[1], rest_y - back_d
                # Unknown sizes fill the seat, in front of the back cushions.
                scale = None if is_measured(self.parts[uid]) else [span / w, (back_y - front_y) / d, 1.0]
                y = (front_y + back_y) / 2 if scale else min(back_y - d / 2, (lo[1] + hi[1]) / 2)
                self.frame.put(uid, [lo[0] + span * (k + 0.5), y, seat_z + t / 2], scale=scale)

        self.place_body_sides(order)
        self.place_joint_hardware(order)

    def place_body_sides(self, bodies: List[str]) -> None:
        """A side piece fitted to a body (an armrest) stands against the
        body's open side, the one with no other body next to it, back in
        line with it."""
        for body in bodies:
            lo, hi = self.frame.box(body)
            right_open = not any(o != body and abs(self.frame.box(o)[0][0] - hi[0]) < 1e-6 for o in bodies)
            for uid in self.of_kind("wall", unplaced=True):
                if body not in self.links[uid]:
                    continue
                t, d, h = self.dims(uid)
                x = hi[0] + t / 2 if right_open else lo[0] - t / 2
                self.frame.put(uid, [x, hi[1] - d / 2, h / 2])

    def place_back_cushions(self) -> None:
        """Back cushions stand on their body's back edge, side by side."""
        for body in self.of_kind("body"):
            backs = [u for u in self.with_role("back_cushion") if body in self.links[u] and not self.placed(u)]
            if not backs:
                continue
            lo, hi = self.frame.box(body)
            seat_z, rest_y = self.body_seat(body)
            span = (hi[0] - lo[0]) / len(backs)
            for k, uid in enumerate(backs):
                w, d, h = self.dims(uid)
                scale = None if is_measured(self.parts[uid]) or len(backs) == 1 else [span / w, 1.0, 1.0]
                self.frame.put(uid, [lo[0] + span * (k + 0.5), rest_y - d / 2, seat_z + h / 2], scale=scale)

    def body_seat(self, body: str) -> Tuple[float, float]:
        """(seat height, the y where its backrest starts) of a body: from its
        traced side outline when it has one (seat height measured a third
        of the way back, backrest where the top rises above it), else its
        top and its back edge."""
        lo, hi = self.frame.box(body)
        profile = self.parts[body].get("profile") or {}
        points = profile.get("path", [])
        if not (profile.get("closed") and profile.get("plane", "side") == "side" and len(points) > 2):
            return hi[2], hi[1]
        us, vs = [p[0] for p in points], [p[1] for p in points]
        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)

        def top_at(u: float) -> float:
            tops = []
            for (ua, va), (ub, vb) in zip(points, points[1:] + points[:1]):
                if min(ua, ub) <= u <= max(ua, ub) and ua != ub:
                    tops.append(va + (vb - va) * (u - ua) / (ub - ua))
            return max(tops) if tops else v1

        seat_v = top_at(u0 + (u1 - u0) / 3)
        rest_u = next((u0 + (u1 - u0) * k / 50 for k in range(50, -1, -1)
                       if top_at(u0 + (u1 - u0) * k / 50) <= seat_v + 0.05 * (v1 - v0)), u1)
        to_y = (hi[1] - lo[1]) / (u1 - u0)
        to_z = (hi[2] - lo[2]) / (v1 - v0)
        return lo[2] + (seat_v - v0) * to_z, lo[1] + (rest_u - u0) * to_y

    def place_joint_hardware(self, bodies: List[str]) -> None:
        """Rails and brackets joined to a body (or to such a rail) go in the
        joint between it and the body next to it: rails low and along the
        joint, brackets spread along it above them."""
        hardware = [u for u in sorted(self.parts) if self.kind[u] in ("beam", "block") and not self.placed(u)]
        joined = [u for u in hardware if self.links[u] & set(bodies)]
        joined += [u for u in hardware if u not in joined and self.links[u] & set(joined)]
        if not joined:
            return

        sides = [w for w in self.of_kind("wall") if self.placed(w) and self.links[w] & set(bodies)]

        def joint_x(body: str, uid: str = "") -> float:
            lo, hi = self.frame.box(body)
            # Hardware fixing a side piece goes in the joint with that piece.
            for side in sides:
                if side in self.links.get(uid, ()) and body in self.links[side]:
                    slo, shi = self.frame.box(side)
                    return slo[0] if slo[0] >= hi[0] - 1e-6 else shi[0]
            for other in bodies:
                olo, ohi = self.frame.box(other)
                if other != body and abs(olo[0] - hi[0]) < 1e-6:
                    return hi[0]
                if other != body and abs(ohi[0] - lo[0]) < 1e-6:
                    return lo[0]
            return hi[0]

        body_of = {u: next((b for b in bodies if b in self.links[u]), bodies[0]) for u in joined}
        z = self.floor + HARDWARE_LIFT
        for uid in (u for u in joined if self.kind[u] == "beam"):
            length, _, h = self.dims(uid)
            lo, hi = self.frame.box(body_of[uid])
            scale = [min(1.0, 0.9 * (hi[1] - lo[1]) / length), 1.0, 1.0]
            self.frame.put(uid, [joint_x(body_of[uid], uid), (lo[1] + hi[1]) / 2, z + h / 2], [0.0, 0.0, 90.0], scale)
            z += h + HARDWARE_LIFT
        blocks = [u for u in joined if self.kind[u] == "block"]
        for k, uid in enumerate(blocks):
            lo, hi = self.frame.box(body_of[uid])
            y = (lo[1] + hi[1]) / 2 + (k - (len(blocks) - 1) / 2) * HARDWARE_SPREAD
            self.frame.put(uid, [joint_x(body_of[uid], uid), y, z + self.dims(uid)[2] / 2])

    def place_plate(self, uid: str, frame_top: float) -> None:
        """A seat or other plate: on top of the highest part it is joined
        to, centred over them."""
        joined = self.linked(uid)
        t = self.dims(uid)[2]
        if not joined:
            self.frame.put(uid, [0.0, 0.0, frame_top + t / 2])
            return
        # It rests on the rails or brackets it is joined to; only with none
        # does it go to the joining height of the uprights.
        resting = [o for o in joined if self.kind[o] not in VERTICAL_KINDS] or joined
        level = max(self.attach_level(o) if self.kind[o] in VERTICAL_KINDS else self.frame.top(o) for o in resting)
        boxes = [self.frame.box(o) for o in joined]
        # Centred over what it rests on; along an axis where that is much
        # narrower than the plate (one side frame), on the frame's middle.
        center = [0.0, 0.0, level + t / 2]
        for axis in (0, 1):
            lo, hi = min(b[0][axis] for b in boxes), max(b[1][axis] for b in boxes)
            if hi - lo >= self.dims(uid)[axis] / 2:
                center[axis] = (lo + hi) / 2
        # A cushion or pad of unknown size covers the plate it lies on.
        scale = None
        hosts = [o for o in joined if self.kind[o] == "plate"]
        if hosts and not is_measured(self.parts[uid]):
            hlo, hhi = self.frame.box(hosts[0])
            w, d, _ = self.dims(uid)
            scale = [(hhi[0] - hlo[0]) / w, (hhi[1] - hlo[1]) / d, 1.0]
            center[0], center[1] = (hlo[0] + hhi[0]) / 2, (hlo[1] + hhi[1]) / 2
        self.frame.put(uid, center, scale=scale)

    def place_leftover(self, uid: str) -> None:
        """Anything no rule placed: on top of the first placed part it is
        joined to, slid outward until clear."""
        joined = self.linked(uid)
        if not joined:
            return
        host = joined[0]
        c = self.frame.final[host]
        self.frame.put(uid, [c[0], c[1], self.frame.top(host) + self.dims(uid)[2] / 2])
        self.push_clear(uid, [c[0] or 1.0, c[1]])

    # -- 4. fasteners, flip, start positions --

    def apply_tilts(self) -> None:
        """Parts with a lean (tilt_deg) turn back about a line across X
        through the bottom of their box: a chair back's top goes back, a
        seat's back edge goes down. A part joined between two parts that
        lean the same way about the same line (slats between back uprights)
        leans with them."""
        frame = self.frame
        pivots: Dict[str, Tuple[float, float, float]] = {}
        for uid in self.parts:
            tilt = float(self.parts[uid].get("tilt_deg") or 0.0)
            if tilt and self.placed(uid):
                lo, _ = frame.box(uid)
                pivots[uid] = (tilt, round(frame.final[uid][1], 4), round(lo[2], 4))
        for uid in self.parts:
            if uid in pivots or not self.placed(uid):
                continue
            leaning = [pivots[o] for o in self.links[uid] if o in pivots]
            if len(leaning) >= 2 and len(set(leaning)) == 1:
                pivots[uid] = leaning[0]
        for uid, (tilt, y0, z0) in pivots.items():
            angle = math.radians(-tilt)
            x, y, z = frame.final[uid]
            dy, dz = y - y0, z - z0
            frame.final[uid] = [x, y0 + dy * math.cos(angle) - dz * math.sin(angle),
                                z0 + dy * math.sin(angle) + dz * math.cos(angle)]
            frame.rotation[uid] = euler_from_matrix(matmul(rotation_matrix([-tilt, 0.0, 0.0]),
                                                           rotation_matrix(frame.rotation.get(uid, [0.0, 0.0, 0.0]))))

    def finish(self) -> Dict[str, Any]:
        self.apply_tilts()
        frame = self.frame
        instance_of = place_fastener_instances(frame.shapes, self.graph, frame.final, frame.rotation, frame.scale)
        for inst in instance_of:
            frame.rotation.setdefault(inst, [0.0, 0.0, 0.0])

        height = max((frame.top(u) for u in self.parts if u in frame.final), default=1.0)
        base = base_part(self.motion, self.structural())
        pivot = None
        if base in frame.final and frame.box(base)[0][2] >= height / 2:
            # Built upside down from a part that ends up on top: lay it all
            # out turned 180 degrees about X through the middle; the finale
            # turns it back.
            pivot = [0.0, 0.0, height / 2]
            flip = rotation_matrix([180.0, 0.0, 0.0])
            for uid in list(frame.final):
                x, y, z = frame.final[uid]
                frame.final[uid] = [x, -y, height - z]
                frame.rotation[uid] = euler_from_matrix(matmul(flip, rotation_matrix(frame.rotation.get(uid, [0.0, 0.0, 0.0]))))

        return {
            "final": frame.final,
            "exploded": explode_outward(frame.final, [0.0, 0.0, height / 2]),
            "rotation": frame.rotation,
            "scale": frame.scale,
            "instance_of": instance_of,
            "pivot": pivot,
        }


def compute_general_positions(shapes: Dict[str, Dict[str, Any]], graph: Dict[str, Any],
                              motion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Final/exploded/rotation/scale per node, fastener instances and the
    flip pivot (None when built upright). None when there are no parts."""
    layout = GeneralLayout(shapes, graph, motion)
    if not layout.parts:
        return None
    return layout.compute()


# --- fasteners and start positions (shared with scene_layout_engine) ---------

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
