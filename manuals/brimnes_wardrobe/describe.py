"""Vision results for the IKEA BRIMNES two-door wardrobe manual (36 pages).

A tall carcass built lying on its back: the left side panel stands on its
edge, the bottom panel, two plinths and a lower compartment (a two-piece
lower back, a divider and a fixed shelf) are fitted to it, then the right
side panel and the top panel. The carcass is turned over, the hardboard
back is nailed on in two halves, and it is stood up and fixed to the wall.
Inside go a clothes rail and an adjustable shelf; the two doors hang on
three hinges each and get a handle each. The manual prints no sizes; they
are estimated from the usual size of this wardrobe (780 wide, 500 deep,
1900 high).

Run: python manuals/brimnes_wardrobe/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

SIDE_PANEL = lambda side: part("", f"{side} side panel", f"tall {side} side panel with hinge mounting plates on its front edge",
                               "panel", "wood", 1, [("hole", 12, "cam lock, dowel and hinge plate holes")], side,
                               size=(18, 500, 1900))
BOTTOM = part("", "bottom panel", "bottom panel between the side panels, just above the plinth", "panel", "wood", 1,
              [("hole", 4, "dowel holes")], "bottom", size=(744, 480, 18))
TOP = part("", "top panel", "top panel across the tops of the side panels", "panel", "wood", 1,
           [("hole", 6, "cam bolt and dowel holes")], "top", size=(780, 500, 18))
PLINTH = lambda qty=2: part("", "plinth", "narrow plinth board under the bottom panel, front and back", "panel", "wood", qty,
                            [("hole", 2, "dowel holes")], "bottom", size=(744, 18, 60))
LOWER_BACK = part("", "lower back panel", "solid lower back of the bottom compartment, two halves joined with cam locks and connector pins",
                  "panel", "wood", 1, [("hole", 9, "dowel holes")], "back", size=(744, 18, 620))
DIVIDER = part("", "divider", "upright divider in the bottom compartment, between the bottom panel and the fixed shelf",
               "panel", "wood", 1, [("hole", 4, "dowel holes")], "center", size=(18, 480, 560))
FIXED_SHELF = part("", "fixed shelf", "fixed shelf across the wardrobe on top of the bottom compartment", "panel", "wood", 1,
                   [("hole", 4, "cam bolt holes")], "center", size=(744, 480, 18))
SHELF = part("", "adjustable shelf", "small loose shelf on four shelf pins in the right half of the bottom compartment",
             "panel", "wood", 1, [], "center", size=(360, 460, 18))
BACK_PANEL = lambda qty=2: part("", "hardboard", "hardboard back half, nailed over the back above the lower back",
                                "panel", "wood", qty, [], "back", size=(390, 3, 1280))
CLOTHES_RAIL = part("122663", "clothes rail", "oval metal clothes rail 122663 hung under the top panel", "beam", "metal", 1,
                    [], "top", size=(744, 30, 15))
DOOR = lambda side: part("", f"{side} door", f"{side} frame-and-panel door, full height, three hinges on its outer edge",
                         "panel", "wood", 1, [("hole", 3, "hinge cup holes")], side, size=(388, 18, 1880))
HINGE = lambda qty=6: part("109336", "hinge", "cup hinge 109336 clipped to a mounting plate 109220 on the side panel",
                           "block", "metal", qty, [], "center")
HANDLE = lambda qty=2: part("124328", "handle", "long upright wooden bar handle 124328, one per door", "beam", "wood", qty,
                            [("hole", 2, "screw holes")], "center", size=(30, 25, 300))

CONFIRMAT = lambda qty: fastener("100214", "screw 100214", "screw", qty)
CAM_LOCK = lambda qty: fastener("119252", "cam lock 119252", "cam", qty)
SCREW_109567 = lambda qty: fastener("109567", "screw 109567", "screw", qty)
DOWEL = lambda qty: fastener("101345", "dowel 101345", "dowel", qty)
CAM_BOLT = lambda qty: fastener("118331", "cam bolt 118331", "bolt", qty)
NAIL = lambda qty: fastener("101206", "nail 101206", "other", qty)
PIN = lambda qty: fastener("106940", "connector pin 106940", "bolt", qty)
PLUG = lambda qty: fastener("123840", "plug 123840", "plug", qty)
NAIL_GUIDE = lambda qty: fastener("105494", "nail guide 105494", "other", qty)
RAIL_HOLDER = lambda qty: fastener("157306", "rail holder 157306", "other", qty)
PLATE = lambda qty: fastener("109220", "mounting plate 109220", "other", qty)
SHELF_PIN = lambda qty: fastener("101532", "shelf pin 101532", "plug", qty)
GLIDE = lambda qty: fastener("107091", "felt pad 107091", "plug", qty)
SCREW_105248 = lambda qty: fastener("105248", "screw 105248", "screw", qty)

DRIVER = tool("cross head screwdriver")
FLAT = tool("flat screwdriver")
HAMMER = tool("hammer")
ALLEN = tool("allen key 100001")
PENCIL = tool("pencil")

SIDES = ("left", "right")

PAGES = [
    page(1, "cover", final="BRIMNES two-door wardrobe: tall carcass with two frame-and-panel doors and two bar handles",
         unc=["Cover page; product name BRIMNES and IKEA logo."]),
    page(2, "warning", unc=["Tip-over warning: the wardrobe must be fixed to the wall."]),
    page(6, "warning", tools=[DRIVER, FLAT, HAMMER, PENCIL],
         unc=["Tools: cross head and flat screwdrivers, hammer, pencil, drill for the wall fixing; two people."]),
    page(8, "parts_list",
         fasteners=[PIN(2), CONFIRMAT(2), CAM_LOCK(20), SCREW_109567(4), DOWEL(27), CAM_BOLT(16), NAIL(40), PLUG(2), NAIL_GUIDE(1)],
         tools=[ALLEN],
         unc=["Bag 1; its lower box is the wall fixing kit (brackets 106989, screws, washers, wall plugs), not part of the wardrobe.",
              "4x spacer 153548 are wall spacers knocked into the back edge (step 29), not modelled."]),
    page(9, "parts_list",
         parts=[CLOTHES_RAIL, HINGE(6), HANDLE(2)],
         fasteners=[RAIL_HOLDER(2), PLATE(6), SHELF_PIN(4), GLIDE(1), SCREW_105248(26)],
         unc=["Bag 2; the two long bars 124328 are the door handles, drawn with the clothes rail 122663 x1."]),
    page(10, "assembly_step",
         parts=[SIDE_PANEL(s) for s in SIDES], fasteners=[PLATE(6), SCREW_105248(12), CAM_BOLT(10)], tools=[DRIVER],
         actions=[
             action("insert", "", "left side panel", "109220", "cross head screwdriver", "down",
                    "step 1: 6x mounting plate 109220 screwed to the inner faces of both side panels with screws 105248, three per side"),
             action("insert", "", "left side panel", "118331", "cross head screwdriver", "down",
                    "step 2: 10x cam bolt 118331 screwed into the inner faces of the side panels"),
         ],
         final="both side panels lying flat with hinge plates and cam bolts"),
    page(11, "assembly_step",
         parts=[SIDE_PANEL("left"), BOTTOM], fasteners=[DOWEL(4), CAM_LOCK(2)], tools=[FLAT],
         actions=[
             action("attach", "bottom panel", "left side panel", "101345", "", "inward",
                    "step 3: left side panel stood on its edge; bottom panel pushed onto 4x dowel 101345 at its lower end"),
             action("tighten", "", "bottom panel", "119252", "flat screwdriver", "clockwise",
                    "step 4: 2x cam lock 119252 turned in the bottom panel"),
         ],
         final="bottom panel standing at the end of the left side panel",
         unc=["The wardrobe is built lying on its back; the left side panel stands on its long edge."]),
    page(12, "assembly_step",
         parts=[LOWER_BACK], fasteners=[DOWEL(9), CAM_LOCK(2), PIN(2)], tools=[FLAT],
         actions=[
             action("insert", "", "lower back panel", "101345", "", "inward",
                    "step 5: 9x dowel 101345 pushed into the edges of the two lower back halves"),
             action("insert", "", "lower back panel", "106940", "", "inward",
                    "step 6-8: 2x cam lock 119252 and 2x connector pin 106940 fitted to join the two halves"),
         ],
         final="two lower back halves ready to join"),
    page(13, "assembly_step",
         parts=[LOWER_BACK, SIDE_PANEL("left"), BOTTOM], fasteners=[CAM_LOCK(2)], tools=[FLAT],
         actions=[
             action("tighten", "", "lower back panel", "119252", "flat screwdriver", "clockwise",
                    "step 9-10: the two halves pushed together and 2x cam lock 119252 turned to join them"),
             action("slide", "lower back panel", "bottom panel", "", "", "inward",
                    "step 11: lower back panel laid flat and slid against the bottom panel"),
         ],
         final="lower back panel in the bottom compartment",
         unc=["Inset: the joint line of the two halves must run the way shown."]),
    page(14, "assembly_step",
         parts=[DIVIDER, LOWER_BACK, BOTTOM], fasteners=[DOWEL(4), CONFIRMAT(2)], tools=[ALLEN],
         actions=[
             action("attach", "divider", "bottom panel", "101345", "", "inward",
                    "step 12: divider stood on its edge on 4x dowel 101345 on the lower back panel, against the bottom panel"),
             action("tighten", "", "divider", "100214", "allen key 100001", "clockwise",
                    "step 13: 2x screw 100214 through the bottom panel into the divider with allen key 100001"),
         ],
         final="divider standing in the bottom compartment"),
    page(15, "assembly_step",
         parts=[FIXED_SHELF, DIVIDER, SIDE_PANEL("left")], fasteners=[CAM_BOLT(2)], tools=[DRIVER],
         actions=[
             action("insert", "", "fixed shelf", "118331", "cross head screwdriver", "down",
                    "step 14: 2x cam bolt 118331 screwed into the fixed shelf"),
             action("attach", "fixed shelf", "divider", "118331", "", "inward",
                    "step 14: fixed shelf pushed onto the divider and the left side panel, closing the bottom compartment"),
         ],
         final="bottom compartment closed by the fixed shelf"),
    page(16, "assembly_step",
         parts=[FIXED_SHELF, PLINTH(2), SIDE_PANEL("left")], fasteners=[CAM_LOCK(2), DOWEL(4)], tools=[FLAT],
         actions=[
             action("tighten", "", "fixed shelf", "119252", "flat screwdriver", "clockwise",
                    "step 15: 2x cam lock 119252 turned to lock the fixed shelf"),
             action("attach", "plinth", "left side panel", "101345", "", "inward",
                    "step 16: 2x plinth pushed onto 4x dowel 101345 in the left side panel under the bottom panel, front and back"),
         ],
         final="plinths in place under the bottom panel"),
    page(17, "assembly_step",
         parts=[SIDE_PANEL("right"), BOTTOM, FIXED_SHELF, PLINTH(2)], fasteners=[DOWEL(2), CAM_LOCK(8)], tools=[FLAT],
         actions=[
             action("attach", "right side panel", "bottom panel", "101345", "", "inward",
                    "step 17: two people lift the right side panel onto 2x dowel 101345 and the cam bolts of the bottom panel, fixed shelf and plinths"),
             action("tighten", "", "right side panel", "119252", "flat screwdriver", "clockwise",
                    "step 18: 8x cam lock 119252 turned to lock the right side panel"),
         ],
         final="carcass with both side panels, lying on its back"),
    page(18, "assembly_step",
         parts=[TOP, SIDE_PANEL("left"), SIDE_PANEL("right")], fasteners=[PLUG(2), CAM_BOLT(4), DOWEL(4)], tools=[HAMMER, DRIVER],
         actions=[
             action("insert", "", "top panel", "123840", "hammer", "down",
                    "step 19: 2x plug 123840 tapped into the top panel"),
             action("insert", "", "top panel", "118331", "cross head screwdriver", "down",
                    "step 20: 4x cam bolt 118331 screwed into the top panel"),
             action("attach", "top panel", "left side panel", "101345", "", "inward",
                    "step 21: top panel pushed onto 4x dowel 101345 at the upper ends of both side panels"),
         ],
         final="top panel on the carcass"),
    page(19, "assembly_step",
         parts=[TOP], fasteners=[CAM_LOCK(4)], tools=[FLAT, PENCIL],
         actions=[action("tighten", "", "top panel", "119252", "flat screwdriver", "clockwise",
                         "step 22: 4x cam lock 119252 turned to lock the top panel")],
         final="carcass complete",
         unc=["Step 23: the carcass is turned over onto its front and the nail lines are marked with a pencil; the turn is not a join."]),
    page(20, "assembly_step",
         parts=[BACK_PANEL(2), TOP, SIDE_PANEL("left"), SIDE_PANEL("right")], fasteners=[NAIL(2), NAIL_GUIDE(1)], tools=[HAMMER],
         actions=[
             action("attach", "hardboard", "top panel", "101206", "hammer", "down",
                    "step 24: first hardboard half laid on the back and fixed with a nail 101206 at the top corner, using the nail guide 105494"),
             action("attach", "hardboard", "right side panel", "101206", "hammer", "down",
                    "step 25: second hardboard half laid beside it and fixed with nails 101206 in its corners"),
         ],
         final="two hardboard back halves laid on the back"),
    page(22, "assembly_step",
         parts=[BACK_PANEL(2), PLINTH(2)], fasteners=[NAIL(33), NAIL_GUIDE(1)], tools=[HAMMER],
         actions=[action("tighten", "", "hardboard", "101206", "hammer", "down",
                         "step 26-28: nail lines marked and the hardboard fixed with 33x nail 101206 all round")],
         final="back panel nailed on",
         unc=["Step 29: 4x spacer 153548 knocked into the rear edge for the wall; not modelled."]),
    page(24, "assembly_step",
         unc=["Steps 30-34 (pages 23-28): wall brackets screwed to the top panel, the wardrobe stood up and fixed to the wall; the wall kit is not part of the wardrobe."]),
    page(29, "assembly_step",
         parts=[CLOTHES_RAIL, SHELF, TOP, SIDE_PANEL("left"), SIDE_PANEL("right"), DIVIDER],
         fasteners=[RAIL_HOLDER(2), SCREW_105248(2), SHELF_PIN(4)], tools=[DRIVER],
         actions=[
             action("insert", "", "left side panel", "157306", "cross head screwdriver", "inward",
                    "step 35: 2x rail holder 157306 screwed to the side panels just under the top panel with screws 105248"),
             action("attach", "clothes rail", "left side panel", "157306", "", "down",
                    "step 35: clothes rail 122663 dropped into the rail holders under the top panel"),
             action("attach", "adjustable shelf", "divider", "101532", "", "down",
                    "step 35: adjustable shelf laid on 4x shelf pin 101532 between the divider and the right side panel"),
         ],
         final="clothes rail and adjustable shelf fitted"),
    page(30, "assembly_step",
         parts=[DOOR("left"), DOOR("right"), HINGE(6)], fasteners=[SCREW_105248(12)], tools=[DRIVER],
         actions=[
             action("attach", "hinge", "left door", "105248", "cross head screwdriver", "down",
                    "step 36: 3x hinge 109336 screwed into the cup holes of the left door with screws 105248"),
             action("attach", "hinge", "right door", "105248", "cross head screwdriver", "down",
                    "step 36: 3x hinge 109336 screwed into the cup holes of the right door"),
         ],
         final="both doors lying flat with three hinges each"),
    page(31, "assembly_step",
         parts=[DOOR("left"), DOOR("right"), SIDE_PANEL("left"), SIDE_PANEL("right")], fasteners=[PLATE(6)], tools=[DRIVER],
         actions=[
             action("attach", "left door", "left side panel", "109220", "cross head screwdriver", "inward",
                    "step 37: left door hung by clipping its three hinges onto the mounting plates 109220 and screwing them tight"),
             action("attach", "right door", "right side panel", "109220", "cross head screwdriver", "inward",
                    "step 37: right door hung on the mounting plates of the right side panel"),
         ],
         final="both doors hung"),
    page(32, "assembly_step",
         parts=[HANDLE(2), DOOR("left"), DOOR("right")], fasteners=[SCREW_109567(4)], tools=[DRIVER],
         actions=[
             action("attach", "handle", "left door", "109567", "cross head screwdriver", "inward",
                    "step 38: handle 124328 screwed to the left door's inner edge with 2x screw 109567"),
             action("attach", "handle", "right door", "109567", "cross head screwdriver", "inward",
                    "step 38: handle screwed to the right door's inner edge with 2x screw 109567"),
         ],
         final="handles on both doors"),
    page(33, "assembly_step",
         parts=[DOOR("right"), DOOR("left")], fasteners=[GLIDE(1)],
         actions=[action("insert", "", "right door", "107091", "", "inward",
                         "step 39: 2x felt pad 107091 stuck to the inside of the doors' lower corners")],
         final="finished BRIMNES wardrobe",
         unc=["Page 34 shows adjusting the hinges up/down, in/out and sideways."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled BRIMNES two-door wardrobe", (0.05, 0.1, 0.4, 0.9), complexity="low", conf=0.95)], []),
    8: ("parts_list", [diagram("part_inventory", "Bag 1: pins 106940 x2, screws 100214 x2, cam locks x20, screws 109567 x4, dowels 101345 x27, cam bolts 118331 x16, nails 101206 x40, wall spacers 153548 x4, plugs 123840 x2, nail guide 105494; wall kit",
                               (0.05, 0.05, 0.95, 0.95), ["106940", "100214", "119252", "109567", "101345", "118331", "101206", "153548", "123840", "105494"],
                               fast=True, tools=True, complexity="medium")], []),
    9: ("parts_list", [diagram("part_inventory", "Bag 2: rail holders 157306 x2, hinges 109336 x6, mounting plates 109220 x6, shelf pins 101532 x4, felt pads 107091, screws 105248 x26; clothes rail 122663",
                               (0.05, 0.05, 0.95, 0.95), ["157306", "109336", "109220", "101532", "107091", "105248", "122663", "124328"],
                               fast=True, complexity="medium")], []),
    15: ("assembly_step", [diagram("exploded_view", "Step 14: fixed shelf closing the bottom compartment", (0.1, 0.4, 0.9, 0.85),
                                   ["118331", "2x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    18: ("assembly_step", [diagram("exploded_view", "Step 21: top panel onto the side panels", (0.5, 0.5, 0.98, 0.95),
                                   ["101345", "4x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    31: ("assembly_step", [diagram("assembly_view", "Step 37: doors hung on the hinges", (0.05, 0.1, 0.95, 0.85),
                                   ["6x"], arrows=False, action_="attach", complexity="medium")], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA BRIMNES Wardrobe")
