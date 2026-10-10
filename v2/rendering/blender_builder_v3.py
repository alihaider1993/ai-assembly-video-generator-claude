import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from config import RENDER_TIMELINE_JSON


GRAPH_PATH = Path("v2/outputs/json/universal_assembly_graph.json")
MOTION_PATH = Path("v2/outputs/json/motion_plan.json")
SCENE_LAYOUT_PATH = Path("v2/outputs/json/scene_layout.json")
PROXY_GEOMETRY_PATH = Path("v2/output/proxy_geometry.json")
OUTPUT_SCRIPT = Path("blender/generated/v3_generated_blender_scene.py")

# Video timing, in frames at 24 fps. Steps that only move fasteners are
# shorter than steps that move parts; the gap between steps is when the
# camera re-frames.
INTRO_FRAMES = 24
PART_STEP_FRAMES = 32
FASTENER_STEP_FRAMES = 22
STEP_GAP_FRAMES = 10
FINALE_PAUSE_FRAMES = 12
FLIP_FRAMES = 60
ORBIT_FRAMES = 120
END_HOLD_FRAMES = 24

ACTION_VERBS = {
    "insert": ("Insert", "into"),
    "attach": ("Attach", "to"),
    "insert_and_rotate": ("Screw in", "into"),
    "rotate": ("Turn", "on"),
    "slide": ("Slide", "onto"),
    "lower": ("Lower", "onto"),
}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    value = int(raw)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value}")
    return value


def base_uid(scene_object: Dict[str, Any]) -> str:
    """The graph node a scene object stands for (a fastener instance
    stands for its fastener)."""
    return scene_object.get("instance_of") or scene_object.get("node_uid", "")


def validate_inputs(motion: Any, scene_layout: Any) -> None:
    """Refuse to generate a script that would render an empty or static scene."""
    layout_uids = {
        base_uid(obj)
        for obj in scene_layout.get("scene_objects", [])
        if obj.get("node_uid")
    }
    if not layout_uids:
        raise ValueError(f"{SCENE_LAYOUT_PATH} has no scene_objects; nothing to render")

    steps = motion.get("steps", [])
    if not steps:
        raise ValueError(f"{MOTION_PATH} has no steps; nothing to animate")

    animatable = [
        uid
        for step in steps
        for uid in step.get("moving_nodes", [])
        if uid in layout_uids
    ]
    if not animatable:
        raise ValueError(
            "No motion step moves a node that exists in scene_layout.json; "
            "the render would be a static scene"
        )


def display_name(name: str) -> str:
    """'long rail 2/2' -> 'long rail'."""
    return re.sub(r"\s+\d+\s*/\s*\d+$", "", str(name)).strip()


# Words naming a fastener; "<part word> <one of these>" is that fastener.
HARDWARE_WORDS = {"pin", "pins", "bolt", "bolts", "screw", "screws", "dowel", "dowels", "plug", "plugs", "lock", "locks",
                  "nut", "nuts", "washer", "washers", "holder", "holders", "plate", "plates", "pad", "pads", "nail", "nails"}


def step_caption(step: Dict[str, Any], moving: List[str], by_uid: Dict[str, Dict[str, Any]]) -> str:
    verb, preposition = ACTION_VERBS.get(step.get("action_type", ""), ("Fit", "to"))

    counts: Dict[str, int] = {}
    for uid in moving:
        name = display_name(by_uid[uid].get("name", uid))
        counts[name] = counts.get(name, 0) + 1
    # The manual's own count ("4x screw 119046") beats the number of copies
    # drawn, which is one per part a fastener goes into.
    evidence = step.get("visual_evidence", "")
    for name in counts:
        words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if len(w) > 2]
        for match in re.finditer(r"(\d+)\s*x\s+([a-z0-9]+(?: [a-z0-9]+){0,3})", evidence.lower()):
            said = match.group(2)
            # "4x shelf pin" counts pins, not the shelf they hold.
            if said.split()[1:2] and said.split()[1] in HARDWARE_WORDS and said.split()[1] not in words:
                continue
            if words and (words[-1] in said.split() or name.lower() in said):
                counts[name] = int(match.group(1))
                break
    items = [f"{count} x {name}" if count > 1 else name for name, count in counts.items()]
    text = f"{verb} {' and '.join(items)}"

    targets = [by_uid[t] for t in step.get("target_nodes", []) if t in by_uid and t not in moving]
    if targets:
        text += f" {preposition} {display_name(targets[0].get('name', ''))}"
    return text


