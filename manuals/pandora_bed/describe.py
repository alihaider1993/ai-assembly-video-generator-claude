"""Vision results for the Habitat Pandora ottoman bed manual (13 pages).

Sizes are the 4'6 (double) column of the parts list.

Run: python manuals/pandora_bed/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

UPHOLSTERED = "fabric-covered board with panel seams"

RIGHT_RAIL = lambda qty=1: part(
    "1", "right side panel", f"long {UPHOLSTERED}, bolt holes at both ends, hinge plate holes near the headboard end",
    "panel", "fabric", qty, [("hole", 4, "bolt holes at each end"), ("hole", 5, "hinge holes near the headboard end")],
    "top", size=(30, 1930, 300))
LEFT_RAIL = lambda qty=1: part(
    "2", "left side panel", f"long {UPHOLSTERED}, bolt holes at both ends, hinge plate holes near the headboard end",
    "panel", "fabric", qty, [("hole", 4, "bolt holes at each end"), ("hole", 5, "hinge holes near the headboard end")],
    "top", size=(30, 1930, 300))
HEADBOARD = part(
    "3", "headboard", "tall upholstered headboard with vertical channels; plain lower section marked FRONT",
    "panel", "fabric", 1, [("hole", 8, "bolt holes up both edges of the lower section")], "top", size=(1465, 40, 995))
FOOTBOARD = part(
    "4", "footboard", f"low {UPHOLSTERED}, bolt holes up both ends and in the middle", "panel", "fabric", 1,
    [("hole", 8, "bolt holes at each end"), ("hole", 2, "holes in the middle for the support block")], "center",
    size=(1460, 30, 300))
HINGE = lambda qty=2: part(
    "5", "hinge", "folding metal lift hinge with a gas piston attached", "bracket", "metal", qty,
    [("hole", 5, "plate holes for the side rail"), ("hole", 3, "holes for the lift frame")], "right")
FOOT = lambda qty=4: part(
    "6", "foot", "small round glide foot, 35mm across and 15mm high", "cylinder", "plastic", qty,
    [("hole", 1, "screw hole through the middle")], "center", size=(35, 35, 15))
FABRIC_BASE = part(
    "7", "fabric base panel", "large flat fabric sheet with velcro edges closing the underside of the bed box",
    "panel", "fabric", 1, [], "right", size=(1420, 1960, 3))
SUPPORT_LEG = lambda qty=2: part(
    "8", "support leg", "round metal leg 205mm long on a flat mounting plate", "cylinder", "metal", qty,
    [("hole", 2, "two bolt holes in the plate")], "left", size=(25, 25, 205))
HEAD_RAIL = part(
    "9", "lift frame back rail", "metal bar with an upturned tab at each end and in the middle; extra holes for the brackets",
    "beam", "metal", 1, [("hole", 6, "bolt holes"), ("hole", 4, "extra holes for the mattress brackets")], "right")
FOOT_RAIL = part(
    "10", "lift frame front rail", "metal bar with an upturned tab at each end and in the middle", "beam", "metal", 1,
    [("hole", 6, "bolt holes")], "left")
LONG_RAIL = lambda qty=2: part(
    "11", "lift frame long rail", "long metal bar with a row of slat cap holes", "beam", "metal", qty,
    [("hole", 28, "slat cap holes along the top"), ("hole", 4, "bolt holes at the ends")], "right")
CENTRE_RAIL = part(
    "12", "lift frame centre rail", "long metal bar with pairs of holes on the underside for the support legs", "beam",
    "metal", 1, [("hole", 14, "slat cap holes"), ("hole", 4, "support leg holes on the underside")], "bottom")
SLAT = lambda qty=28: part(
    "13", "slat", "thin bentwood slat arched upwards", "panel", "wood", qty, [("slot", 2, "fits into slat caps at each end")],
    "right", size=(675, 53, 9))
MIDDLE_CAP = lambda qty=14: part(
    "14", "middle cap", "plastic double cap holding two slat ends, peg underneath", "block", "plastic", qty,
    [("peg", 1, "peg into the centre rail")], "left", size=(55, 60, 15))
CROSS_RAIL = part(
    "15", "box cross rail", "metal bar with a bent-down tab at each end", "beam", "metal", 1,
    [("hole", 4, "two screw holes in each end tab")], "right")
SUPPORT_BLOCK = part(
    "16", "centre support block", "small wooden block with two bolt holes", "block", "wood", 1,
    [("hole", 2, "bolt holes")], "left", size=(130, 30, 30))
BRACKET = lambda qty=2: part(
    "17", "retainer bracket", "tall U-shaped metal mattress retainer on a foot plate", "bracket", "metal", qty,
    [("hole", 2, "bolt holes in the foot plate")], "right")
END_CAP = lambda qty=28: part(
    "18", "end cap", "plastic single cap holding one slat end, peg underneath", "block", "plastic", qty,
    [("peg", 1, "peg into the long rail")], "left", size=(55, 40, 15))

BOLT45 = lambda qty: fastener("A", "8x45mm bolt", "bolt", qty)
BOLT25 = lambda qty: fastener("B", "8x25mm bolt", "bolt", qty)
BOLT30 = lambda qty: fastener("C", "8x30mm bolt", "bolt", qty)
SCREW45 = lambda qty: fastener("D", "4x45mm wood screw", "screw", qty)
NUT = lambda qty: fastener("E", "nut", "nut", qty)
WASHER = lambda qty: fastener("F", "17mm flat washer", "washer", qty)
SPRING = lambda qty: fastener("G", "12mm spring washer", "washer", qty)
SCREW30 = lambda qty: fastener("J", "4x30mm wood screw", "screw", qty)

ALLEN = tool("5mm allen key")
SPANNER = tool("spanner")
BOX_SPANNER = tool("box spanner")
DRIVER = tool("phillips screwdriver")

PAGES = [
    page(1, "cover",
         final="Pandora ottoman bed: tall channelled headboard, upholstered box with the slatted lift-up base raised on gas hinges",
         unc=["Cover page; product name Pandora and Habitat logo."]),
    page(2, "warning", unc=["Product details, safety and care advice, ottoman safety warnings; text only."]),
    page(3, "parts_list",
         fasteners=[BOLT45(8), BOLT25(20), BOLT30(26), SCREW45(4), NUT(6), WASHER(54), SPRING(28), SCREW30(4)],
         unc=["Fittings A-J shown to scale; there is no H or I."]),
    page(4, "parts_list",
         parts=[RIGHT_RAIL(), LEFT_RAIL(), HEADBOARD, FOOTBOARD, HINGE(), FOOT(), FABRIC_BASE, SUPPORT_LEG(),
                HEAD_RAIL, FOOT_RAIL, LONG_RAIL(), CENTRE_RAIL, SLAT()],
         unc=["Sizes listed for 4', 4'6 and 5' beds; the 4'6 sizes are used.",
              "Hinge 5 comes as one pair with the piston attached.",
              "Ottoman end frame (headboard) 9 has extra holes for the mattress brackets."]),
    page(5, "parts_list",
         parts=[CROSS_RAIL, SUPPORT_BLOCK, BRACKET()],
         unc=["Double slat caps 14 and single slat caps 18: 14 and 28 for 4'6, 15 and 30 for 5'.",
              "Stretcher 15 is called box cross rail here; it runs across the box between the side rails."]),
    page(6, "parts_list",
         tools=[ALLEN, SPANNER, BOX_SPANNER, tool("ruler/tape measure"), DRIVER],
         unc=["Tools required; allen key, spanner and box spanner supplied."]),
    page(7, "assembly_step",
         parts=[HEADBOARD, FOOTBOARD, SUPPORT_BLOCK],
         fasteners=[BOLT30(16), WASHER(18), SPRING(16), BOLT45(2)],
         tools=[ALLEN],
         actions=[
             action("insert", "", "headboard", "C", "", "inward",
                    "8x30mm bolts C with spring washer G and flat washer F screwed loosely into both edges of headboard 3 (8x)"),
             action("insert", "", "footboard", "C", "", "inward",
                    "8x30mm bolts C with spring washer G and flat washer F screwed loosely into both ends of footboard 4 (8x)"),
             action("attach", "centre support block", "footboard", "A", "5mm allen key", "down",
                    "step 2: centre support block 16 bolted to the middle of footboard 4 with 2x 8x45mm bolt A and flat washer F"),
         ],
         final="headboard and footboard lying face down with bolts started in their ends; support block on the footboard",
         unc=["Steps 1 and 2. Leave screws loose. Headboard and footboard drawn lying flat on a protected surface."]),
    page(8, "assembly_step",
         parts=[HEADBOARD, FOOTBOARD, RIGHT_RAIL(), LEFT_RAIL(), CROSS_RAIL],
         fasteners=[BOLT30(16), SCREW45(4)],
         tools=[ALLEN, DRIVER],
         actions=[
             action("attach", "right side panel", "headboard", "C", "5mm allen key", "inward",
                    "right side panel 1 hooked onto the bolts C in headboard 3 (holes at headboard end) and tightened"),
             action("attach", "left side panel", "headboard", "C", "5mm allen key", "inward",
                    "left side panel 2 hooked onto the bolts C in headboard 3"),
             action("attach", "footboard", "right side panel", "C", "5mm allen key", "inward",
                    "footboard 4 hooked onto the foot ends of right side panel 1 and left side panel 2 with bolts C"),
             action("attach", "box cross rail", "right side panel", "D", "phillips screwdriver", "inward",
                    "step 4: box cross rail 15 screwed across between right side panel 1 and left side panel 2 with 4x 4x45mm wood screw D"),
         ],
         final="upholstered bed box: headboard, two side rails, footboard and a cross rail across the middle",
         unc=["Steps 3 and 4. Do not fully tighten fixings. Turn product after step 4."]),
    page(9, "assembly_step",
         parts=[FABRIC_BASE, FOOT(), RIGHT_RAIL(), LEFT_RAIL()],
         fasteners=[SCREW30(4)],
         tools=[DRIVER],
         actions=[
             action("place", "fabric base panel", "right side panel", "", "", "inward",
                    "step 5: fabric base panel 7 pressed onto the underside of the box with velcro fastening (arrows)"),
             action("attach", "foot", "right side panel", "J", "phillips screwdriver", "inward",
                    "step 6: foot 6 screwed to each corner of the underside with 4x30mm wood screw J, 4x"),
         ],
         final="bed box closed underneath with four feet at the corners",
         unc=["Steps 5 and 6; the box is drawn on its side. Turn product after step 5 and again after step 6.",
              "Feet sit at the corners under the side rails, headboard and footboard."]),
    page(10, "assembly_step",
         parts=[HINGE(), RIGHT_RAIL(), LEFT_RAIL(), SUPPORT_LEG(), CENTRE_RAIL],
         fasteners=[BOLT30(10), WASHER(14), BOLT25(4)],
         tools=[ALLEN],
         actions=[
             action("attach", "hinge", "right side panel", "C", "5mm allen key", "inward",
                    "step 7: one hinge 5 bolted inside right side panel 1 near the headboard with 5x 8x30mm bolt C and washer F"),
             action("attach", "hinge", "left side panel", "C", "5mm allen key", "inward",
                    "the other hinge 5 bolted inside left side panel 2 near the headboard with 5x 8x30mm bolt C and washer F"),
             action("attach", "support leg", "lift frame centre rail", "B", "5mm allen key", "down",
                    "step 8: support leg 8 bolted to the holes on the underside of lift frame centre rail 12 with 8x25mm bolt B and washer F, 2x"),
         ],
         final="hinges inside the box at the headboard end; centre rail with two legs (shown upside down)",
         unc=["Steps 7 and 8. Beware of risk of entrapment from folding hinges."]),
    page(11, "assembly_step",
         parts=[HEAD_RAIL, FOOT_RAIL, LONG_RAIL(), CENTRE_RAIL, BRACKET()],
         fasteners=[BOLT25(16), WASHER(16), SPRING(12)],
         tools=[ALLEN],
         actions=[
             action("attach", "lift frame back rail", "lift frame long rail", "B", "5mm allen key", "inward",
                    "step 9: lift frame back rail 9 bolted across the headboard ends of both lift frame long rails 11 with 8x25mm bolt B, spring washer G and washer F, 2x"),
             action("attach", "lift frame front rail", "lift frame long rail", "B", "5mm allen key", "inward",
                    "lift frame front rail 10 bolted across the footboard ends of both lift frame long rails 11, 2x"),
             action("attach", "lift frame centre rail", "lift frame back rail", "B", "5mm allen key", "inward",
                    "lift frame centre rail 12 (legs at the footboard end) bolted between the middle tabs of lift frame back rail 9 and lift frame front rail 10"),
             action("attach", "retainer bracket", "lift frame back rail", "B", "5mm allen key", "inward",
                    "step 10: retainer bracket 17 bolted to the extra holes in lift frame back rail 9 with 8x25mm bolt B and washer F, 2x"),
         ],
         final="rectangular metal lift frame with a centre rail, two legs and two mattress brackets at the head end",
         unc=["Steps 9 and 10. Frame shown upside down; turn product after step 10."]),
    page(12, "assembly_step",
         parts=[HINGE(), LONG_RAIL(), RIGHT_RAIL(), LEFT_RAIL()],
         fasteners=[BOLT45(6), NUT(6), WASHER(6)],
         tools=[ALLEN, SPANNER, BOX_SPANNER],
         actions=[
             action("attach", "lift frame long rail", "right side panel", "A", "5mm allen key", "down",
                    "step 11: lift frame lowered onto the box; lift frame long rail 11 bolted to the hinge on right side panel 1 with 8x45mm bolt A, washer F and nut E, held with the spanner"),
             action("attach", "lift frame long rail", "left side panel", "A", "5mm allen key", "down",
                    "the other lift frame long rail 11 bolted to the hinge on left side panel 2 the same way. Repeat both sides"),
         ],
         final="slatted lift frame hinged into the bed box at the headboard end; pistons connected",
         unc=["Steps 11 and 12. Ensure frame is square.",
              "Step 12: the hinge piston is clipped onto its ball with the box spanner (nut pre-assembled), both sides; it is part of hinge 5, so no join.",
              "Two people required; tighten all fixings before proceeding."]),
    page(13, "assembly_step",
         parts=[SLAT(2), LONG_RAIL(), CENTRE_RAIL],
         actions=[
             action("place", "slat", "lift frame long rail", "", "", "down",
                    "slats 13 lie across the lift frame from lift frame long rail 11 to lift frame centre rail 12, arching upwards. Repeat x14"),
         ],
         final="finished ottoman bed with 14 rows of arched slats across the lift frame",
         unc=["Step 13. Repeat x14 for 4' and 4'6, x15 for 5'. Slats to arch upwards.",
              "a-c: each pair of slats is joined by a double slat cap 14 in the middle and single slat caps 18 at the outer ends; "
              "the caps peg into the long and centre rails. The 42 small caps are left out of the parts so the video shows the slats."]),
]

SMALL = dict(parts=False, fast=True, complexity="low")

PART_LIST_DIAGRAMS = [
    diagram("part_inventory", f"{name} ({size}) x{qty}", region, [label, f"{qty}x"], complexity="low", conf=0.9)
    for label, name, size, qty, region in [
        ("1", "Right side panel", "1930 x 300mm", 1, (0.05, 0.13, 0.45, 0.25)),
        ("2", "Left side panel", "1930 x 300mm", 1, (0.05, 0.26, 0.45, 0.37)),
        ("3", "Headboard", "1465 x 995mm", 1, (0.55, 0.13, 0.95, 0.37)),
        ("4", "Footboard", "1460 x 300mm", 1, (0.05, 0.38, 0.45, 0.49)),
        ("6", "Foot", "35 x 15mm", 4, (0.05, 0.53, 0.45, 0.6)),
        ("7", "Fabric base panel", "1960 x 1420mm", 1, (0.55, 0.49, 0.95, 0.62)),
        ("8", "Support leg", "25 x 205mm", 2, (0.05, 0.63, 0.45, 0.7)),
        ("9", "Lift frame back rail", "1363 x 85mm", 1, (0.55, 0.63, 0.95, 0.76)),
        ("10", "Lift frame front rail", "1363 x 85mm", 1, (0.05, 0.74, 0.45, 0.85)),
        ("11", "Lift frame long rail", "1822 x 30mm", 2, (0.55, 0.77, 0.95, 0.84)),
        ("12", "Lift frame centre rail", "1822 x 30mm", 1, (0.05, 0.87, 0.45, 0.93)),
        ("13", "Slat", "675 x 53mm", 28, (0.55, 0.87, 0.95, 0.95)),
    ]
] + [diagram("part_inventory", "Hinge x1 pair, piston attached", (0.55, 0.38, 0.95, 0.47), ["5", "2x"], complexity="low")]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Pandora ottoman bed with the lift-up base raised", (0.03, 0.08, 0.5, 0.6),
                          complexity="medium", conf=0.95)], []),
    2: ("warning", [], ["Text only."]),
    3: ("parts_list", [
        diagram("part_inventory", "8x45mm bolt x8", (0.1, 0.18, 0.45, 0.3), ["A", "8x"], **SMALL),
        diagram("part_inventory", "8x25mm bolt x20", (0.5, 0.18, 0.9, 0.3), ["B", "20x"], **SMALL),
        diagram("part_inventory", "8x30mm bolt x26", (0.1, 0.3, 0.45, 0.42), ["C", "26x"], **SMALL),
        diagram("part_inventory", "4x45mm wood screw x4", (0.5, 0.3, 0.9, 0.42), ["D", "4x"], **SMALL),
        diagram("part_inventory", "Nut x6", (0.1, 0.42, 0.45, 0.53), ["E", "6x"], **SMALL),
        diagram("part_inventory", "17mm flat washer x54", (0.5, 0.42, 0.9, 0.53), ["F", "54x"], **SMALL),
        diagram("part_inventory", "12mm spring washer x28", (0.1, 0.53, 0.45, 0.65), ["G", "28x"], **SMALL),
        diagram("part_inventory", "4x30mm wood screw x4", (0.5, 0.53, 0.9, 0.65), ["J", "4x"], **SMALL),
    ], []),
    4: ("parts_list", PART_LIST_DIAGRAMS, ["4'6 sizes used."]),
    5: ("parts_list", [
        diagram("part_inventory", "Middle cap (55mm) x14", (0.05, 0.13, 0.45, 0.28), ["14", "14x"], complexity="low"),
        diagram("part_inventory", "Box cross rail (1390 x 25mm) x1", (0.5, 0.13, 0.95, 0.28), ["15", "1x"], complexity="low"),
        diagram("part_inventory", "Centre support block (130 x 30mm) x1", (0.05, 0.3, 0.45, 0.42), ["16", "1x"], complexity="low"),
        diagram("part_inventory", "Retainer bracket x2", (0.5, 0.3, 0.95, 0.42), ["17", "2x"], complexity="low"),
        diagram("part_inventory", "End cap (55mm) x28", (0.05, 0.45, 0.45, 0.58), ["18", "28x"], complexity="low"),
    ], []),
    6: ("parts_list", [diagram("part_inventory", "Tools: allen key, spanner, box spanner (supplied), tape measure, Phillips screwdriver",
                               (0.05, 0.12, 0.95, 0.42), parts=False, tools=True, complexity="low")], []),
    7: ("assembly_step", [
        diagram("exploded_view", "Bolts C with washers G and F started in headboard 3 and footboard 4",
                (0.05, 0.1, 0.95, 0.58), ["3", "4", "C", "F", "G"], fast=True, arrows=True, action_="insert"),
        diagram("exploded_view", "Support block 16 bolted to footboard 4 with bolts A and washers F",
                (0.1, 0.6, 0.9, 0.95), ["4", "16", "A", "F"], fast=True, tools=True, arrows=True, action_="attach"),
    ], ["Two steps on one page."]),
    8: ("assembly_step", [
        diagram("assembly_view", "Side rails 1 and 2 hooked onto the headboard 3 and footboard 4 bolts",
                (0.05, 0.08, 0.95, 0.5), ["1", "2", "3", "4", "C"], fast=True, tools=True, action_="attach", complexity="high"),
        diagram("assembly_view", "Cross rail 15 screwed between side rails 1 and 2 with screws D",
                (0.05, 0.52, 0.95, 0.97), ["1", "2", "15", "D"], fast=True, tools=True, action_="attach"),
    ], []),
    9: ("assembly_step", [
        diagram("assembly_view", "Fabric base 7 pressed onto the underside with velcro", (0.1, 0.08, 0.9, 0.45), ["7"],
                arrows=True, action_="place"),
        diagram("assembly_view", "Feet 6 screwed to the underside corners with screws J", (0.1, 0.48, 0.9, 0.95), ["6", "J"],
                fast=True, tools=True, action_="attach"),
    ], []),
    10: ("assembly_step", [
        diagram("assembly_view", "Hinges 5 bolted inside side rails 1 and 2 with bolts C and washers F", (0.05, 0.08, 0.95, 0.53),
                ["1", "2", "5", "C", "F"], fast=True, tools=True, action_="attach", complexity="high"),
        diagram("exploded_view", "Support legs 8 bolted under centre rail 12 with bolts B and washers F", (0.05, 0.55, 0.95, 0.95),
                ["8", "12", "B", "F"], fast=True, tools=True, action_="attach"),
    ], []),
    11: ("assembly_step", [
        diagram("exploded_view", "Lift frame: rails 9, 10, 11, 11 and 12 bolted with B, G and F (upside down)",
                (0.05, 0.08, 0.95, 0.5), ["9", "10", "11", "12", "B", "G", "F"], fast=True, tools=True, action_="attach", complexity="high"),
        diagram("exploded_view", "Mattress brackets 17 bolted to head rail 9", (0.05, 0.53, 0.95, 0.95),
                ["9", "10", "17", "B", "F"], fast=True, tools=True, action_="attach"),
    ], []),
    12: ("assembly_step", [
        diagram("assembly_view", "Lift frame lowered into the box and bolted to hinges 5 with A, F and E",
                (0.05, 0.08, 0.95, 0.53), ["1", "2", "5", "9", "10", "11", "A", "E", "F"], fast=True, tools=True,
                arrows=True, action_="attach", complexity="high"),
        diagram("close_up", "Piston clipped on with the box spanner, nut pre-assembled", (0.05, 0.55, 0.95, 0.95),
                ["1", "2", "5"], tools=True, action_="tighten", complexity="high"),
    ], []),
    13: ("assembly_step", [
        diagram("exploded_view", "a: slats 13 into middle cap 14 and end caps 18, repeat x14", (0.1, 0.05, 0.95, 0.3),
                ["13", "14", "18"], arrows=True, action_="insert"),
        diagram("assembly_view", "Slat rows pressed onto lift frame rails 11 and 12; slats arch upwards",
                (0.1, 0.3, 0.95, 0.98), ["1", "2", "8", "11", "12", "13", "14", "18"], arrows=True, action_="place", complexity="high"),
    ], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="Habitat Pandora Ottoman Bed")
