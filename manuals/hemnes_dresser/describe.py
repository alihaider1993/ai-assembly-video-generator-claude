"""Vision results for the IKEA HEMNES 8-drawer dresser manual (48 pages).

A frame-and-panel dresser built lying on its side: the two side frames
(two legs with a side panel between them) lie on the floor, the front and
back rails stand up from them with the centre divider, the other side frame
goes on top, and the frame is stood upright. Then the top panel, the
two-piece back panel (nailed, with the dresser on its front), and eight
drawers: two columns, each with two small drawers side by side at the top
and two wide drawers below. The manual prints no sizes; they are estimated
from the usual size of this dresser (about 1600 wide, 500 deep, 960 high).

Run: python manuals/hemnes_dresser/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

LEG = lambda side, end: part("", f"{side} {end} leg", f"{side} {end} corner leg, a tall square post", "beam", "wood", 1,
                             [("hole", 6, "dowel and cam bolt holes")], side, size=(50, 50, 940))
SIDE_PANEL = lambda side: part("", f"{side} side panel", f"{side} side panel between the {side} legs, with runners inside",
                               "panel", "wood", 1, [("hole", 6, "cam lock and dowel holes")], side, size=(18, 400, 780))
DIVIDER = part("", "divider", "centre divider frame: two posts and a panel with runners on both faces, between the drawer columns",
               "frame", "wood", 1, [("hole", 8, "dowel and cam bolt holes")], "center", size=(40, 400, 780))
FRONT_RAIL = lambda qty=4: part("", "front rail", "long front rail running between the side frames between drawer rows",
                                "beam", "wood", qty, [("hole", 4, "dowel and cam bolt holes")], "center", size=(1500, 30, 50))
BACK_RAIL = lambda qty=2: part("", "back rail", "long back rail between the side frames, top and bottom",
                               "beam", "wood", qty, [("hole", 4, "dowel and cam bolt holes")], "center", size=(1500, 30, 50))
TOP = part("", "top panel", "solid top panel with cam bolts underneath", "panel", "wood", 1,
           [("hole", 11, "cam bolt holes underneath")], "top", size=(1600, 500, 20))
BACK_PANEL = lambda qty=2: part("", "back panel", "thin fibreboard back panel half, nailed to the back of the frame",
                                "panel", "wood", qty, [], "center", size=(780, 3, 820))
SMALL_FRONT = lambda qty=4: part("", "small drawer front", "small drawer front, one knob", "panel", "wood", qty,
                                 [("hole", 1, "knob hole")], "center", size=(360, 18, 160))
WIDE_FRONT = lambda qty=4: part("", "wide drawer front", "wide drawer front, two knobs", "panel", "wood", qty,
                                [("hole", 2, "knob holes")], "center", size=(720, 18, 230))
DRAWER_SIDE = lambda qty=16: part("", "drawer side", "drawer side with a groove for the bottom", "panel", "wood", qty,
                                  [("hole", 4, "dowel and cam holes")], "center", size=(12, 400, 120))
DRAWER_BACK = lambda qty=8: part("", "drawer back", "drawer back board", "panel", "wood", qty, [], "center", size=(680, 12, 120))
DRAWER_BOTTOM = lambda qty=8: part("", "drawer bottom", "thin fibreboard drawer bottom sliding into the grooves", "panel", "wood", qty,
                                   [], "center", size=(680, 400, 3))
RUNNER = lambda qty=32: part("156500", "drawer runner", "metal drawer runner 156500, on the carcass and on the drawer sides",
                             "beam", "metal", qty, [("hole", 3, "screw holes")], "center", size=(400, 12, 35))
KNOB = lambda qty=12: part("117615", "knob", "round wooden knob 117615", "block", "wood", qty, [], "center")

CAM_BOLT = lambda qty: fastener("118331", "cam bolt 118331", "bolt", qty)
CAM_LOCK = lambda qty: fastener("110630", "cam lock 110630", "cam", qty)
DOWEL = lambda qty: fastener("101350", "dowel 101350", "dowel", qty)
SMALL_DOWEL = lambda qty: fastener("101345", "dowel 101345", "dowel", qty)
SHORT_CAM_BOLT = lambda qty: fastener("123492", "cam bolt 123492", "bolt", qty)
LONG_CAM_BOLT = lambda qty: fastener("603440", "cam bolt 603440", "bolt", qty)
RUNNER_SCREW = lambda qty: fastener("100349", "screw 100349", "screw", qty)
GUIDE_SCREW = lambda qty: fastener("100365", "screw 100365", "screw", qty)
DRAWER_SCREW = lambda qty: fastener("100347", "screw 100347", "screw", qty)
LONG_SCREW = lambda qty: fastener("100214", "screw 100214", "screw", qty)
BLACK_SCREW = lambda qty: fastener("100232", "screw 100232", "screw", qty)
KNOB_SCREW = lambda qty: fastener("100413", "screw 100413", "screw", qty)
PLUG = lambda qty: fastener("110519", "plug 110519", "plug", qty)
NAIL = lambda qty: fastener("101221", "nail 101221", "other", qty)
GLIDER = lambda qty: fastener("191064", "floor glider 191064", "plug", qty)
FOOT = lambda qty: fastener("107862", "adjustable foot 107862", "bolt", qty)
ROD = lambda qty: fastener("131294", "stabiliser rod 131294", "other", qty)
ROD_SCREW = lambda qty: fastener("105344", "screw 105344", "screw", qty)

DRIVER = tool("cross head screwdriver")
FLAT = tool("flat screwdriver")
HAMMER = tool("hammer")
ALLEN = tool("allen key 100001")
ALLEN_LONG = tool("allen key 100006")

SIDES = ("left", "right")
LEGS = [LEG(s, e) for s in SIDES for e in ("front", "back")]

PAGES = [
    page(1, "cover", final="HEMNES 8-drawer dresser: four small drawers along the top, four wide drawers below, on four legs",
         unc=["Cover page; product name HEMNES and IKEA logo."]),
    page(2, "warning", unc=["Tip-over warning: the dresser must be fixed to the wall."]),
    page(3, "warning", tools=[DRIVER, FLAT, HAMMER],
         unc=["Tools: cross head and flat screwdrivers, hammer, drill for the wall fixing; two people; call IKEA if unsure."]),
    page(4, "parts_list", fasteners=[CAM_BOLT(22), CAM_LOCK(12), DOWEL(8), RUNNER_SCREW(12)],
         unc=["Bag 1 is used from step 1; the second box on this page is the wall fixing kit (strap 107967, screws, plug), used on page 33.",
              "The wall fixing kit attaches the dresser to the wall and is not part of the dresser itself."]),
    page(5, "parts_list",
         fasteners=[DOWEL(24), CAM_BOLT(11), BLACK_SCREW(2), LONG_SCREW(9), CAM_LOCK(25), GUIDE_SCREW(26), FOOT(1), NAIL(1), LONG_CAM_BOLT(4)],
         tools=[ALLEN, ALLEN_LONG], unc=["Bag 2 is used from step 7."]),
    page(6, "parts_list",
         parts=[RUNNER(32), KNOB(12)],
         fasteners=[CAM_LOCK(32), KNOB_SCREW(12), SMALL_DOWEL(32), PLUG(36), SHORT_CAM_BOLT(32), DRAWER_SCREW(32), ROD_SCREW(8),
                    ROD(4), GLIDER(4)],
         unc=["Bag 3 is for the drawers (page 38).", "Four kinds of runner 156500, 8 of each: carcass and drawer halves, left and right."]),
    page(7, "assembly_step",
         parts=LEGS,
         fasteners=[CAM_BOLT(12)],
         tools=[DRIVER],
         actions=[action("insert", "", "left front leg", "118331", "cross head screwdriver", "inward",
                         "step 1: the four legs (labelled L1, L2, R2, R1) laid on the floor; 12x cam bolt 118331 screwed into their inner faces, repeat x4")],
         final="four legs lying side by side with cam bolts in them",
         unc=["The dresser is built lying on its side; the legs lie flat in pairs, one pair per side frame."]),
    page(8, "assembly_step",
         parts=LEGS + [SIDE_PANEL(s) for s in SIDES],
         fasteners=[DOWEL(8), CAM_LOCK(12)],
         tools=[DRIVER],
         actions=[
             action("attach", "left side panel", "left front leg", "101350", "", "inward",
                    "step 2: left side panel laid between the left front leg and the left back leg on 8x dowel 101350"),
             action("attach", "left side panel", "left back leg", "101350", "", "inward",
                    "step 2: left side panel pushed onto the dowels in the left back leg"),
             action("attach", "right side panel", "right front leg", "101350", "", "inward",
                    "step 2: right side panel laid between the right front leg and the right back leg"),
             action("attach", "right side panel", "right back leg", "101350", "", "inward",
                    "step 2: right side panel pushed onto the dowels in the right back leg"),
             action("tighten", "", "left side panel", "110630", "cross head screwdriver", "clockwise",
                    "step 3: 12x cam lock 110630 turned in the side panels to lock the cam bolts"),
         ],
         final="two side frames lying on the floor: each a side panel between two legs"),
    page(9, "assembly_step",
         parts=[SIDE_PANEL(s) for s in SIDES] + [RUNNER(6)],
         fasteners=[RUNNER_SCREW(12)],
         tools=[DRIVER],
         actions=[
             action("attach", "drawer runner", "left side panel", "100349", "cross head screwdriver", "down",
                    "step 4: 3x drawer runner 156500 screwed to the inner face of the left side panel with 6x screw 100349"),
             action("attach", "drawer runner", "right side panel", "100349", "cross head screwdriver", "down",
                    "step 4: 3x drawer runner 156500 screwed to the right side panel with 6x screw 100349"),
         ],
         final="runners on the inside of both side panels",
         unc=["Inset: use screw 100349, not 100347 or 100365."]),
    page(10, "assembly_step",
         parts=LEGS, fasteners=[GLIDER(4)],
         actions=[action("insert", "", "left front leg", "191064", "", "inward",
                         "step 5: 4x floor glider 191064 pressed into the bottom ends of the four legs")],
         final="floor gliders in the leg ends"),
    page(11, "assembly_step",
         parts=[SIDE_PANEL("left")] + LEGS, fasteners=[CAM_BOLT(10)], tools=[DRIVER],
         actions=[action("insert", "", "left front leg", "118331", "cross head screwdriver", "inward",
                         "step 6: 10x cam bolt 118331 screwed into the upward faces of the left side frame for the rails")],
         final="left side frame with cam bolts facing up"),
    page(12, "assembly_step",
         parts=[SIDE_PANEL("left"), FRONT_RAIL(2), BACK_RAIL(1)] + LEGS, fasteners=[DOWEL(2)],
         actions=[
             action("attach", "back rail", "left back leg", "101350", "", "up",
                    "step 7: back rail stood up on 2x dowel 101350 in the left back leg (the dresser lies on its left side)"),
             action("attach", "front rail", "left front leg", "101350", "", "up",
                    "step 7: front rail stood up on dowels in the left front leg"),
         ],
         final="first rails standing up from the left side frame",
         unc=["Info inset: the short rails and the long rails must not be swapped.",
              "Because the dresser is built lying on its left side, the rails are drawn standing up; in the finished dresser they run across."]),
    page(13, "assembly_step",
         parts=[SIDE_PANEL("left"), FRONT_RAIL(2), BACK_RAIL(1)], fasteners=[CAM_LOCK(2)], tools=[DRIVER],
         actions=[action("tighten", "", "front rail", "110630", "cross head screwdriver", "clockwise",
                         "step 8: 2x cam lock 110630 turned to lock the rails")],
         final="rails locked to the left side frame"),
    page(14, "assembly_step",
         parts=[SIDE_PANEL("left"), FRONT_RAIL(4), BACK_RAIL(2)] + LEGS, fasteners=[DOWEL(3)],
         actions=[action("attach", "front rail", "left front leg", "101350", "", "up",
                         "step 9: the other front rails and back rail stood up on 3x dowel 101350 in the left side frame, repeat x3")],
         final="all front and back rails standing up from the left side frame"),
    page(15, "assembly_step",
         parts=[FRONT_RAIL(4), BACK_RAIL(2)], fasteners=[CAM_LOCK(3)], tools=[DRIVER],
         actions=[action("tighten", "", "front rail", "110630", "cross head screwdriver", "clockwise",
                         "step 10: 3x cam lock 110630 turned to lock the rails")],
         final="all rails locked"),
    page(16, "assembly_step",
         parts=[DIVIDER, RUNNER(3)], fasteners=[GUIDE_SCREW(9)], tools=[DRIVER],
         actions=[action("attach", "drawer runner", "divider", "100365", "cross head screwdriver", "down",
                         "step 11: 3x drawer runner 156500 screwed to one face of the divider with 9x screw 100365")],
         final="divider with runners on one face"),
    page(17, "assembly_step",
         parts=[DIVIDER, RUNNER(3)], fasteners=[GUIDE_SCREW(9)], tools=[DRIVER],
         actions=[action("attach", "drawer runner", "divider", "100365", "cross head screwdriver", "down",
                         "step 12: divider turned over; 3x drawer runner screwed to its other face with 9x screw 100365")],
         final="divider with runners on both faces"),
    page(18, "assembly_step",
         parts=[DIVIDER], fasteners=[DOWEL(1), LONG_CAM_BOLT(4)], tools=[DRIVER],
         actions=[action("insert", "", "divider", "603440", "cross head screwdriver", "inward",
                         "step 13: 1x dowel 101350 and 4x cam bolt 603440 screwed into the divider")],
         final="divider ready"),
    page(19, "assembly_step",
         parts=[DIVIDER, FRONT_RAIL(4)], fasteners=[DOWEL(2)],
         actions=[action("attach", "divider", "front rail", "101350", "", "down",
                         "step 14: divider lowered between the rails onto 2x dowel 101350, halfway along them")],
         final="divider standing across the middle of the rails"),
    page(20, "assembly_step",
         parts=[DIVIDER, FRONT_RAIL(4)], fasteners=[LONG_SCREW(3)], tools=[ALLEN],
         actions=[action("tighten", "", "divider", "100214", "allen key 100001", "clockwise",
                         "step 15: 3x screw 100214 through the rails into the divider with allen key 100001")],
         final="divider screwed to the rails"),
    page(23, "assembly_step",
         parts=[DIVIDER], fasteners=[CAM_LOCK(2)], tools=[DRIVER],
         actions=[action("tighten", "", "divider", "110630", "cross head screwdriver", "clockwise",
                         "step 18: 2x cam lock 110630 turned to lock the divider")],
         final="divider locked in place",
         unc=["Steps 16 and 17 (pages 21-22) repeat steps 14 and 15 for the rest of the divider."]),
    page(24, "assembly_step",
         parts=[SIDE_PANEL("right"), FRONT_RAIL(4)], fasteners=[DOWEL(5)],
         actions=[action("attach", "right side panel", "front rail", "101350", "", "down",
                         "step 19: right side frame (right side panel with its legs) lowered onto the tops of the rails on 5x dowel 101350")],
         final="right side frame on top of the rails"),
    page(25, "assembly_step",
         parts=[SIDE_PANEL("right")], fasteners=[CAM_LOCK(5)], tools=[DRIVER],
         actions=[action("tighten", "", "right side panel", "110630", "cross head screwdriver", "clockwise",
                         "step 20: 5x cam lock 110630 turned in the right side frame")],
         final="frame complete, lying on its left side"),
    page(26, "assembly_step",
         parts=[DIVIDER], fasteners=[FOOT(1)],
         actions=[action("insert", "", "divider", "107862", "", "clockwise",
                         "step 21: 1x adjustable foot 107862 screwed into the bottom of the divider")],
         final="frame stood upright",
         unc=["The frame is turned upright after this step; the turn is not a join."]),
    page(27, "assembly_step", parts=[RUNNER(4)], fasteners=[GUIDE_SCREW(4)], tools=[DRIVER],
         unc=["Steps 22-23: runners screwed to the two small drawer guides that go between the small top drawers; drawn small, not modelled separately."]),
    page(28, "assembly_step",
         parts=[DIVIDER, FRONT_RAIL(4)], fasteners=[BLACK_SCREW(2), LONG_SCREW(2)], tools=[ALLEN, ALLEN_LONG],
         actions=[action("tighten", "", "front rail", "100214", "allen key 100001", "clockwise",
                         "step 24: the small drawer guides fixed between the top rails with 2x screw 100232 and 2x screw 100214")],
         final="upright frame with all runners in place"),
    page(29, "assembly_step",
         parts=[TOP, SIDE_PANEL("left"), SIDE_PANEL("right")], fasteners=[CAM_BOLT(11), DOWEL(9)], tools=[DRIVER],
         actions=[
             action("insert", "", "top panel", "118331", "cross head screwdriver", "inward",
                    "step 25: top panel laid upside down; 11x cam bolt 118331 screwed into its underside"),
             action("attach", "top panel", "left side panel", "101350", "", "down",
                    "step 26: top panel turned over and lowered onto the frame on 9x dowel 101350"),
         ],
         final="top panel on the frame"),
    page(30, "assembly_step",
         parts=[TOP], fasteners=[LONG_SCREW(4), CAM_LOCK(11)], tools=[ALLEN, DRIVER],
         actions=[action("tighten", "", "top panel", "110630", "cross head screwdriver", "clockwise",
                         "step 27-28: 4x screw 100214 up through the top rail and 11x cam lock 110630 turned to lock the top panel")],
         final="top panel fixed"),
    page(32, "assembly_step",
         parts=[BACK_PANEL(2), BACK_RAIL(2)], fasteners=[NAIL(28)], tools=[HAMMER],
         actions=[action("attach", "back panel", "back rail", "101221", "hammer", "down",
                         "step 29-33: dresser laid on its front; the two back panel halves laid on the back and fixed with 28x nail 101221")],
         final="back panel nailed on",
         unc=["Steps 29-30 mark where the nails go with a pencil; page 31 shows the first nail in each corner."]),
    page(37, "assembly_step",
         unc=["Steps 34-38 (pages 34-37): the dresser stood up and fixed to the wall with the wall fixing kit; it is not part of the dresser."]),
    page(39, "assembly_step",
         parts=[SMALL_FRONT(4), WIDE_FRONT(4), DRAWER_SIDE(16)], fasteners=[SMALL_DOWEL(32), SHORT_CAM_BOLT(32)], tools=[DRIVER],
         actions=[
             action("attach", "drawer side", "small drawer front", "101345", "cross head screwdriver", "up",
                    "step 39-41: 2x drawer side pushed onto dowels 101345 and cam bolts 123492 in each drawer front, repeat x8"),
             action("attach", "drawer side", "wide drawer front", "101345", "cross head screwdriver", "up",
                    "step 41: 2x drawer side onto each wide drawer front, repeat x4"),
         ],
         final="eight drawer fronts, each with two sides standing up",
         unc=["Drawers come in three sizes: 4 small, 2 wide, 2 wide and deeper (the bottom row)."]),
    page(40, "assembly_step",
         parts=[DRAWER_SIDE(16), DRAWER_BACK(8), DRAWER_BOTTOM(8)], fasteners=[CAM_LOCK(32)], tools=[DRIVER],
         actions=[
             action("tighten", "", "drawer side", "110630", "cross head screwdriver", "clockwise",
                    "step 42: 4x cam lock 110630 turned in each drawer, repeat x8"),
             action("attach", "drawer bottom", "drawer side", "", "", "down",
                    "step 43: drawer bottom slid down into the grooves of the drawer sides, repeat x8"),
         ],
         final="drawer boxes with bottoms"),
    page(41, "assembly_step",
         parts=[DRAWER_BACK(8), DRAWER_SIDE(16)], fasteners=[PLUG(36)], tools=[HAMMER],
         actions=[action("attach", "drawer back", "drawer side", "110519", "hammer", "down",
                         "step 44: drawer back pushed down between the drawer sides and fixed with plugs 110519 tapped in, repeat x8")],
         final="drawer boxes closed with their backs"),
    page(42, "assembly_step",
         parts=[DRAWER_BOTTOM(8), WIDE_FRONT(4)], fasteners=[ROD(4), ROD_SCREW(8)], tools=[DRIVER],
         actions=[action("insert", "", "drawer bottom", "131294", "cross head screwdriver", "inward",
                         "step 45: on each wide drawer a stabiliser rod 131294 fixed under the bottom with screws 105344, repeat x4")],
         final="wide drawers with stabiliser rods"),
    page(43, "assembly_step",
         parts=[DRAWER_SIDE(16), RUNNER(16)], fasteners=[DRAWER_SCREW(32)], tools=[DRIVER],
         actions=[action("attach", "drawer runner", "drawer side", "100347", "cross head screwdriver", "inward",
                         "step 46: a drawer runner 156500 screwed to each drawer side with screws 100347, repeat x16")],
         final="runners on the drawer sides"),
    page(44, "assembly_step",
         parts=[KNOB(12), SMALL_FRONT(4), WIDE_FRONT(4)], fasteners=[KNOB_SCREW(12)], tools=[DRIVER],
         actions=[
             action("attach", "knob", "wide drawer front", "100413", "cross head screwdriver", "inward",
                    "step 47: 2x knob 117615 screwed to each wide drawer front with screw 100413, repeat x4"),
             action("attach", "knob", "small drawer front", "100413", "cross head screwdriver", "inward",
                    "step 47: 1x knob 117615 screwed to each small drawer front, repeat x4"),
         ],
         final="eight finished drawers"),
    page(45, "assembly_step",
         parts=[WIDE_FRONT(4), DIVIDER, SIDE_PANEL("left")],
         actions=[action("slide", "wide drawer front", "divider", "", "", "inward",
                         "step 48-50: the wide drawers lifted onto the runners and pushed in, the deeper ones in the bottom row, repeat x4")],
         final="wide drawers in place",
         unc=["Info inset: the drawer with the warning label goes top left; the deeper drawers go in the bottom row."]),
    page(46, "assembly_step",
         parts=[SMALL_FRONT(4), DIVIDER],
         actions=[action("slide", "small drawer front", "divider", "", "", "inward",
                         "step 49: the four small drawers pushed in along the top row, repeat x4")],
         final="all eight drawers in place"),
    page(47, "assembly_step", parts=[SMALL_FRONT(4), WIDE_FRONT(4)],
         final="finished HEMNES 8-drawer dresser",
         unc=["Steps 50-51 show the drawers opening and closing."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled HEMNES 8-drawer dresser", (0.05, 0.2, 0.8, 0.6), complexity="low", conf=0.95)], []),
    4: ("parts_list", [diagram("part_inventory", "Bag 1: cam bolt 118331 x22, cam lock 110630 x12, dowel 101350 x8, screw 100349 x12",
                               (0.05, 0.05, 0.95, 0.35), ["118331", "110630", "101350", "100349"], parts=False, fast=True, complexity="low")], []),
    5: ("parts_list", [diagram("part_inventory", "Bag 2: dowel 101350 x24, cam bolt 118331 x11, screws 100232 x2 and 100214 x9, cam lock 110630 x25, screw 100365 x26, foot 107862, nails 101221, cam bolts 603440 x4",
                               (0.05, 0.05, 0.95, 0.9), ["101350", "118331", "100232", "100214", "110630", "100365", "107862", "101221", "603440"],
                               parts=False, fast=True, tools=True, complexity="medium")], []),
    6: ("parts_list", [diagram("part_inventory", "Bag 3: cam lock x32, screw 100413 x12, dowel 101345 x32, plug 110519 x36, cam bolt 123492 x32, knob 117615 x12, screws 100347 x32 and 105344 x8; runners 156500 4 kinds x8; rods 131294 x4; gliders 191064 x4",
                               (0.05, 0.05, 0.95, 0.95), ["110630", "100413", "101345", "110519", "123492", "117615", "156500", "131294", "191064"],
                               fast=True, complexity="medium")], []),
    8: ("assembly_step", [diagram("exploded_view", "Steps 2-3: side panels between the legs on dowels, cam locks", (0.5, 0.05, 0.98, 0.95),
                                  ["101350", "110630", "8x", "12x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    24: ("assembly_step", [diagram("exploded_view", "Step 19: right side frame lowered onto the rails", (0.5, 0.05, 0.98, 0.95),
                                   ["101350", "5x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    29: ("assembly_step", [diagram("exploded_view", "Steps 25-26: top panel onto the frame", (0.05, 0.05, 0.95, 0.95),
                                   ["118331", "101350", "11x", "9x"], fast=True, arrows=True, action_="attach", complexity="high")], []),
    45: ("assembly_step", [diagram("assembly_view", "Step 48: drawers in, deeper ones at the bottom", (0.05, 0.05, 0.95, 0.95),
                                   arrows=True, action_="insert", complexity="medium")], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA HEMNES 8-Drawer Dresser")
