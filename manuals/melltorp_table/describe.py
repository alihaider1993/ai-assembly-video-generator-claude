"""Vision results for the IKEA MELLTORP table underframe manual (8 pages).

Run: python manuals/melltorp_table/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

TABLETOP = lambda desc, pos="bottom": part(
    "", "tabletop", desc, "panel", "wood", 1,
    [("hole", 8, "small pre-drilled holes on the underside along both long edges")], pos)
LONG_RAIL = lambda desc, pos="center": part(
    "", "long rail", desc, "beam", "metal", 2,
    [("hole", 4, "screw holes along the top face"), ("slot", 2, "slotted open ends")], pos)
SHORT_RAIL = part(
    "", "short rail", "short rectangular steel tube rail with slotted open ends",
    "beam", "metal", 2, [("slot", 2, "slotted open ends")], "left")
BRACKET = lambda qty, pos: part(
    "131337", "corner bracket",
    "small folded metal bracket with one round centre hole and two side flanges",
    "bracket", "metal", qty,
    [("hole", 1, "centre of the bracket face"), ("connector", 2, "side flanges that hook into the rail ends")], pos)
LEG = part(
    "", "leg", "long square steel tube leg standing upright with a hole near its top end",
    "beam", "metal", 4, [("hole", 1, "near the top end, facing the corner bracket")], "center")
FRAME = lambda desc: part("", "assembled frame", desc, "frame", "mixed", 1, [], "bottom")

PAGES = [
    page(1, "cover",
         final="MELLTORP rectangular table: flat tabletop on a metal underframe of four rails and four square-tube legs",
         unc=["Cover page; product name MELLTORP printed at the top."]),
    page(2, "warning",
         unc=["General advice pictograms: assemble on a soft surface, do not hammer, contact IKEA if unsure. No assembly action."]),
    page(3, "parts_list",
         parts=[BRACKET(4, "top")],
         fasteners=[
             fastener("10051905", "hex socket screw", "screw", "8x"),
             fastener("100469", "hex head bolt (100469 / 131128)", "bolt", "4x"),
             fastener("100843", "spring washer", "washer", "4x"),
             fastener("190015", "plastic plug", "dowel", "8x"),
         ],
         tools=[tool("spanner 128632"), tool("allen key 100001")],
         unc=["Structural parts (tabletop, rails, legs) are not shown in this inventory; only hardware and tools."]),
    page(4, "assembly_step",
         parts=[
             TABLETOP("large flat rectangular tabletop lying upside down"),
             LONG_RAIL("two long rectangular steel tube rails held above the tabletop along its long edges"),
         ],
         fasteners=[fastener("10051905", "hex socket screw", "screw", 8),
                    fastener("190015", "plastic plug", "dowel", 8)],
         tools=[tool("allen key 100001")],
         actions=[
             action("insert", "", "tabletop", "190015", "", "down",
                    "8x plastic plug 190015 pressed into the holes on the underside of the tabletop"),
             action("place", "long rail", "tabletop", "", "", "down",
                    "two long rails lowered onto the tabletop along the long edges, over the plastic plugs"),
             action("tighten", "long rail", "tabletop", "10051905", "allen key 100001", "clockwise",
                    "8x hex socket screw 10051905 driven down through the long rail into the tabletop and turned clockwise with allen key 100001"),
         ],
         final="two long rails screwed to the underside of the upside-down tabletop",
         unc=["Step number 1. Inset shows the rail end profile with its slot."]),
    page(5, "assembly_step",
         parts=[
             TABLETOP("upside-down tabletop with the two long rails already screwed on"),
             LONG_RAIL("long rails fixed along the long edges of the tabletop"),
             BRACKET(4, "right"),
             SHORT_RAIL,
         ],
         actions=[
             action("insert", "131337", "long rail", "", "", "inward",
                    "4x corner bracket 131337 pushed into the open slotted end of each long rail (arrow in close-up)"),
             action("slide", "short rail", "long rail", "", "", "inward",
                    "two short rails pushed in between the long rail ends at the short edges of the tabletop (arrows)"),
             action("rotate", "131337", "short rail", "", "", "counterclockwise",
                    "4x corner bracket 131337 turned so its flange hooks into the end of the short rail (curved arrow)"),
         ],
         final="rectangular rail frame of two long and two short rails on the upside-down tabletop",
         unc=["Page holds steps 2 and 3."]),
    page(6, "assembly_step",
         parts=[
             LEG,
             FRAME("upside-down tabletop with long and short rails joined by corner brackets"),
             BRACKET(1, "top"),
         ],
         fasteners=[fastener("100469", "hex head bolt (100469 / 131128)", "bolt", "4x"),
                    fastener("100843", "spring washer", "washer", 4)],
         tools=[tool("spanner 128632")],
         actions=[
             action("place", "leg", "assembled frame", "", "", "down",
                    "4 legs set upright into the inside corners of the assembled frame"),
             action("insert", "131337", "leg", "100469", "spanner 128632", "clockwise",
                    "4x hex head bolt 100469 with spring washer 100843 put through the corner bracket 131337 into each leg and screwed in clockwise"),
         ],
         final="four legs standing in the corners of the upside-down frame with bolts loosely fitted",
         unc=["Step 4. Two pictograms: spring washer under the bolt head is correct; the crossed-out one shows the wrong fit."]),
    page(7, "assembly_step",
         parts=[
             LEG,
             FRAME("upside-down tabletop and rail frame with four legs attached at the corners"),
             BRACKET(1, "top"),
         ],
         fasteners=[fastener("", "hex head bolt", "bolt", 4)],
         tools=[tool("spanner 128632")],
         actions=[
             action("tighten", "leg", "assembled frame", "hex head bolt", "spanner 128632", "clockwise",
                    "4x hex head bolt in each corner bracket fully tightened clockwise with spanner 128632"),
         ],
         final="complete table underframe with four legs bolted to the rail frame, still upside down",
         unc=["Step 5. Info panel shows the spanner crossed out over a waste bin; probably means keep the spanner for re-tightening.",
              "Bolt label numbers are not printed on this page."]),
    page(8, "unknown",
         unc=["Back page with copyright and date only; no assembly content."]),
]


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled MELLTORP table: rectangular top on four square legs",
                          (0.05, 0.3, 0.95, 0.75), complexity="low", conf=0.95)], []),
    2: ("warning", [
        diagram("warning", "Do not assemble on a hard floor (crossed out); use a soft rug instead",
                (0.06, 0.04, 0.94, 0.24), parts=False, complexity="low", action_="warning"),
        diagram("warning", "Confused person with hammer and manual; person phoning IKEA for help",
                (0.06, 0.27, 0.94, 0.47), parts=False, tools=True, complexity="low", action_="warning"),
    ], ["General safety and help advice."]),
    3: ("parts_list", [
        diagram("part_inventory", "Hex socket screw 8x", (0.05, 0.05, 0.15, 0.32), ["10051905", "8x"], parts=False, fast=True, complexity="low", conf=0.9),
        diagram("part_inventory", "Hex head bolt 4x", (0.19, 0.11, 0.3, 0.32), ["100469", "131128", "4x"], parts=False, fast=True, complexity="low", conf=0.9),
        diagram("part_inventory", "Folded metal corner bracket with centre hole 4x", (0.35, 0.14, 0.58, 0.32), ["131337", "4x"], complexity="low", conf=0.85),
        diagram("part_inventory", "Spring washer 4x", (0.62, 0.22, 0.75, 0.32), ["100843", "4x"], parts=False, fast=True, complexity="low", conf=0.9),
        diagram("part_inventory", "Plastic plug 8x", (0.82, 0.21, 0.94, 0.32), ["190015", "8x"], parts=False, fast=True, complexity="low", conf=0.85),
        diagram("part_inventory", "Combination spanner 1x", (0.05, 0.37, 0.73, 0.59), ["128632", "1x"], parts=False, tools=True, complexity="low", conf=0.9),
        diagram("part_inventory", "Allen key 1x", (0.78, 0.42, 0.94, 0.59), ["100001", "1x"], parts=False, tools=True, complexity="low", conf=0.9),
    ], []),
    4: ("assembly_step", [
        diagram("exploded_view", "Two long rails above the upside-down tabletop with screws above and plastic plugs below each rail hole",
                (0.05, 0.57, 0.94, 0.9), ["1"], fast=True, arrows=False, action_="attach", complexity="high"),
        diagram("close_up", "Screw 10051905 driven with allen key 100001 through the rail; plug 190015 under the rail",
                (0.64, 0.04, 0.94, 0.55), ["8x", "100001", "10051905", "190015"], fast=True, tools=True, arrows=True, action_="tighten"),
        diagram("close_up", "Rail end profile showing the slotted open end", (0.08, 0.81, 0.26, 0.91), action_="none", complexity="low", conf=0.7),
    ], []),
    5: ("assembly_step", [
        diagram("assembly_view", "Step 2: corner brackets placed at the four ends of the long rails on the tabletop",
                (0.05, 0.18, 0.93, 0.42), ["2"], action_="insert"),
        diagram("close_up", "Bracket 131337 pushed into the rail end (arrow)", (0.66, 0.04, 0.9, 0.18), ["4x", "131337"], arrows=True, action_="insert"),
        diagram("assembly_view", "Step 3: short rails pushed between the long rail ends (arrows)", (0.05, 0.66, 0.94, 0.92), ["3"], arrows=True, action_="slide"),
        diagram("close_up", "Bracket turned to hook into the short rail end (curved arrow)", (0.48, 0.5, 0.7, 0.65), ["4x"], arrows=True, action_="rotate"),
    ], ["Two steps on one page."]),
    6: ("assembly_step", [
        diagram("assembly_view", "Four legs placed upright into the corners of the upside-down rail frame",
                (0.1, 0.43, 0.75, 0.81), ["4"], fast=True, action_="attach", complexity="high"),
        diagram("close_up", "Bolt 100469 with spring washer 100843 through the corner bracket into the leg; spanner 128632",
                (0.4, 0.12, 0.94, 0.4), ["4x", "100843", "100469", "131128", "128632"], fast=True, tools=True, arrows=True, action_="tighten"),
        diagram("warning", "Washer under bolt head correct vs crossed-out wrong fit", (0.06, 0.29, 0.35, 0.4), fast=True, parts=False, action_="warning", complexity="low"),
    ], []),
    7: ("assembly_step", [
        diagram("assembly_view", "Underframe with four legs bolted at the corners", (0.18, 0.34, 0.78, 0.69), ["5"], fast=True, action_="tighten"),
        diagram("close_up", "Bolt in corner bracket tightened with spanner 128632", (0.39, 0.04, 0.94, 0.31), ["4x", "128632"], fast=True, tools=True, arrows=True, action_="tighten"),
        diagram("warning", "Info: spanner crossed out over a waste bin", (0.51, 0.72, 0.94, 0.92), parts=False, tools=True, arrows=True, action_="warning", complexity="low", conf=0.6),
    ], []),
    8: ("unknown", [], ["Back page: copyright and date only."]),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS)
