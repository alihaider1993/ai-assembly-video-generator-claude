"""Vision results for the IKEA NEIDEN bed frame manual (16 pages).

Run: python manuals/neiden_bed/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 140 x 200 cm bed. Beams are
# length first: size=(length, thickness, height).
POST = lambda side, end, h: part(
    "", f"{side} {end} post", f"{side} {end} leg, two pine boards joined with dowels and screws", "beam", "wood", 1,
    [("hole", 4, "bolt and screw holes")], "center", size=(55, 55, h))
HEAD_TOP = part("", "headboard top rail", "thick headboard top rail with rounded ends, two boards screwed together",
                "beam", "wood", 1, [("hole", 4, "dowel and lag screw holes")], "top", size=(1400, 40, 120))
HEAD_BOTTOM = part("", "headboard bottom rail", "headboard bottom rail between the headboard posts at mattress height",
                   "beam", "wood", 1, [("hole", 4, "dowel and lag screw holes"), ("hole", 2, "bolt holes for the centre rail")],
                   "center", size=(1400, 28, 115))
FOOT_RAIL = part("", "footboard rail", "foot rail between the footboard posts", "beam", "wood", 1,
                 [("hole", 4, "dowel and lag screw holes"), ("hole", 2, "bolt holes for the centre rail")],
                 "center", size=(1400, 28, 115))
SIDE_RAIL = lambda side: part("", f"{side} side rail", f"long {side} side rail with a ledge for the slats", "beam", "wood", 1,
                              [("hole", 4, "bolt holes at the ends")], "center", size=(2000, 28, 115))
CENTRE_RAIL = part("", "centre support rail", "long rail down the middle from the headboard to the foot rail",
                   "beam", "wood", 1, [("hole", 4, "dowel and bolt holes at the ends")], "center", size=(2000, 28, 70))
CROSS_RAIL = lambda side: part("", f"{side} cross rail", f"{side} short cross bar between the side rail and the centre rail",
                               "beam", "wood", 1, [("hole", 2, "bracket screw holes")], "center", size=(650, 30, 30))
BRACKET = lambda qty=4: part("10036350", "rail bracket", "metal hook bracket at each end of a cross rail", "bracket", "metal", qty,
                             [("hole", 3, "screw holes")], "center")

PAGES = [
    page(1, "cover", final="NEIDEN pine bed frame: headboard with one wide top rail, four square legs, side rails, slatted base"),
    page(2, "warning", unc=["Tools (flat and cross-head screwdrivers); soft surface; ask IKEA; two people."]),
    page(3, "parts_list",
         parts=[BRACKET(4)],
         fasteners=[fastener("120209", "long bolt", "bolt", "4x"), fastener("120208", "short bolt", "bolt", "4x"),
                    fastener("128745", "lag screw", "screw", "12x"), fastener("109594", "bracket wood screw", "screw", "8x"),
                    fastener("146899", "bracket screw", "screw", "4x"), fastener("128780", "steel dowel", "dowel", "4x"),
                    fastener("100217", "joint screw", "screw", "12x"), fastener("101357", "large wooden dowel", "dowel", "22x"),
                    fastener("101348", "small wooden dowel", "dowel", "10x"), fastener("100514", "barrel nut", "nut", "8x")],
         tools=[tool("allen key 100001"), tool("allen key 100092"), tool("extension bar 121030")],
         unc=["Info: allen key 100092 goes into extension bar 121030."]),
    page(4, "assembly_step",
         parts=[HEAD_TOP],
         fasteners=[fastener("101348", "small wooden dowel", "dowel", 2), fastener("100217", "joint screw", "screw", 4)],
         tools=[tool("allen key 100001")],
         actions=[
             action("insert", "", "headboard top rail", "101348", "", "down",
                    "step 1: 2x small wooden dowel 101348 into the lower board of the headboard top rail"),
             action("insert", "", "headboard top rail", "100217", "allen key 100001", "clockwise",
                    "steps 2-3: second board laid on and joined with 4x joint screw 100217"),
         ],
         final="headboard top rail made of two boards",
         unc=["The headboard top rail is two boards laminated together; described as one part."]),
    page(5, "assembly_step",
         parts=[HEAD_TOP, HEAD_BOTTOM, FOOT_RAIL,
                POST("left", "headboard", 640), POST("right", "headboard", 640),
                POST("left", "footboard", 300), POST("right", "footboard", 300)],
         fasteners=[fastener("101357", "large wooden dowel", "dowel", 10), fastener("101348", "small wooden dowel", "dowel", 8),
                    fastener("100217", "joint screw", "screw", 4)],
         tools=[tool("allen key 100001")],
         actions=[
             action("insert", "", "headboard bottom rail", "101357", "", "inward",
                    "step 4: 10x large wooden dowel 101357 into the ends of the headboard top rail, headboard bottom rail and footboard rail"),
             action("insert", "", "footboard rail", "101357", "", "inward", "step 4: large wooden dowel 101357 into the footboard rail"),
             action("insert", "", "left headboard post", "100217", "allen key 100001", "clockwise",
                    "steps 5-6: each leg's two boards joined with small wooden dowels 101348 and joint screws 100217"),
         ],
         final="rails with dowels; four legs made up",
         unc=["Each leg is a long board and a short spacer board; described as one part."]),
    page(6, "assembly_step",
         parts=[HEAD_TOP, HEAD_BOTTOM, FOOT_RAIL,
                POST("left", "headboard", 640), POST("right", "headboard", 640),
                POST("left", "footboard", 300), POST("right", "footboard", 300)],
         fasteners=[fastener("128745", "lag screw", "screw", 12)],
         tools=[tool("allen key 100092"), tool("extension bar 121030")],
         actions=[
             action("attach", "left headboard post", "headboard top rail", "128745", "allen key 100092", "clockwise",
                    "step 7: left headboard post screwed to the headboard top rail and headboard bottom rail with lag screws 128745"),
             action("attach", "right headboard post", "headboard top rail", "128745", "allen key 100092", "clockwise",
                    "step 7: right headboard post screwed to the headboard top rail"),
             action("attach", "left headboard post", "headboard bottom rail", "128745", "allen key 100092", "clockwise",
                    "step 7: left headboard post screwed to the headboard bottom rail"),
             action("attach", "right headboard post", "headboard bottom rail", "128745", "allen key 100092", "clockwise",
                    "step 7: right headboard post screwed to the headboard bottom rail"),
             action("attach", "left footboard post", "footboard rail", "128745", "allen key 100092", "clockwise",
                    "step 7: left footboard post screwed to the footboard rail"),
             action("attach", "right footboard post", "footboard rail", "128745", "allen key 100092", "clockwise",
                    "step 7: right footboard post screwed to the footboard rail, 12x lag screw 128745 in all"),
         ],
         final="headboard end and foot end assembled"),
    page(7, "assembly_step",
         parts=[POST("left", "headboard", 640), POST("right", "headboard", 640),
                POST("left", "footboard", 300), POST("right", "footboard", 300)],
         fasteners=[fastener("101357", "large wooden dowel", "dowel", 4)],
         actions=[action("insert", "", "left headboard post", "101357", "", "inward",
                         "step 8: 4x large wooden dowel 101357 into the inner faces of the four posts")],
         final="dowels ready for the side rails"),
    page(8, "assembly_step",
         parts=[SIDE_RAIL("left"), SIDE_RAIL("right"), POST("left", "headboard", 640), POST("right", "headboard", 640)],
         fasteners=[fastener("120209", "long bolt", "bolt", 2), fastener("100514", "barrel nut", "nut", 2)],
         tools=[tool("allen key 100001"), tool("flat screwdriver")],
         actions=[
             action("attach", "left side rail", "left headboard post", "120209", "allen key 100001", "clockwise",
                    "step 9: left side rail bolted to the left headboard post with long bolt 120209 into barrel nut 100514; 120208 crossed out"),
             action("attach", "right side rail", "right headboard post", "120209", "allen key 100001", "clockwise",
                    "step 9: right side rail bolted to the right headboard post, 2x long bolt 120209"),
         ],
         final="side rails standing out from the headboard"),
    page(9, "assembly_step",
         parts=[CENTRE_RAIL],
         fasteners=[fastener("128780", "steel dowel", "dowel", 4)],
         actions=[action("insert", "", "centre support rail", "128780", "", "inward",
                         "step 10: 2x steel dowel 128780 into each end of the centre support rail, fully in")],
         final="centre support rail with steel dowels"),
    page(10, "assembly_step",
         parts=[CENTRE_RAIL, HEAD_BOTTOM],
         fasteners=[fastener("120208", "short bolt", "bolt", 2), fastener("100514", "barrel nut", "nut", 2)],
         tools=[tool("allen key 100001")],
         actions=[action("attach", "centre support rail", "headboard bottom rail", "120208", "allen key 100001", "clockwise",
                         "step 11: centre support rail bolted to the middle of the headboard bottom rail with 2x short bolt 120208 and barrel nut 100514")],
         final="centre support rail fixed to the headboard"),
    page(11, "assembly_step",
         parts=[FOOT_RAIL, POST("left", "footboard", 300), POST("right", "footboard", 300), SIDE_RAIL("left"), SIDE_RAIL("right")],
         fasteners=[fastener("120209", "long bolt", "bolt", 2), fastener("100514", "barrel nut", "nut", 2)],
         tools=[tool("allen key 100001")],
         actions=[
             action("attach", "left side rail", "left footboard post", "120209", "allen key 100001", "clockwise",
                    "step 12: foot end fitted; left side rail bolted to the left footboard post with long bolt 120209 and barrel nut 100514"),
             action("attach", "right side rail", "right footboard post", "120209", "allen key 100001", "clockwise",
                    "step 12: right side rail bolted to the right footboard post, 2x long bolt 120209"),
         ],
         final="bed frame closed at the foot"),
    page(12, "assembly_step",
         parts=[CENTRE_RAIL, FOOT_RAIL],
         fasteners=[fastener("120208", "short bolt", "bolt", 2), fastener("100514", "barrel nut", "nut", 2)],
         tools=[tool("allen key 100001")],
         actions=[action("attach", "centre support rail", "footboard rail", "120208", "allen key 100001", "clockwise",
                         "step 13: centre support rail bolted to the footboard rail with 2x short bolt 120208 and barrel nut 100514")],
         final="centre support rail fixed at both ends"),
    page(13, "assembly_step",
         parts=[SIDE_RAIL("left"), SIDE_RAIL("right"), POST("left", "headboard", 640)],
         fasteners=[fastener("100217", "joint screw", "screw", 4)],
         tools=[tool("allen key 100001")],
         actions=[action("tighten", "left side rail", "left headboard post", "100217", "allen key 100001", "clockwise",
                         "step 14: 4x joint screw 100217 tightened at the ends of the side rails")],
         final="frame tightened"),
    page(14, "assembly_step",
         parts=[CROSS_RAIL("left"), CROSS_RAIL("right"), BRACKET(4), SIDE_RAIL("left"), SIDE_RAIL("right"), CENTRE_RAIL],
         fasteners=[fastener("146899", "bracket screw", "screw", 4), fastener("109594", "bracket wood screw", "screw", 8)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "rail bracket", "left cross rail", "146899", "cross head screwdriver", "clockwise",
                    "step 15: rail bracket 10036350 screwed to each end of the left cross rail with bracket screw 146899"),
             action("attach", "rail bracket", "right cross rail", "146899", "cross head screwdriver", "clockwise",
                    "step 15: rail bracket screwed to each end of the right cross rail; 4x in all"),
             action("attach", "left cross rail", "left side rail", "109594", "cross head screwdriver", "down",
                    "step 16: left cross rail hooked between the left side rail and the centre support rail, brackets screwed with bracket wood screw 109594"),
             action("attach", "left cross rail", "centre support rail", "109594", "cross head screwdriver", "down",
                    "step 16: left cross rail bracket screwed to the centre support rail"),
             action("attach", "right cross rail", "right side rail", "109594", "cross head screwdriver", "down",
                    "step 16: right cross rail hooked between the right side rail and the centre support rail"),
             action("attach", "right cross rail", "centre support rail", "109594", "cross head screwdriver", "down",
                    "step 16: right cross rail bracket screwed to the centre support rail, 8x screw 109594 in all"),
         ],
         final="cross rails across the middle of the bed"),
    page(15, "assembly_step",
         unc=["Info: with a sprung slatted base use no dowels; with a plain slatted base (not included) continue to page 16."]),
    page(16, "assembly_step",
         parts=[SIDE_RAIL("left"), SIDE_RAIL("right")],
         fasteners=[fastener("101357", "large wooden dowel", "dowel", 8)],
         actions=[action("insert", "", "left side rail", "101357", "", "down",
                         "step 17: 8x large wooden dowel 101357 into the tops of the side rails and centre rail as slat stops")],
         final="finished NEIDEN bed frame; slatted base (not included) rolled out on it",
         unc=["The slatted base is sold separately and not described as a part."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "NEIDEN bed frame", (0.05, 0.1, 0.95, 0.9), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Tools and advice", (0.03, 0.03, 0.97, 0.97), parts=False, tools=True, complexity="low", action_="warning")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Bolts, screws, dowels, barrel nuts", (0.03, 0.05, 0.75, 0.5),
                ["120209", "120208", "128745", "109594", "146899", "128780", "100217", "101357", "101348", "100514"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Rail bracket 4x", (0.75, 0.05, 0.97, 0.25), ["10036350", "4x"], complexity="low"),
        diagram("part_inventory", "Allen keys and extension bar", (0.2, 0.5, 0.97, 0.7), ["100001", "100092", "121030"], parts=False, tools=True, complexity="low"),
    ], []),
    4: ("assembly_step", [step_view("Headboard top rail boards joined", ["1", "2", "3", "2x", "4x", "101348", "100217"], "attach", fast=True, tools=True)], []),
    5: ("assembly_step", [step_view("Dowels in rails; legs made up", ["4", "5", "6", "10x", "8x", "4x", "101357", "101348", "100217"], "insert", fast=True)], []),
    6: ("assembly_step", [step_view("Posts screwed to the head and foot rails", ["7", "12x", "128745"], "attach", fast=True, tools=True)], []),
    7: ("assembly_step", [step_view("Dowels in the posts", ["8", "4x", "101357"], "insert", fast=True)], []),
    8: ("assembly_step", [step_view("Side rails bolted to the headboard posts", ["9", "2x", "120209", "100514"], "attach", fast=True, tools=True)], []),
    9: ("assembly_step", [step_view("Steel dowels in the centre rail", ["10", "2x", "128780"], "insert", fast=True)], []),
    10: ("assembly_step", [step_view("Centre rail bolted to the headboard bottom rail", ["11", "2x", "120208", "100514"], "attach", fast=True, tools=True)], []),
    11: ("assembly_step", [step_view("Foot end bolted on", ["12", "2x", "120209", "100514"], "attach", fast=True, tools=True)], []),
    12: ("assembly_step", [step_view("Centre rail bolted to the foot rail", ["13", "1x", "120208"], "attach", fast=True, tools=True)], []),
    13: ("assembly_step", [step_view("Joint screws tightened", ["14", "4x", "100217"], "tighten", fast=True, tools=True)], []),
    14: ("assembly_step", [step_view("Brackets on the cross rails; cross rails fitted", ["15", "16", "4x", "146899", "109594", "10036350"], "attach", fast=True, tools=True)], []),
    15: ("assembly_step", [step_view("Slatted base options", ["8x", "101357", "16"], "none", parts=False)], []),
    16: ("assembly_step", [step_view("Slat stop dowels; slatted base laid on", ["17", "8x", "101357"], "insert", fast=True)], []),
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA NEIDEN Bed Frame")
