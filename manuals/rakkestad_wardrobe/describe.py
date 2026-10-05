"""Vision results for the IKEA RAKKESTAD three-door wardrobe manual (32 pages).

A wide carcass built lying on its back: two side panels and a divider, the
bottom panel, three fixed shelves between the divider and the right side
panel, two plinths and the top panel. Three hardboard back strips are nailed
on, the wardrobe is stood up and fixed to the wall, a clothes rail goes into
the wide left section and three doors hang on three hinges each (left door
on the left side panel, middle door on the divider, right door on the right
side panel), each with a knob. The manual prints no sizes; they are
estimated from the usual size of this wardrobe (1170 wide, 580 deep, 1760
high).

Run: python manuals/rakkestad_wardrobe/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

SIDE_PANEL = lambda side: part("", f"{side} side panel", f"tall {side} side panel with three hinge mounting plates on its front edge",
                               "panel", "wood", 1, [("hole", 12, "screw, dowel and hinge plate holes")], side,
                               size=(18, 580, 1760))
DIVIDER = part("", "divider", "upright divider between the wide hanging section and the shelf section, with three hinge plates",
               "panel", "wood", 1, [("hole", 12, "dowel and hinge plate holes")], "center", size=(18, 560, 1660))
BOTTOM = part("", "bottom panel", "bottom panel across the wardrobe above the plinths", "panel", "wood", 1,
              [("hole", 8, "dowel and screw holes")], "bottom", size=(1134, 560, 18))
TOP = part("", "top panel", "top panel across the tops of the side panels and divider, with a wall bracket underneath", "panel", "wood", 1,
           [("hole", 8, "screw and plug holes")], "top", size=(1170, 580, 18))
SHELF = lambda qty=3: part("", "shelf", "fixed shelf between the divider and the right side panel", "panel", "wood", qty,
                           [("hole", 6, "dowel holes")], "center", size=(380, 560, 18))
PLINTH = lambda qty=2: part("", "plinth", "plinth board under the bottom panel, front and back", "panel", "wood", qty,
                            [("hole", 4, "dowel holes")], "bottom", size=(1134, 18, 70))
BACK_PANEL = lambda qty=3: part("", "back panel", "hardboard back strip, three nailed side by side over the back", "panel", "wood", qty,
                                [], "back", size=(390, 3, 1700))
CLOTHES_RAIL = part("146857", "clothes rail", "round metal clothes rail 146857 in the wide left section under the top panel",
                    "beam", "metal", 1, [], "top", size=(740, 25, 25))
DOOR = lambda name: part("", f"{name} door", f"{name} frame-and-panel door with three glass-style panes, full height, three hinges",
                         "panel", "wood", 1, [("hole", 3, "hinge cup holes")], name, size=(388, 18, 1680))
HINGE = lambda qty=9: part("109338", "hinge", "cup hinge 109338 clipped to a mounting plate 109221", "block", "metal", qty, [], "center")
KNOB = lambda qty=3: part("119595", "knob", "round wooden knob 119595 on each door", "block", "wood", qty, [], "center",
                         size=(40, 30, 40))

SCREW_100219 = lambda qty: fastener("100219", "screw 100219", "screw", qty)
DOWEL = lambda qty: fastener("101345", "dowel 101345", "dowel", qty)
SCREW_109567 = lambda qty: fastener("109567", "screw 109567", "screw", qty)
SCREW_105248 = lambda qty: fastener("105248", "screw 105248", "screw", qty)
SCREW_109041 = lambda qty: fastener("109041", "screw 109041", "screw", qty)
PLUG = lambda qty: fastener("109837", "plug 109837", "plug", qty)
BRACKET = lambda qty: fastener("103717", "angle bracket 103717", "other", qty)
GLIDE = lambda qty: fastener("107091", "felt pad 107091", "plug", qty)
NAIL_GUIDE = lambda qty: fastener("105494", "nail guide 105494", "other", qty)
PLATE = lambda qty: fastener("109221", "mounting plate 109221", "other", qty)
RAIL_HOLDER = lambda qty: fastener("157308", "rail holder 157308", "other", qty)
SPACER = lambda qty: fastener("158568", "spacer 158568", "plug", qty)
NAIL = lambda qty: fastener("405950", "nail 405950", "other", qty)

DRIVER = tool("cross head screwdriver")
HAMMER = tool("hammer")
ALLEN = tool("allen key 100001")

SIDES = ("left", "right")

PAGES = [
    page(1, "cover", final="RAKKESTAD three-door wardrobe: three frame-and-panel doors with knobs",
         unc=["Cover page; product name RAKKESTAD and IKEA logo."]),
    page(2, "warning", unc=["Tip-over warning: the wardrobe must be fixed to the wall."]),
    page(3, "warning", tools=[DRIVER, HAMMER],
         unc=["Tools: cross head screwdriver, hammer, drill and spirit level for the wall fixing; two people."]),
    page(4, "parts_list", unc=["Wall fixing kit (brackets 106989, screws, washers, wall plugs): not part of the wardrobe."]),
    page(5, "parts_list",
         parts=[HINGE(9), KNOB(3), CLOTHES_RAIL],
         fasteners=[SCREW_100219(16), DOWEL(38), SCREW_109567(3), SCREW_105248(38), SCREW_109041(2), PLUG(4), BRACKET(1),
                    GLIDE(1), NAIL_GUIDE(1), PLATE(9), RAIL_HOLDER(2), SPACER(8), NAIL(2)],
         tools=[ALLEN],
         unc=["Spacers 158568 x8 go on the plinths; nails 405950 come in 2 bags."]),
    page(6, "parts_list", parts=[SIDE_PANEL("left"), DIVIDER, SIDE_PANEL("right")],
         unc=["Info: which tall panel is which — the left side panel, the shorter divider and the right side panel, with their hinge plates."]),
    page(7, "assembly_step",
         parts=[SIDE_PANEL("left"), DIVIDER, SIDE_PANEL("right")], fasteners=[PLATE(9), SCREW_105248(18)], tools=[DRIVER],
         actions=[action("insert", "", "left side panel", "109221", "cross head screwdriver", "down",
                         "step 1: 9x mounting plate 109221 screwed to the three tall panels with screws 105248, three per panel")],
         final="three tall panels lying flat with hinge plates"),
    page(8, "assembly_step",
         parts=[DIVIDER, SHELF(3)], fasteners=[DOWEL(22)],
         actions=[
             action("insert", "", "divider", "101345", "", "inward",
                    "step 2: 4x dowel 101345 pushed into the end of the divider"),
             action("insert", "", "shelf", "101345", "", "inward",
                    "step 3: 18x dowel 101345 pushed into the edges of the three shelves"),
         ],
         final="divider and shelves with dowels"),
    page(9, "assembly_step",
         parts=[BOTTOM, SIDE_PANEL("left"), TOP], fasteners=[SCREW_100219(2), DOWEL(8)], tools=[ALLEN],
         actions=[
             action("attach", "bottom panel", "left side panel", "100219", "allen key 100001", "inward",
                    "step 4: left side panel stood on its edge; bottom panel fixed at its lower end with 2x screw 100219"),
             action("insert", "", "top panel", "101345", "", "inward",
                    "step 5: 8x dowel 101345 pushed into the edges of the top panel"),
         ],
         final="bottom panel standing at the end of the left side panel",
         unc=["The wardrobe is built lying on its back; the side panels stand on their long edges."]),
    page(10, "assembly_step",
         parts=[TOP], fasteners=[PLUG(4), BRACKET(1), SCREW_109041(1)], tools=[HAMMER, DRIVER],
         actions=[
             action("insert", "", "top panel", "109837", "hammer", "down",
                    "step 6: 4x plug 109837 tapped into the top panel"),
             action("insert", "", "top panel", "103717", "cross head screwdriver", "down",
                    "step 7: top panel turned over; angle bracket 103717 screwed to it with 1x screw 109041 (not the longer screw)"),
         ],
         final="top panel ready"),
    page(11, "assembly_step",
         parts=[DIVIDER, BOTTOM, SIDE_PANEL("left")], fasteners=[SCREW_100219(4)], tools=[ALLEN],
         actions=[
             action("attach", "divider", "bottom panel", "100219", "allen key 100001", "inward",
                    "step 8-9: divider stood on its edge and fixed to the bottom panel with 2x screw 100219, repeat x2"),
         ],
         final="divider standing on the bottom panel"),
    page(12, "assembly_step",
         parts=[SHELF(3), DIVIDER], fasteners=[SCREW_100219(2), DOWEL(18)], tools=[ALLEN],
         actions=[
             action("attach", "shelf", "divider", "101345", "", "inward",
                    "step 10: 3x shelf pushed onto the dowels of the divider, beside the bottom panel"),
             action("tighten", "", "divider", "100219", "allen key 100001", "clockwise",
                    "step 11: 2x screw 100219 through the divider"),
         ],
         final="three shelves standing off the divider"),
    page(13, "assembly_step",
         parts=[SIDE_PANEL("right"), SHELF(3), BOTTOM], fasteners=[SCREW_100219(6), DOWEL(9)], tools=[ALLEN],
         actions=[
             action("attach", "right side panel", "shelf", "101345", "", "inward",
                    "step 12: right side panel pushed onto the shelf dowels and fixed with 4x screw 100219"),
             action("attach", "right side panel", "bottom panel", "100219", "allen key 100001", "inward",
                    "step 13: 2x screw 100219 through the right side panel into the bottom panel"),
         ],
         final="carcass with both side panels, divider and shelves, lying on its back"),
    page(14, "assembly_step",
         parts=[PLINTH(2)], fasteners=[DOWEL(4), SPACER(8)], tools=[HAMMER],
         actions=[
             action("insert", "", "plinth", "101345", "", "inward",
                    "step 14: 4x dowel 101345 pushed into the ends of the two plinths"),
             action("insert", "", "plinth", "158568", "hammer", "down",
                    "step 15: 4x spacer 158568 knocked into the two plinths"),
         ],
         final="two plinths ready"),
    page(15, "assembly_step",
         parts=[PLINTH(2), SIDE_PANEL("left"), BOTTOM], fasteners=[DOWEL(4)],
         actions=[
             action("attach", "plinth", "left side panel", "101345", "", "inward",
                    "step 16-17: 2x plinth pushed onto the dowels under the bottom panel, back then front"),
         ],
         final="plinths under the bottom panel"),
    page(16, "assembly_step",
         parts=[TOP, SIDE_PANEL("left"), SIDE_PANEL("right"), DIVIDER], fasteners=[SCREW_100219(4), DOWEL(8)], tools=[ALLEN],
         actions=[
             action("attach", "top panel", "left side panel", "101345", "", "inward",
                    "step 18: top panel pushed onto the upper ends of the side panels and divider"),
             action("tighten", "", "top panel", "100219", "allen key 100001", "clockwise",
                    "step 18: 4x screw 100219 through the side panels into the top panel"),
         ],
         final="carcass complete"),
    page(17, "assembly_step",
         parts=[TOP, DIVIDER], fasteners=[SCREW_109041(1)], tools=[DRIVER],
         actions=[action("tighten", "", "divider", "109041", "cross head screwdriver", "clockwise",
                         "step 19: 1x screw 109041 through the angle bracket into the divider")],
         final="divider fixed to the top panel"),
    page(18, "assembly_step",
         parts=[BACK_PANEL(3), TOP, BOTTOM], fasteners=[NAIL(1), NAIL_GUIDE(1)], tools=[HAMMER],
         actions=[
             action("attach", "back panel", "top panel", "405950", "hammer", "down",
                    "step 20-21: three back panel strips laid on the back side by side, first nail 405950 in a corner using the nail guide 105494"),
         ],
         final="three hardboard back strips on the back"),
    page(19, "assembly_step",
         parts=[BACK_PANEL(3), SIDE_PANEL("left"), SIDE_PANEL("right")], fasteners=[NAIL(14)], tools=[HAMMER],
         actions=[
             action("attach", "back panel", "left side panel", "405950", "hammer", "down",
                    "step 22-23: back panel strips squared and fixed with nails 405950 into the side panels and divider"),
         ],
         final="back strips held in place"),
    page(20, "assembly_step",
         parts=[BACK_PANEL(3)], fasteners=[NAIL(44)], tools=[HAMMER],
         actions=[action("tighten", "", "back panel", "405950", "hammer", "down",
                         "step 24: 44x nail 405950 all round the back panels")],
         final="back panel nailed on"),
    page(21, "assembly_step",
         unc=["Steps 25-32 (pages 21-26): the wardrobe stood up and fixed to the wall with the wall kit; the turn and the wall kit are not joins."]),
    page(26, "assembly_step",
         parts=[SIDE_PANEL("left"), DIVIDER], fasteners=[RAIL_HOLDER(2), SCREW_105248(4)], tools=[DRIVER],
         actions=[action("insert", "", "left side panel", "157308", "cross head screwdriver", "inward",
                         "step 33: 2x rail holder 157308 screwed to the left side panel and the divider with screws 105248")],
         final="rail holders in the wide section"),
    page(27, "assembly_step",
         parts=[CLOTHES_RAIL, SIDE_PANEL("left"), DOOR("left"), DOOR("middle"), DOOR("right"), HINGE(9)],
         fasteners=[SCREW_105248(18), RAIL_HOLDER(2)], tools=[DRIVER],
         actions=[
             action("attach", "clothes rail", "left side panel", "157308", "", "down",
                    "step 34: clothes rail 146857 dropped into the rail holders under the top panel"),
             action("attach", "hinge", "left door", "105248", "cross head screwdriver", "down",
                    "step 35: 9x hinge 109338 screwed into the cup holes of the three doors with screws 105248, three per door"),
         ],
         final="clothes rail fitted; three doors lying flat with hinges"),
    page(28, "assembly_step",
         parts=[DOOR("left"), DOOR("middle"), DOOR("right"), SIDE_PANEL("left"), DIVIDER, SIDE_PANEL("right")],
         fasteners=[PLATE(9)], tools=[DRIVER],
         actions=[
             action("attach", "left door", "left side panel", "109221", "cross head screwdriver", "inward",
                    "step 36: left door hung by clipping its hinges onto the mounting plates 109221 of the left side panel"),
             action("attach", "middle door", "divider", "109221", "cross head screwdriver", "inward",
                    "step 36: middle door hung on the mounting plates of the divider"),
             action("attach", "right door", "right side panel", "109221", "cross head screwdriver", "inward",
                    "step 36: right door hung on the mounting plates of the right side panel"),
         ],
         final="three doors hung"),
    page(29, "assembly_step",
         parts=[KNOB(3), DOOR("left"), DOOR("middle"), DOOR("right")], fasteners=[SCREW_109567(3)], tools=[DRIVER],
         actions=[
             action("attach", "knob", "left door", "109567", "cross head screwdriver", "inward",
                    "step 37: knob 119595 screwed to the left door with screw 109567"),
             action("attach", "knob", "middle door", "109567", "cross head screwdriver", "inward",
                    "step 37: knob screwed to the middle door"),
             action("attach", "knob", "right door", "109567", "cross head screwdriver", "inward",
                    "step 37: knob screwed to the right door"),
         ],
         final="knobs on all three doors"),
    page(30, "assembly_step",
         parts=[DOOR("left"), SIDE_PANEL("left")], fasteners=[GLIDE(1)],
         actions=[action("insert", "", "left side panel", "107091", "", "inward",
                         "step 38: felt pads 107091 stuck inside the front edges as door stops")],
         final="finished RAKKESTAD wardrobe",
         unc=["Page 31 shows adjusting the hinges up/down, in/out and sideways."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled RAKKESTAD three-door wardrobe", (0.05, 0.1, 0.5, 0.8), complexity="low", conf=0.95)], []),
    5: ("parts_list", [diagram("part_inventory", "Fittings: screws 100219 x16, dowels 101345 x38, screws 109567 x3, 105248 x38, 109041 x2, plugs 109837 x4, knobs 119595 x3, bracket 103717, felt pads, nail guide, plates 109221 x9, hinges 109338 x9, rail holders 157308 x2, spacers 158568 x8, nails 405950 x2 bags, clothes rail 146857",
                               (0.05, 0.05, 0.95, 0.95), ["100219", "101345", "109567", "105248", "109041", "109837", "119595", "103717", "109221", "109338", "157308", "158568", "405950", "146857"],
                               fast=True, tools=True, complexity="medium")], []),
    6: ("parts_list", [diagram("part_inventory", "Which tall panel is which: left side panel, divider, right side panel", (0.05, 0.05, 0.95, 0.95),
                               complexity="low")], []),
    16: ("assembly_step", [diagram("exploded_view", "Step 18: top panel onto the side panels", (0.05, 0.1, 0.95, 0.9),
                                   ["100219", "4x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    28: ("assembly_step", [diagram("assembly_view", "Step 36: three doors hung on the hinges", (0.05, 0.1, 0.95, 0.85),
                                   ["9x"], arrows=True, action_="attach", complexity="medium")], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA RAKKESTAD Wardrobe")
