"""Vision results for the IKEA MALM chest of 4 drawers manual (28 pages).

Run: python manuals/malm_drawer_chest/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 80 x 48 cm chest, 100 cm high.
SIDE_PANEL = lambda side, desc: part(
    "", f"{side} side panel", desc, "panel", "wood", 1,
    [("hole", 6, "cam bolt holes along the front and back edges"), ("hole", 12, "runner screw holes")],
    "bottom", size=(18, 480, 1000))
FRONT_RAIL = lambda qty=4: part(
    "", "front rail", "narrow board running across the front between the side panels, between drawer rows",
    "beam", "wood", qty, [("hole", 4, "dowel and cam lock holes at both ends")], "center", size=(764, 50, 18))
BACK_PANEL = lambda qty=2: part(
    "", "back panel", "board closing one half of the back between the side panels",
    "panel", "wood", qty, [("hole", 4, "dowel and cam lock holes at the ends")], "center", size=(382, 12, 900))
BOTTOM = part("", "bottom panel", "bottom panel across the foot of the carcass", "panel", "wood", 1,
              [("hole", 6, "cam lock holes")], "top", size=(764, 460, 18))
TOP = lambda desc: part("", "top panel", desc, "panel", "wood", 1,
                        [("hole", 4, "cam bolt holes underneath")], "bottom", size=(800, 480, 18))
PLINTH = part("", "plinth", "low board across the front under the bottom panel", "panel", "wood", 1,
              [("hole", 4, "bracket screw holes")], "bottom", size=(764, 18, 80))
PLINTH_BRACKET = lambda qty=2: part(
    "10038685", "plinth bracket", "metal angle bracket with several holes, at each end of the plinth",
    "bracket", "metal", qty, [("hole", 4, "screw holes")], "center")
RUNNER = lambda qty, desc: part(
    "10084399", "drawer runner", desc, "rail", "metal", qty, [("hole", 3, "screw holes")], "center")
DRAWER_FRONT = lambda qty=4, desc="drawer front lying face down": part(
    "", "drawer front", desc, "panel", "wood", qty,
    [("slot", 1, "groove for the drawer bottom")], "bottom", size=(796, 18, 235))
DRAWER_SIDE = lambda qty=2: part(
    "", "drawer side", "drawer side with a groove for the bottom", "panel", "wood", qty,
    [("slot", 1, "groove"), ("hole", 2, "dowel holes"), ("hole", 2, "cam lock holes")], "center", size=(12, 440, 160))
DRAWER_BOTTOM = part("", "drawer bottom", "thin drawer bottom slid into the grooves", "panel", "fibreboard", 4,
                     [], "center", size=(730, 440, 3))
DRAWER_BACK = part("", "drawer back", "drawer back board with a slot for the wire stiffener", "panel", "wood", 4,
                   [("hole", 4, "pin holes at the ends")], "top", size=(730, 12, 140))

PAGES = [
    page(1, "cover", final="MALM chest of 4 drawers: carcass on a low plinth, four equal full-width drawers"),
    page(2, "warning", unc=["Tip-over warning text. No assembly action."]),
    page(3, "warning",
         unc=["Tools: flat, cross-head and pozidriv screwdrivers, pencil, hammer, drill with 8 mm and 3 mm bits.",
              "Wall-fixing kit and wall types; two people for heavy parts. No assembly action."]),
    page(4, "warning",
         fasteners=[fastener("109567", "wall screw", "screw", "2x"), fastener("10087223", "wall plug", "dowel", "2x"),
                    fastener("109049", "bracket screw", "screw", "2x"), fastener("100823", "washer", "washer", "4x"),
                    fastener("106989", "wall fixing bracket", "bracket", "2x")],
         unc=["Assemble on a soft surface; ask IKEA if unsure. Wall-fixing kit 370766 contents."]),
    page(5, "parts_list",
         parts=[PLINTH_BRACKET(2), RUNNER(16, "metal drawer runner set 10084399: carcass and drawer halves")],
         fasteners=[fastener("118331", "cam bolt", "bolt", "16x"), fastener("119030", "cam lock", "cam", "16x"),
                    fastener("101345", "wooden dowel", "dowel", "18x"), fastener("155669", "bracket screw", "screw", "8x"),
                    fastener("10048881", "runner screw", "screw", "24x"), fastener("153548", "floor glide", "other", "6x")],
         unc=["Bag 1 (carcass). Runner sets 10084399 drawn as 4x sets; each set has a carcass and a drawer runner for both sides, 16 runners in all.",
              "Panels are not shown in the inventory."]),
    page(6, "parts_list",
         fasteners=[fastener("101345", "wooden dowel", "dowel", "16x"), fastener("110519", "drawer pin", "nail", "16x"),
                    fastener("118331", "cam bolt", "bolt", "16x"), fastener("119030", "cam lock", "cam", "16x"),
                    fastener("146114", "drawer runner screw", "screw", "24x"), fastener("10040242", "wire stiffener", "other", "4x")],
         unc=["Bag 2 (drawers)."]),
    page(7, "assembly_step",
         parts=[SIDE_PANEL("right", "right side panel (IKEA CR) lying flat, inner face up"),
                SIDE_PANEL("left", "left side panel (IKEA CL) lying flat, inner face up"),
                RUNNER(8, "carcass drawer runner laid across the side panel")],
         fasteners=[fastener("10048881", "runner screw", "screw", 24)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "drawer runner", "right side panel", "10048881", "cross head screwdriver", "clockwise",
                    "step 1: 4x drawer runner screwed to the inner face of the right side panel (IKEA CR) with 12x runner screw 10048881; 146114 crossed out"),
             action("attach", "drawer runner", "left side panel", "10048881", "cross head screwdriver", "clockwise",
                    "step 1: 4x drawer runner screwed to the inner face of the left side panel (IKEA CL) with 12x runner screw 10048881"),
         ],
         final="four runners on each side panel"),
    page(8, "assembly_step",
         parts=[SIDE_PANEL("right", "right side panel with runners"), SIDE_PANEL("left", "left side panel with runners"),
                FRONT_RAIL(4), BACK_PANEL(2)],
         fasteners=[fastener("118331", "cam bolt", "bolt", 12), fastener("101345", "wooden dowel", "dowel", 16)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("insert", "", "left side panel", "118331", "cross head screwdriver", "clockwise",
                    "step 2: 12x cam bolt 118331 screwed into the edges of the left side panel and right side panel"),
             action("insert", "", "right side panel", "118331", "cross head screwdriver", "clockwise",
                    "step 2: cam bolt 118331 screwed into the right side panel"),
             action("insert", "", "front rail", "101345", "", "inward",
                    "step 3: 16x wooden dowel 101345 pushed into the ends of the four front rails and two back panels"),
             action("insert", "", "back panel", "101345", "", "inward",
                    "step 3: wooden dowel 101345 pushed into the ends of the back panels"),
         ],
         final="side panels with cam bolts; rails and back panels with dowels"),
    page(9, "assembly_step",
         parts=[SIDE_PANEL("left", "left side panel lying flat"), FRONT_RAIL(4)],
         fasteners=[fastener("119030", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "front rail", "left side panel", "", "", "down",
                    "step 4: 4x front rail stood on the cam bolts along the front edge of the left side panel"),
             action("tighten", "front rail", "left side panel", "119030", "flat screwdriver", "clockwise",
                    "step 5: 4x cam lock 119030 turned in the front rails"),
         ],
         final="four front rails standing on the left side panel",
         unc=["The carcass is built lying on the left side panel; the rails stand upright here and run across the front in the chest."]),
    page(10, "assembly_step",
         parts=[SIDE_PANEL("left", "left side panel lying flat"), BACK_PANEL(2)],
         fasteners=[fastener("119030", "cam lock", "cam", 2)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "back panel", "left side panel", "", "", "down",
                    "step 6: 2x back panel stood along the back edge of the left side panel"),
             action("tighten", "back panel", "left side panel", "119030", "flat screwdriver", "clockwise",
                    "step 7: 2x cam lock 119030 turned in the back panels"),
         ],
         final="rails and back panels standing on the left side panel"),
    page(11, "assembly_step",
         parts=[PLINTH, PLINTH_BRACKET(2)],
         fasteners=[fastener("155669", "bracket screw", "screw", 4), fastener("153548", "floor glide", "other", 2)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "plinth bracket", "plinth", "155669", "cross head screwdriver", "clockwise",
                    "step 8: 2x plinth bracket 10038685 screwed to the ends of the plinth with 2x bracket screw 155669 each"),
             action("insert", "", "plinth", "153548", "", "inward",
                    "step 9: 2x floor glide 153548 pressed into the bottom edge of the plinth"),
         ],
         final="plinth with a bracket at each end and two glides"),
    page(12, "assembly_step",
         parts=[SIDE_PANEL("right", "right side panel lowered onto the rails"), SIDE_PANEL("left", "left side panel"),
                PLINTH, PLINTH_BRACKET(1), BOTTOM, FRONT_RAIL(4)],
         fasteners=[fastener("155669", "bracket screw", "screw", 2), fastener("119030", "cam lock", "cam", 6)],
         tools=[tool("cross head screwdriver"), tool("flat screwdriver")],
         actions=[
             action("attach", "right side panel", "front rail", "", "", "down",
                    "step 10: right side panel lowered onto the free ends of the front rails and back panels"),
             action("attach", "plinth", "left side panel", "155669", "cross head screwdriver", "clockwise",
                    "step 10: plinth bracket screwed to the left side panel with 2x bracket screw 155669"),
             action("attach", "bottom panel", "left side panel", "", "", "down",
                    "step 11: bottom panel lowered onto the dowels at the foot of the side panels"),
             action("tighten", "bottom panel", "right side panel", "119030", "flat screwdriver", "clockwise",
                    "step 12: 6x cam lock 119030 turned in the bottom panel"),
         ],
         final="carcass upside down: two sides, rails, back panels, plinth and bottom",
         unc=["The carcass has been stood up on its top end; the bottom panel goes on top here."]),
    page(13, "assembly_step",
         parts=[SIDE_PANEL("right", "right side panel"), SIDE_PANEL("left", "left side panel"), PLINTH, PLINTH_BRACKET(1)],
         fasteners=[fastener("155669", "bracket screw", "screw", 2), fastener("153548", "floor glide", "other", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "plinth", "right side panel", "155669", "cross head screwdriver", "clockwise",
                    "step 13: plinth bracket screwed to the right side panel with 2x bracket screw 155669"),
             action("insert", "", "left side panel", "153548", "", "inward",
                    "step 14: 4x floor glide 153548 pressed into the bottom edges of the left side panel and right side panel"),
         ],
         final="carcass with plinth fixed and glides fitted"),
    page(14, "assembly_step",
         parts=[TOP("top panel lying face down")],
         fasteners=[fastener("106989", "wall fixing bracket", "bracket", 2), fastener("109049", "bracket screw", "screw", 2),
                    fastener("100823", "washer", "washer", 2), fastener("118331", "cam bolt", "bolt", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("insert", "", "top panel", "106989", "cross head screwdriver", "clockwise",
                    "step 15: 2x wall fixing bracket 106989 screwed to the back edge of the top panel with bracket screw 109049 and washer 100823"),
             action("insert", "", "top panel", "118331", "cross head screwdriver", "clockwise",
                    "step 16: 4x cam bolt 118331 screwed into the underside of the top panel"),
         ],
         final="top panel with wall fixing brackets and cam bolts"),
    page(15, "assembly_step",
         parts=[SIDE_PANEL("left", "left side panel of the upright carcass")],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 2)],
         actions=[
             action("insert", "", "left side panel", "101345", "", "down",
                    "step 17: 2x wooden dowel 101345 pushed into the top edges of the side panels"),
         ],
         final="carcass standing upright with dowels in the tops of the sides",
         unc=["The carcass is turned over to stand on its plinth (curved arrow); turning is not a join."]),
    page(16, "assembly_step",
         parts=[TOP("top panel lowered onto the carcass"), SIDE_PANEL("left", "left side panel"),
                SIDE_PANEL("right", "right side panel")],
         fasteners=[fastener("119030", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "top panel", "left side panel", "", "", "down",
                    "step 18: top panel lowered onto the dowels and cam bolts at the top of the side panels"),
             action("tighten", "top panel", "right side panel", "119030", "flat screwdriver", "clockwise",
                    "step 19: 4x cam lock 119030 turned in the side panels"),
         ],
         final="finished carcass with top"),
    page(17, "assembly_step",
         unc=["Steps 20-21: read the wall-fixing leaflet; the wall fixing brackets are bent down and the chest pushed against the wall. No part joins."]),
    page(18, "warning", unc=["Step 22: drilling and plug guidance for solid, hollow and wooden walls. No assembly action."]),
    page(19, "assembly_step",
         unc=["Step 23: 2x wall screw 109567 with washer 100823 through the wall fixing brackets into the wall. The wall is not a part."]),
    page(20, "assembly_step",
         parts=[DRAWER_FRONT(), DRAWER_SIDE(8)],
         fasteners=[fastener("118331", "cam bolt", "bolt", 4), fastener("101345", "wooden dowel", "dowel", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("insert", "", "drawer front", "118331", "cross head screwdriver", "clockwise",
                    "step 24: 4x cam bolt 118331 screwed into the drawer front, repeat x4 (one per drawer)"),
             action("insert", "", "drawer side", "101345", "", "inward",
                    "step 25: 4x wooden dowel 101345 pushed into the ends of the two drawer sides, repeat x4"),
         ],
         final="drawer front with cam bolts, drawer sides with dowels",
         unc=["Inset: four drawers are built the same way (4x)."]),
    page(21, "assembly_step",
         parts=[DRAWER_FRONT(), DRAWER_SIDE(8), DRAWER_BOTTOM],
         fasteners=[fastener("119030", "cam lock", "cam", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "drawer side", "drawer front", "", "", "down",
                    "step 26: 2x drawer side pushed onto the drawer front, repeat x4"),
             action("tighten", "drawer side", "drawer front", "119030", "flat screwdriver", "clockwise",
                    "step 27: 4x cam lock 119030 turned in the drawer sides, repeat x4"),
             action("slide", "drawer bottom", "drawer side", "", "", "down",
                    "step 28: drawer bottom slid down the grooves of the drawer sides, repeat x4"),
         ],
         final="drawer front with sides and bottom"),
    page(22, "assembly_step",
         parts=[DRAWER_BACK, DRAWER_SIDE(8)],
         fasteners=[fastener("10040242", "wire stiffener", "other", 1)],
         actions=[
             action("insert", "", "drawer back", "10040242", "", "down",
                    "step 29: wire stiffener 10040242 pushed into the holes in the drawer back, notched end down, repeat x4"),
             action("attach", "drawer back", "drawer side", "", "", "down",
                    "step 30: drawer back tilted down between the drawer sides over the drawer bottom, repeat x4"),
         ],
         final="drawer box closed by its back"),
    page(23, "assembly_step",
         parts=[DRAWER_SIDE(8), DRAWER_BACK, RUNNER(8, "drawer runner for the drawer sides")],
         fasteners=[fastener("110519", "drawer pin", "nail", 4), fastener("146114", "drawer runner screw", "screw", 6)],
         tools=[tool("hammer"), tool("cross head screwdriver")],
         actions=[
             action("insert", "drawer back", "drawer side", "110519", "hammer", "inward",
                    "step 31: 4x drawer pin 110519 hammered through the drawer sides into the drawer back, repeat x4"),
             action("attach", "drawer runner", "drawer side", "146114", "cross head screwdriver", "clockwise",
                    "step 32: drawer runner hooked onto each drawer side and screwed with 6x drawer runner screw 146114, repeat x4"),
         ],
         final="finished drawer with runners"),
    page(24, "assembly_step",
         parts=[DRAWER_FRONT(1, "top drawer, finished"), SIDE_PANEL("right", "right side panel of the carcass"),
                RUNNER(1, "carcass runner of the top drawer")],
         fasteners=[fastener("", "anti-tip catch", "other", 1)],
         actions=[
             action("insert", "", "drawer runner", "anti-tip catch", "", "inward",
                    "step 33: 1x anti-tip catch clipped onto the carcass drawer runner of each drawer, repeat x4 (steps 33, 35, 37, 39)"),
             action("slide", "drawer front", "drawer runner", "", "", "inward",
                    "step 34: finished drawer put on the carcass runners and pushed in, top drawer first, repeat x4"),
         ],
         final="top drawer in place",
         unc=["Info: fill the drawers from the bottom up; never pull out more than one drawer at a time.",
              "Pages 25-27 (steps 35-40) fit the anti-tip catch and push in the other three drawers the same way."]),
    page(25, "unknown", unc=["Steps 35-36: second drawer, same as steps 33-34."]),
    page(26, "unknown", unc=["Steps 37-38: third drawer, same as steps 33-34."]),
    page(27, "unknown", unc=["Steps 39-40: bottom drawer, same as steps 33-34."]),
    page(28, "unknown", unc=["Adjusting the drawer runners (insets 2 and 3). No part joins."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "MALM chest of 4 drawers", (0.05, 0.1, 0.8, 0.85), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Tip-over warning", (0.05, 0.05, 0.95, 0.6), parts=False, complexity="low", action_="warning")], []),
    3: ("warning", [diagram("warning", "Tools and wall-fixing advice", (0.03, 0.02, 0.97, 0.98), parts=False, tools=True, complexity="low", action_="warning")], []),
    4: ("warning", [diagram("part_inventory", "Wall-fixing kit 370766", (0.05, 0.55, 0.95, 0.95),
                            ["109567", "10087223", "109049", "100823", "106989", "2x", "4x"], parts=False, fast=True, complexity="low")], []),
    5: ("parts_list", [
        diagram("part_inventory", "Bag 1 hardware", (0.03, 0.05, 0.95, 0.35), ["118331", "119030", "101345", "155669", "10048881", "16x", "18x", "8x", "24x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Floor glide 6x, plinth bracket 2x", (0.08, 0.35, 0.9, 0.6), ["153548", "10038685", "6x", "2x"], fast=True, complexity="low"),
        diagram("part_inventory", "Drawer runner sets 4x", (0.05, 0.62, 0.95, 0.95), ["10084399", "4x"], complexity="low"),
    ], []),
    6: ("parts_list", [diagram("part_inventory", "Bag 2 hardware", (0.03, 0.05, 0.97, 0.35),
                               ["101345", "110519", "118331", "119030", "146114", "10040242", "16x", "24x", "4x"], parts=False, fast=True, complexity="low")], []),
    7: ("assembly_step", [step_view("Runners screwed to both side panels", ["1", "12x", "10048881", "146114"], "attach", fast=True, tools=True, arrows=True)], []),
    8: ("assembly_step", [step_view("Cam bolts in the side panels; dowels in rails and back panels", ["2", "3", "12x", "16x", "118331", "101345"], "insert", fast=True, tools=True)], []),
    9: ("assembly_step", [step_view("Front rails stood on the left side panel; cam locks", ["4", "5", "4x", "119030"], "attach", fast=True, tools=True, arrows=True)], []),
    10: ("assembly_step", [step_view("Back panels stood on the left side panel; cam locks", ["6", "7", "2x", "119030"], "attach", fast=True, tools=True, arrows=True)], []),
    11: ("assembly_step", [step_view("Plinth brackets and glides", ["8", "9", "2x", "155669", "10038685", "153548"], "attach", fast=True, tools=True, arrows=True)], []),
    12: ("assembly_step", [step_view("Right side panel on; plinth screwed; bottom panel on; cam locks", ["10", "11", "12", "6x", "155669", "119030"], "attach", fast=True, tools=True, arrows=True)], []),
    13: ("assembly_step", [step_view("Plinth screwed to the other side; glides", ["13", "14", "4x", "155669", "153548"], "attach", fast=True, tools=True)], []),
    14: ("assembly_step", [step_view("Wall brackets and cam bolts on the top panel", ["15", "16", "2x", "4x", "109049", "100823", "118331"], "insert", fast=True, tools=True)], []),
    15: ("assembly_step", [step_view("Carcass turned over; dowels in the side tops", ["17", "2x", "101345"], "insert", fast=True, arrows=True)], []),
    16: ("assembly_step", [step_view("Top panel lowered on; cam locks", ["18", "19", "4x", "119030"], "attach", fast=True, tools=True, arrows=True)], []),
    17: ("assembly_step", [step_view("Wall fixing: brackets bent, chest pushed to the wall", ["20", "21", "2x"], "none", parts=False, tools=True)], []),
    18: ("warning", [diagram("warning", "Wall types A, B, C and drilling", (0.03, 0.02, 0.97, 0.98), parts=False, tools=True, complexity="low", action_="warning")], []),
    19: ("assembly_step", [step_view("Wall screws through the brackets", ["23", "2x", "109567", "100823"], "none", parts=False, fast=True, tools=True)], []),
    20: ("assembly_step", [step_view("Cam bolts in the drawer front; dowels in the drawer sides (4x drawers)", ["24", "25", "4x", "118331", "101345"], "insert", fast=True, tools=True)], []),
    21: ("assembly_step", [step_view("Drawer sides on; cam locks; bottom slid in", ["26", "27", "28", "4x", "119030"], "attach", fast=True, tools=True, arrows=True)], []),
    22: ("assembly_step", [step_view("Wire stiffener in the drawer back; back tilted in", ["29", "30", "10040242"], "attach", fast=True, arrows=True)], []),
    23: ("assembly_step", [step_view("Drawer pins hammered; runners screwed on", ["31", "32", "4x", "2x", "6x", "110519", "146114"], "attach", fast=True, tools=True, arrows=True)], []),
    24: ("assembly_step", [step_view("Anti-tip catch; top drawer pushed in", ["33", "34", "1x"], "slide", fast=True, arrows=True)], []),
    25: ("unknown", [], ["Same as page 24 for the next drawer."]),
    26: ("unknown", [], ["Same as page 24 for the next drawer."]),
    27: ("unknown", [], ["Same as page 24 for the next drawer."]),
    28: ("unknown", [], ["Runner adjustment."]),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA MALM Chest of 4 Drawers")
