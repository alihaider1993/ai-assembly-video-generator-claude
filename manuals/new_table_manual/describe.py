"""Vision results for the IKEA NORDEN extendable dining table manual (20 pages).

The manual prints no sizes for the wooden parts, so they get default sizes
by role. Built upside down on the tabletop, then turned over.

Run: python manuals/new_table_manual/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

TABLETOP = part(
    "", "tabletop", "two table leaves locked together, lying upside down on the floor", "panel", "wood", 1,
    [("hole", 16, "pre-drilled holes for the slide runner rails"), ("connector", 2, "leaf locks on the join")], "center")
SIDE_RAIL = lambda qty=2: part(
    "", "long side rail", "long wooden apron rail with cam bolt holes along its inner face", "beam", "wood", qty,
    [("hole", 4, "cam bolt holes on the inner face"), ("hole", 4, "bracket screw holes at each end")], "center")
END_RAIL = lambda qty=2: part(
    "", "end rail", "short wooden apron rail with notched ends and dowel holes", "beam", "wood", qty,
    [("hole", 4, "dowel holes in the ends"), ("slot", 2, "notches at the ends")], "left")
CROSS_RAIL = lambda qty=2: part(
    "", "cross rail", "wooden bar spanning the frame between the two long side rails", "beam", "wood", qty,
    [("hole", 4, "dowel holes in the ends"), ("hole", 2, "cam lock holes")], "center")
GUIDE_RAIL = lambda qty=2: part(
    "", "guide rail", "short wooden guide rail inside the frame between a cross rail and the end rail", "beam", "wood", qty,
    [("hole", 2, "dowel holes in the ends")], "center")
RUNNER = lambda qty=4: part(
    "", "slide runner rail", "short wooden runner rail screwed to the underside of the tabletop", "beam", "wood", qty,
    [("hole", 4, "screw holes")], "center")
BRACKET = lambda qty=4: part(
    "118254", "corner bracket", "cast metal leg bracket with a large centre hole and screw lugs", "bracket", "metal", qty,
    [("hole", 1, "centre hole for the leg's threaded rod"), ("hole", 4, "screw holes in the lugs")], "right")
LEG = lambda qty=4: part(
    "", "leg", "long square wooden leg with a cross dowel hole and threaded rod at the top", "beam", "wood", qty,
    [("hole", 1, "cross dowel hole near the top"), ("hole", 2, "dowel and cam bolt holes for the stretchers")], "center")
END_STRETCHER = lambda qty=2: part(
    "", "end stretcher", "short wooden stretcher board between two legs with a cam bolt in the middle", "beam", "wood", qty,
    [("hole", 2, "dowel holes in the ends"), ("hole", 1, "cam bolt hole in the middle")], "center")
LONG_STRETCHER = lambda qty=1: part(
    "", "long stretcher", "long wooden stretcher board running between the two end stretchers", "beam", "wood", qty,
    [("hole", 2, "dowel holes in the ends")], "center")

DOWEL_LONG = lambda qty: fastener("101353", "wooden dowel 101353 (long)", "dowel", qty)
DOWEL = lambda qty: fastener("101350", "wooden dowel 101350", "dowel", qty)
CAM_BOLT = lambda qty: fastener("118331", "cam bolt", "bolt", qty)
CAM_LOCK = lambda qty: fastener("113434", "cam lock", "nut", qty)
RUNNER_SCREW = lambda qty: fastener("114727", "runner screw", "screw", qty)
STOP_SCREW = lambda qty: fastener("105896", "stop screw", "screw", qty)
SCREW = lambda qty: fastener("100325", "screw 100325", "screw", qty)
CROSS_DOWEL = lambda qty: fastener("100535", "cross dowel", "dowel", qty)
ROD = lambda qty: fastener("100038", "threaded rod", "bolt", qty)
NUT = lambda qty: fastener("100712", "nut", "nut", qty)
WASHER = lambda qty: fastener("100833", "washer", "washer", qty)
ANGLE = lambda qty: fastener("117841", "metal angle plate", "bracket", qty)
GLIDE = lambda qty: fastener("117559", "floor glide", "washer", qty)

SCREWDRIVER = tool("screwdriver")
SPANNER = tool("adjustable spanner")
HAMMER = tool("hammer")

PAGES = [
    page(1, "cover",
         final="NORDEN extendable dining table: long two-leaf top on four square legs with an H-shaped stretcher frame",
         unc=["Cover page; product name NORDEN and IKEA logo."]),
    page(2, "warning",
         tools=[tool("flat screwdriver"), tool("cross-head screwdriver"), SPANNER],
         unc=["Tools needed; assemble with two people; protect the floor; call IKEA if unsure."]),
    page(3, "parts_list",
         parts=[BRACKET()],
         fasteners=[DOWEL_LONG(6), DOWEL(12), CAM_BOLT(10), CAM_LOCK(10), RUNNER_SCREW(16), STOP_SCREW(2), SCREW(24),
                    CROSS_DOWEL(4), ROD(4), NUT(4), WASHER(4), ANGLE(4), GLIDE(4)],
         unc=["Hardware inventory only; wooden parts are not listed and no sizes are printed."]),
    page(4, "assembly_step",
         parts=[SIDE_RAIL(), END_RAIL(), BRACKET()],
         fasteners=[SCREW(16), CAM_BOLT(4)],
         tools=[SCREWDRIVER],
         actions=[
             action("attach", "corner bracket", "long side rail", "100325", "screwdriver", "down",
                    "4x corner bracket 118254 screwed onto the ends of the two long side rails with screws 100325"),
             action("insert", "", "long side rail", "118331", "screwdriver", "down",
                    "4x cam bolt 118331 screwed into the inner face of the long side rails"),
         ],
         final="two long side rails with corner brackets at both ends and cam bolts along them",
         unc=["Steps 1 and 2."]),
    page(5, "assembly_step",
         parts=[SIDE_RAIL(), CROSS_RAIL()],
         fasteners=[DOWEL(4), CAM_LOCK(4)],
         tools=[SCREWDRIVER],
         actions=[
             action("insert", "", "cross rail", "101350", "", "inward",
                    "4x wooden dowel 101350 pushed into the ends of the cross rails"),
             action("attach", "cross rail", "long side rail", "", "", "inward",
                    "two cross rails pushed in between the long side rails onto the dowels and cam bolts (arrows)"),
             action("tighten", "", "cross rail", "113434", "screwdriver", "clockwise",
                    "4x cam lock 113434 set into the cross rails and turned clockwise to lock the cam bolts"),
         ],
         final="ladder of two long side rails joined by two cross rails",
         unc=["Steps 3 and 4; the inset shows the short dowel 101350, not the long 101353."]),
    page(6, "assembly_step",
         parts=[SIDE_RAIL(), CROSS_RAIL(), GUIDE_RAIL(), END_RAIL(), BRACKET()],
         fasteners=[DOWEL(8), SCREW(4)],
         tools=[SCREWDRIVER],
         actions=[
             action("attach", "guide rail", "cross rail", "101350", "", "inward",
                    "two short guide rails fitted on dowels 101350 between each cross rail and the end of the frame"),
             action("attach", "end rail", "long side rail", "100325", "screwdriver", "inward",
                    "end rails pushed onto the dowels at both ends of the frame; 4x screw 100325 through the corner brackets"),
         ],
         final="complete rectangular frame: long side rails, end rails, cross rails and guide rails",
         unc=["Steps 5 and 6; 8x dowel 101350 in the end rails and guide rails."]),
    page(7, "assembly_step",
         parts=[TABLETOP, RUNNER()],
         fasteners=[RUNNER_SCREW(16)],
         tools=[SCREWDRIVER],
         actions=[
             action("attach", "slide runner rail", "tabletop", "114727", "screwdriver", "down",
                    "4 slide runner rails screwed to the underside of the tabletop with 16x screw 114727"),
         ],
         final="upside-down tabletop, its two leaves locked together, with four slide runner rails on the underside",
         unc=["Steps 7 and 8. Step 7 turns both leaves upside down and closes the 2 leaf locks."]),
    page(8, "assembly_step",
         parts=[TABLETOP, SIDE_RAIL(), RUNNER()],
         actions=[
             action("place", "long side rail", "tabletop", "", "", "down",
                    "the assembled frame lowered upside down onto the tabletop and slid along the slide runner rails (arrows)"),
         ],
         final="frame resting on the upside-down tabletop, held by the runners",
         unc=["Step 9; insets show the frame's notch catching the runner."]),
    page(9, "assembly_step",
         parts=[LEG()],
         fasteners=[CROSS_DOWEL(4), ROD(4), CAM_BOLT(4)],
         tools=[tool("flat screwdriver"), SCREWDRIVER],
         actions=[
             action("insert", "", "leg", "100535", "flat screwdriver", "inward",
                    "4x cross dowel 100535 pushed into the hole near the top of each leg, slot turned to face the rod"),
             action("insert", "", "leg", "100038", "", "clockwise",
                    "4x threaded rod 100038 screwed into the top end of each leg"),
             action("insert", "", "leg", "118331", "screwdriver", "down",
                    "4x cam bolt 118331 screwed into the side of each leg"),
         ],
         final="four legs, each with a threaded rod in its top",
         unc=["Steps 10 and 11; inset shows the correct slot orientation of the cross dowel."]),
    page(10, "assembly_step",
         parts=[TABLETOP, SIDE_RAIL(), LEG(1), BRACKET(1)],
         fasteners=[SCREW(8), ANGLE(4), WASHER(1), NUT(1)],
         tools=[SCREWDRIVER, SPANNER],
         actions=[
             action("insert", "", "tabletop", "117841", "screwdriver", "down",
                    "4 metal angle plates 117841 screwed to the underside of the tabletop beside the frame with 8x screw 100325"),
             action("attach", "leg", "corner bracket", "100712", "adjustable spanner", "down",
                    "leg stood upright in the corner bracket 118254 with its threaded rod through the bracket; washer 100833 and nut 100712 tightened with a spanner"),
         ],
         final="first leg bolted upright into a corner bracket",
         unc=["Steps 12 and 13."]),
    page(11, "assembly_step",
         parts=[END_STRETCHER(), LONG_STRETCHER()],
         fasteners=[CAM_BOLT(2), DOWEL_LONG(6)],
         tools=[SCREWDRIVER],
         actions=[
             action("insert", "", "end stretcher", "118331", "screwdriver", "down",
                    "2x cam bolt 118331 screwed into the middle of the end stretchers"),
             action("insert", "", "long stretcher", "101353", "", "inward",
                    "6x long wooden dowel 101353 pushed into the ends of the long stretcher and the end stretchers"),
         ],
         final="stretchers with dowels and cam bolts ready",
         unc=["Steps 14 and 15; a small picture shows the finished stretcher frame."]),
    page(12, "assembly_step",
         parts=[TABLETOP, LEG(2), END_STRETCHER(1), BRACKET(2)],
         fasteners=[DOWEL_LONG(2), WASHER(1), NUT(1)],
         tools=[SPANNER],
         actions=[
             action("attach", "end stretcher", "leg", "101353", "", "inward",
                    "end stretcher pushed onto the dowels in the side of the first leg (arrow)"),
             action("attach", "leg", "corner bracket", "100712", "adjustable spanner", "down",
                    "second leg pushed onto the other end of the end stretcher and bolted into its corner bracket with washer 100833 and nut 100712"),
         ],
         final="two legs at one end joined by an end stretcher",
         unc=["Steps 16 and 17."]),
    page(13, "assembly_step",
         parts=[TABLETOP, LEG(2), END_STRETCHER(1), LONG_STRETCHER(), BRACKET(1)],
         fasteners=[DOWEL_LONG(1), WASHER(1), NUT(1)],
         tools=[SPANNER],
         actions=[
             action("attach", "leg", "corner bracket", "100712", "adjustable spanner", "down",
                    "third leg bolted into a corner bracket at the other end with washer 100833 and nut 100712"),
             action("attach", "long stretcher", "end stretcher", "101353", "", "inward",
                    "two people fit the long stretcher into the middle of the end stretcher (arrow)"),
         ],
         final="three legs up, long stretcher fitted to one end stretcher",
         unc=["Steps 18 and 19; two people shown."]),
    page(14, "assembly_step",
         parts=[END_STRETCHER(1), LONG_STRETCHER(), LEG(2)],
         fasteners=[DOWEL_LONG(1)],
         actions=[
             action("attach", "end stretcher", "long stretcher", "101353", "", "inward",
                    "second end stretcher fitted onto the other end of the long stretcher and the third leg (arrows)"),
         ],
         final="H-shaped stretcher frame between three legs",
         unc=["Step 20."]),
    page(15, "assembly_step",
         parts=[LEG(1), END_STRETCHER(1), BRACKET(1)],
         fasteners=[WASHER(1), NUT(1)],
         tools=[SPANNER],
         actions=[
             action("attach", "leg", "corner bracket", "100712", "adjustable spanner", "down",
                    "last leg pushed onto the end stretcher and bolted into its corner bracket with washer 100833 and nut 100712"),
         ],
         final="all four legs and the stretcher frame in place, table still upside down",
         unc=["Step 21."]),
    page(16, "assembly_step",
         parts=[LEG(4), END_STRETCHER(2), LONG_STRETCHER()],
         fasteners=[CAM_LOCK(6), GLIDE(4)],
         tools=[SCREWDRIVER, HAMMER],
         actions=[
             action("tighten", "", "end stretcher", "113434", "screwdriver", "clockwise",
                    "6x cam lock 113434 set into the stretchers and legs and turned clockwise"),
             action("insert", "", "leg", "117559", "hammer", "down",
                    "4x floor glide 117559 hammered into the foot of each leg"),
         ],
         final="complete table, upside down, with floor glides on the legs",
         unc=["Steps 22 and 23."]),
    page(17, "assembly_step",
         parts=[TABLETOP],
         fasteners=[STOP_SCREW(2)],
         tools=[SCREWDRIVER],
         actions=[
             action("insert", "", "tabletop", "105896", "screwdriver", "up",
                    "2x stop screw 105896 screwed in under the tabletop so the leaves can't slide off"),
         ],
         final="table turned upright; leaf locks opened; stop screws fitted",
         unc=["Steps 24 and 25: turn the table over, open the 2 leaf locks, fit the stop screws."]),
    page(18, "unknown", unc=["Info page: how to open the table and fold out the extension leaf."]),
    page(19, "unknown", unc=["Info page: how to pull the leaves apart and lock them again."]),
    page(20, "unknown", unc=["Back page; copyright only."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled NORDEN extendable table", (0.02, 0.2, 0.75, 0.6),
                          complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Tools, two people, soft floor, call IKEA if unsure", (0.05, 0.05, 0.95, 0.95),
                            parts=False, tools=True, action_="warning", complexity="low")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Fittings: dowels 101353 and 101350, cam bolts 118331, cam locks 113434, screws 114727, 105896 and 100325",
                (0.05, 0.05, 0.95, 0.3), ["101353", "101350", "118331", "113434", "114727", "105896", "100325"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Cross dowel 100535, threaded rod 100038, nut 100712, washer 100833",
                (0.05, 0.35, 0.95, 0.5), ["100535", "100038", "100712", "100833"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Corner bracket 118254 x4", (0.05, 0.58, 0.45, 0.92), ["118254", "4x"], complexity="low"),
        diagram("part_inventory", "Floor glide 117559 and metal angle plate 117841", (0.5, 0.55, 0.95, 0.92), ["117559", "117841"],
                parts=False, fast=True, complexity="low"),
    ], ["No part sizes printed."]),
    4: ("assembly_step", [
        diagram("exploded_view", "Step 1: corner brackets screwed to the long side rail ends", (0.05, 0.05, 0.95, 0.48),
                ["1", "118254", "100325"], fast=True, tools=True, action_="attach"),
        diagram("exploded_view", "Step 2: cam bolts into the long side rails", (0.05, 0.52, 0.95, 0.95),
                ["2", "118331"], fast=True, tools=True, action_="insert"),
    ], []),
    5: ("assembly_step", [
        diagram("exploded_view", "Step 3: cross rails pushed between the long side rails (arrows)", (0.05, 0.03, 0.95, 0.47),
                ["3", "101350"], fast=True, arrows=True, action_="insert"),
        diagram("assembly_view", "Step 4: cam locks set in and turned", (0.05, 0.5, 0.95, 0.95),
                ["4", "113434"], fast=True, tools=True, action_="tighten"),
    ], []),
    6: ("assembly_step", [
        diagram("exploded_view", "Step 5: guide rails and end rails on dowels", (0.05, 0.03, 0.95, 0.47),
                ["5", "101350"], fast=True, action_="insert"),
        diagram("assembly_view", "Step 6: screws through the corner brackets", (0.05, 0.5, 0.95, 0.95),
                ["6", "100325"], fast=True, tools=True, action_="tighten"),
    ], []),
    7: ("assembly_step", [
        diagram("assembly_view", "Step 7: tabletop leaves upside down, 2 leaf locks closed", (0.05, 0.03, 0.95, 0.55),
                ["7"], action_="flip"),
        diagram("exploded_view", "Step 8: slide runner rails screwed to the tabletop", (0.05, 0.58, 0.95, 0.95),
                ["8", "114727"], fast=True, action_="attach"),
    ], []),
    8: ("assembly_step", [diagram("assembly_view", "Step 9: frame lowered onto the tabletop and slid along the runners",
                                  (0.05, 0.03, 0.95, 0.95), ["9"], arrows=True, action_="slide", complexity="high")], []),
    9: ("assembly_step", [
        diagram("exploded_view", "Step 10: cross dowels and threaded rods into the legs", (0.05, 0.03, 0.95, 0.58),
                ["10", "100535", "100038"], fast=True, action_="insert"),
        diagram("exploded_view", "Step 11: cam bolts into the legs", (0.05, 0.62, 0.95, 0.95),
                ["11", "118331"], fast=True, action_="insert"),
    ], []),
    10: ("assembly_step", [
        diagram("assembly_view", "Step 12: metal angle plates screwed to the tabletop", (0.05, 0.03, 0.95, 0.48),
                ["12", "117841", "100325"], fast=True, tools=True, action_="attach"),
        diagram("assembly_view", "Step 13: first leg bolted into a corner bracket with washer and nut", (0.05, 0.5, 0.95, 0.95),
                ["13", "100833", "100712"], fast=True, tools=True, action_="tighten", complexity="high"),
    ], []),
    11: ("assembly_step", [
        diagram("exploded_view", "Step 14: cam bolts into the end stretchers", (0.05, 0.03, 0.95, 0.45),
                ["14", "118331"], fast=True, action_="insert"),
        diagram("exploded_view", "Step 15: long dowels into the stretcher ends", (0.05, 0.5, 0.95, 0.95),
                ["15", "101353"], fast=True, action_="insert"),
    ], []),
    12: ("assembly_step", [
        diagram("assembly_view", "Step 16: end stretcher onto the first leg", (0.05, 0.03, 0.95, 0.45), ["16"], arrows=True, action_="attach"),
        diagram("assembly_view", "Step 17: second leg bolted in", (0.05, 0.5, 0.95, 0.95), ["17", "100833", "100712"],
                fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
    ], []),
    13: ("assembly_step", [
        diagram("assembly_view", "Step 18: third leg bolted in", (0.05, 0.03, 0.95, 0.45), ["18", "100833", "100712"],
                fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
        diagram("assembly_view", "Step 19: long stretcher fitted by two people", (0.05, 0.5, 0.95, 0.95), ["19"],
                arrows=True, action_="attach", complexity="high"),
    ], []),
    14: ("assembly_step", [diagram("assembly_view", "Step 20: second end stretcher fitted", (0.05, 0.05, 0.95, 0.7), ["20"],
                                   arrows=True, action_="attach", complexity="high")], []),
    15: ("assembly_step", [diagram("assembly_view", "Step 21: last leg bolted in", (0.05, 0.05, 0.95, 0.95), ["21", "100833", "100712"],
                                   fast=True, tools=True, arrows=True, action_="attach", complexity="high")], []),
    16: ("assembly_step", [
        diagram("assembly_view", "Step 22: cam locks tightened", (0.05, 0.03, 0.95, 0.47), ["22", "113434"], fast=True, tools=True, action_="tighten"),
        diagram("assembly_view", "Step 23: floor glides hammered in", (0.05, 0.5, 0.95, 0.95), ["23", "117559"], fast=True, tools=True, action_="insert"),
    ], []),
    17: ("assembly_step", [
        diagram("final_product", "Step 24: table turned over, leaf locks opened", (0.05, 0.03, 0.95, 0.47), ["24"], arrows=True, action_="flip"),
        diagram("close_up", "Step 25: stop screws fitted", (0.05, 0.5, 0.95, 0.95), ["25", "105896"], fast=True, action_="insert"),
    ], []),
    18: ("unknown", [], ["Extension instructions."]),
    19: ("unknown", [], ["Extension instructions."]),
    20: ("unknown", [], ["Back page."]),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA NORDEN Extendable Table")
