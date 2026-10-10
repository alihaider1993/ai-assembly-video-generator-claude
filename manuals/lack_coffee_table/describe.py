"""Vision results for the IKEA LACK coffee table manual (8 pages).

Run: python manuals/lack_coffee_table/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 118 x 78 cm table, 45 cm high.
TABLETOP = lambda desc: part(
    "", "tabletop", desc, "panel", "wood", 1,
    [("hole", 4, "pre-drilled hole in each corner of the underside")], "bottom",
    size=(1180, 780, 50))
LEG = lambda desc, qty=4: part(
    "", "leg", desc, "beam", "wood", qty,
    [("hole", 1, "centre hole in the top end"), ("hole", 2, "pre-drilled bracket holes on the inner face")],
    "center", size=(50, 50, 400))
BRACKET = lambda qty, pos="center": part(
    "120298", "shelf bracket",
    "small angle bracket with an upright face holding a round hole and a slotted hole, and a foot with one hole",
    "bracket", "metal", qty,
    [("hole", 2, "upright face, round and slotted"), ("hole", 1, "foot")], pos, size=(30, 25, 30))
SHELF = lambda desc: part(
    "", "shelf", desc, "panel", "wood", 1,
    [("hole", 4, "small holes in the edges near each corner")], "center", size=(1080, 680, 16))

PAGES = [
    page(1, "cover",
         final="LACK coffee table: thick rectangular top on four square legs with a shelf near the floor between the legs",
         unc=["Cover shows two sizes of the same table; described as the larger 118 x 78 cm one."]),
    page(2, "warning",
         unc=["Tools needed (screwdriver, hammer, awl) and general advice: assemble on a soft surface, ask IKEA if unsure. No assembly action."]),
    page(3, "parts_list",
         parts=[BRACKET(4, "top")],
         fasteners=[
             fastener("115980", "double-ended screw", "screw", "4x"),
             fastener("108530", "bracket screw", "screw", "4x"),
             fastener("109041", "short shelf screw", "screw", "4x"),
         ],
         unc=["Tabletop, legs and shelf are not shown in this inventory; only hardware.",
              "Part 120938 (1x) is a plastic drilling template used in steps 3 and 5 to mark the bracket holes; it is a jig, not part of the table."]),
    page(4, "assembly_step",
         parts=[TABLETOP("thick rectangular tabletop lying upside down"),
                LEG("four square legs held upright over the corners of the upside-down tabletop")],
         fasteners=[fastener("115980", "double-ended screw", "screw", 4)],
         actions=[
             action("insert", "", "tabletop", "115980", "", "clockwise",
                    "4x double-ended screw 115980 turned by hand into the hole in each corner of the tabletop (step 1)"),
             action("attach", "leg", "tabletop", "115980", "", "clockwise",
                    "4x leg lowered onto the double-ended screw and turned clockwise until tight against the tabletop (step 2)"),
         ],
         final="four legs standing up from the corners of the upside-down tabletop",
         unc=["Page holds steps 1 and 2."]),
    page(5, "assembly_step",
         parts=[LEG("two legs on one long side of the upside-down table", 2)],
         final="bracket hole positions marked on two legs",
         unc=["Step 3: the plastic template 120938 is pressed onto the inner face of a leg (2x) to mark the bracket holes, then lifted off. Template is a jig, not a part; no part moves."]),
    page(6, "assembly_step",
         parts=[LEG("two legs on one long side of the upside-down table", 2), BRACKET(2, "center")],
         fasteners=[fastener("108530", "bracket screw", "screw", 2)],
         tools=[tool("screwdriver")],
         actions=[
             action("attach", "shelf bracket", "leg", "108530", "screwdriver", "clockwise",
                    "2x shelf bracket 120298 screwed to the inner face of a leg with bracket screw 108530, not the shorter 109041 (step 4)"),
         ],
         final="two shelf brackets fixed to the legs on one side",
         unc=["Step 5 on the same page repeats the template marking on the other two legs."]),
    page(7, "assembly_step",
         parts=[LEG("two legs on the other long side", 2), BRACKET(2, "center"),
                SHELF("flat rectangular shelf panel tilted in between the four legs")],
         fasteners=[fastener("108530", "bracket screw", "screw", 2)],
         tools=[tool("screwdriver")],
         actions=[
             action("attach", "shelf bracket", "leg", "108530", "screwdriver", "clockwise",
                    "2x shelf bracket 120298 screwed to the inner face of the other legs with bracket screw 108530 (step 6)"),
             action("place", "shelf", "shelf bracket", "", "", "inward",
                    "shelf tilted and slid in between the four legs onto the shelf brackets (step 7)"),
         ],
         final="shelf resting on the four shelf brackets between the legs, table still upside down",
         unc=["Page holds steps 6 and 7."]),
    page(8, "assembly_step",
         parts=[SHELF("shelf between the legs on the four brackets"), BRACKET(4, "center")],
         fasteners=[fastener("109041", "short shelf screw", "screw", 4)],
         tools=[tool("screwdriver")],
         actions=[
             action("tighten", "shelf", "shelf bracket", "109041", "screwdriver", "clockwise",
                    "4x short shelf screw 109041 driven through each shelf bracket into the edge of the shelf (step 8, insets 1-4)"),
         ],
         final="complete LACK coffee table, upside down; turned over to stand on its legs",
         unc=["Turning the table upright is not drawn but implied."]),
]


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Two LACK coffee tables: top on four square legs with a low shelf",
                          (0.02, 0.08, 0.98, 0.9), complexity="low", conf=0.95)], []),
    2: ("warning", [
        diagram("warning", "Tools: screwdriver, hammer, awl", (0.05, 0.02, 0.95, 0.24), parts=False, tools=True, complexity="low", action_="warning"),
        diagram("warning", "Do not assemble on a hard floor; use a soft surface", (0.05, 0.27, 0.95, 0.47), parts=False, complexity="low", action_="warning"),
        diagram("warning", "Confused person; person phoning IKEA for help", (0.05, 0.5, 0.95, 0.7), parts=False, complexity="low", action_="warning"),
    ], []),
    3: ("parts_list", [
        diagram("part_inventory", "Double-ended screw 4x", (0.08, 0.05, 0.14, 0.45), ["115980", "4x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Bracket screw 4x", (0.22, 0.29, 0.28, 0.45), ["108530", "4x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Short shelf screw 4x", (0.36, 0.33, 0.42, 0.45), ["109041", "4x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Angle shelf bracket 4x", (0.5, 0.29, 0.63, 0.45), ["120298", "4x"], complexity="low"),
        diagram("part_inventory", "Plastic drilling template 1x", (0.07, 0.62, 0.55, 0.9), ["120938", "1x"], parts=False, tools=True, complexity="low"),
    ], ["Template is a jig, not a table part."]),
    4: ("assembly_step", [
        diagram("close_up", "Double-ended screw turned into the tabletop corner", (0.02, 0.1, 0.4, 0.4), ["1", "4x", "115980"], fast=True, arrows=True, action_="insert"),
        diagram("assembly_view", "Upside-down tabletop with screws standing in the corners", (0.4, 0.1, 0.98, 0.4), ["1"], fast=True, action_="insert"),
        diagram("assembly_view", "Legs turned onto the screws in the corners", (0.02, 0.55, 0.98, 0.95), ["2", "4x"], arrows=True, action_="attach"),
    ], []),
    5: ("assembly_step", [
        diagram("close_up", "Template pressed onto a leg to mark holes, then removed", (0.02, 0.1, 0.98, 0.95), ["3", "2x", "120938"], parts=False, tools=True, arrows=True, action_="none"),
    ], ["Marking only."]),
    6: ("assembly_step", [
        diagram("close_up", "Bracket screwed to the leg with screw 108530; 109041 crossed out", (0.02, 0.02, 0.5, 0.3), ["4", "2x", "108530", "109041", "120298"], fast=True, tools=True, arrows=True, action_="attach"),
        diagram("assembly_view", "Template marking on the other legs", (0.02, 0.35, 0.98, 0.95), ["5", "2x", "120938"], parts=False, tools=True, arrows=True, action_="none"),
    ], []),
    7: ("assembly_step", [
        diagram("close_up", "Bracket screwed to the other legs", (0.02, 0.02, 0.98, 0.45), ["6", "2x", "108530", "120298"], fast=True, tools=True, arrows=True, action_="attach"),
        diagram("assembly_view", "Shelf tilted in between the legs", (0.02, 0.5, 0.98, 0.95), ["7"], arrows=True, action_="slide"),
    ], []),
    8: ("assembly_step", [
        diagram("assembly_view", "Shelf screwed to the four brackets, insets 1-4", (0.02, 0.05, 0.98, 0.9), ["8", "1", "2", "3", "4"], fast=True, tools=True, arrows=True, action_="tighten"),
    ], []),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA LACK Coffee Table")
