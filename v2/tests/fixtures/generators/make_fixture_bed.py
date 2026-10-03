"""Vision fixture for the Habitat Kaycie 3ft single bed (uploads/7255030_D001.pdf).

Usage (from the repo root):
    python v2/tests/fixtures/generators/make_fixture_bed.py . v2/tests/fixtures/vision_kaycie_bed
"""
import sys
from pathlib import Path

from fixture_lib import action, diagram, fastener, page, part, tool, write_fixture

POST = "square wooden post with dowel holes and bolt holes up one face"


def head_foot(label, side):
    return part(label, f"{side} headboard foot", f"long {POST}", "beam", "wood", 1,
                [("hole", 10, "dowel and bolt holes along the inner face")], "left")


def foot_foot(label, side):
    return part(label, f"{side} footboard foot", f"short {POST}", "beam", "wood", 1,
                [("hole", 4, "dowel and bolt holes near the top")], "center")


CENTRAL_LEG = lambda qty=2: part(
    "5", "central leg", "short square wooden leg with a through hole near the top", "beam", "wood", qty,
    [("hole", 2, "through holes near the top end")], "top")
WIDE_RAIL = lambda qty=4: part(
    "6", "wide headboard rail", "wide flat wooden board with dowel holes in both ends", "beam", "wood", qty,
    [("hole", 4, "two dowel holes in each end")], "center")
NARROW_RAIL = lambda qty=2: part(
    "7", "narrow headboard rail", "narrow flat wooden board with dowel holes in both ends", "beam", "wood", qty,
    [("hole", 4, "two dowel holes in each end")], "center")
STAMP_SLAT = part(
    "8", "slat with stamp", "flat wooden slat with a printed safety label near one end", "panel", "wood", 1,
    [("hole", 2, "one screw hole at each end")], "bottom")
SLAT = lambda qty=13: part(
    "9", "slat", "flat wooden slat with a screw hole at each end", "panel", "wood", qty,
    [("hole", 2, "one screw hole at each end")], "bottom")
RIGHT_RAIL = lambda qty=2: part(
    "10", "right side rail", "long wooden side rail with a slat ledge, dowels in one end and a round nut pocket",
    "beam", "wood", qty, [("hole", 6, "screw holes along the slat ledge"), ("hole", 1, "round pocket for the nut near one end")], "bottom")
LEFT_RAIL = lambda qty=2: part(
    "11", "left side rail", "long wooden side rail with a slat ledge, dowels in one end and a round nut pocket",
    "beam", "wood", qty, [("hole", 6, "screw holes along the slat ledge"), ("hole", 1, "round pocket for the nut near one end")], "bottom")

DOWEL = lambda qty: fastener("A", "wooden dowel 10 x 40mm", "dowel", qty)
SCREW = lambda qty: fastener("B", "4 x 35mm screw", "screw", qty)
HEADLESS = lambda qty: fastener("C", "headless bolt 1/4 x 155mm", "bolt", qty)
BOLT80 = lambda qty: fastener("D", "7 x 80mm bolt", "bolt", qty)
SPACER = lambda qty: fastener("E", "70mm spacer", "spacer", qty)
NUT = lambda qty: fastener("F", "nut 1/4", "nut", qty)
WASHER = lambda qty: fastener("G", "curved washer", "washer", qty)
BOLT90 = lambda qty: fastener("L", "1/4 x 90mm bolt", "bolt", qty)
MOON = lambda qty: fastener("M", "1/4 half moon nut", "nut", qty)

HEX = tool("hex key I")
SPANNER = tool("spanner H")
DRIVER = tool("cross-head screwdriver")