def build_timeline(motion: Dict[str, Any], scene_layout: Dict[str, Any]) -> Dict[str, Any]:
    """Frame timing for the video: one entry per motion step that still has
    something to move (a node moved by an earlier step stays assembled),
    then the finale (turn-over, if the layout asks for it) and a slow orbit
    around the finished assembly. Also the on-screen captions."""
    scene_objects = scene_layout.get("scene_objects", [])
    by_uid = {obj["node_uid"]: obj for obj in scene_objects if obj.get("node_uid")}
    instances: Dict[str, List[str]] = {}
    for uid, obj in by_uid.items():
        instances.setdefault(base_uid(obj), []).append(uid)

    # A run of steps doing the same thing to the same kind of part (four
    # legs attached one after another) plays as one step that moves them
    # all together.
    moved = set()
    merged: List[Dict[str, Any]] = []
    for step in sorted(motion.get("steps", []), key=lambda s: s.get("start_frame", 1)):
        moving = [
            uid
            for node in step.get("moving_nodes", [])
            for uid in instances.get(node, [])
            if uid not in moved
        ]
        if not moving:
            continue
        moved.update(moving)

        kinds = sorted({display_name(by_uid[uid].get("name", uid)) for uid in moving})
        previous = merged[-1] if merged else None
        if previous and previous["step"].get("action_type") == step.get("action_type") and previous["kinds"] == kinds:
            previous["moving"].extend(moving)
        else:
            merged.append({"step": step, "moving": moving, "kinds": kinds})

    steps = []
    frame = 1 + INTRO_FRAMES
    for entry in merged:
        step, moving = entry["step"], entry["moving"]
        fasteners_only = all(by_uid[uid].get("node_type") == "fastener" for uid in moving)
        duration = FASTENER_STEP_FRAMES if fasteners_only else PART_STEP_FRAMES
        steps.append({
            "step_uid": step.get("step_uid", ""),
            "moving_nodes": moving,
            "start_frame": frame,
            "end_frame": frame + duration,
            "caption": step_caption(step, moving, by_uid),
        })
        frame += duration + STEP_GAP_FRAMES

    # Sub-assemblies (scene_layout_engine.stage_subassemblies): a base part
    # shows up at its staging spot with the first part fitted to it, and its
    # own step carries everything on it one level closer to its place.
    def bases_moving(step: Dict[str, Any]) -> set:
        return {base_uid(by_uid[u]) for u in step["moving_nodes"]}

    for step in steps:
        step["carried"], step["reveal"] = [], []
    for uid, obj in by_uid.items():
        for carry in obj.get("carry", []):
            step = next((s for s in steps if carry["base"] in bases_moving(s)), None)
            if step is not None:
                step["carried"].append({"uid": uid, "from": carry["from"], "to": carry["to"]})
        if obj.get("reveal_with"):
            step = next((s for s in steps if bases_moving(s) & set(obj["reveal_with"])), None)
            if step is not None and uid not in step["moving_nodes"]:
                step["reveal"].append(uid)

    last_end = steps[-1]["end_frame"] if steps else 1
    flips = scene_layout.get("finale", {}).get("type") == "flip"
    flip_start = last_end + FINALE_PAUSE_FRAMES
    flip_end = flip_start + FLIP_FRAMES if flips else flip_start
    orbit_start = flip_end + STEP_GAP_FRAMES
    orbit_end = orbit_start + ORBIT_FRAMES
    frame_end = orbit_end + END_HOLD_FRAMES

    captions = []
    for index, step in enumerate(steps):
        captions.append({
            "start_frame": step["start_frame"] - STEP_GAP_FRAMES // 2,
            "end_frame": step["end_frame"] + STEP_GAP_FRAMES // 2,
            "label": f"Step {index + 1} of {len(steps)}",
            "text": step["caption"],
        })
    if flips:
        captions.append({
            "start_frame": flip_start - FINALE_PAUSE_FRAMES // 2,
            "end_frame": flip_end,
            "label": "Finish",
            "text": "Turn the assembly over",
        })
    captions.append({
        "start_frame": orbit_start,
        "end_frame": frame_end,
        "label": "Done",
        "text": "Assembly complete",
    })

    return {
        "fps": motion.get("fps", 24),
        "steps": steps,
        "flip": {"start_frame": flip_start, "end_frame": flip_end} if flips else None,
        "orbit": {"start_frame": orbit_start, "end_frame": orbit_end},
        "frame_end": frame_end,
        "captions": captions,
    }


