"""Vision results for the IKEA HAUGA chest of 3 drawers with shelf unit manual (36 pages).

Run: python manuals/hauga_chest/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 70 x 46 cm chest, 84 cm high, with a
# 25 cm deep open shelf unit (hutch) on top, 116 cm high overall.
SIDE = lambda side: part("", f"{side} side panel", f"{side} side panel of the chest, front top corner cut off", "panel", "wood", 1,
                         [("hole", 6, "runner screw holes"), ("slot", 1, "back panel groove")], "bottom", size=(18, 460, 840))
TOP = part("", "top panel", "top panel of the chest between the side panels", "panel", "wood", 1,
           [("hole", 4, "click fitting holes")], "center", size=(664, 460, 18))
BOTTOM = part("", "bottom panel", "bottom panel of the chest", "panel", "wood", 1,
              [("hole", 4, "click fitting holes")], "center", size=(664, 440, 18))
BACK_RAIL = part("", "back rail", "U-shaped metal rail across the back of the chest", "beam", "metal", 1,
                 [("hole", 2, "screw holes at the ends")], "center", size=(664, 20, 20))
BACK = part("", "back panel", "folding hardboard back panel of the chest", "panel", "fibreboard", 1, [], "center", size=(690, 3, 820))
PLINTH = part("", "plinth", "kick board across the front under the bottom panel", "panel", "wood", 1,
              [("hole", 2, "dowel holes")], "center", size=(664, 18, 60))
HUTCH_SIDE = lambda side: part("", f"hutch {side} side panel", f"{side} side panel of the open shelf unit", "panel", "wood", 1,
                               [("slot", 1, "back panel groove")], "center", size=(18, 250, 330))
HUTCH_TOP = part("", "hutch top panel", "top panel of the open shelf unit", "panel", "wood", 1,
                 [("hole", 4, "dowel holes")], "center", size=(664, 250, 18))
HUTCH_SHELF = part("", "hutch shelf", "shelf in the middle of the open shelf unit", "panel", "wood", 1,
                   [("hole", 4, "dowel holes")], "center", size=(664, 240, 18))
HUTCH_RAIL = part("", "hutch back rail", "rail across the bottom back of the open shelf unit", "beam", "wood", 1,
                  [("hole", 3, "dowel holes")], "center", size=(664, 18, 60))
HUTCH_BACK = part("", "hutch back panel", "hardboard back panel of the open shelf unit", "panel", "fibreboard", 1,
                  [], "center", size=(680, 3, 330))
SMALL_FRONT = part("", "small drawer front", "shallow top drawer front with two knobs", "panel", "wood", 1,
                   [("slot", 1, "groove for the drawer bottom")], "bottom", size=(664, 18, 160))
LARGE_FRONT = lambda qty=2: part("", "large drawer front", "deep drawer front with two knobs", "panel", "wood", qty,
                                 [("slot", 1, "groove for the drawer bottom")], "bottom", size=(664, 18, 250))
DRAWER_SIDE = lambda qty=6: part("", "drawer side", "drawer side with a groove for the bottom", "panel", "wood", qty,
                                 [("slot", 1, "groove"), ("hole", 2, "dowel holes")], "center", size=(12, 420, 140))
DRAWER_BACK = lambda qty=3: part("", "drawer back", "drawer back with holes for the wire stiffener", "panel", "wood", qty,
                                 [], "top", size=(620, 12, 130))
DRAWER_BOTTOM = lambda qty=3: part("", "drawer bottom", "thin drawer bottom", "panel", "fibreboard", qty, [], "center",
                                   size=(620, 420, 3))
RUNNER = lambda qty, desc: part("10043622", "drawer runner", desc, "rail", "metal", qty, [("hole", 3, "screw holes")], "center")
KNOB = lambda qty=6: part("10052019", "knob", "round wooden knob", "block", "wood", qty, [], "center")

PAGES = [
    page(1, "cover", final="HAUGA chest of 3 drawers with an open shelf unit on top"),
    page(2, "warning", unc=["Tip-over warning text."]),
    page(3, "warning", unc=["Tools, wall fixing advice, two people."]),
    page(4, "warning", unc=["Soft surface; ask IKEA; wall fixing parts."]),
    page(5, "parts_list", unc=["Bag 1 hardware: click fittings, dowels, screws, connector plates (labels too small to matter)."]),
    page(6, "parts_list",
         fasteners=[fastener("101345", "wooden dowel", "dowel", "24x"), fastener("119030", "cam lock", "cam", "12x"),
                    fastener("110519", "drawer pin", "nail", "12x"), fastener("146114", "runner screw", "screw", "24x"),
                    fastener("10040242", "wire stiffener", "other", "3x")],
         parts=[KNOB(6)],
         unc=["Bag A (drawers)."]),
    page(7, "parts_list", parts=[RUNNER(12, "drawer runner set: carcass and drawer halves")],
         unc=["3x runner sets, 12 runners in all."]),
    page(8, "assembly_step",
         parts=[SIDE("right"), SIDE("left"), RUNNER(6, "carcass drawer runner")],
         fasteners=[fastener("146114", "runner screw", "screw", 18)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "drawer runner", "right side panel", "146114", "cross head screwdriver", "clockwise",
                    "step 1: 3x drawer runner screwed to the right side panel (IKEA CR)"),
             action("attach", "drawer runner", "left side panel", "146114", "cross head screwdriver", "clockwise",
                    "step 1: 3x drawer runner screwed to the left side panel (IKEA CL)"),
         ],
         final="runners on both side panels"),
    page(9, "assembly_step",
         parts=[SIDE("right"), TOP, BOTTOM],
         actions=[
             action("attach", "top panel", "right side panel", "", "", "inward",
                    "step 2: top panel pushed onto the click fittings of the right side panel until it clicks (4x)"),
             action("attach", "bottom panel", "right side panel", "", "", "inward",
                    "step 2: bottom panel pushed onto the right side panel until it clicks"),
         ],
         final="top and bottom panels standing on the right side panel"),
    page(10, "assembly_step",
         parts=[SIDE("left"), TOP, BOTTOM],
         actions=[action("attach", "left side panel", "top panel", "", "", "down",
                         "step 3: left side panel pushed onto the top panel and bottom panel until it clicks (4x)")],
         final="chest carcass box"),
    page(11, "assembly_step",
         parts=[BACK_RAIL, SIDE("left"), SIDE("right")],
         fasteners=[fastener("105811", "rail screw", "screw", 2)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "back rail", "left side panel", "", "", "inward",
                    "step 4: metal back rail fitted between the side panels at the back, flanges as the inset shows"),
             action("tighten", "back rail", "right side panel", "105811", "cross head screwdriver", "clockwise",
                    "step 5: 2x rail screw 105811 through the back rail into the side panels"),
         ],
         final="back rail fixed"),
    page(12, "assembly_step",
         parts=[BACK, SIDE("left"), SIDE("right")],
         fasteners=[fastener("151708", "back panel fixing", "plug", 8)],
         actions=[
             action("slide", "back panel", "left side panel", "", "", "inward",
                    "step 6: folding back panel slid into the grooves of the side panels"),
             action("insert", "back panel", "right side panel", "151708", "", "down",
                    "step 7: 8x back panel fixing 151708 pressed through the back panel into the top panel and bottom panel"),
         ],
         final="back panel in place"),
    page(13, "assembly_step",
         parts=[BACK],
         fasteners=[fastener("10093081", "back panel clip", "other", 6), fastener("151707", "back panel pin", "plug", 8)],
         actions=[
             action("insert", "", "back panel", "10093081", "", "inward",
                    "step 8: 6x back panel clip 10093081 with wedge 10093082 at the fold of the back panel"),
             action("insert", "", "back panel", "151707", "", "down", "step 9: 8x back panel pin 151707 pressed in along the back panel"),
         ],
         final="back panel held"),
    page(14, "assembly_step",
         parts=[PLINTH, BOTTOM, SIDE("left")],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 2), fastener("153548", "floor glide", "other", 2),
                    fastener("10051022", "foot", "other", 2)],
         actions=[
             action("attach", "plinth", "bottom panel", "101345", "", "inward",
                    "step 10: plinth pushed onto 2x wooden dowel 101345 under the bottom panel at the front"),
             action("insert", "", "left side panel", "153548", "", "inward",
                    "step 11: 2x floor glide 153548 at the front and 2x foot 10051022 at the back of the side panels"),
         ],
         final="chest carcass complete, lying on its back"),
    page(15, "assembly_step",
         parts=[TOP],
         fasteners=[fastener("10047146", "plug", "plug", 2)],
         actions=[action("insert", "", "top panel", "10047146", "", "inward",
                         "step 12: chest stood upright (turning is not a join); 2x plug 10047146 into the back edge of the top panel")],
         final="chest standing upright"),
    page(16, "assembly_step",
         parts=[HUTCH_TOP, HUTCH_SHELF, HUTCH_SIDE("left")],
         fasteners=[fastener("120173", "long dowel", "dowel", 4)],
         actions=[
             action("insert", "", "hutch top panel", "120173", "", "inward",
                    "step 13: 4x long dowel 120173 into the hutch top panel and hutch shelf"),
             action("insert", "", "hutch shelf", "120173", "", "inward", "step 13: long dowel into the hutch shelf"),
             action("attach", "hutch top panel", "hutch left side panel", "", "", "inward",
                    "step 14: hutch top panel and hutch shelf pushed into the hutch left side panel until they click"),
             action("attach", "hutch shelf", "hutch left side panel", "", "", "inward",
                    "step 14: hutch shelf clicked into the hutch left side panel"),
         ],
         final="shelf unit begun"),
    page(17, "assembly_step",
         parts=[HUTCH_SIDE("right"), HUTCH_TOP, HUTCH_SHELF, HUTCH_RAIL],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 3)],
         actions=[
             action("attach", "hutch right side panel", "hutch top panel", "", "", "down",
                    "step 15: hutch right side panel pushed on until it clicks"),
             action("attach", "hutch back rail", "hutch right side panel", "101345", "", "inward",
                    "step 16: hutch rail with 3x wooden dowel 101345 fitted between the hutch side panels at the bottom back"),
         ],
         final="shelf unit frame"),
    page(18, "assembly_step",
         parts=[HUTCH_BACK, HUTCH_SIDE("left"), HUTCH_SIDE("right"), HUTCH_RAIL],
         fasteners=[fastener("151708", "back panel fixing", "plug", 2)],
         actions=[
             action("insert", "", "hutch left side panel", "151708", "", "inward", "step 17: 2x back panel fixing 151708 and pin 151707"),
             action("slide", "hutch back panel", "hutch back rail", "", "", "down",
                    "step 18: hutch back panel slid down the grooves of the hutch side panels into the hutch rail"),
         ],
         final="shelf unit complete"),
    page(19, "assembly_step",
         parts=[HUTCH_SIDE("left"), SIDE("left"), HUTCH_SIDE("right"), SIDE("right")],
         fasteners=[fastener("10049270", "connector plate", "bracket", 2), fastener("144575", "connector screw", "screw", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "hutch left side panel", "left side panel", "10049270", "cross head screwdriver", "clockwise",
                    "step 19: shelf unit set on the chest; connector plate 10049270 screwed across the hutch left side panel and left side panel"),
             action("attach", "hutch right side panel", "right side panel", "10049270", "cross head screwdriver", "clockwise",
                    "step 19: connector plate across the hutch right side panel and right side panel; 2x in all"),
         ],
         final="shelf unit fixed on top of the chest"),
    page(20, "assembly_step",
         parts=[HUTCH_SIDE("left")],
         fasteners=[fastener("10093081", "back panel clip", "other", 2)],
         actions=[action("insert", "", "hutch left side panel", "10093081", "", "inward",
                         "steps 20-21: 2x clip 10093081 and wall spacers 150688 fitted at the back")],
         final="back fittings in place"),
    *[page(n, "assembly_step", unc=["Steps 22-27: wall spacers and wall fixing. The wall is not a part."]) for n in range(21, 28)],
    page(28, "assembly_step",
         parts=[SMALL_FRONT, LARGE_FRONT(2)],
         fasteners=[fastener("118331", "cam bolt", "bolt", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("insert", "", "small drawer front", "118331", "cross head screwdriver", "clockwise",
                    "step 28: 2x cam bolt 118331 into the small drawer front"),
             action("insert", "", "large drawer front", "118331", "cross head screwdriver", "clockwise",
                    "step 28: 4x cam bolt 118331 into each large drawer front, repeat x2"),
         ],
         final="drawer fronts with cam bolts",
         unc=["Insets: one small drawer (1x) and two large drawers (2x)."]),
    page(29, "assembly_step",
         parts=[SMALL_FRONT, LARGE_FRONT(2), DRAWER_SIDE(6)],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 12)],
         actions=[
             action("insert", "", "drawer side", "101345", "", "inward", "step 29: 2x wooden dowel 101345 into each drawer side, repeat x3"),
             action("attach", "drawer side", "small drawer front", "", "", "down",
                    "step 30: 2x drawer side pushed onto the small drawer front"),
             action("attach", "drawer side", "large drawer front", "", "", "down",
                    "step 30: 2x drawer side pushed onto each large drawer front, repeat x2"),
         ],
         final="drawer sides standing on the fronts"),
    page(30, "assembly_step",
         parts=[DRAWER_SIDE(6), SMALL_FRONT],
         fasteners=[fastener("119030", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[action("tighten", "drawer side", "small drawer front", "119030", "flat screwdriver", "clockwise",
                         "step 31: 4x cam lock 119030 turned in the drawer sides, repeat x3")],
         final="drawer sides locked"),
    page(31, "assembly_step",
         parts=[DRAWER_BOTTOM(3), DRAWER_SIDE(6), DRAWER_BACK(3)],
         fasteners=[fastener("10040242", "wire stiffener", "other", 1)],
         tools=[tool("hammer")],
         actions=[
             action("slide", "drawer bottom", "drawer side", "", "", "down", "step 32: drawer bottom slid into the grooves, repeat x3"),
             action("insert", "", "drawer back", "10040242", "hammer", "down",
                    "step 33: wire stiffener 10040242 tapped into the drawer back, repeat x3"),
         ],
         final="drawer bottoms in"),
    page(32, "assembly_step",
         parts=[DRAWER_BACK(3), DRAWER_SIDE(6)],
         fasteners=[fastener("110519", "drawer pin", "nail", 4)],
         actions=[
             action("attach", "drawer back", "drawer side", "", "", "down", "step 34: drawer back tilted in over the drawer bottom, repeat x3"),
             action("insert", "drawer back", "drawer side", "110519", "", "inward",
                    "step 35: 4x drawer pin 110519 pushed through the drawer sides into the drawer back, repeat x3"),
         ],
         final="drawer boxes closed"),
    page(33, "assembly_step",
         parts=[DRAWER_SIDE(6), RUNNER(6, "drawer runner for the drawer sides")],
         fasteners=[fastener("119030", "cam lock", "cam", 4), fastener("146114", "runner screw", "screw", 6)],
         tools=[tool("cross head screwdriver"), tool("flat screwdriver")],
         actions=[
             action("insert", "", "drawer side", "119030", "flat screwdriver", "clockwise",
                    "step 36: 4x cam lock 119030 turned in the tops of the drawer sides, repeat x3"),
             action("attach", "drawer runner", "drawer side", "146114", "cross head screwdriver", "clockwise",
                    "step 37: drawer runner (IKEA DR, DL) hooked onto each drawer side and screwed with 6x runner screw 146114, repeat x3"),
         ],
         final="drawers with runners"),
    page(34, "assembly_step",
         parts=[SMALL_FRONT, LARGE_FRONT(2), KNOB(6), RUNNER(1, "carcass runner")],
         fasteners=[fastener("119976", "knob screw", "screw", 2)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "knob", "small drawer front", "119976", "cross head screwdriver", "clockwise",
                    "step 38: 2x knob 10052019 screwed to the small drawer front with knob screw 119976"),
             action("attach", "knob", "large drawer front", "119976", "cross head screwdriver", "clockwise",
                    "step 38: 2x knob screwed to each large drawer front, repeat x2"),
             action("slide", "small drawer front", "drawer runner", "", "", "inward",
                    "step 39: drawers put on the carcass runners and pushed in, small drawer at the top"),
             action("slide", "large drawer front", "drawer runner", "", "", "inward",
                    "step 39: the two large drawers pushed in below, repeat x2"),
         ],
         final="finished HAUGA chest with shelf unit",
         unc=["Info: never pull out more than one drawer at a time."]),
    page(35, "unknown", unc=["Blank page."]),
    page(36, "unknown", unc=["Back page."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "HAUGA chest with shelf unit", (0.05, 0.08, 0.9, 0.85), complexity="low", conf=0.95)], []),
    **{n: ("warning", [diagram("warning", "Warnings and advice", (0.03, 0.03, 0.97, 0.97), parts=False, complexity="low", action_="warning")], [])
       for n in (2, 3, 4)},
    5: ("parts_list", [diagram("part_inventory", "Bag 1 hardware", (0.03, 0.03, 0.97, 0.97), [], parts=False, fast=True, complexity="medium")], []),
    6: ("parts_list", [diagram("part_inventory", "Bag A hardware and knobs", (0.03, 0.03, 0.97, 0.97),
                               ["101345", "119030", "110519", "146114", "10040242", "10052019"], fast=True, complexity="medium")], []),
    7: ("parts_list", [diagram("part_inventory", "Runner sets 3x", (0.03, 0.03, 0.97, 0.97), ["10043622", "3x"], complexity="low")], []),
    8: ("assembly_step", [step_view("Runners on the side panels", ["1", "146114"], "attach", fast=True, tools=True)], []),
    9: ("assembly_step", [step_view("Top and bottom clicked into a side", ["2", "4x"], "attach", arrows=True)], []),
    10: ("assembly_step", [step_view("Other side clicked on", ["3", "4x"], "attach", arrows=True)], []),
    11: ("assembly_step", [step_view("Back rail and screws", ["4", "5", "2x", "105811"], "attach", fast=True, tools=True)], []),
    12: ("assembly_step", [step_view("Back panel slid in; fixings", ["6", "7", "8x", "151708"], "slide", fast=True, arrows=True)], []),
    13: ("assembly_step", [step_view("Back panel clips and pins", ["8", "9", "6x", "8x", "10093081", "151707"], "insert", fast=True)], []),
    14: ("assembly_step", [step_view("Plinth; glides and feet", ["10", "11", "2x", "101345", "153548", "10051022"], "attach", fast=True)], []),
    15: ("assembly_step", [step_view("Chest stood up; plugs", ["12", "2x", "10047146"], "insert", fast=True, arrows=True)], []),
    16: ("assembly_step", [step_view("Shelf unit top and shelf on a side", ["13", "14", "4x", "120173"], "attach", fast=True, arrows=True)], []),
    17: ("assembly_step", [step_view("Other hutch side; hutch rail", ["15", "16", "3x", "101345"], "attach", fast=True, arrows=True)], []),
    18: ("assembly_step", [step_view("Hutch back panel", ["17", "18", "2x", "151708"], "slide", fast=True, arrows=True)], []),
    19: ("assembly_step", [step_view("Connector plates join shelf unit and chest", ["19", "2x", "10049270", "144575"], "attach", fast=True, tools=True)], []),
    20: ("assembly_step", [step_view("Clips and wall spacers", ["20", "21", "2x", "10093081", "150688"], "insert", fast=True)], []),
    **{n: ("assembly_step", [step_view("Wall fixing", [], "none", parts=False, tools=True)], []) for n in range(21, 28)},
    28: ("assembly_step", [step_view("Cam bolts in the drawer fronts", ["28", "118331"], "insert", fast=True, tools=True)], []),
    29: ("assembly_step", [step_view("Drawer sides onto the fronts", ["29", "30", "2x", "4x", "101345"], "attach", fast=True, arrows=True)], []),
    30: ("assembly_step", [step_view("Cam locks", ["31", "4x", "119030"], "tighten", fast=True, tools=True)], []),
    31: ("assembly_step", [step_view("Drawer bottoms; wire stiffeners", ["32", "33", "10040242"], "slide", fast=True, tools=True, arrows=True)], []),
    32: ("assembly_step", [step_view("Drawer backs; pins", ["34", "35", "4x", "110519"], "attach", fast=True, arrows=True)], []),
    33: ("assembly_step", [step_view("Cam locks; drawer runners", ["36", "37", "4x", "6x", "119030", "146114"], "attach", fast=True, tools=True)], []),
    34: ("assembly_step", [step_view("Knobs; drawers pushed in", ["38", "39", "2x", "119976", "10052019"], "slide", fast=True, tools=True)], []),
    35: ("unknown", [], []), 36: ("unknown", [], []),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA HAUGA Chest of Drawers with Shelf")