PAGES = [
    page(1, "cover",
         final="Kaycie single bed: slatted headboard on two tall posts, low footboard, side rails with a central leg each side and a slatted base",
         unc=["Cover page; product name Kaycie and Habitat logo."]),
    page(2, "warning", unc=["Safety and care advice text only."]),
    page(3, "warning", unc=["Bed warnings and standards text only."]),
    page(4, "parts_list",
         parts=[
             head_foot("1", "left"), head_foot("2", "right"),
             foot_foot("3", "left"), foot_foot("4", "right"),
             CENTRAL_LEG(), WIDE_RAIL(), NARROW_RAIL(), STAMP_SLAT, SLAT(),
             RIGHT_RAIL(), LEFT_RAIL(),
         ],
         unc=["Panels list with sizes for every part."]),
    page(5, "parts_list",
         fasteners=[DOWEL(28), SCREW(28), HEADLESS(2), BOLT80(8), SPACER(2), NUT(4), WASHER(4), BOLT90(4), MOON(4)],
         tools=[SPANNER, HEX, DRIVER, tool("small hammer"), tool("ruler/tape measure"), tool("scissors")],
         unc=["Fittings A-M, then tools required (not provided): tape measure, scissors, screwdriver, hammer."]),
    page(6, "assembly_step",
         parts=[WIDE_RAIL(1), NARROW_RAIL(1), LEFT_RAIL(1), RIGHT_RAIL(1)],
         fasteners=[DOWEL(28)],
         actions=[
             action("insert", "", "wide headboard rail", "A", "", "inward",
                    "wooden dowel A pushed into both ends of wide headboard rail 6, repeat x4"),
             action("insert", "", "narrow headboard rail", "A", "", "inward",
                    "two wooden dowels A pushed into each end of narrow headboard rail 7, repeat x2"),
             action("insert", "", "left side rail", "A", "", "inward",
                    "wooden dowels A pushed into the ends of left side rail 11, repeat x2"),
             action("insert", "", "right side rail", "A", "", "inward",
                    "wooden dowels A pushed into the ends of right side rail 10, repeat x2"),
         ],
         final="headboard rails and side rails with dowels in their ends",
         unc=["Step 1."]),
    page(7, "assembly_step",
         parts=[head_foot("1", "left"), head_foot("2", "right"), WIDE_RAIL(3), NARROW_RAIL(2),
                foot_foot("3", "left"), foot_foot("4", "right")],
         fasteners=[BOLT80(8)],
         tools=[HEX],
         actions=[
             action("attach", "wide headboard rail", "left headboard foot", "D", "hex key I", "inward",
                    "three wide headboard rails 6 pushed onto the dowels in left headboard foot 1 and bolted with 80mm bolt D"),
             action("attach", "narrow headboard rail", "left headboard foot", "D", "hex key I", "inward",
                    "two narrow headboard rails 7 pushed onto left headboard foot 1"),
             action("attach", "right headboard foot", "wide headboard rail", "D", "hex key I", "inward",
                    "right headboard foot 2 pushed onto the other ends of the rails and bolted with 80mm bolt D (arrows)"),
             action("attach", "left footboard foot", "wide headboard rail", "D", "hex key I", "inward",
                    "step 3: left footboard foot 3 bolted to one end of a wide rail 6 with 80mm bolt D"),
             action("attach", "right footboard foot", "wide headboard rail", "D", "hex key I", "inward",
                    "step 3: right footboard foot 4 bolted to the other end of the same rail with 80mm bolt D"),
         ],
         final="headboard of five rails between two tall posts; footboard of one wide rail between two short posts",
         unc=["Steps 2 and 3 on one page. Step 3 inset labels the footboard rail 8, but the main drawing shows rail 6."]),
    page(8, "assembly_step",
         parts=[CENTRAL_LEG(1), RIGHT_RAIL(1)],
         fasteners=[HEADLESS(1)],
         actions=[
             action("insert", "", "central leg", "C", "", "inward",
                    "headless bolt C pushed through the hole in central leg 5"),
             action("slide", "right side rail", "central leg", "C", "", "inward",
                    "right side rail 10 slid onto the headless bolt against central leg 5 (arrows), repeat x2"),
         ],
         final="central leg against the end of the right side rail with the headless bolt through both",
         unc=["Step 4."]),
    page(9, "assembly_step",
         parts=[CENTRAL_LEG(1), RIGHT_RAIL(1)],
         fasteners=[NUT(2), WASHER(2), HEADLESS(1)],
         tools=[SPANNER],
         actions=[
             action("tighten", "", "right side rail", "F", "spanner H", "clockwise",
                    "curved washer G and nut F fitted on the headless bolt inside the round pocket of right side rail 10 and tightened with spanner H"),
         ],
         final="right side rail fixed to the central leg",
         unc=["Step 5."]),
    page(10, "assembly_step",
         parts=[CENTRAL_LEG(1), RIGHT_RAIL(1), LEFT_RAIL(1)],
         fasteners=[HEADLESS(1), NUT(2), WASHER(2)],
         tools=[SPANNER],
         actions=[
             action("slide", "left side rail", "central leg", "C", "", "inward",
                    "left side rail 11 slid onto the other end of the headless bolt through central leg 5 (arrows), repeat x2"),
             action("tighten", "", "left side rail", "F", "spanner H", "clockwise",
                    "curved washer G and nut F tightened inside the pocket of left side rail 11 with spanner H"),
         ],
         final="two long sides, each a right and left side rail joined at a central leg",
         unc=["Step 6."]),
    page(11, "assembly_step",
         parts=[head_foot("1", "left"), head_foot("2", "right"), RIGHT_RAIL(2), CENTRAL_LEG(2)],
         fasteners=[BOLT90(2), MOON(2)],
         tools=[HEX],
         actions=[
             action("attach", "right side rail", "left headboard foot", "L", "hex key I", "inward",
                    "one long side pushed onto the dowels of left headboard foot 1; bolt L through the post into half moon nut M in the rail"),
             action("attach", "right side rail", "right headboard foot", "L", "hex key I", "inward",
                    "the other long side bolted to right headboard foot 2 with bolt L and half moon nut M"),
         ],
         final="both long sides bolted to the headboard",
         unc=["Step 7."]),
    page(12, "assembly_step",
         parts=[foot_foot("3", "left"), foot_foot("4", "right"), LEFT_RAIL(2)],
         fasteners=[BOLT90(2), MOON(2)],
         tools=[HEX],
         actions=[
             action("attach", "left footboard foot", "left side rail", "L", "hex key I", "inward",
                    "footboard post 3 bolted to the foot end of one side with bolt L into half moon nut M"),
             action("attach", "right footboard foot", "left side rail", "L", "hex key I", "inward",
                    "footboard post 4 bolted to the foot end of the other side with bolt L into half moon nut M"),
         ],
         final="complete bed frame: headboard, footboard and two long sides",
         unc=["Step 8."]),
    page(13, "assembly_step",
         parts=[STAMP_SLAT, SLAT(1), RIGHT_RAIL(1), LEFT_RAIL(1)],
         fasteners=[SCREW(4)],
         tools=[DRIVER],
         actions=[
             action("place", "slat with stamp", "left side rail", "B", "cross-head screwdriver", "down",
                    "slat with stamp 8 laid on the side rail ledges 5mm from the footboard and screwed down with 4 x 35mm screw B"),
             action("place", "slat", "right side rail", "B", "cross-head screwdriver", "down",
                    "one slat 9 laid on the ledges at the headboard end and screwed down with screw B"),
         ],
         final="first and last slats fixed across the frame",
         unc=["Step 9. Close-up shows the safety label on slat 8 and a 5mm gap to the footboard."]),
    page(14, "assembly_step",
         parts=[SLAT(13), RIGHT_RAIL(2), LEFT_RAIL(2)],
         fasteners=[SCREW(24), SPACER(2)],
         tools=[DRIVER],
         actions=[
             action("place", "slat", "right side rail", "B", "cross-head screwdriver", "down",
                    "remaining slats 9 laid evenly across the side rail ledges and screwed down with 24x screw B"),
             action("insert", "", "left side rail", "E", "", "down",
                    "two 70mm spacers E set on the ledge at the ends to keep the slats spaced"),
         ],
         final="finished single bed with a full slatted base",
         unc=["Step 10."]),
    page(15, "unknown", unc=["Guarantee and registration text; no assembly content."]),
]

