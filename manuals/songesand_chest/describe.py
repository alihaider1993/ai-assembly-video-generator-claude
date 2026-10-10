"""Vision results for the IKEA SONGESAND chest of 6 drawers manual (36 pages).

The carcass is three upright panels (two sides and a divider) joined by front
and back rails at top and bottom, with a hardboard back, a metal brace and a
top. The six drawers are built from a separate booklet; here they are only
pushed in (step 43).

Run: python manuals/songesand_chest/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 161 x 48 cm chest, 92 cm high.
# Beams are length first: size=(length, thickness, height).
SIDE = lambda side: part("", f"{side} side panel", f"{side} side panel with three drawer runners inside", "panel", "wood", 1,
                         [("hole", 8, "rail and dowel holes"), ("hole", 9, "runner screw holes")], "center", size=(18, 470, 880))
DIVIDER = part("", "divider", "middle upright panel with drawer runners on both faces", "panel", "wood", 1,
               [("hole", 8, "rail holes"), ("hole", 18, "runner screw holes")], "center", size=(18, 450, 860))
RAIL = lambda name, qty=2: part("", name, f"{name}, one in each bay between the upright panels", "beam", "wood", qty,
                                [("hole", 4, "dowel and cam bolt holes at the ends")], "center", size=(770, 18, 60))
BACK = part("", "back panel", "two-part hardboard back panel", "panel", "fibreboard", 1, [], "center", size=(1580, 3, 860))
BRACE = part("158473", "back brace", "metal angle brace across the top of the back", "beam", "metal", 1,
             [("hole", 4, "screw holes")], "center", size=(1540, 20, 20))
TOP = part("", "top panel", "top panel with an overhanging moulded edge", "panel", "wood", 1,
           [("hole", 6, "cam bolt holes underneath")], "bottom", size=(1610, 480, 25))
RUNNER = lambda qty=12: part("158672", "drawer runner", "metal carcass drawer runner", "rail", "metal", qty,
                             [("hole", 3, "screw holes")], "center")
DRAWER = lambda qty=6: part("", "drawer front", "finished drawer (built from its own booklet), seen by its front", "panel", "wood", qty,
                            [], "center", size=(770, 18, 260))

PAGES = [
    page(1, "cover", final="SONGESAND chest of six drawers: two columns of three drawers under a top"),
    *[page(n, "warning", unc=["Safety and tip-over text. No assembly action."]) for n in (2, 3, 4, 5)],
    page(6, "warning", unc=["Tools and wall fixing advice."]),
    page(7, "parts_list", unc=["Soft surface; ask IKEA. Rails shown: 6x and 2x."]),
    page(8, "parts_list",
         fasteners=[fastener("101345", "wooden dowel", "dowel", "18x"), fastener("118331", "cam bolt", "bolt", "22x"),
                    fastener("146114", "runner screw", "screw", "36x"), fastener("119252", "cam lock", "cam", "18x"),
                    fastener("153548", "floor glide", "other", "6x"), fastener("105248", "brace screw", "screw", "4x"),
                    fastener("10093081", "back panel clip", "other", "18x"), fastener("109049", "back screw", "screw", "4x")],
         parts=[RUNNER(12)],
         unc=["Hardware bag 1; wall fixing kit drawn separately."]),
    page(9, "assembly_step",
         parts=[RAIL("top front rail"), RAIL("bottom front rail"), RAIL("top back rail"), RAIL("bottom back rail")],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 12)],
         actions=[action("insert", "", "top front rail", "101345", "", "inward",
                         "step 1: 12x wooden dowel 101345 into the ends of six rails")],
         final="rails with dowels",
         unc=["Top insets: this booklet builds the frame; the 6 drawers have their own booklet."]),
    page(10, "assembly_step",
         parts=[SIDE("left"), DIVIDER, SIDE("right"), RUNNER(12)],
         fasteners=[fastener("146114", "runner screw", "screw", 36)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "drawer runner", "left side panel", "146114", "cross head screwdriver", "clockwise",
                    "steps 2-3: 3x drawer runner screwed to the left side panel with runner screw 146114"),
             action("attach", "drawer runner", "divider", "146114", "cross head screwdriver", "clockwise",
                    "steps 2-3: 6x drawer runner screwed to both faces of the divider"),
             action("attach", "drawer runner", "right side panel", "146114", "cross head screwdriver", "clockwise",
                    "steps 2-3: 3x drawer runner screwed to the right side panel"),
         ],
         final="runners on the three upright panels"),
    page(11, "assembly_step", parts=[SIDE("left"), DIVIDER, SIDE("right")],
         fasteners=[fastener("118331", "cam bolt", "bolt", 8)],
         tools=[tool("cross head screwdriver")],
         actions=[action("insert", "", "divider", "118331", "cross head screwdriver", "clockwise",
                         "steps 4-5: cam bolts 118331 screwed into the edges of the panels")],
         final="cam bolts in the panels"),
    page(12, "assembly_step", parts=[SIDE("left"), DIVIDER],
         fasteners=[fastener("118331", "cam bolt", "bolt", 8)],
         tools=[tool("cross head screwdriver")],
         actions=[action("insert", "", "left side panel", "118331", "cross head screwdriver", "clockwise",
                         "steps 6-7: more cam bolts 118331 into the panel edges")],
         final="panels ready"),
    page(13, "assembly_step",
         parts=[RAIL("bottom front rail"), RAIL("bottom back rail"), SIDE("right")],
         fasteners=[fastener("153548", "floor glide", "other", 4)],
         actions=[
             action("insert", "", "bottom front rail", "153548", "", "inward",
                    "step 8: 2x floor glide 153548 into the underside of each bottom rail"),
             action("attach", "bottom front rail", "right side panel", "", "", "down",
                    "step 9: right side panel lying flat; bottom front rail stood on its cam bolt"),
         ],
         final="first rail standing on the right side panel",
         unc=["The carcass is built lying on its right side; rails drawn standing up run across the chest."]),
    page(14, "assembly_step",
         parts=[RAIL("top front rail"), RAIL("top back rail"), SIDE("right")],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 4)],
         actions=[
             action("insert", "", "top front rail", "101345", "", "down", "step 10: 4x wooden dowel 101345 into the top rails"),
             action("attach", "top front rail", "right side panel", "", "", "down",
                    "step 11: top front rail stood on the right side panel"),
         ],
         final="two rails on the right side panel"),
    page(15, "assembly_step",
         parts=[RAIL("top back rail"), RAIL("bottom back rail"), SIDE("right")],
         actions=[
             action("attach", "top back rail", "right side panel", "", "", "down", "step 12: top back rail stood on the right side panel"),
             action("attach", "bottom back rail", "right side panel", "", "", "down", "step 12: bottom back rail stood on the right side panel"),
         ],
         final="four rails standing on the right side panel"),
    page(16, "assembly_step",
         parts=[SIDE("right"), RAIL("bottom front rail")],
         fasteners=[fastener("119252", "cam lock", "cam", 3), fastener("105248", "brace screw", "screw", 2)],
         tools=[tool("flat screwdriver")],
         actions=[action("tighten", "bottom front rail", "right side panel", "119252", "flat screwdriver", "clockwise",
                         "steps 13-14: 3x cam lock 119252 turned in the rails; angle bracket 158473 screwed with 105248")],
         final="rails locked to the right side panel"),
    page(17, "assembly_step",
         parts=[DIVIDER, RAIL("top front rail"), RAIL("bottom front rail")],
         actions=[
             action("attach", "divider", "top front rail", "", "", "down", "steps 15-16: divider turned over and lowered onto the four rails"),
             action("attach", "divider", "bottom front rail", "", "", "down", "steps 15-16: divider on the bottom rails"),
         ],
         final="first bay closed by the divider"),
    page(18, "assembly_step",
         parts=[DIVIDER, RAIL("top back rail")],
         fasteners=[fastener("119252", "cam lock", "cam", 3), fastener("118331", "cam bolt", "bolt", 3)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("tighten", "divider", "top back rail", "119252", "flat screwdriver", "clockwise",
                    "step 17: 3x cam lock 119252 turned in the rails"),
             action("insert", "", "divider", "118331", "", "down", "step 18: 3x cam bolt 118331 into the top edge of the divider"),
         ],
         final="first bay locked"),
    page(19, "assembly_step", unc=["Step 19: the bay stood upright (curved arrow); lift by the panels, not the rails. Not a join."]),
    page(20, "assembly_step",
         parts=[DIVIDER, RAIL("top front rail"), RAIL("bottom front rail"), RAIL("top back rail"), RAIL("bottom back rail")],
         fasteners=[fastener("105248", "brace screw", "screw", 2)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "top front rail", "divider", "", "", "inward",
                    "steps 21-22: second set of top and bottom front rails pushed onto the divider's cam bolts"),
             action("attach", "top back rail", "divider", "", "", "inward",
                    "steps 21-22: second set of back rails pushed onto the divider"),
         ],
         final="rails of the second bay on the divider",
         unc=["Step 20: angle bracket screws 105248 (2x)."]),
    page(21, "assembly_step",
         parts=[SIDE("left"), DIVIDER, RAIL("top front rail"), RAIL("bottom front rail")],
         fasteners=[fastener("119252", "cam lock", "cam", 3)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("tighten", "top front rail", "divider", "119252", "flat screwdriver", "clockwise", "step 23: 3x cam lock 119252 turned"),
             action("attach", "left side panel", "top front rail", "", "", "inward",
                    "step 24: left side panel pushed onto the free ends of the second bay's rails"),
             action("attach", "left side panel", "bottom front rail", "", "", "inward", "step 24: left side panel onto the bottom rails"),
         ],
         final="carcass of three panels and eight rails"),
    page(22, "assembly_step",
         parts=[SIDE("left"), BACK, RAIL("top back rail")],
         fasteners=[fastener("119252", "cam lock", "cam", 3)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("tighten", "left side panel", "top back rail", "119252", "flat screwdriver", "clockwise", "step 25: 3x cam lock 119252 turned"),
             action("slide", "back panel", "left side panel", "", "", "inward",
                    "step 26: back panel slid into the grooves of the side panels from one end"),
         ],
         final="back panel slid in"),
    page(23, "assembly_step",
         parts=[BACK, RAIL("bottom back rail")],
         fasteners=[fastener("10093081", "back panel clip", "other", 8), fastener("153548", "floor glide", "other", 6)],
         actions=[
             action("insert", "", "back panel", "10093081", "", "down", "step 27: 8x back panel clip 10093081 with wedge 10093082"),
             action("insert", "", "bottom back rail", "153548", "", "inward", "step 28: 6x floor glide 153548 along the bottom edges"),
         ],
         final="back panel held; glides fitted"),
    page(24, "assembly_step",
         parts=[BRACE, SIDE("left"), SIDE("right")],
         actions=[
             action("place", "back brace", "left side panel", "", "", "down",
                    "step 30: metal back brace 158473 laid across the top back corner between the left side panel and right side panel"),
         ],
         final="brace in place",
         unc=["Step 29: carcass turned upright; not a join."]),
    page(25, "assembly_step",
         parts=[BRACE, SIDE("right"), TOP],
         fasteners=[fastener("105248", "brace screw", "screw", 4), fastener("118331", "cam bolt", "bolt", 6)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("tighten", "back brace", "right side panel", "105248", "cross head screwdriver", "clockwise",
                    "step 31: 2x and 2x brace screw 105248 through the back brace"),
             action("insert", "", "top panel", "118331", "cross head screwdriver", "clockwise", "step 32: 6x cam bolt 118331 into the top panel"),
         ],
         final="brace screwed; top panel with cam bolts"),
    page(26, "assembly_step", parts=[TOP], unc=["Step 33: wall fixing brackets screwed to the top panel's back edge (2x 109049, 100823)."]),
    page(27, "assembly_step",
         parts=[TOP, SIDE("left"), SIDE("right"), DIVIDER],
         fasteners=[fastener("101345", "wooden dowel", "dowel", 6)],
         actions=[
             action("insert", "", "left side panel", "101345", "", "down", "step 34: 6x wooden dowel 101345 into the tops of the panels"),
             action("attach", "top panel", "left side panel", "", "", "down", "step 35: top panel lowered onto the dowels"),
             action("attach", "top panel", "right side panel", "", "", "down", "step 35: top panel on the right side panel"),
             action("attach", "top panel", "divider", "", "", "down", "step 35: top panel on the divider"),
         ],
         final="top panel on"),
    page(28, "assembly_step",
         parts=[TOP, BACK, SIDE("left")],
         fasteners=[fastener("119252", "cam lock", "cam", 6), fastener("10093081", "back panel clip", "other", 10)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("tighten", "top panel", "left side panel", "119252", "flat screwdriver", "clockwise", "step 36: 6x cam lock 119252 turned"),
             action("insert", "", "back panel", "10093081", "", "inward", "step 37: 10x back panel clip 10093081 along the back"),
         ],
         final="top locked"),
    page(29, "assembly_step",
         parts=[BACK, BRACE],
         fasteners=[fastener("109049", "back screw", "screw", 4)],
         tools=[tool("cross head screwdriver")],
         actions=[action("tighten", "back panel", "back brace", "109049", "cross head screwdriver", "clockwise",
                         "step 38: 4x back screw 109049 through the back panel into the back brace")],
         final="carcass complete"),
    *[page(n, "assembly_step", unc=["Steps 39-42: wall fixing. The wall is not a part."]) for n in (30, 31, 32, 33)],
    page(34, "assembly_step",
         parts=[DRAWER(6), RUNNER(1)],
         actions=[action("slide", "drawer front", "drawer runner", "", "", "inward",
                         "step 43: 6x finished drawer put on the carcass runners and pushed in, repeat x6")],
         final="finished SONGESAND chest of six drawers",
         unc=["The drawers are assembled from the separate SONGESAND drawer booklet (2x)."]),
    page(35, "unknown", unc=["Drawer runner adjustment. No join."]),
    page(36, "unknown", unc=["Blank back page."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "SONGESAND chest of 6 drawers", (0.05, 0.1, 0.9, 0.6), complexity="low", conf=0.95)], []),
    **{n: ("warning", [diagram("warning", "Safety text", (0.03, 0.03, 0.97, 0.97), parts=False, complexity="low", action_="warning")], [])
       for n in (2, 3, 4, 5, 6)},
    7: ("parts_list", [diagram("part_inventory", "Rails", (0.03, 0.5, 0.97, 0.97), ["6x", "2x"], complexity="low")], []),
    8: ("parts_list", [diagram("part_inventory", "Hardware", (0.03, 0.03, 0.97, 0.97),
                               ["101345", "118331", "146114", "119252", "153548", "158672"], fast=True, complexity="medium")], []),
    **{n: ("assembly_step", [step_view(f"Steps on page {n}", [], "attach", fast=True, tools=True, arrows=True)], [])
       for n in range(9, 35)},
    35: ("unknown", [], []), 36: ("unknown", [], []),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA SONGESAND Chest of 6 Drawers")
