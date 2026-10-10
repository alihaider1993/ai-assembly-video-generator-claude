"""Vision results for the IKEA BILLY bookcase manual (16 pages).

Run: python manuals/billy_bookcase/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 80 x 28 cm bookcase, 106 cm high.
SIDE = lambda side, desc: part(
    "", f"{side} side panel", desc, "panel", "wood", 1,
    [("hole", 4, "cam bolt holes at top and bottom"), ("hole", 40, "two rows of shelf pin holes"),
     ("slot", 1, "groove along the back edge for the back panel")],
    "bottom", size=(15, 280, 1060))
TOP = part("", "top panel", "top panel with a groove along its back edge", "panel", "wood", 1,
           [("hole", 4, "dowel holes in the ends"), ("hole", 2, "cam lock holes")], "center", size=(770, 280, 15))
BOTTOM = part("", "bottom panel", "bottom panel with a groove along its back edge", "panel", "wood", 1,
              [("hole", 4, "dowel holes in the ends"), ("hole", 2, "cam lock holes")], "center", size=(770, 260, 15))
PLINTH = part("", "plinth", "narrow kick board across the front under the bottom panel", "panel", "wood", 1,
              [("hole", 4, "dowel holes in the ends")], "center", size=(770, 15, 60))
BACK = part("", "back panel", "folded hardboard back panel", "panel", "fibreboard", 1, [], "center", size=(790, 3, 1050))
SHELF = lambda qty=2: part("", "shelf", "loose shelf resting on four shelf pins", "panel", "wood", qty,
                           [], "center", size=(760, 260, 15))

PAGES = [
    page(1, "cover", final="BILLY bookcase: two tall side panels, top, bottom on a plinth, hardboard back and two shelves",
         unc=["Cover shows the bookcase in two widths; described as the 80 cm one."]),
    page(2, "warning", unc=["Tip-over warning in many languages. No assembly action."]),
    page(3, "warning", unc=["Tip-over warning, continued."]),
    page(4, "warning", unc=["Tip-over warning, continued."]),
    page(5, "warning", unc=["Tools (screwdrivers, hammer, awl); soft surface; ask IKEA; fix to the wall."]),
    page(6, "parts_list",
         fasteners=[fastener("118331", "cam bolt", "bolt", "8x"), fastener("101351", "wooden dowel", "dowel", "12x"),
                    fastener("101201", "nail", "nail", "4x"), fastener("119081", "cam lock", "cam", "8x"),
                    fastener("131372", "shelf pin", "plug", "8x"), fastener("109041", "wall bracket screw", "screw", "2x"),
                    fastener("100823", "washer", "washer", "4x"), fastener("106989", "wall fixing bracket", "bracket", "2x")],
         unc=["Panels are not shown in the inventory; only hardware."]),
    page(7, "assembly_step",
         parts=[TOP, BOTTOM, PLINTH, SIDE("left", "left side panel lying flat"), SIDE("right", "right side panel lying flat")],
         fasteners=[fastener("101351", "wooden dowel", "dowel", 12), fastener("118331", "cam bolt", "bolt", 8)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("insert", "", "top panel", "101351", "", "inward",
                    "step 1: 12x wooden dowel 101351 pushed into the ends of the top panel, bottom panel and plinth"),
             action("insert", "", "bottom panel", "101351", "", "inward", "step 1: wooden dowel 101351 into the bottom panel"),
             action("insert", "", "plinth", "101351", "", "inward", "step 1: wooden dowel 101351 into the plinth"),
             action("insert", "", "left side panel", "118331", "cross head screwdriver", "clockwise",
                    "step 2: 8x cam bolt 118331 screwed into the left side panel and right side panel"),
             action("insert", "", "right side panel", "118331", "cross head screwdriver", "clockwise",
                    "step 2: cam bolt 118331 into the right side panel"),
         ],
         final="boards with dowels, side panels with cam bolts"),
    page(8, "assembly_step",
         parts=[SIDE("left", "left side panel lying flat"), TOP, BOTTOM, PLINTH],
         fasteners=[fastener("119081", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "bottom panel", "left side panel", "", "", "down",
                    "step 3: bottom panel stood on the cam bolts of the left side panel, groove to the back"),
             action("attach", "plinth", "left side panel", "", "", "down",
                    "step 3: plinth stood in front of the bottom panel on the left side panel"),
             action("attach", "top panel", "left side panel", "", "", "down",
                    "step 3: top panel stood at the other end of the left side panel, groove to the back"),
             action("tighten", "top panel", "left side panel", "119081", "flat screwdriver", "clockwise",
                    "step 4: 4x cam lock 119081 turned in the top panel and bottom panel"),
         ],
         final="top, bottom and plinth standing on the left side panel",
         unc=["The carcass is built lying on its side; inset shows the groove edge facing the right way."]),
    page(9, "assembly_step",
         parts=[SIDE("right", "right side panel lowered on"), TOP, BOTTOM],
         fasteners=[fastener("119081", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "right side panel", "top panel", "", "", "down",
                    "step 5: right side panel lowered onto the dowels of the top panel, bottom panel and plinth"),
             action("tighten", "right side panel", "bottom panel", "119081", "flat screwdriver", "clockwise",
                    "step 6: 4x cam lock 119081 turned in the top panel and bottom panel"),
         ],
         final="carcass box lying on its side"),
    page(10, "assembly_step",
         parts=[BACK, TOP, BOTTOM],
         fasteners=[fastener("101201", "nail", "nail", 4)],
         tools=[tool("hammer")],
         actions=[
             action("slide", "back panel", "top panel", "", "", "inward",
                    "step 7: back panel unfolded and slid into the grooves of the side panels, top panel and bottom panel"),
             action("insert", "back panel", "bottom panel", "101201", "hammer", "down",
                    "step 7: 4x nail 101201 hammered through the back panel into the bottom panel and top panel"),
         ],
         final="carcass with back panel, then stood upright",
         unc=["Lower right: the carcass is turned to stand upright; turning is not a join."]),
    page(11, "assembly_step",
         unc=["Steps 8-9: tip-over warning; marking the wall and fixing the wall fixing brackets 106989 to the wall with screws and washers 100823. The wall is not a part."]),
    page(12, "assembly_step",
         unc=["Steps 10-11: bookcase pushed against the wall and the brackets screwed to the top panel with screw 109041 and washer 100823."]),
    page(13, "assembly_step",
         parts=[SIDE("left", "left side panel of the upright bookcase"), SIDE("right", "right side panel"), SHELF(2)],
         fasteners=[fastener("131372", "shelf pin", "plug", 8)],
         actions=[
             action("insert", "", "left side panel", "131372", "", "inward",
                    "step 12: 8x shelf pin 131372 pushed into the shelf pin holes of the left side panel and right side panel"),
             action("insert", "", "right side panel", "131372", "", "inward", "step 12: shelf pin 131372 into the right side panel"),
             action("place", "shelf", "left side panel", "", "", "down",
                    "step 13: 2x shelf laid on the shelf pins between the left side panel and right side panel"),
             action("place", "shelf", "right side panel", "", "", "down",
                    "step 13: shelf resting on the pins of the right side panel"),
         ],
         final="finished BILLY bookcase with two shelves"),
    page(14, "unknown", unc=["Blank page."]),
    page(15, "unknown", unc=["Blank page."]),
    page(16, "unknown", unc=["Back page."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "BILLY bookcases in two widths", (0.02, 0.08, 0.95, 0.85), complexity="low", conf=0.95)], []),
    **{n: ("warning", [diagram("warning", "Tip-over warning text", (0.03, 0.03, 0.97, 0.97), parts=False, complexity="low", action_="warning")], []) for n in (2, 3, 4)},
    5: ("warning", [diagram("warning", "Tools and general advice", (0.03, 0.03, 0.97, 0.97), parts=False, tools=True, complexity="low", action_="warning")], []),
    6: ("parts_list", [
        diagram("part_inventory", "Hardware", (0.05, 0.15, 0.95, 0.3),
                ["118331", "101351", "101201", "119081", "131372", "109041", "100823", "8x", "12x", "4x", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Wall fixing bracket 2x", (0.05, 0.35, 0.5, 0.5), ["106989", "2x"], parts=False, fast=True, complexity="low"),
    ], []),
    7: ("assembly_step", [step_view("Dowels into top, bottom and plinth; cam bolts into the sides", ["1", "2", "12x", "8x", "101351", "118331"], "insert", fast=True, tools=True)], []),
    8: ("assembly_step", [step_view("Bottom, plinth and top stood on a side panel; cam locks", ["3", "4", "4x", "119081"], "attach", fast=True, tools=True, arrows=True)], []),
    9: ("assembly_step", [step_view("Other side panel lowered on; cam locks", ["5", "6", "4x", "119081"], "attach", fast=True, tools=True)], []),
    10: ("assembly_step", [step_view("Back panel slid into the grooves and nailed", ["7", "4x", "101201"], "slide", fast=True, tools=True, arrows=True)], []),
    11: ("assembly_step", [step_view("Wall fixing", ["8", "9", "2x", "106989", "100823"], "none", parts=False, fast=True, tools=True)], []),
    12: ("assembly_step", [step_view("Wall brackets screwed to the top", ["10", "11", "2x", "109041"], "none", parts=False, fast=True, tools=True)], []),
    13: ("assembly_step", [step_view("Shelf pins and shelves", ["12", "13", "8x", "2x", "131372"], "place", fast=True, arrows=True)], []),
    14: ("unknown", [], []), 15: ("unknown", [], []), 16: ("unknown", [], []),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA BILLY Bookcase")