def build_blender_script():
    project_root = PROJECT_ROOT

    graph = load_json(project_root / GRAPH_PATH)
    motion = load_json(project_root / MOTION_PATH)
    scene_layout = load_json(project_root / SCENE_LAYOUT_PATH)
    proxy_geometry = load_json(project_root / PROXY_GEOMETRY_PATH)

    validate_inputs(motion, scene_layout)

    timeline = build_timeline(motion, scene_layout)
    if not timeline["steps"]:
        raise ValueError("No motion step moves an object in scene_layout.json; nothing to animate")

    RENDER_TIMELINE_JSON.parent.mkdir(parents=True, exist_ok=True)
    RENDER_TIMELINE_JSON.write_text(json.dumps(timeline, indent=2), encoding="utf-8")

    # Optional overrides for quick preview renders; defaults keep full quality.
    resolution_percent = env_int("V3_RESOLUTION_PERCENT", 100, 10, 100)
    frame_step = env_int("V3_FRAME_STEP", 1, 1, 24)
    # The render engine: EEVEE (default) needs a GPU; a server without one
    # uses WORKBENCH (fast, flat studio light) or CYCLES on the CPU.
    render_engine = os.environ.get("V3_RENDER_ENGINE", "").strip().upper() or "EEVEE"
    if render_engine not in ("EEVEE", "WORKBENCH", "CYCLES"):
        raise ValueError(f"V3_RENDER_ENGINE must be EEVEE, WORKBENCH or CYCLES, got {render_engine}")
    cycles_samples = env_int("V3_CYCLES_SAMPLES", 16, 1, 1024)

    output_script = project_root / OUTPUT_SCRIPT

    script = f"""
import bpy
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector

PROJECT_ROOT = Path(r"{project_root}")
sys.path.insert(0, str(PROJECT_ROOT))

from config import FRAMES_V3_DIR, ensure_project_dirs

GRAPH = {repr(graph)}
SCENE_LAYOUT = {repr(scene_layout)}
PROXY_GEOMETRY = {repr(proxy_geometry)}
TIMELINE = {repr(timeline)}

ensure_project_dirs()

OUTPUT_DIR = FRAMES_V3_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Clear old frames before rendering
for old_frame in OUTPUT_DIR.glob("*.png"):
    old_frame.unlink()

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()


# A part glows in this colour while it moves: each material mixes it in by
# the object's "highlight" property (0..1), which is keyframed per step.
HIGHLIGHT_COLOR = (1.0, 0.42, 0.05, 1.0)
HIGHLIGHT_EMISSION = 0.35


def socket(sockets, name, kind):
    return next(s for s in sockets if s.name == name and s.type == kind)


def mat(name, color, roughness=0.45, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Emission Color"].default_value = HIGHLIGHT_COLOR

    highlight = nodes.new("ShaderNodeAttribute")
    highlight.attribute_type = "OBJECT"
    highlight.attribute_name = "highlight"

    mix = nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    socket(mix.inputs, "A", "RGBA").default_value = color
    socket(mix.inputs, "B", "RGBA").default_value = HIGHLIGHT_COLOR
    links.new(highlight.outputs["Fac"], mix.inputs["Factor"])
    links.new(socket(mix.outputs, "Result", "RGBA"), bsdf.inputs["Base Color"])

    glow = nodes.new("ShaderNodeMath")
    glow.operation = "MULTIPLY"
    glow.inputs[1].default_value = HIGHLIGHT_EMISSION
    links.new(highlight.outputs["Fac"], glow.inputs[0])
    links.new(glow.outputs["Value"], bsdf.inputs["Emission Strength"])

    material.diffuse_color = color
    return material


MATERIALS = {{
    "wood": mat("Birch Wood Proxy", (0.66, 0.45, 0.26, 1), 0.5, 0.0),
    "metal": mat("Dark Metal Proxy", (0.10, 0.11, 0.13, 1), 0.35, 0.6),
    "fabric": mat("Light Fabric Proxy", (0.70, 0.70, 0.66, 1), 0.7, 0.0),
    "plastic": mat("Moulded Plastic Proxy", (0.86, 0.86, 0.84, 1), 0.4, 0.0),
    "fibreboard": mat("Hardboard Proxy", (0.42, 0.30, 0.20, 1), 0.75, 0.0),
    "fastener": mat("Steel Fastener", (0.62, 0.63, 0.66, 1), 0.3, 0.9),
    "hole": mat("Black Hole Marker", (0.01, 0.01, 0.01, 1), 0.5, 0.0),
    "floor": mat("Studio Floor", (0.50, 0.53, 0.58, 1), 0.6, 0.0),
}}


def create_empty(uid, location):
    obj = bpy.data.objects.new(uid, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = 0.25
    obj.location = Vector(location)
    return obj


# Every board's edges are slightly rounded so they catch the light: the
# seams between drawer fronts, and a panel's edge against the one behind it,
# then show instead of merging into one flat face.
EDGE_BEVEL = 0.0015


def create_box(name, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    width = min(EDGE_BEVEL, min(dimensions) * 0.25)
    if width > 0:
        bevel = obj.modifiers.new("Edge_Bevel", "BEVEL")
        bevel.width = width
        bevel.segments = 2
    return obj


def create_cylinder(name, dimensions, material):
    radius = max(dimensions[0], dimensions[1]) / 2
    depth = dimensions[2]
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=depth,
        location=(0, 0, 0)
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def create_rounded_box(name, dimensions, material):
    obj = create_box(name, dimensions, material)
    bevel = obj.modifiers.new("Rounded_Corners", "BEVEL")
    bevel.width = min(0.08, min(dimensions) * 0.3)
    bevel.segments = 4
    obj.modifiers.new("Weighted_Normal", "WEIGHTED_NORMAL")
    return obj


def join_boxes(name, pieces, material):
    # One mesh from (dimensions, centre) boxes laid out around the origin.
    boxes = []
    for dimensions, location in pieces:
        box = create_box(name, dimensions, material)
        box.location = Vector(location)
        boxes.append(box)
    bpy.ops.object.select_all(action="DESELECT")
    for box in boxes:
        box.select_set(True)
    bpy.context.view_layer.objects.active = boxes[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    # Origin back at the centre of the whole frame.
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return obj


def create_u_frame(name, dimensions, material):
    # Two legs joined by a rail across their tops, e.g. a chair's front legs.
    width, depth, height = dimensions
    rail_height = min(0.07, height * 0.2)
    leg_x = width / 2 - depth / 2
    return join_boxes(name, [
        ([depth, depth, height], (-leg_x, 0, 0)),
        ([depth, depth, height], (leg_x, 0, 0)),
        ([width - 2 * depth, depth * 0.8, rail_height], (0, 0, height / 2 - rail_height / 2)),
    ], material)


BACK_SLATS = 5


def create_slatted_back(name, dimensions, material):
    # A chair back: two tall back legs, a top rail, a lower rail just above
    # seat height and vertical slats between the rails.
    width, depth, height = dimensions
    inner = width - 2 * depth
    leg_x = width / 2 - depth / 2
    top_height, low_height = 0.08, 0.05
    top_z = height / 2 - top_height / 2
    low_z = -height / 2 + height * 0.58
    slat_bottom, slat_top = low_z + low_height / 2, top_z - top_height / 2
    slat_width = inner / (2 * BACK_SLATS + 1)
    pieces = [
        ([depth, depth, height], (-leg_x, 0, 0)),
        ([depth, depth, height], (leg_x, 0, 0)),
        ([inner, depth, top_height], (0, 0, top_z)),
        ([inner, depth * 0.8, low_height], (0, 0, low_z)),
    ]
    for i in range(BACK_SLATS):
        x = -inner / 2 + slat_width * (2 * i + 1.5)
        pieces.append(([slat_width, depth * 0.5, slat_top - slat_bottom], (x, 0, (slat_top + slat_bottom) / 2)))
    return join_boxes(name, pieces, material)


SIDE_FRAME_SEAT_FRACTION = 0.48  # same as general_layout.py


def create_side_frame(name, dimensions, material):
    # A chair side standing in the Y/Z plane: a front leg up to seat height,
    # a full-height back leg, a seat rail between them and a lower rail.
    thickness, depth, height = dimensions
    seat_height = height * SIDE_FRAME_SEAT_FRACTION
    bottom = -height / 2
    leg_y = depth / 2 - thickness / 2
    inner = depth - 2 * thickness
    rail_height, low_height = 0.07, 0.035
    return join_boxes(name, [
        ([thickness, thickness, seat_height], (0, -leg_y, bottom + seat_height / 2)),
        ([thickness, thickness, height], (0, leg_y, 0)),
        ([thickness * 0.8, inner, rail_height], (0, 0, bottom + seat_height - rail_height / 2)),
        ([thickness * 0.8, inner, low_height], (0, 0, bottom + seat_height * 0.4)),
    ], material)


def profile_axes(plane):
    # (axis of u, axis of v, axis the outline is extruded along) for an
    # outline traced in the side view (y, z), front view (x, z) or from
    # above (x, y).
    if plane == "front":
        return 0, 2, 1
    if plane == "top":
        return 0, 1, 2
    return 1, 2, 0


def prism_mesh(name, polygons, axes, depth, material):
    # One mesh: each 2D polygon extruded `depth` along the third axis.
    u_axis, v_axis, w_axis = axes
    verts, faces = [], []
    for polygon in polygons:
        n = len(polygon)
        base = len(verts)
        for w in (-depth / 2, depth / 2):
            for u, v in polygon:
                point = [0.0, 0.0, 0.0]
                point[u_axis], point[v_axis], point[w_axis] = u, v, w
                verts.append(point)
        faces.append(list(range(base, base + n))[::-1])
        faces.append(list(range(base + n, base + 2 * n)))
        for i in range(n):
            j = (i + 1) % n
            faces.append([base + i, base + j, base + n + j, base + n + i])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.data.materials.append(material)
    return obj


def create_profile(name, dimensions, profile, material):
    # A traced outline (mm), centred in the part's box. A closed outline
    # ("closed": True) is filled: a sofa body's side, seat and backrest.
    # Otherwise it is a strip `thickness` wide along the path, with a round
    # joint at each bend: bentwood frames, curved slats and uprights.
    path = [(p[0] / 1000.0, p[1] / 1000.0) for p in profile.get("path", [])]
    axes = profile_axes(profile.get("plane", "side"))
    depth = dimensions[axes[2]]
    if len(path) < 2:
        return create_box(name, dimensions, material)
    thickness = profile.get("thickness", 30) / 1000.0
    mid_u = (min(p[0] for p in path) + max(p[0] for p in path)) / 2
    mid_v = (min(p[1] for p in path) + max(p[1] for p in path)) / 2
    points = [(u - mid_u, v - mid_v) for u, v in path]
    if profile.get("closed"):
        polygons = [points]
    else:
        polygons = []
        half = thickness / 2
        for (u0, v0), (u1, v1) in zip(points, points[1:]):
            length = math.hypot(u1 - u0, v1 - v0)
            if length < 1e-6:
                continue
            nu, nv = -(v1 - v0) / length * half, (u1 - u0) / length * half
            polygons.append([(u0 + nu, v0 + nv), (u1 + nu, v1 + nv), (u1 - nu, v1 - nv), (u0 - nu, v0 - nv)])
        for u, v in points[1:-1]:
            polygons.append([(u + half * math.cos(a * math.pi / 8), v + half * math.sin(a * math.pi / 8)) for a in range(16)])
    obj = prism_mesh(name, polygons, axes, depth, material)
    if profile.get("closed") and profile.get("rounded", True):
        bevel = obj.modifiers.new("Rounded_Corners", "BEVEL")
        bevel.width = min(0.06, depth * 0.15)
        bevel.segments = 3
    return obj


COMPOSITE_PRIMITIVES = ("u_frame", "slatted_back", "side_frame", "profile")


MIN_HOLE_RADIUS = 0.008


def add_holes(mesh, holes, dimensions):
    # Holes go on the largest face: the underside of a flat part (thinnest
    # along Z), otherwise the -Y face.
    flat = dimensions[2] <= min(dimensions[0], dimensions[1])
    for i, hole in enumerate(holes, start=1):
        rel = hole.get("relative_position", [0.5, 0.5])
        x = (rel[0] - 0.5) * dimensions[0]
        if flat:
            y = (rel[1] - 0.5) * dimensions[1]
            z = -dimensions[2] / 2
        else:
            y = -dimensions[1] / 2
            z = (rel[1] - 0.5) * dimensions[2]

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=6,
            radius=max(hole.get("radius_hint", 0.04), MIN_HOLE_RADIUS),
            location=(x, y, z)
        )
        h = bpy.context.object
        h.name = f"{{mesh.name}}_hole_{{i}}"
        h.data.materials.append(MATERIALS["hole"])
        h.parent = mesh


def proxy_lookup():
    result = {{}}
    for obj in PROXY_GEOMETRY.get("objects", []):
        part_uid = obj.get("part_uid")
        if part_uid:
            result[part_uid] = obj
    return result


def graph_node_lookup():
    result = {{}}

    for p in GRAPH.get("parts", []):
        uid = p.get("part_uid")
        if uid:
            result[uid] = p

    for a in GRAPH.get("assemblies", []):
        uid = a.get("assembly_uid")
        if uid:
            result[uid] = a

    for f in GRAPH.get("fasteners", []):
        uid = f.get("fastener_uid")
        if uid:
            result[uid] = f

    return result


def choose_material(layout_obj, graph_obj):
    node_type = layout_obj.get("node_type", "")
    name = str(layout_obj.get("name", "")).lower()
    material_hint = str(graph_obj.get("material_hint", "")).lower()

    if node_type == "fastener":
        return MATERIALS["fastener"]

    if "bolt" in name or "screw" in name or "washer" in name:
        return MATERIALS["fastener"]

    if material_hint in ("hardboard", "fiberboard"):
        material_hint = "fibreboard"
    if material_hint in ("wood", "metal", "fabric", "plastic", "fibreboard"):
        return MATERIALS[material_hint]

    if "leg" in name or "rail" in name or "support" in name:
        return MATERIALS["metal"]

    if "seat" in name:
        return MATERIALS["fabric"]

    return MATERIALS["wood"]


def fallback_dimensions(layout_obj, graph_obj):
    node_type = layout_obj.get("node_type", "")
    name = str(layout_obj.get("name", "")).lower()
    shape = str(graph_obj.get("shape_family", "")).lower()
    material_hint = str(graph_obj.get("material_hint", "")).lower()

    if node_type == "fastener":
        return "cylinder", [0.08, 0.08, 0.35]

    if "seat" in name or material_hint == "fabric":
        return "rounded_box", [1.6, 1.2, 0.18]

    if "back" in name or "frame" in name or shape == "frame":
        return "box", [1.6, 0.18, 1.35]

    if "rail" in name or "beam" in name or shape == "beam":
        return "box", [1.8, 0.18, 0.18]

    if "leg" in name:
        return "box", [0.22, 0.22, 1.25]

    if shape == "panel":
        return "box", [1.2, 0.2, 0.45]

    return "box", [0.6, 0.3, 0.3]


# Real-scale fasteners (a few mm across) vanish in a whole-product shot,
# so they are enlarged to at least this size (metres, longest side).
MIN_FASTENER_SIZE = 0.08


def visible_dimensions(layout_obj, dimensions):
    if layout_obj.get("node_type") != "fastener":
        return dimensions
    factor = max(1.0, MIN_FASTENER_SIZE / max(max(dimensions), 1e-6))
    return [d * factor for d in dimensions]


def create_mesh_for_layout(parent, layout_obj, graph_obj, proxy_obj):
    uid = layout_obj.get("node_uid")
    material = choose_material(layout_obj, graph_obj)

    if proxy_obj:
        name = f"{{uid}}_mesh"
        primitive = proxy_obj.get("primitive", "box")
        if proxy_obj.get("shape_type") == "rounded_panel" and primitive != "profile":
            primitive = "rounded_box"
        dimensions = proxy_obj.get("dimensions", [1, 1, 1])
        holes = proxy_obj.get("holes", [])
    else:
        name = f"{{uid}}_fallback"
        primitive, dimensions = fallback_dimensions(layout_obj, graph_obj)
        holes = []

    true_dimensions = dimensions
    dimensions = visible_dimensions(layout_obj, dimensions)

    if primitive == "cylinder":
        mesh = create_cylinder(name, dimensions, material)
    elif primitive == "rounded_box":
        mesh = create_rounded_box(name, dimensions, material)
    elif primitive == "u_frame":
        mesh = create_u_frame(name, dimensions, material)
    elif primitive == "slatted_back":
        mesh = create_slatted_back(name, dimensions, material)
    elif primitive == "side_frame":
        mesh = create_side_frame(name, dimensions, material)
    elif primitive == "profile" and proxy_obj and proxy_obj.get("profile"):
        mesh = create_profile(name, dimensions, proxy_obj["profile"], material)
    else:
        mesh = create_box(name, dimensions, material)

    # A frame's bounding box faces are mostly open space, so no hole markers.
    if primitive not in COMPOSITE_PRIMITIVES:
        add_holes(mesh, holes, dimensions)
    mesh.parent = parent
    # scene_layout rotation is XYZ Euler in degrees (e.g. a short rail
    # turned 90 degrees about Z to run along Y).
    mesh.rotation_euler = [math.radians(a) for a in layout_obj.get("rotation", [0, 0, 0])]
    mesh.scale = layout_obj.get("scale", [1, 1, 1])
    mesh["highlight"] = 0.0
    # How much smaller the part really is than drawn (fasteners only).
    mesh["true_size"] = true_dimensions[0] / dimensions[0] if dimensions[0] else 1.0
    return mesh, primitive


def keyframe_location(obj, location, frame):
    obj.location = Vector(location)
    obj.keyframe_insert(data_path="location", frame=frame)


def keyframe_scale(obj, value, frame):
    obj.scale = (value, value, value)
    obj.keyframe_insert(data_path="scale", frame=frame)


def keyframe_highlight(mesh, value, frame):
    mesh["highlight"] = value
    mesh.keyframe_insert(data_path='["highlight"]', frame=frame)


layout_objects = SCENE_LAYOUT.get("scene_objects", [])
layout_by_uid = {{
    obj.get("node_uid"): obj
    for obj in layout_objects
    if obj.get("node_uid")
}}

proxy_by_uid = proxy_lookup()
graph_by_uid = graph_node_lookup()

# Everything hangs off one pivot so the finished assembly can be turned
# over as a whole. Node empties are keyframed in pivot space; the pivot
# doesn't move until the finale, so pivot space is world space minus PIVOT.
FINALE = SCENE_LAYOUT.get("finale") or {{}}
PIVOT = Vector(FINALE.get("pivot", [0, 0, 0]))
pivot_obj = create_empty("Assembly_Pivot", PIVOT)


def local(position):
    return Vector(position) - PIVOT


node_objects = {{}}
node_meshes = {{}}
spinning = set()
# uid -> (local min corner, local max corner) of the node's mesh
node_extents = {{}}

for layout_obj in layout_objects:
    uid = layout_obj.get("node_uid")
    if not uid:
        continue

    parent = create_empty(uid, local(layout_obj.get("start_position", [0, 0, 1])))
    parent.parent = pivot_obj
    node_objects[uid] = parent

    # An assembly node is a logical group of the parts that are drawn
    # individually; giving it a solid mesh would hide those parts. A
    # fastener no step uses would just float loose in the scene.
    if layout_obj.get("node_type") == "assembly":
        continue
    if layout_obj.get("node_type") == "fastener" and not layout_obj.get("is_moving"):
        continue

    graph_uid = layout_obj.get("instance_of") or uid
    graph_obj = graph_by_uid.get(graph_uid, {{}})
    proxy_obj = proxy_by_uid.get(graph_uid)

    mesh, primitive = create_mesh_for_layout(parent, layout_obj, graph_obj, proxy_obj)
    node_meshes[uid] = mesh
    if primitive == "cylinder" and layout_obj.get("node_type") == "fastener":
        spinning.add(uid)

    corners = [mesh.matrix_basis @ Vector(c) for c in mesh.bound_box]
    node_extents[uid] = (
        Vector([min(c[i] for c in corners) for i in range(3)]),
        Vector([max(c[i] for c in corners) for i in range(3)]),
    )


# Each part pops in just before its step, glows while it moves into place,
# and fades back to its own colour. Screws and bolts turn as they go in.
APPEAR_FRAMES = 8
HIDDEN_SCALE = 0.001
HIGHLIGHT_FADE_FRAMES = 10
SPIN_TURNS = 2

steps = TIMELINE["steps"]
first_step_of = {{}}

revealed = set()


for index, step in enumerate(steps):
    start_frame = step["start_frame"]
    end_frame = step["end_frame"]

    # A sub-assembly's base appears at its staging spot when the first part
    # is fitted to it.
    for uid in step.get("reveal", []):
        obj = node_objects.get(uid)
        layout_obj = layout_by_uid.get(uid)
        if not obj or not layout_obj or uid in revealed:
            continue
        revealed.add(uid)
        appear_frame = start_frame - APPEAR_FRAMES
        if appear_frame > 1:
            keyframe_scale(obj, HIDDEN_SCALE, appear_frame)
            keyframe_scale(obj, 1.0, start_frame)
        keyframe_location(obj, local(layout_obj.get("start_position", [0, 0, 1])), start_frame)

    # Parts already fitted to a sub-assembly move with it.
    for carried in step.get("carried", []):
        obj = node_objects.get(carried["uid"])
        if not obj:
            continue
        keyframe_location(obj, local(carried["from"]), start_frame)
        keyframe_location(obj, local(carried["to"]), end_frame)

    for uid in step["moving_nodes"]:
        obj = node_objects.get(uid)
        layout_obj = layout_by_uid.get(uid)
        if not obj or not layout_obj:
            continue

        first_step_of[uid] = index

        appear_frame = start_frame - APPEAR_FRAMES
        if appear_frame > 1 and uid not in revealed:
            keyframe_scale(obj, HIDDEN_SCALE, appear_frame)
            keyframe_scale(obj, 1.0, start_frame)

        # A member of a sub-assembly goes onto it at its staging spot; the
        # base's own step then carries it into place.
        end_position = layout_obj.get("own_end") or layout_obj.get("final_position", [0, 0, 1])
        keyframe_location(obj, local(layout_obj.get("start_position", [0, 0, 1])), start_frame)
        keyframe_location(obj, local(end_position), end_frame)

        mesh = node_meshes.get(uid)
        if mesh is None:
            continue

        keyframe_highlight(mesh, 1.0, start_frame)
        keyframe_highlight(mesh, 1.0, end_frame)
        keyframe_highlight(mesh, 0.0, end_frame + HIGHLIGHT_FADE_FRAMES)

        # A fastener drawn larger than life to be seen going in shrinks to
        # its real size once it's in, instead of sticking out of the joint.
        if mesh["true_size"] < 1.0:
            keyframe_scale(mesh, 1.0, end_frame)
            keyframe_scale(mesh, mesh["true_size"], end_frame + HIGHLIGHT_FADE_FRAMES)

        if uid in spinning:
            base_angle = mesh.rotation_euler[2]
            mesh.keyframe_insert(data_path="rotation_euler", index=2, frame=start_frame)
            mesh.rotation_euler[2] = base_angle + SPIN_TURNS * 2 * math.pi
            mesh.keyframe_insert(data_path="rotation_euler", index=2, frame=end_frame)

animated_count = len(first_step_of)

if animated_count == 0:
    print("ERROR: V3 no motion step moves an object in the scene; refusing to render a static video")
    sys.exit(1)


def bounds_of(entries, upright=False):
    # World-space box around each (uid, position) entry. With upright=True
    # the positions are mapped through the finale's turn-over (180 degrees
    # about X through PIVOT), i.e. where they end up after it.
    lo = None
    hi = None
    for uid, position in entries:
        extent = node_extents.get(uid)
        if not extent:
            continue
        p = Vector(position)
        a = p + extent[0]
        b = p + extent[1]
        if upright:
            a, b = (
                Vector((a.x, -b.y, 2 * PIVOT.z - b.z)),
                Vector((b.x, -a.y, 2 * PIVOT.z - a.z)),
            )
        lo = a if lo is None else Vector([min(lo[i], a[i]) for i in range(3)])
        hi = b if hi is None else Vector([max(hi[i], b[i]) for i in range(3)])
    return lo, hi


def union(box_a, box_b):
    if box_a[0] is None:
        return box_b
    if box_b[0] is None:
        return box_a
    return (
        Vector([min(box_a[0][i], box_b[0][i]) for i in range(3)]),
        Vector([max(box_a[1][i], box_b[1][i]) for i in range(3)]),
    )


static_entries = [
    (uid, layout_by_uid[uid].get("start_position", [0, 0, 1]))
    for uid in node_objects
    if uid not in first_step_of
]


def entries_for_step(index):
    # Everything on screen while step `index` plays.
    entries = list(static_entries)
    for uid, step_index in first_step_of.items():
        layout_obj = layout_by_uid[uid]
        if step_index < index:
            entries.append((uid, layout_obj.get("final_position", [0, 0, 1])))
        elif step_index == index:
            entries.append((uid, layout_obj.get("start_position", [0, 0, 1])))
            entries.append((uid, layout_obj.get("final_position", [0, 0, 1])))
    return entries


final_entries = [
    (uid, layout_obj.get("final_position", [0, 0, 1]))
    for uid, layout_obj in layout_by_uid.items()
]
upright_box = bounds_of(final_entries, upright=bool(FINALE))

all_entries = []
for uid, layout_obj in layout_by_uid.items():
    all_entries.append((uid, layout_obj.get("start_position", [0, 0, 1])))
    all_entries.append((uid, layout_obj.get("final_position", [0, 0, 1])))

scene_lo, scene_hi = union(bounds_of(all_entries), upright_box)
if scene_lo is None:
    print("ERROR: V3 scene has no visible meshes; refusing to render")
    sys.exit(1)

scene_size = max(max(scene_hi - scene_lo), 0.5)

scene = bpy.context.scene
fps = TIMELINE.get("fps", 24)
frame_end = TIMELINE["frame_end"]

scene.frame_start = 1
scene.frame_end = frame_end
scene.frame_step = {frame_step}
scene.render.fps = fps
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = {resolution_percent}
scene.render.filepath = str(OUTPUT_DIR / "frame_")
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"


# Finale: lift the assembly just enough to clear the floor, turn it over
# about X, and set it back down upright.
flip = TIMELINE.get("flip")
lift = 0.0
if flip:
    radius = 0.0
    for uid, position in final_entries:
        extent = node_extents.get(uid)
        if not extent:
            continue
        for y in (position[1] + extent[0].y, position[1] + extent[1].y):
            for z in (position[2] + extent[0].z, position[2] + extent[1].z):
                radius = max(radius, math.hypot(y - PIVOT.y, z - PIVOT.z))
    lift = max(0.0, radius - PIVOT.z) + 0.03

    flip_start = flip["start_frame"]
    flip_end = flip["end_frame"]
    flip_mid = (flip_start + flip_end) // 2

    pivot_obj.keyframe_insert(data_path="rotation_euler", frame=flip_start)
    pivot_obj.rotation_euler = (math.radians(FINALE.get("angle", 180.0)), 0, 0)
    pivot_obj.keyframe_insert(data_path="rotation_euler", frame=flip_end)

    keyframe_location(pivot_obj, PIVOT, flip_start)
    keyframe_location(pivot_obj, PIVOT + Vector((0, 0, lift)), flip_mid)
    keyframe_location(pivot_obj, PIVOT, flip_end)


# Camera: a fixed viewing angle that eases between framings. During the
# build the framing only ever grows (all parts so far plus the moving
# ones), so it widens gradually instead of jumping in and out. It then
# frames the turn-over and slowly orbits the finished assembly.
CAMERA_DIRECTION = Vector((0.95, -1.20, 0.72)).normalized()
# The orbit turns this far, clockwise seen from above: from front-right
# across the front to front-left, so the last shot shows the front (-Y).
ORBIT_DEGREES = -100
ORBIT_KEY_SPACING = 6

bpy.ops.object.camera_add(location=(0, 0, 0))
camera = bpy.context.object
camera.name = "Assembly_Camera"
camera.data.lens = 35
camera.data.clip_start = 0.01
camera.data.clip_end = 1000
scene.camera = camera

camera_target = create_empty("Camera_Target", (0, 0, 0))
track = camera.constraints.new(type="TRACK_TO")
track.target = camera_target
track.track_axis = "TRACK_NEGATIVE_Z"
track.up_axis = "UP_Y"

# Sensor fit AUTO puts the sensor width on the longer (horizontal) side.
tan_half_x = camera.data.sensor_width / (2 * camera.data.lens)
tan_half_y = tan_half_x * scene.render.resolution_y / scene.render.resolution_x
# The top TITLE_BAND of the frame holds the product title (render_video.py):
# the furniture is framed in the rest, by shifting the view up by half the
# band (shift is a fraction of the wider side) and fitting a shorter height.
TITLE_BAND = 0.12
camera.data.shift_y = TITLE_BAND / 2 * scene.render.resolution_y / scene.render.resolution_x
tan_half_y *= 1 - TITLE_BAND
FRAME_MARGIN = 1.06


def framing(box, direction=CAMERA_DIRECTION):
    # (target, camera location) at the smallest distance along `direction`
    # that keeps every corner of the box in frame.
    lo, hi = box
    center = (lo + hi) / 2
    forward = -direction
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward).normalized()

    distance = 0.3
    for corner in (Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)):
        offset = corner - center
        depth = offset.dot(forward)
        distance = max(
            distance,
            abs(offset.dot(right)) * FRAME_MARGIN / tan_half_x - depth,
            abs(offset.dot(up)) * FRAME_MARGIN / tan_half_y - depth,
        )
    return center, center + direction * distance


def keyframe_camera(shot, frame):
    target, location = shot
    keyframe_location(camera_target, target, frame)
    keyframe_location(camera, location, frame)


def focus_box(index):
    # The moving parts where they land, plus the last stretch of their
    # approach, at least FOCUS_MIN_SIZE across: what a close-up of the step
    # shows.
    entries = []
    for uid, step_index in first_step_of.items():
        if step_index != index:
            continue
        layout_obj = layout_by_uid[uid]
        end = Vector(layout_obj.get("final_position", [0, 0, 1]))
        start = Vector(layout_obj.get("start_position", [0, 0, 1]))
        entries.append((uid, end))
        entries.append((uid, end + (start - end) * FOCUS_APPROACH))
    lo, hi = bounds_of(entries)
    if lo is None:
        return lo, hi
    center = (lo + hi) / 2
    half = Vector([max((hi[i] - lo[i]) / 2, FOCUS_MIN_SIZE / 2) for i in range(3)])
    return center - half, center + half


def blend(shot_a, shot_b, share):
    return tuple(a.lerp(b, share) for a, b in zip(shot_a, shot_b))


# Steps whose parts are small next to what is built so far get a closer
# shot: part of the way from the whole build toward the moving parts, so
# the piece stays in view for context.
FOCUS_APPROACH = 0.35
FOCUS_MIN_SIZE = 0.35
FOCUS_ZOOM = 0.6
FOCUS_WHEN_SMALLER = 0.5

build_box = (None, None)
for index, step in enumerate(steps):
    build_box = union(build_box, bounds_of(entries_for_step(index)))
    shot = framing(build_box)
    focus = focus_box(index)
    if focus[0] is not None:
        if max(focus[1] - focus[0]) < FOCUS_WHEN_SMALLER * max(build_box[1] - build_box[0]):
            shot = blend(shot, framing(focus), FOCUS_ZOOM)
    if index == 0:
        keyframe_camera(shot, 1)
    keyframe_camera(shot, step["start_frame"])
    keyframe_camera(shot, step["end_frame"])

if flip:
    lifted_hi = Vector((upright_box[1].x, upright_box[1].y, upright_box[1].z + lift))
    flip_box = union(union(build_box, upright_box), (upright_box[0], lifted_hi))
    flip_shot = framing(flip_box)
    keyframe_camera(flip_shot, flip["start_frame"])
    keyframe_camera(flip_shot, flip["end_frame"])

orbit = TIMELINE["orbit"]
orbit_frames = orbit["end_frame"] - orbit["start_frame"]
key_frames = list(range(orbit["start_frame"], orbit["end_frame"], ORBIT_KEY_SPACING)) + [orbit["end_frame"]]
for frame in key_frames:
    angle = math.radians(ORBIT_DEGREES) * (frame - orbit["start_frame"]) / orbit_frames
    direction = Matrix.Rotation(angle, 3, "Z") @ CAMERA_DIRECTION
    keyframe_camera(framing(upright_box, direction), frame)


# Studio background (EEVEE/Cycles read the world node tree, not world.color).
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.color = (0.80, 0.82, 0.86)
if world.node_tree is None:
    world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (0.80, 0.82, 0.86, 1.0)
    background.inputs["Strength"].default_value = 0.35


def look_at(obj, target):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


# Light energy scales with the square of the distance to the scene.
light_scale = (scene_size / 4) ** 2
scene_center = (scene_lo + scene_hi) / 2

# Large soft key light
bpy.ops.object.light_add(
    type="AREA",
    location=(scene_center.x + scene_size * 0.6, scene_center.y - scene_size * 1.5, scene_center.z + scene_size * 1.9)
)
key_light = bpy.context.object
key_light.name = "Large Softbox Key Light"
key_light.data.energy = 1500 * light_scale
key_light.data.size = scene_size * 1.2
look_at(key_light, scene_center)

# Dimmer fill from the other side keeps the shadow side readable.
bpy.ops.object.light_add(
    type="AREA",
    location=(scene_center.x - scene_size * 1.4, scene_center.y + scene_size * 0.4, scene_center.z + scene_size * 1.0)
)
fill_light = bpy.context.object
fill_light.name = "Cool Fill Light"
fill_light.data.energy = 450 * light_scale
fill_light.data.size = scene_size * 1.4
fill_light.data.color = (0.85, 0.9, 1.0)
look_at(fill_light, scene_center)

# Rim light from behind separates the parts from the background.
bpy.ops.object.light_add(
    type="AREA",
    location=(scene_center.x - scene_size * 0.4, scene_center.y + scene_size * 1.6, scene_center.z + scene_size * 1.4)
)
rim_light = bpy.context.object
rim_light.name = "Rim Light"
rim_light.data.energy = 700 * light_scale
rim_light.data.size = scene_size * 0.6
look_at(rim_light, scene_center)

# Floor just under the lowest point any part reaches.
bpy.ops.mesh.primitive_plane_add(
    size=scene_size * 20,
    location=(scene_center.x, scene_center.y, scene_lo.z - 0.002)
)
floor = bpy.context.object
floor.name = "Floor"
floor.data.materials.append(MATERIALS["floor"])

RENDER_ENGINE = "{render_engine}"
if RENDER_ENGINE == "CYCLES":
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = {cycles_samples}
    scene.cycles.use_denoising = True
elif RENDER_ENGINE == "WORKBENCH":
    # Parts keep their colours through each material's diffuse_color.
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.render_aa = "8"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.color_type = "MATERIAL"
    shading.show_shadows = True
    shading.shadow_intensity = 0.35
    shading.show_cavity = True
    shading.cavity_type = "WORLD"
else:
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 32
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = -0.3
scene.view_settings.gamma = 1

print("V3 project root:", PROJECT_ROOT)
print("V3 frames output:", OUTPUT_DIR)
print("V3 layout objects:", len(layout_objects))
print("V3 created objects:", len(node_objects))
print("V3 animated objects:", animated_count)
print("V3 motion steps:", len(steps))
print("V3 frame range:", scene.frame_start, "-", scene.frame_end, "step", scene.frame_step)
print("Rendering V3 frames...")

bpy.ops.render.render(animation=True)
"""

    save_text(script, output_script)
    print(f"Saved Blender V3 script to {output_script}")
    print(f"Saved render timeline to {RENDER_TIMELINE_JSON}")


if __name__ == "__main__":
    build_blender_script()
