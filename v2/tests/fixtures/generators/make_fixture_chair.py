"""Vision fixture for the Habitat Banbury dining chair (uploads/tablechair.pdf).

The box holds a pair of chairs and every step says "Repeat x2"; quantities
here are for one chair, so the video builds one.

Usage (from the repo root):
    python v2/tests/fixtures/generators/make_fixture_chair.py . v2/tests/fixtures/vision_banbury_chair
"""
import sys
from pathlib import Path

from fixture_lib import action, diagram, fastener, page, part, tool, write_fixture

SIDE_RAIL = lambda qty=2: part(
    "1", "side rail", "flat wooden seat rail with dowel holes and a bolt hole in each end and slotted screw pockets",
    "beam", "wood", qty, [("hole", 3, "two dowel holes and one bolt hole in each end"), ("slot", 2, "screw pockets on the inner face")], "left")
FRONT_LEG = lambda qty=1: part(
    "2", "front leg frame", "U-shaped wooden frame: two front legs joined by a top rail, with dowel and bolt holes at the top",
    "frame", "wood", qty, [("hole", 6, "dowel and bolt holes in the tops of both legs")], "center")
SEAT = lambda qty=1: part(
    "3", "seat pad", "upholstered padded seat with rounded edges", "panel", "fabric", qty,
    [("hole", 6, "pre-drilled screw holes in the underside board")], "bottom")
BACK = lambda qty=1: part(
    "4", "chair back", "tall wooden chair back: two curved back legs with a top rail, a lower rail and five vertical slats",
    "frame", "wood", qty, [("hole", 6, "dowel and bolt holes in each back leg at seat height")], "right")

DOWEL = lambda qty: fastener("A", "40mm wood dowel", "dowel", qty)
BOLT = lambda qty: fastener("B", "M6x50mm bolt", "bolt", qty)
LOCK = lambda qty: fastener("C", "lock washer", "washer", qty)
FLAT = lambda qty: fastener("D", "flat washer", "washer", qty)
SCREW = lambda qty: fastener("E", "M4x30mm screw", "screw", qty)

ALLEN = tool("M4 allen key F")
DRIVER = tool("cross head screwdriver G")

