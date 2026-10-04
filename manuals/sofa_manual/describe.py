"""Vision results for the IKEA KIVIK chaise longue manual (16 pages).

A chaise longue section fitted to the end of an existing KIVIK sofa: four
feet go under the chaise frame, the sofa's end armrest comes off, a
connecting rail and a joining rail are fixed to the sofa's end, the armrest
is refitted to the chaise's outer side with two corner brackets and a clamp
bracket, the chaise is hooked onto the sofa, and the seat and back cushions
go on. The manual prints no sizes; they are estimated from the drawings and
the usual size of these pieces (chaise about 900 x 1630, sofa section about
1900 x 950, seat height about 450).

Run: python manuals/sofa_manual/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# The sofa's side outline (y front to back, z up, mm): seat at the front,
# backrest leaning back at the rear.
SOFA_PROFILE = {"path": [(0, 0), (950, 0), (950, 830), (760, 830), (690, 450), (0, 450)], "closed": True}
SOFA = part("", "sofa section", "existing upholstered KIVIK 2-seat sofa section with its backrest, laid on its back, its end armrest taken off",
            "frame", "fabric", 1, [("hole", 4, "threaded studs and holes in the end of the base frame")], "left",
            size=(1900, 950, 830), profile=SOFA_PROFILE)
CHAISE = part("", "chaise frame", "long upholstered chaise longue base frame, spring base open underneath",
              "frame", "fabric", 1, [("hole", 4, "foot holes in the corners of the base"), ("hole", 4, "bracket holes in the end")],
              "center", size=(900, 1630, 450))
ARMREST = part("", "armrest", "upholstered end armrest taken off the sofa and refitted to the outer side of the chaise",
               "frame", "fabric", 1, [("hole", 4, "bracket holes on its inner face")], "right", size=(150, 950, 650))
FOOT = lambda qty=4: part("121236", "foot", "square tapered plastic foot 121236", "block", "plastic", qty,
                          [("hole", 1, "push-fit peg on top")], "bottom", size=(60, 60, 100))
CONNECTING_RAIL = part("121230", "connecting rail", "long metal bar 121230 with an angled end plate at each end",
                       "beam", "metal", 1, [("hole", 4, "bolt holes in the end plates")], "bottom")
JOINING_RAIL = part("121227", "joining rail", "flat metal strip 121227 with three pegs", "beam", "metal", 1,
                    [("hole", 3, "screw holes")], "bottom")
BRACKET = lambda qty=2: part("121228", "corner bracket", "metal angle bracket 121228 with round and slotted holes",
                             "bracket", "metal", qty, [("slot", 2, "slotted holes"), ("hole", 2, "round holes")], "right")
CLAMP = part("121231", "clamp bracket", "U-shaped metal clamp bracket 121231 with a screw and pressure disc",
             "bracket", "metal", 1, [("hole", 1, "threaded hole for the clamp screw")], "right")
SEAT_CUSHION = part("", "seat cushion", "long upholstered chaise seat cushion", "panel", "fabric", 1, [], "top",
                    size=(820, 1400, 150))
BACK_CUSHION = part("", "back cushion", "upholstered back cushion", "panel", "fabric", 1, [], "top", size=(820, 220, 450))

NUT = lambda qty: fastener("100712", "nut 100712", "nut", qty)
WASHER = lambda qty: fastener("100854", "washer 100854", "washer", qty)
TOOTH_WASHER = lambda qty: fastener("100851", "toothed washer 100851", "washer", qty)
SCREW_SHORT = lambda qty: fastener("111374", "screw 111374", "screw", qty)
SCREW = lambda qty: fastener("121365", "screw 121365", "screw", qty)
BOLT = lambda qty: fastener("100471", "bolt 100471", "bolt", qty)

ALLEN = tool("allen key 100002")
SPANNER = tool("box spanner 120202")

PAGES = [
    page(1, "cover", final="KIVIK chaise longue section with a long seat cushion and a back cushion",
         unc=["Cover page; product name KIVIK and IKEA logo."]),
    page(2, "warning",
         unc=["Two people needed; assemble on a soft floor; call IKEA if unsure."]),
    page(3, "parts_list",
         parts=[FOOT(4), BRACKET(2), CONNECTING_RAIL, JOINING_RAIL, CLAMP],
         fasteners=[NUT(5), WASHER(5), TOOTH_WASHER(4), SCREW_SHORT(4), SCREW(4), BOLT(4)],
         tools=[ALLEN, SPANNER],
         unc=["Only the hardware and the joining kit are drawn; the chaise frame, sofa, armrest and cushions appear in the steps.",
              "Inset: the chaise is fitted to the end of a sofa, forming an L."]),
    page(4, "warning",
         unc=["Unpacking: cut the packaging open without a knife into the fabric; lay the chaise on its back on a soft surface."]),
    page(5, "assembly_step",
         parts=[CHAISE, FOOT(4)],
         actions=[
             action("insert", "foot", "chaise frame", "", "", "inward",
                    "step 1: 4x foot 121236 pushed and turned into the corners of the base of the chaise frame lying on its back"),
         ],
         final="chaise frame on its back with four feet in its base corners"),
    page(6, "assembly_step",
         parts=[SOFA, ARMREST],
         fasteners=[NUT(4), WASHER(4)],
         tools=[SPANNER],
         final="sofa section on its back with the end armrest taken off",
         unc=["Step 2: the 4 nuts 100712 and washers 100854 holding the sofa's end armrest are undone with box spanner 120202 and the armrest is lifted away, to be refitted to the chaise later. A removal, so no action is recorded."]),
    page(7, "assembly_step",
         parts=[SOFA, CONNECTING_RAIL, JOINING_RAIL, BRACKET(2)],
         fasteners=[NUT(1), WASHER(1), SCREW(1)],
         tools=[SPANNER, ALLEN],
         actions=[
             action("attach", "connecting rail", "sofa section", "121365", "allen key 100002", "inward",
                    "step 3: connecting rail 121230 held against the end of the sofa section base and fixed with 1x screw 121365 using allen key 100002"),
             action("tighten", "", "connecting rail", "100712", "box spanner 120202", "clockwise",
                    "step 3: 1x nut 100712 and washer 100854 tightened on the stud through the connecting rail end plate with box spanner 120202"),
         ],
         final="connecting rail fixed across the end of the sofa base",
         unc=["Info inset: shows where the joining kit (connecting rail 121230, joining rail 121227, 2x corner bracket 121228) goes."]),
    page(8, "assembly_step",
         parts=[SOFA, JOINING_RAIL, CONNECTING_RAIL],
         fasteners=[SCREW(3)],
         tools=[ALLEN],
         actions=[
             action("attach", "joining rail", "sofa section", "121365", "allen key 100002", "inward",
                    "step 4: joining rail 121227 screwed to the sofa section base frame with 3x screw 121365 and allen key 100002, pegs facing out"),
         ],
         final="joining rail along the bottom of the sofa's end",
         unc=["Inset: the pegs on the joining rail must face outward, not inward."]),
    page(9, "assembly_step",
         parts=[CHAISE, ARMREST, BRACKET(2)],
         fasteners=[SCREW_SHORT(4)],
         tools=[ALLEN],
         actions=[
             action("attach", "corner bracket", "armrest", "111374", "allen key 100002", "inward",
                    "step 5: chaise frame stood on its end; 2x corner bracket 121228 screwed to the inner face of the armrest with 4x screw 111374 and allen key 100002"),
             action("attach", "armrest", "chaise frame", "", "", "inward",
                    "step 5: armrest stood against the outer side of the chaise frame"),
         ],
         final="armrest standing against the chaise frame's outer side with two corner brackets"),
    page(10, "assembly_step",
         parts=[CHAISE, CLAMP, ARMREST],
         actions=[
             action("attach", "clamp bracket", "chaise frame", "", "", "up",
                    "step 6: clamp bracket 121231 hooked over the edge of the chaise frame and the armrest, its screw turned in by hand"),
         ],
         final="clamp bracket holding the armrest to the chaise frame"),
    page(11, "assembly_step",
         parts=[CHAISE, BRACKET(1), ARMREST],
         fasteners=[BOLT(2), TOOTH_WASHER(2), WASHER(2), NUT(2)],
         tools=[SPANNER],
         actions=[
             action("attach", "corner bracket", "chaise frame", "100471", "box spanner 120202", "inward",
                    "step 7: the lower corner bracket on the armrest bolted to the chaise frame with 2x bolt 100471, toothed washer 100851, washer 100854 and nut 100712 using box spanner 120202"),
         ],
         final="armrest bolted to the chaise frame at the bottom"),
    page(12, "assembly_step",
         parts=[CHAISE, CLAMP, BRACKET(1), ARMREST],
         fasteners=[BOLT(2), TOOTH_WASHER(2), WASHER(2), NUT(2)],
         tools=[SPANNER],
         actions=[
             action("tighten", "", "clamp bracket", "", "", "up",
                    "step 8: clamp bracket pushed up against the frame and tightened"),
             action("attach", "corner bracket", "chaise frame", "100471", "box spanner 120202", "inward",
                    "step 9: the upper corner bracket bolted to the chaise frame with 2x bolt 100471, toothed washer 100851, washer 100854 and nut 100712"),
         ],
         final="armrest fixed to the chaise frame at both brackets"),
    page(13, "assembly_step",
         parts=[CHAISE, SOFA, JOINING_RAIL],
         actions=[
             action("attach", "chaise frame", "sofa section", "", "", "down",
                    "step 10: chaise turned upright and its end lowered so its hooks drop onto the 2x pegs of the joining rail on the sofa section"),
         ],
         final="chaise longue standing beside the sofa, joined at its end, forming an L",
         unc=["The pieces are turned upright between steps 9 and 10; the turn is not a join."]),
    page(14, "assembly_step",
         parts=[CHAISE, SEAT_CUSHION, BACK_CUSHION],
         actions=[
             action("place", "seat cushion", "chaise frame", "", "", "down",
                    "step 11: seat cushion laid into the chaise frame, its strip pressed onto the fastening tape"),
             action("place", "back cushion", "chaise frame", "", "", "down",
                    "step 12: back cushion set against the back of the chaise frame"),
         ],
         final="finished chaise longue with seat and back cushions"),
    page(15, "other", final="finished chaise longue; keep the instructions",
         unc=["Shows the finished chaise and the instruction leaflet kept with it."]),
    page(16, "other", final="examples of KIVIK sofas combined with a chaise longue",
         unc=["Combination examples only; no assembly."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled KIVIK chaise longue", (0.05, 0.25, 0.8, 0.75), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Two people, soft floor, call IKEA if unsure", (0.05, 0.05, 0.95, 0.95),
                            parts=False, action_="warning", complexity="low")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Fittings: nut 100712 x5, washer 100854 x5, toothed washer 100851 x4, screw 111374 x4, screw 121365 x4, bolt 100471 x4",
                (0.05, 0.25, 0.95, 0.45), ["100712", "100854", "100851", "111374", "121365", "100471", "5x", "4x"],
                parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Allen key 100002 x1 and box spanner 120202 x1", (0.05, 0.05, 0.45, 0.7),
                ["100002", "120202", "1x"], parts=False, tools=True, complexity="low"),
        diagram("part_inventory", "Foot 121236 x4", (0.45, 0.45, 0.85, 0.7), ["121236", "4x"], complexity="low"),
        diagram("part_inventory", "Joining kit: connecting rail 121230 x1, joining rail 121227 x1, corner bracket 121228 x2, clamp bracket 121231 x1",
                (0.05, 0.75, 0.95, 0.98), ["121230", "121227", "121228", "121231", "1x", "2x"], complexity="medium"),
    ], []),
    5: ("assembly_step", [diagram("exploded_view", "Step 1: 4x foot 121236 into the base of the chaise frame",
                                  (0.05, 0.3, 0.95, 0.95), ["121236", "4x"], arrows=True, action_="insert", complexity="medium")], []),
    6: ("assembly_step", [diagram("assembly_view", "Step 2: armrest removed from the sofa end, 4x nut 100712 and washer 100854 with box spanner 120202",
                                  (0.05, 0.3, 0.95, 0.95), ["100712", "100854", "120202", "4x"], fast=True, tools=True, arrows=True,
                                  action_="none", complexity="high")], []),
    7: ("assembly_step", [diagram("exploded_view", "Step 3: connecting rail 121230 fixed to the sofa end with screw 121365, nut 100712, washer 100854",
                                  (0.05, 0.4, 0.95, 0.95), ["121230", "121365", "100712", "100854", "120202", "100002"],
                                  fast=True, tools=True, arrows=True, action_="attach", complexity="high")], []),
    8: ("assembly_step", [diagram("exploded_view", "Step 4: joining rail 121227 screwed to the sofa base with 3x screw 121365",
                                  (0.05, 0.05, 0.95, 0.95), ["121227", "121365", "100002", "3x"], fast=True, tools=True, arrows=True,
                                  action_="attach", complexity="high")], []),
    9: ("assembly_step", [diagram("exploded_view", "Step 5: 2x corner bracket 121228 screwed to the armrest with 4x screw 111374",
                                  (0.05, 0.05, 0.95, 0.95), ["121228", "111374", "100002", "2x", "4x"], fast=True, tools=True, arrows=True,
                                  action_="attach", complexity="high")], []),
    10: ("assembly_step", [diagram("exploded_view", "Step 6: clamp bracket 121231 hooked onto the chaise frame and armrest",
                                   (0.05, 0.05, 0.95, 0.95), ["121231"], arrows=True, action_="attach", complexity="medium")], []),
    11: ("assembly_step", [diagram("exploded_view", "Step 7: 2x bolt 100471 with toothed washer 100851, washer 100854, nut 100712",
                                   (0.05, 0.05, 0.95, 0.95), ["100471", "100851", "100854", "100712", "120202", "2x"],
                                   fast=True, tools=True, arrows=True, action_="tighten", complexity="high")], []),
    12: ("assembly_step", [
        diagram("assembly_view", "Step 8: clamp bracket pushed up and tightened", (0.05, 0.05, 0.95, 0.48), arrows=True, action_="tighten"),
        diagram("exploded_view", "Step 9: 2x bolt 100471 with toothed washer, washer and nut", (0.05, 0.5, 0.95, 0.95),
                ["100471", "100851", "100854", "100712", "2x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
    ], []),
    13: ("assembly_step", [diagram("assembly_view", "Step 10: turned upright, chaise hooked onto the joining rail pegs (2x)",
                                   (0.05, 0.05, 0.95, 0.95), ["2x"], arrows=True, action_="attach", complexity="high")], []),
    14: ("assembly_step", [
        diagram("assembly_view", "Step 11: seat cushion into the chaise frame", (0.05, 0.05, 0.95, 0.48), arrows=True, action_="place"),
        diagram("assembly_view", "Step 12: back cushion onto the chaise", (0.05, 0.5, 0.95, 0.95), arrows=True, action_="place"),
    ], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS)
