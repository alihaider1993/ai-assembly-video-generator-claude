"""Vision results for the IKEA ÅLHULT dining chair manual (8 pages).

The chair is built from two side frames (front leg, tall back leg and two
rails each) joined by a front and a back rail, with four back slats and a
top rail. The manual prints no sizes, so parts get default sizes by role.

Run: python manuals/alhult_chair/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

SIDE_FRAME = lambda side: part(
    "", f"{side} side frame", f"{side} wooden chair side: a short front leg and a tall angled back leg joined by a seat rail and a lower rail",
    "frame", "wood", 1, [("hole", 4, "dowel and bolt holes on the inner face of each leg"), ("hole", 2, "slat and top rail holes in the back leg")], side)
FRONT_RAIL = lambda qty=1: part(
    "", "front rail", "straight wooden seat rail between the two front legs, dowel holes in each end", "beam", "wood", qty,
    [("hole", 4, "two dowel holes in each end"), ("hole", 2, "bolt holes in the ends")], "center")
BACK_RAIL = lambda qty=1: part(
    "", "back rail", "straight wooden seat rail between the two back legs, dowel holes in each end and slat holes on top", "beam", "wood", qty,
    [("hole", 4, "two dowel holes in each end"), ("hole", 4, "slat holes along the top edge")], "center")
SLAT = lambda qty=4: part(
    "", "back slat", "long thin wooden back slat", "beam", "wood", qty, [], "center")
TOP_RAIL = lambda qty=1: part(
    "", "top rail", "slightly curved wooden crest rail across the tops of the back legs and slats", "beam", "wood", qty,
    [("hole", 4, "slat holes underneath"), ("hole", 2, "screw holes in the ends")], "top")
SEAT = lambda qty=1: part(
    "", "seat", "flat wooden seat board with notches for the back legs", "panel", "wood", qty,
    [("hole", 4, "pre-drilled screw holes underneath")], "bottom")
# Bracket 102646 (4x), named by the side frame it is screwed to so each
# frame gets its own two; no label, so the two names stay separate parts.
BRACKET = lambda side: part(
    "", f"{side} corner bracket", "small metal angle bracket 102646 with a slotted hole in each leg", "bracket", "metal", 2,
    [("slot", 2, "slotted screw holes")], side)
SIDES = ("left", "right")

BOLT = lambda qty: fastener("128745", "frame bolt 128745", "bolt", qty)
TOP_SCREW = lambda qty: fastener("100215", "top rail screw 100215", "screw", qty)
BRACKET_SCREW = lambda qty: fastener("109598", "bracket screw 109598", "screw", qty)
SEAT_SCREW = lambda qty: fastener("100400", "seat screw 100400", "screw", qty)
DOWEL_PLAIN = lambda qty: fastener("101357", "wooden dowel 101357", "dowel", qty)
DOWEL = lambda qty: fastener("101350", "wooden dowel 101350", "dowel", qty)

ALLEN = tool("allen key 100092")
DRIVER = tool("cross head screwdriver")

PAGES = [
    page(1, "cover", final="ÅLHULT dining chair: four legs, seat, tall back with vertical slats under a top rail",
         unc=["Cover page; product name and IKEA logo."]),
    page(2, "warning", tools=[DRIVER],
         unc=["Cross head screwdriver needed (not supplied); soft floor; call IKEA if unsure."]),
    page(3, "parts_list",
         fasteners=[BOLT(4), TOP_SCREW(2), BRACKET_SCREW(4), SEAT_SCREW(4), DOWEL_PLAIN(2), DOWEL(6)],
         parts=[BRACKET(side) for side in SIDES],
         tools=[ALLEN],
         unc=["Only the hardware is drawn; the wooden parts appear in the steps.",
              "A slotted spacer strip (1x) is kept for steps 7 and 9; it is a temporary jig, not part of the chair."]),
    page(4, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BRACKET("left"), BRACKET("right"), FRONT_RAIL(), BACK_RAIL()],
         fasteners=[BRACKET_SCREW(4), DOWEL_PLAIN(2), DOWEL(6)],
         tools=[DRIVER],
         actions=[
             action("attach", "left corner bracket", "left side frame", "109598", "cross head screwdriver", "down",
                    "step 1: 2x left corner bracket (102646) screwed with screw 109598 to the inside of the seat rail of the left side frame lying on the floor"),
             action("attach", "right corner bracket", "right side frame", "109598", "cross head screwdriver", "down",
                    "step 1: 2x right corner bracket (102646) screwed with screw 109598 to the inside of the seat rail of the right side frame"),
             action("insert", "", "front rail", "101357", "", "inward",
                    "step 2: wooden dowels 101357 and 101350 pushed into the holes in the ends of the front rail"),
             action("insert", "", "back rail", "101350", "", "inward",
                    "step 2: 2x dowel 101350 in each end of the back rail"),
         ],
         final="two side frames with corner brackets; front and back rails with dowels in their ends",
         unc=["Steps 1 and 2 on one page. Brackets must sit flush with the rail top (shown in the right/wrong inset)."]),
    page(5, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), FRONT_RAIL(), BACK_RAIL()],
         fasteners=[DOWEL(2), BOLT(2)],
         tools=[ALLEN],
         actions=[
             action("attach", "front rail", "left side frame", "101350", "", "down",
                    "step 3: front rail stood on its end and pushed with its dowels into the holes of the left side frame lying on the floor"),
             action("attach", "back rail", "left side frame", "101350", "", "down",
                    "step 3: back rail pushed with its dowels into the left side frame"),
             action("attach", "right side frame", "back rail", "128745", "allen key 100092", "down",
                    "step 4: right side frame laid on the ends of the front rail and back rail and fixed with 2x frame bolt 128745 tightened with allen key 100092"),
         ],
         final="chair frame lying on its side: two side frames joined by the front and back rails",
         unc=["Steps 3 and 4 on one page; the frame is turned over between them."]),
    page(6, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), FRONT_RAIL(), BACK_RAIL(), SLAT()],
         fasteners=[BOLT(2)],
         tools=[ALLEN],
         actions=[
             action("tighten", "", "front rail", "128745", "allen key 100092", "clockwise",
                    "step 5: frame turned over; 2x frame bolt 128745 tightened through the other side frame into the rails"),
             action("insert", "back slat", "back rail", "", "", "down",
                    "step 6: chair stood upright; 4x back slat pushed down into the holes along the top of the back rail"),
         ],
         final="upright chair frame with four back slats standing in the back rail",
         unc=["Steps 5 and 6 on one page."]),
    page(7, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), SLAT(), TOP_RAIL()],
         fasteners=[TOP_SCREW(2)],
         tools=[ALLEN],
         actions=[
             action("attach", "top rail", "left side frame", "100215", "allen key 100092", "down",
                    "step 8: top rail pressed down onto the slat tops and the back legs, fixed with 2x screw 100215 through the back legs using allen key 100092; no power drill"),
         ],
         final="chair frame with the top rail across the back legs and slats",
         unc=["Step 7: the slotted spacer strip is laid over the slat tops to space them; it is not drawn in the video."]),
    page(8, "assembly_step",
         parts=[SEAT(), BRACKET("left"), BRACKET("right"), SIDE_FRAME("left"), SIDE_FRAME("right")],
         fasteners=[SEAT_SCREW(4)],
         tools=[DRIVER],
         actions=[
             action("place", "seat", "left corner bracket", "100400", "cross head screwdriver", "down",
                    "step 10: chair turned upside down onto the seat lying on a table; 4x seat screw 100400 driven through the corner brackets into the seat"),
         ],
         final="finished chair",
         unc=["Step 9: the spacer strip is pulled out of the top rail; nothing is fitted."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled ÅLHULT chair", (0.1, 0.25, 0.4, 0.9), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Cross head screwdriver, soft floor, call IKEA if unsure", (0.53, 0.05, 0.97, 0.7),
                            parts=False, tools=True, action_="warning", complexity="low")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Fittings: frame bolt 128745 x4, screw 100215 x2, screw 109598 x4, screw 100400 x4",
                (0.02, 0.05, 0.47, 0.4), ["128745", "100215", "109598", "100400", "4x", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Corner bracket 102646 x4", (0.24, 0.2, 0.32, 0.4), ["102646", "4x"], complexity="low"),
        diagram("part_inventory", "Allen key 100092 x1", (0.18, 0.15, 0.24, 0.4), ["100092", "1x"], parts=False, tools=True, complexity="low"),
        diagram("part_inventory", "Wooden dowels 101357 x2 and 101350 x6", (0.02, 0.45, 0.17, 0.6), ["101357", "101350", "2x", "6x"],
                parts=False, fast=True, complexity="low"),
        diagram("warning", "Keep the slotted spacer strip (1x)", (0.02, 0.73, 0.47, 0.93), parts=False, complexity="low"),
    ], []),
    4: ("assembly_step", [
        diagram("exploded_view", "Step 1: corner brackets 102646 screwed with 109598 onto both side frames",
                (0.52, 0.03, 0.98, 0.55), ["102646", "109598", "4x"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
        diagram("exploded_view", "Step 2: dowels 101357 and 101350 into the ends of the front and back rails",
                (0.52, 0.57, 0.98, 0.95), ["101357", "101350", "2x"], fast=True, arrows=True, action_="insert"),
    ], []),
    5: ("assembly_step", [
        diagram("exploded_view", "Step 3: front and back rails pushed onto one side frame",
                (0.02, 0.03, 0.47, 0.4), ["2x"], fast=True, arrows=True, action_="insert", complexity="high"),
        diagram("assembly_view", "Step 4: second side frame bolted with 2x 128745 using allen key 100092",
                (0.02, 0.42, 0.47, 0.95), ["128745", "100092", "2x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
    ], []),
    6: ("assembly_step", [
        diagram("assembly_view", "Step 5: frame turned over, 2x bolt 128745 through the other side frame",
                (0.53, 0.03, 0.98, 0.45), ["128745", "100092", "2x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
        diagram("exploded_view", "Step 6: chair upright, 4 back slats into the back rail",
                (0.53, 0.47, 0.98, 0.95), ["4x"], arrows=True, action_="insert"),
    ], []),
    7: ("assembly_step", [
        diagram("assembly_view", "Step 7: spacer strip laid over the slat tops", (0.02, 0.03, 0.47, 0.35), arrows=True, action_="insert"),
        diagram("exploded_view", "Step 8: top rail onto the back legs, 2x screw 100215 with allen key 100092, no drill",
                (0.02, 0.4, 0.47, 0.95), ["100215", "100092", "2x"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
    ], []),
    8: ("assembly_step", [
        diagram("assembly_view", "Step 9: spacer strip removed", (0.53, 0.03, 0.98, 0.35), arrows=True, action_="none"),
        diagram("assembly_view", "Step 10: chair upside down on the seat, 4x screw 100400 through the brackets",
                (0.53, 0.4, 0.98, 0.95), ["100400", "4x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
    ], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS)
