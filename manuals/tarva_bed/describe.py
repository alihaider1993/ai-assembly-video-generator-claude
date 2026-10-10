"""Vision results for the IKEA TARVA bed frame manual (24 pages, 25 steps).

The manual prints no wooden parts list and no sizes. Parts are named by where
they sit in the finished bed; sizes are estimated for the 160 x 200 cm frame.
Fittings use the IKEA article numbers printed beside them.

Run: python manuals/tarva_bed/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

PINE = "solid pine"


def head_post(side):
    return part("1" if side == "left" else "2", f"{side} headboard post", f"tall square {PINE} post, dowel holes up the inner face and two guide pins near the bottom",
                "beam", "wood", 1, [("hole", 11, "dowel holes for the headboard rails"), ("hole", 2, "bolt holes for the side rail")],
                "left" if side == "left" else "right", size=(55, 55, 920))


def foot_post(side):
    return part("3" if side == "left" else "4", f"{side} footboard post", f"short square {PINE} leg with dowel holes, guide pins and bolt holes",
                "beam", "wood", 1, [("hole", 2, "dowel holes for the footboard rail"), ("hole", 2, "bolt holes for the side rail")],
                "left" if side == "left" else "right", size=(55, 55, 380))


TOP_RAIL = part("5", "headboard top rail", f"long square {PINE} bar with a cam stud and a dowel in the middle", "beam", "wood", 1,
                [("hole", 2, "dowel holes in each end"), ("hole", 2, "cam stud and dowel holes in the middle")], "top",
                size=(1500, 45, 45))
BOTTOM_RAIL = part("6", "headboard bottom rail", f"wide flat {PINE} board with dowel holes in the ends and a bolt hole in the middle",
                   "panel", "wood", 1, [("hole", 3, "dowel holes in each end"), ("hole", 1, "bolt hole in the middle")], "bottom",
                   size=(1500, 22, 140))
UPRIGHT = part("7", "centre upright", f"flat {PINE} board with a cam lock at the top and a bolt at the bottom, dowel holes down both edges",
               "panel", "wood", 1, [("hole", 8, "dowel holes for the short headboard rails")], "center", size=(110, 22, 560))
LEFT_RAILS = lambda qty=4: part("8", "left headboard rail", f"short square {PINE} bar with two dowel holes in each end", "beam", "wood", qty,
                                [("hole", 4, "two dowel holes in each end")], "left", size=(700, 40, 40))
RIGHT_RAILS = lambda qty=4: part("9", "right headboard rail", f"short square {PINE} bar with two dowel holes in each end", "beam", "wood", qty,
                                 [("hole", 4, "two dowel holes in each end")], "right", size=(700, 40, 40))
FOOT_RAIL = part("10", "footboard rail", f"wide flat {PINE} board with dowels and barrel nut holes at both ends", "panel", "wood", 1,
                 [("hole", 4, "dowel holes in the ends"), ("hole", 2, "barrel nut holes")], "bottom", size=(1600, 28, 140))
LEFT_SIDE = part("11", "left side rail", f"long flat {PINE} board with dowel and barrel nut holes at both ends", "panel", "wood", 1,
                 [("hole", 4, "dowel holes"), ("hole", 4, "barrel nut holes"), ("hole", 8, "screw holes for the slat support rail")],
                 "left", size=(2000, 28, 140))
RIGHT_SIDE = part("12", "right side rail", f"long flat {PINE} board with dowel and barrel nut holes at both ends", "panel", "wood", 1,
                  [("hole", 4, "dowel holes"), ("hole", 4, "barrel nut holes"), ("hole", 8, "screw holes for the slat support rail")],
                  "right", size=(2000, 28, 140))
CENTRE_RAIL = part("13", "centre support rail", "long wooden beam with angled ends and screw holes near each end", "beam", "wood", 1,
                   [("hole", 4, "screw holes at the ends")], "center", size=(2000, 45, 70))
HEAD_HOLDER = part("116791", "head centre holder", "bent metal plate with a cradle for the centre rail and two screw holes",
                   "bracket", "metal", 1, [("hole", 2, "screw holes")], "center", size=(110, 60, 40))
END_HOLDER = part("116791b", "end centre holder", "bent metal plate with a cradle for the centre rail and two screw holes",
                  "bracket", "metal", 1, [("hole", 2, "screw holes")], "center", size=(110, 60, 40))
SLEEVE = part("14", "centre sleeve", "metal saddle that slides along the centre rail, with hooks on both sides", "block", "metal", 1,
              [("slot", 2, "hooks for the cross rails")], "center", size=(70, 80, 75))
LEFT_LEDGE = part("114290", "left side ledge", "long metal strip with a row of holes and slots", "beam", "metal", 1,
                  [("hole", 8, "screw slots")], "left", size=(1950, 20, 25))
RIGHT_LEDGE = part("114291", "right side ledge", "long metal strip with a row of holes and slots", "beam", "metal", 1,
                   [("hole", 8, "screw slots")], "right", size=(1950, 20, 25))
LEFT_CROSS = part("124401", "left cross rail", "metal bar with a hook at one end and a screw tab at the other", "beam", "metal", 1,
                  [("hole", 1, "screw hole in the end tab")], "left", size=(740, 25, 25))
RIGHT_CROSS = part("124402", "right cross rail", "metal bar with a hook at one end and a screw tab at the other", "beam", "metal", 1,
                   [("hole", 1, "screw hole in the end tab")], "right", size=(740, 25, 25))

PIN = lambda qty: fastener("128780", "guide pin", "dowel", qty)
DOWEL = lambda qty: fastener("101350", "wooden dowel", "dowel", qty)
BOLT_SHORT = lambda qty: fastener("105105", "connector bolt", "bolt", qty)
CAM_STUD = lambda qty: fastener("115312", "cam stud", "screw", qty)
SLAT_HOLDER = lambda qty: fastener("191315", "slat holder", "clip", qty)
SCREW_SMALL = lambda qty: fastener("117327", "short machine screw", "screw", qty)
SCREW_HOLDER = lambda qty: fastener("105163", "slat holder screw", "screw", qty)
SLEEVE_NUT = lambda qty: fastener("100600", "sleeve nut", "nut", qty)
WOOD_SCREW = lambda qty: fastener("105307", "wood screw", "screw", qty)
BOLT_LONG = lambda qty: fastener("105330", "long bolt", "bolt", qty)
CAM_LOCK = lambda qty: fastener("103430", "cam lock", "cam", qty)
BARREL = lambda qty: fastener("100514", "barrel nut", "nut", qty)
GLIDE = lambda qty: fastener("102370", "floor glide", "glide", qty)

KEY_LARGE = tool("allen key 100001")
KEY_SMALL = tool("allen key 100002")
FLAT_DRIVER = tool("flat screwdriver")
CROSS_DRIVER = tool("cross-head screwdriver")
HAMMER = tool("hammer")

HEAD_PARTS = [head_post("left"), head_post("right"), TOP_RAIL, BOTTOM_RAIL, UPRIGHT, LEFT_RAILS(), RIGHT_RAILS()]

PAGES = [
    page(1, "cover",
         final="TARVA bed frame: tall headboard of horizontal rails split by a centre upright, low side and foot rails on four square legs, centre support rail",
         unc=["Cover page; product name TARVA and IKEA logo."]),
    page(2, "parts_list",
         fasteners=[PIN(8), DOWEL(43), BOLT_SHORT(1), CAM_STUD(1), SLAT_HOLDER(8), SCREW_SMALL(4), SCREW_HOLDER(8),
                    SLEEVE_NUT(1), WOOD_SCREW(20)],
         tools=[FLAT_DRIVER, CROSS_DRIVER, HAMMER],
         unc=["Tools needed: flat and cross-head screwdrivers and a hammer. Safety advice drawings.",
              "No wooden parts list and no sizes are printed; sizes are estimated for a 160 x 200 cm frame."]),
    page(3, "parts_list",
         parts=[HEAD_HOLDER, END_HOLDER, SLEEVE, LEFT_CROSS, RIGHT_CROSS, LEFT_LEDGE, RIGHT_LEDGE],
         fasteners=[BOLT_LONG(14), CAM_LOCK(1), BARREL(14), GLIDE(4)],
         tools=[KEY_LARGE, KEY_SMALL],
         unc=["Metal parts: 2x centre holder 116791, 1x sleeve, 2x cross rail 124401/124402, 2x slat support rail 114290/114291.",
              "Two allen keys 100001 and 100002 supplied."]),
    page(4, "assembly_step",
         parts=[TOP_RAIL],
         fasteners=[CAM_STUD(1), DOWEL(1)],
         tools=[CROSS_DRIVER],
         actions=[
             action("insert", "", "headboard top rail", "115312", "cross-head screwdriver", "down",
                    "step 1: 1x cam stud 115312 screwed into the middle of headboard top rail"),
             action("insert", "", "headboard top rail", "101350", "", "down",
                    "step 2: 1x wooden dowel 101350 pushed in beside the cam stud in headboard top rail"),
         ],
         final="headboard top rail with a cam stud and a dowel in the middle",
         unc=["Steps 1 and 2."]),
    page(5, "assembly_step",
         parts=[TOP_RAIL, UPRIGHT],
         fasteners=[CAM_LOCK(1)],
         tools=[FLAT_DRIVER],
         actions=[
             action("attach", "headboard top rail", "centre upright", "103430", "flat screwdriver", "inward",
                    "step 3: headboard top rail joined to the end of centre upright on the cam stud and locked with 1x cam lock 103430"),
         ],
         final="centre upright standing off the middle of the top rail in a T",
         unc=["Step 3. The T is then turned over (curved arrow); that is not a join."]),
    page(6, "assembly_step",
         parts=[TOP_RAIL, UPRIGHT, BOTTOM_RAIL],
         fasteners=[BOLT_SHORT(1), SLEEVE_NUT(1)],
         tools=[KEY_LARGE, KEY_SMALL],
         actions=[
             action("attach", "headboard bottom rail", "centre upright", "105105", "allen key 100001", "inward",
                    "step 4: headboard bottom rail bolted to the end of centre upright with 1x connector bolt 105105 and sleeve nut 100600"),
         ],
         final="headboard frame: top rail and bottom rail joined by the centre upright",
         unc=["Step 4. Insets: the bottom rail's marked face and holes must point the right way."]),
    page(7, "assembly_step",
         parts=[UPRIGHT, LEFT_RAILS(4), RIGHT_RAILS(4), head_post("left"), head_post("right"), foot_post("left"), foot_post("right")],
         fasteners=[DOWEL(8), PIN(8)],
         tools=[HAMMER],
         actions=[
             action("attach", "left headboard rail", "centre upright", "101350", "", "inward",
                    "step 5: four left headboard rails pushed onto wooden dowels 101350 in the left edge of centre upright"),
             action("attach", "right headboard rail", "centre upright", "101350", "", "inward",
                    "step 5: four right headboard rails pushed onto wooden dowels 101350 in the right edge of centre upright"),
             action("insert", "", "left headboard post", "128780", "hammer", "down",
                    "step 6: guide pins 128780 hammered into left headboard post, 20 mm left standing, repeat x2"),
             action("insert", "", "left footboard post", "128780", "hammer", "down",
                    "step 6: guide pins 128780 hammered into left footboard post, 20 mm left standing, repeat x2"),
         ],
         final="headboard rails fitted either side of the centre upright; guide pins in all four posts",
         unc=["Steps 5 and 6. Step 6 shows 8x guide pins: two in each of the four posts."]),
    page(8, "assembly_step",
         parts=[head_post("left"), head_post("right"), LEFT_RAILS(4), RIGHT_RAILS(4), TOP_RAIL, BOTTOM_RAIL],
         fasteners=[DOWEL(22), BOLT_LONG(4), BARREL(4)],
         tools=[KEY_LARGE, FLAT_DRIVER],
         actions=[
             action("insert", "", "left headboard rail", "101350", "", "inward",
                    "step 7: 22x wooden dowels 101350 pushed into the outer ends of the headboard rails, top rail and bottom rail"),
             action("attach", "left headboard post", "left headboard rail", "105330", "allen key 100001", "inward",
                    "step 7: left headboard post pushed onto the dowels in the outer ends of the left headboard rail, repeat x4"),
             action("attach", "left headboard post", "headboard top rail", "105330", "allen key 100001", "inward",
                    "step 8: left headboard post bolted to the end of headboard top rail with long bolt 105330 into barrel nut 100514"),
             action("attach", "left headboard post", "headboard bottom rail", "105330", "allen key 100001", "inward",
                    "step 8: left headboard post bolted to the end of headboard bottom rail with long bolt 105330 into barrel nut 100514"),
             action("attach", "right headboard post", "right headboard rail", "105330", "allen key 100001", "inward",
                    "step 7: right headboard post pushed onto the dowels in the outer ends of the right headboard rail, repeat x4"),
             action("attach", "right headboard post", "headboard top rail", "105330", "allen key 100001", "inward",
                    "step 8: right headboard post bolted to the end of headboard top rail with long bolt 105330 into barrel nut 100514"),
             action("attach", "right headboard post", "headboard bottom rail", "105330", "allen key 100001", "inward",
                    "step 8: right headboard post bolted to the end of headboard bottom rail with long bolt 105330 into barrel nut 100514"),
         ],
         final="complete headboard lying flat: two posts with the top rail, eight short rails and the bottom rail between them",
         unc=["Steps 7 and 8. Step 8 shows 4x barrel nut 100514 and four long bolts, two per post."]),
    page(9, "assembly_step",
         parts=[FOOT_RAIL, foot_post("left"), foot_post("right")],
         fasteners=[DOWEL(4), BOLT_LONG(2), BARREL(2)],
         tools=[KEY_LARGE, FLAT_DRIVER],
         actions=[
             action("insert", "", "footboard rail", "101350", "", "inward",
                    "step 9: 4x wooden dowels 101350 pushed into both ends of footboard rail"),
             action("attach", "left footboard post", "footboard rail", "105330", "allen key 100001", "inward",
                    "step 10: left footboard post bolted to footboard rail with long bolt 105330 into barrel nut 100514"),
             action("attach", "right footboard post", "footboard rail", "105330", "allen key 100001", "inward",
                    "step 10: right footboard post bolted to footboard rail with long bolt 105330 into barrel nut 100514"),
         ],
         final="footboard: wide foot rail between two short posts, lying beside the headboard",
         unc=["Steps 9 and 10. Step 10 shows 2x barrel nut 100514."]),
    page(10, "assembly_step",
         parts=[head_post("left"), head_post("right"), foot_post("left"), foot_post("right")],
         fasteners=[GLIDE(4)],
         tools=[HAMMER],
         actions=[
             action("insert", "", "left headboard post", "102370", "hammer", "up",
                    "step 11: floor glide 102370 hammered into the bottom of left headboard post"),
             action("insert", "", "right headboard post", "102370", "hammer", "up",
                    "step 11: floor glide 102370 hammered into the bottom of right headboard post"),
             action("insert", "", "left footboard post", "102370", "hammer", "up",
                    "step 11: floor glide 102370 hammered into the bottom of left footboard post"),
             action("insert", "", "right footboard post", "102370", "hammer", "up",
                    "step 11: floor glide 102370 hammered into the bottom of right footboard post"),
         ],
         final="glides under all four posts",
         unc=["Step 11. 4x glides, one per post."]),
    page(11, "assembly_step",
         parts=[BOTTOM_RAIL, FOOT_RAIL, HEAD_HOLDER, END_HOLDER],
         fasteners=[WOOD_SCREW(4)],
         tools=[CROSS_DRIVER],
         actions=[
             action("attach", "head centre holder", "headboard bottom rail", "105307", "cross-head screwdriver", "inward",
                    "step 12: head centre holder screwed to the middle of headboard bottom rail with 2x wood screw 105307"),
             action("attach", "end centre holder", "footboard rail", "105307", "cross-head screwdriver", "inward",
                    "step 12: end centre holder screwed to the middle of footboard rail with 2x wood screw 105307"),
         ],
         final="a centre holder in the middle of the headboard and of the foot rail",
         unc=["Step 12. Inset: the holder's cradle faces up."]),
    page(12, "assembly_step",
         parts=[foot_post("left"), foot_post("right"), LEFT_SIDE, RIGHT_SIDE, FOOT_RAIL],
         actions=[
             action("attach", "left side rail", "left footboard post", "", "", "inward",
                    "step 13: left side rail pushed onto the guide pins of left footboard post (two people)"),
             action("attach", "right side rail", "right footboard post", "", "", "inward",
                    "step 13: right side rail pushed onto the guide pins of right footboard post"),
         ],
         final="footboard standing with both side rails pushed onto its posts",
         unc=["Step 13. Insets: the side rails' holes face inwards; two people."]),
    page(13, "assembly_step",
         parts=[foot_post("left"), foot_post("right"), LEFT_SIDE, RIGHT_SIDE, head_post("left"), head_post("right")],
         fasteners=[BOLT_LONG(4), BARREL(4)],
         tools=[KEY_LARGE, FLAT_DRIVER],
         actions=[
             action("tighten", "left side rail", "left footboard post", "105330", "allen key 100001", "inward",
                    "step 14: left side rail bolted to left footboard post with 2x long bolt 105330 into barrel nuts 100514"),
             action("tighten", "right side rail", "right footboard post", "105330", "allen key 100001", "inward",
                    "step 14: right side rail bolted to right footboard post with 2x long bolt 105330 into barrel nuts 100514"),
             action("attach", "left headboard post", "left side rail", "", "", "inward",
                    "step 15: headboard pushed onto the head end of left side rail on the guide pins (two people)"),
             action("attach", "right headboard post", "right side rail", "", "", "inward",
                    "step 15: headboard pushed onto the head end of right side rail on the guide pins"),
         ],
         final="bed frame standing: headboard, two side rails and footboard",
         unc=["Steps 14 and 15. The headboard is fitted as one unit."]),
    page(14, "assembly_step",
         parts=[head_post("left"), head_post("right"), LEFT_SIDE, RIGHT_SIDE],
         fasteners=[BOLT_LONG(4), BARREL(4)],
         tools=[KEY_LARGE, FLAT_DRIVER],
         actions=[
             action("tighten", "left side rail", "left headboard post", "105330", "allen key 100001", "inward",
                    "step 16: left side rail bolted to left headboard post with 2x long bolt 105330 into barrel nuts 100514"),
             action("tighten", "right side rail", "right headboard post", "105330", "allen key 100001", "inward",
                    "step 16: right side rail bolted to right headboard post with 2x long bolt 105330 into barrel nuts 100514"),
         ],
         final="frame bolted at all four corners",
         unc=["Step 16."]),
    page(15, "assembly_step",
         parts=[LEFT_SIDE, RIGHT_SIDE, LEFT_LEDGE, RIGHT_LEDGE],
         fasteners=[WOOD_SCREW(16)],
         tools=[CROSS_DRIVER],
         actions=[
             action("attach", "left side ledge", "left side rail", "105307", "cross-head screwdriver", "inward",
                    "step 17: left side ledge screwed along the inside of left side rail with 8x wood screw 105307"),
             action("attach", "right side ledge", "right side rail", "105307", "cross-head screwdriver", "inward",
                    "step 17: right side ledge screwed along the inside of right side rail with 8x wood screw 105307"),
         ],
         final="metal slat support rails along the inside of both side rails",
         unc=["Step 17: 16x wood screws in all."]),
    page(16, "assembly_step",
         parts=[CENTRE_RAIL, SLEEVE],
         actions=[
             action("slide", "centre sleeve", "centre support rail", "", "", "along",
                    "step 18: centre sleeve slid along centre support rail to its middle"),
         ],
         final="centre support rail with the sleeve at its middle",
         unc=["Step 18."]),
    page(17, "assembly_step",
         parts=[CENTRE_RAIL, HEAD_HOLDER, END_HOLDER, BOTTOM_RAIL, FOOT_RAIL],
         actions=[
             action("place", "centre support rail", "headboard bottom rail", "", "", "down",
                    "step 19: head end of centre support rail laid into head centre holder"),
             action("place", "centre support rail", "footboard rail", "", "", "down",
                    "step 20: other end of centre support rail lowered into end centre holder"),
         ],
         final="centre support rail running from headboard to footboard down the middle",
         unc=["Steps 19 and 20."]),
    page(18, "assembly_step",
         parts=[LEFT_CROSS, LEFT_SIDE, CENTRE_RAIL],
         fasteners=[SCREW_SMALL(1)],
         tools=[CROSS_DRIVER],
         actions=[
             action("attach", "left cross rail", "left side rail", "117327", "cross-head screwdriver", "down",
                    "step 21: left cross rail screwed to left side ledge on left side rail with 1x short machine screw 117327"),
         ],
         final="one cross rail fixed to the left side, its other end lying on the centre support rail",
         unc=["Step 21. Box: 2x cross rail, slide the hook end out."]),
    page(19, "assembly_step",
         parts=[LEFT_CROSS, SLEEVE, CENTRE_RAIL],
         actions=[
             action("attach", "left cross rail", "centre sleeve", "", "", "down",
                    "step 22: hook of left cross rail dropped into the centre sleeve on centre support rail"),
         ],
         final="cross rail hooked into the sleeve",
         unc=["Step 22. The cross rails must be straight across, not angled."]),
    page(20, "assembly_step",
         parts=[RIGHT_CROSS, RIGHT_SIDE, SLEEVE],
         fasteners=[SCREW_SMALL(1)],
         tools=[CROSS_DRIVER],
         actions=[
             action("attach", "right cross rail", "right side rail", "117327", "cross-head screwdriver", "down",
                    "step 23: right cross rail hooked into centre sleeve and screwed to right side ledge on right side rail with 1x short machine screw 117327"),
         ],
         final="two cross rails from the side rails to the sleeve in the middle",
         unc=["Step 23."]),
    page(21, "assembly_step",
         parts=[CENTRE_RAIL, HEAD_HOLDER, END_HOLDER],
         fasteners=[SCREW_SMALL(2)],
         tools=[CROSS_DRIVER],
         actions=[
             action("tighten", "centre support rail", "head centre holder", "117327", "cross-head screwdriver", "down",
                    "step 24: centre support rail screwed into head centre holder with short machine screw 117327"),
             action("tighten", "centre support rail", "end centre holder", "117327", "cross-head screwdriver", "down",
                    "step 24: centre support rail screwed into end centre holder with short machine screw 117327"),
         ],
         final="finished bed frame with centre support",
         unc=["Step 24."]),
    page(22, "info",
         final="finished frame; a slatted base or slats are laid in from above",
         unc=["Information only: bed base and slats are sold separately; slat holders and their screws are not used with this kind of base."]),
    page(23, "info",
         final="slat holders can be screwed onto the rails for roll-out slat bases",
         unc=["Step 25 (info box): 8x slat holders 191315 with screws 105163, only for roll-out slat bases sold separately; not animated."]),
    page(24, "blank", unc=["Blank back page."]),
]

DIAGRAMS = {
    2: ("parts_list", [
        diagram("part_inventory", "Fittings: 8x guide pin 128780, 43x dowel 101350, 1x bolt 105105, 1x cam stud 115312, 8x slat holder 191315, "
                "4x screw 117327, 8x screw 105163, 1x sleeve nut 100600, 20x wood screw 105307", (0.05, 0.75, 0.95, 0.95),
                ["8x", "43x", "1x", "8x", "4x", "20x"], parts=False, fast=True),
    ], []),
    3: ("parts_list", [
        diagram("part_inventory", "Metal parts: 2x holder 116791, 1x sleeve, 2x cross rail 124401, 2x slat support rail 114290; "
                "14x bolt 105330, allen keys, 4x glide 102370, 1x cam lock 103430, 14x barrel nut 100514", (0.02, 0.02, 0.98, 0.98),
                ["116791", "124401", "114290", "2x", "1x", "14x", "4x"], fast=True, tools=True),
    ], []),
    7: ("assembly_step", [
        diagram("exploded_view", "Short headboard rails pushed onto dowels either side of the centre upright", (0.05, 0.05, 0.95, 0.5),
                ["8x", "101350"], fast=True, arrows=True, action_="attach", complexity="high"),
        diagram("close_up", "Guide pins hammered into the four posts, 20 mm standing", (0.05, 0.52, 0.95, 0.95),
                ["8x", "128780"], fast=True, tools=True, action_="insert"),
    ], []),
    8: ("assembly_step", [
        diagram("exploded_view", "Headboard posts onto the rail ends with 22 dowels, then bolted with barrel nuts", (0.05, 0.05, 0.95, 0.95),
                ["22x", "4x", "105330", "100514"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
    ], []),
    12: ("assembly_step", [
        diagram("assembly_view", "Two people push the side rails onto the footboard posts", (0.05, 0.1, 0.95, 0.9),
                [], arrows=True, action_="attach"),
    ], []),
    13: ("assembly_step", [
        diagram("assembly_view", "Side rails bolted to the foot posts; headboard pushed on", (0.05, 0.05, 0.95, 0.95),
                ["4x", "105330", "100514"], fast=True, tools=True, arrows=True, action_="attach", complexity="high"),
    ], []),
    23: ("assembly_step", [
        diagram("close_up", "Slat holders screwed onto the rails", (0.05, 0.05, 0.5, 0.45),
                ["8x", "191315", "105163"], fast=True, action_="attach"),
        diagram("assembly_view", "Finished frame with slat holders", (0.05, 0.5, 0.95, 0.95), [], action_="none"),
    ], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA TARVA Bed Frame")