PAGES = [
    page(1, "cover",
         final="Banbury dining chair: padded seat, four legs, tall back with five vertical slats",
         unc=["Cover page; product name Banbury and Habitat logo."]),
    page(2, "warning", unc=["Safety, care and guidance text only."]),
    page(3, "parts_list",
         parts=[SIDE_RAIL(), FRONT_LEG(), SEAT(), BACK()],
         fasteners=[DOWEL(6), BOLT(6), LOCK(6), FLAT(6), SCREW(6)],
         tools=[ALLEN, DRIVER],
         unc=["The box holds a pair of chairs (parts x4/x2, fittings x12); quantities here are for one chair."]),
    page(4, "assembly_step",
         parts=[SIDE_RAIL(), FRONT_LEG()],
         fasteners=[DOWEL(4), BOLT(2), LOCK(2), FLAT(2)],
         tools=[ALLEN],
         actions=[
             action("insert", "", "front leg frame", "A", "", "down",
                    "wood dowels A pushed into the holes in the tops of front leg frame 2"),
             action("attach", "side rail", "front leg frame", "B", "M4 allen key F", "down",
                    "side rails 1 pushed onto the dowels at each top corner of front leg frame 2; M6x50mm bolt B with lock washer C and flat washer D tightened with allen key F"),
             action("insert", "", "side rail", "C", "", "down",
                    "lock washer C and flat washer D under the head of bolt B inside the rail pocket"),
         ],
         final="front leg frame with two side rails standing up from its top corners",
         unc=["Steps 1 and 2 on one page; both say repeat x2 for the second chair."]),
    page(5, "assembly_step",
         parts=[SIDE_RAIL(), FRONT_LEG(), BACK(), SEAT()],
         fasteners=[DOWEL(2), BOLT(4), LOCK(4), FLAT(4), SCREW(6)],
         tools=[ALLEN, DRIVER],
         actions=[
             action("attach", "chair back", "side rail", "A", "", "down",
                    "step 2-3: the free ends of the side rails 1 pushed onto dowels A in chair back 4, then bolted with M6x50mm bolt B, lock washer C and flat washer D"),
             action("tighten", "", "chair back", "B", "M4 allen key F", "clockwise",
                    "4x bolt B with washers C and D tightened through the side rails into chair back 4"),
             action("place", "seat pad", "side rail", "E", "cross head screwdriver G", "down",
                    "step 4: frame set on seat pad 3 and fixed with 6x M4x30mm screw E through the rail pockets using screwdriver G"),
         ],
         final="complete chair frame with the seat pad screwed on",
         unc=["Steps 3 and 4 on one page; the frame is shown upside down on the seat pad for step 4."]),
    page(6, "unknown", final="assembled Banbury chair standing upright",
         unc=["Step 5: picture of the finished chair, 'Assemble is completed'."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled Banbury chair", (0.27, 0.22, 0.73, 0.77), complexity="low", conf=0.95)], []),
    2: ("warning", [], ["Text only."]),
    3: ("parts_list", [
        diagram("part_inventory", "Left / Right Side Rail (310 x 60mm) x4", (0.05, 0.2, 0.33, 0.36), ["1", "4x"], complexity="low", conf=0.9),
        diagram("part_inventory", "Front Leg (430 x 415mm) x2", (0.37, 0.12, 0.58, 0.36), ["2", "2x"], complexity="low", conf=0.9),
        diagram("part_inventory", "Seat Pad (450 x 355mm) x2", (0.05, 0.4, 0.35, 0.49), ["3", "2x"], complexity="low", conf=0.9),
        diagram("part_inventory", "Chair Back (905 x 403mm) x2", (0.7, 0.13, 0.92, 0.5), ["4", "2x"], complexity="low", conf=0.9),
        diagram("part_inventory", "Fittings: 40mm wood dowel, M6x50mm bolt, lock washer, flat washer, M4x30mm screw, M4 allen key",
                (0.1, 0.58, 0.9, 0.84), ["A", "B", "C", "D", "E", "F"], parts=False, fast=True, tools=True, complexity="low"),
        diagram("part_inventory", "Cross head screwdriver (not provided)", (0.08, 0.9, 0.55, 0.96), ["G"], parts=False, tools=True, complexity="low"),
    ], []),
    4: ("assembly_step", [
        diagram("exploded_view", "Step 1: side rails 1 with dowels A onto the top of front leg frame 2; bolt B, washers C and D, allen key F",
                (0.12, 0.17, 0.9, 0.53), ["1", "2", "A", "B", "C", "D", "F"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
        diagram("exploded_view", "Step 2: side rails pushed onto dowels A in chair back 4",
                (0.07, 0.53, 0.95, 0.9), ["1", "4", "A"], fast=True, action_="insert", complexity="high"),
    ], []),
    5: ("assembly_step", [
        diagram("assembly_view", "Step 3: bolts B with washers C and D through the side rails into the chair back",
                (0.07, 0.03, 0.95, 0.43), ["B", "C", "D"], fast=True, action_="tighten"),
        diagram("assembly_view", "Step 4: frame upside down on seat pad 3, screws E driven with screwdriver G",
                (0.07, 0.47, 0.9, 0.96), ["3", "4", "E", "G"], fast=True, tools=True, action_="tighten", complexity="high"),
    ], []),
    6: ("unknown", [diagram("final_product", "Finished chair, 'Assemble is completed'", (0.27, 0.05, 0.67, 0.52), complexity="low", conf=0.95)], []),
}

if __name__ == "__main__":
    write_fixture(Path(sys.argv[1]), Path(sys.argv[2]), PAGES, DIAGRAMS)