PART_LIST_DIAGRAMS = [
    diagram("part_inventory", f"{name} ({size}) x{qty}", (0.05, y, 0.9, y + 0.05), [label, f"{qty}x"],
            complexity="low", conf=0.9)
    for label, name, size, qty, y in [
        ("1", "Left headboard foot", "925 x 42mm", 1, 0.45),
        ("2", "Right headboard foot", "925 x 42mm", 1, 0.40),
        ("3", "Left footboard foot", "333 x 42mm", 1, 0.33),
        ("4", "Right footboard foot", "333 x 42mm", 1, 0.29),
        ("5", "Central leg", "333 x 42mm", 2, 0.21),
        ("6", "Wide headboard rail", "889 x 90mm", 4, 0.52),
        ("7", "Narrow headboard rail", "889 x 65mm", 2, 0.57),
        ("8", "Slat with stamp", "910 x 70mm", 1, 0.63),
        ("9", "Slats", "910 x 70mm", 13, 0.69),
        ("10", "Right side rail", "929 x 90mm", 2, 0.75),
        ("11", "Left side rail", "929 x 90mm", 2, 0.82),
    ]
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled Kaycie single bed with slatted headboard", (0.03, 0.08, 0.38, 0.75),
                          complexity="low", conf=0.95)], []),
    2: ("warning", [], ["Text only."]),
    3: ("warning", [], ["Text only."]),
    4: ("parts_list", PART_LIST_DIAGRAMS, []),
    5: ("parts_list", [
        diagram("part_inventory", "Wooden dowel 10 x 40mm x28", (0.1, 0.14, 0.3, 0.21), ["A", "28x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "4 x 35mm screw x28", (0.4, 0.14, 0.6, 0.21), ["B", "28x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Headless bolt 1/4 x 155mm x2", (0.63, 0.14, 0.9, 0.21), ["C", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "7 x 80mm bolt x8", (0.1, 0.24, 0.35, 0.31), ["D", "8x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "70mm spacer x2", (0.4, 0.24, 0.6, 0.31), ["E", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Nut 1/4 x4", (0.63, 0.24, 0.85, 0.31), ["F", "4x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Washer x4", (0.1, 0.33, 0.3, 0.4), ["G", "4x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Spanner x2 and hex key x1", (0.4, 0.33, 0.85, 0.4), ["H", "I"], parts=False, tools=True, complexity="low"),
        diagram("part_inventory", "1/4 x 90mm bolt x4 and 1/4 half moon nut x4", (0.1, 0.43, 0.55, 0.5), ["L", "M"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Tools required: tape measure, scissors, cross-head screwdriver, small hammer",
                (0.05, 0.78, 0.7, 0.95), parts=False, tools=True, complexity="low"),
    ], []),
    6: ("assembly_step", [diagram("exploded_view", "Dowels A going into the ends of rails 6, 7, 11 and 10, each with a repeat badge",
                                  (0.15, 0.17, 0.85, 0.93), ["6", "7", "10", "11", "A"], fast=True, arrows=True, action_="insert")], []),
    7: ("assembly_step", [
        diagram("exploded_view", "Headboard: rails 6, 7, 7, 6, 6 between posts 1 and 2, bolts D driven in with hex key I",
                (0.12, 0.12, 0.88, 0.53), ["1", "2", "6", "7", "D", "I"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
        diagram("exploded_view", "Footboard: rail 6 between short posts 3 and 4 with bolts D",
                (0.18, 0.64, 0.88, 0.96), ["3", "4", "6", "8", "D", "I"], fast=True, tools=True, action_="attach"),
    ], ["Two steps on one page."]),
    8: ("assembly_step", [diagram("exploded_view", "Headless bolt C through central leg 5 into right side rail 10 (arrows)",
                                  (0.1, 0.2, 0.9, 0.9), ["5", "10", "C"], fast=True, arrows=True, action_="insert")], []),
    9: ("assembly_step", [diagram("close_up", "Washer G and nut F on the headless bolt tightened with spanner H",
                                  (0.13, 0.3, 0.85, 0.9), ["5", "10", "C", "F", "G", "H"], fast=True, tools=True, arrows=True, action_="tighten")], []),
    10: ("assembly_step", [diagram("exploded_view", "Left side rail 11 joined to rail 10 at central leg 5; nut F and washer G tightened with spanner H",
                                   (0.05, 0.15, 0.95, 0.95), ["5", "10", "11", "F", "G", "H"], fast=True, tools=True, arrows=True, action_="tighten")], []),
    11: ("assembly_step", [diagram("assembly_view", "Long sides bolted to the headboard posts with bolt L and half moon nut M",
                                   (0.05, 0.3, 0.95, 0.8), ["L", "M", "I"], fast=True, tools=True, action_="attach", complexity="high")], []),
    12: ("assembly_step", [diagram("assembly_view", "Footboard bolted to the foot ends of the long sides with bolt L and nut M",
                                   (0.05, 0.27, 0.95, 0.82), ["L", "M", "I"], fast=True, tools=True, action_="attach", complexity="high")], []),
    13: ("assembly_step", [diagram("assembly_view", "Slat 8 at the foot end and slat 9 at the head end screwed down with screw B",
                                   (0.08, 0.2, 0.92, 0.95), ["8", "9", "B"], fast=True, tools=True, action_="tighten", complexity="high")], []),
    14: ("assembly_step", [diagram("assembly_view", "Remaining slats 9 laid across and screwed down; spacers E at the ends",
                                   (0.05, 0.2, 0.95, 0.95), ["9", "B", "E"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high")], []),
    15: ("unknown", [], ["Guarantee page."]),
}

if __name__ == "__main__":
    write_fixture(Path(sys.argv[1]), Path(sys.argv[2]), PAGES, DIAGRAMS)
