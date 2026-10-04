"""Vision results for the IKEA POÄNG armchair manual (12 pages).

A cantilevered bentwood armchair: four slats across between two S-curved
back uprights make the back, a fabric seat is screwed to the bottom of the
uprights with a side rail along each of its edges, and two bentwood side
frames (armrest bending down into the front leg and a floor runner) are
fixed to the seat side rails and joined by a front rail and a rear base
rail. The manual prints no sizes; sizes and outlines are estimated.

Run: python manuals/poang_chair/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# Sizes are estimated from the drawings and the usual size of this chair
# (about 680 wide, 820 deep, 1000 high, seat about 400 high). Outlines are
# traced in the side view: y from front to back, z up, in mm.
SIDE_PROFILE = {"path": [(650, 560), (120, 600), (40, 540), (60, 380), (180, 120), (300, 30), (790, 30)],
                "thickness": 45}
BACK_PROFILE = {"path": [(0, 0), (70, 250), (40, 480), (120, 740), (250, 960)], "thickness": 40}
# A back slat seen from above (x across, y front to back): a shallow arc.
SLAT_PROFILE = {"path": [(0, 0), (130, 25), (260, 35), (390, 25), (520, 0)], "thickness": 15, "plane": "top"}
# The cushion in the side view: along the seat, then up the back.
CUSHION_PROFILE = {"path": [(0, 60), (420, 40), (520, 120), (600, 600)], "thickness": 80}

SLAT = lambda qty=4: part("", "back slat", "curved bentwood slat running across between the back uprights; one has hook-and-loop tape",
                          "beam", "wood", qty, [("hole", 2, "screw holes in the ends")], "center", size=(520, 50, 70),
                          profile=SLAT_PROFILE)
BACK_UPRIGHT = lambda side: part("", f"{side} back upright",
                                 f"long S-curved bentwood upright on the {side} of the back, leaning back towards its top",
                                 "beam", "wood", 1, [("hole", 4, "slat screw holes"), ("hole", 1, "seat screw hole at the bottom")],
                                 side, size=(45, 290, 1000), profile=BACK_PROFILE)
SEAT = part("", "seat", "fabric seat stretched on a frame, screwed to the bottom of the back uprights", "panel", "fabric", 1,
            [("hole", 2, "screw holes at the back corners")], "center", size=(540, 480, 20))
SEAT_SIDE_RAIL = lambda qty=2: part("", "seat side rail", "flat bentwood strip along one side edge of the seat", "beam", "wood", qty,
                                    [("hole", 2, "screw holes"), ("hole", 1, "dowel and bolt hole")], "center", size=(480, 25, 60))
SIDE_FRAME = lambda side: part("", f"{side} side frame",
                               f"{side} bentwood side frame: armrest bending down into the front leg and back along the floor as a runner",
                               "frame", "wood", 1, [("hole", 3, "bolt and dowel holes")], side,
                               size=(60, 820, 640), profile=SIDE_PROFILE)
FRONT_RAIL = part("", "front rail", "straight wooden crossbar joining the two side frames at the front, under the seat", "beam", "wood", 1,
                  [("hole", 2, "bolt holes in the ends"), ("hole", 2, "barrel nut holes")], "bottom", size=(560, 40, 60))
REAR_RAIL = part("", "rear base rail", "straight wooden crossbar joining the ends of the two floor runners at the back", "beam", "wood", 1,
                 [("hole", 2, "bolt holes in the ends"), ("hole", 2, "barrel nut holes")], "bottom", size=(560, 40, 40))
CUSHION = part("", "seat cushion", "padded chair cushion over the seat and back, fixed with hook-and-loop tape",
               "panel", "fabric", 1, [], "top", size=(540, 680, 640), profile=CUSHION_PROFILE)

LONG_BOLT = lambda qty: fastener("122606", "bolt 122606", "bolt", qty)
BOLT = lambda qty: fastener("146654", "bolt 146654", "bolt", qty)
DOWEL = lambda qty: fastener("123786", "dowel 123786", "dowel", qty)
SLAT_SCREW = lambda qty: fastener("119046", "screw 119046", "screw", qty)
SEAT_SCREW = lambda qty: fastener("120925", "screw 120925", "screw", qty)
BARREL_NUT = lambda qty: fastener("100514", "barrel nut 100514", "nut", qty)
WASHER = lambda qty: fastener("102319", "washer 102319", "washer", qty)

ALLEN = tool("allen key 100001")

PAGES = [
    page(1, "cover", final="POÄNG armchair: bentwood cantilever frame, slatted back, seat and cushion",
         unc=["Cover page; product name POÄNG and IKEA logo."]),
    page(2, "warning",
         unc=["Use the supplied allen key, no power drill; soft floor; call IKEA if unsure."]),
    page(3, "parts_list",
         fasteners=[LONG_BOLT(4), BOLT(2), DOWEL(2), SLAT_SCREW(8), SEAT_SCREW(6), BARREL_NUT(4), WASHER(2)],
         tools=[ALLEN],
         unc=["Only the hardware is drawn; the wooden parts appear in the steps.",
              "Info box shows the finished frame from the side."]),
    page(4, "assembly_step",
         parts=[SLAT(4), BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         actions=[
             action("insert", "back slat", "left back upright", "", "", "down",
                    "step 1: back drawn lying on its side; 4x back slat pushed into the holes of the left back upright, the more curved ones as in the info inset"),
             action("attach", "right back upright", "back slat", "", "", "down",
                    "step 2: right back upright pressed down onto the other ends of the 4 back slats"),
         ],
         final="back lying on its side: 4 slats across between the two back uprights",
         unc=["The back is drawn lying on its side; in the finished chair the uprights stand and the slats run across."]),
    page(5, "assembly_step",
         parts=[SLAT(4), BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         fasteners=[SLAT_SCREW(8)],
         tools=[ALLEN],
         actions=[
             action("tighten", "", "right back upright", "119046", "allen key 100001", "clockwise",
                    "step 3: 4x screw 119046 through the right back upright into the back slats with allen key 100001"),
             action("tighten", "", "left back upright", "119046", "allen key 100001", "clockwise",
                    "step 4: back turned over; 4x screw 119046 through the left back upright into the back slats"),
         ],
         final="back screwed together",
         unc=["Insets: use screw 119046 here, not 120925.", "The back is turned over between steps 3 and 4; not a join."]),
    page(6, "assembly_step",
         parts=[SEAT, BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         fasteners=[SEAT_SCREW(2)],
         tools=[ALLEN],
         actions=[
             action("attach", "seat", "left back upright", "120925", "allen key 100001", "inward",
                    "step 5: seat frame screwed to the bottom ends of the left back upright and right back upright with 2x screw 120925 and allen key 100001"),
         ],
         final="seat hanging from the bottom of the back"),
    page(7, "assembly_step",
         parts=[SEAT, SEAT_SIDE_RAIL(2)],
         fasteners=[SEAT_SCREW(4)],
         tools=[ALLEN],
         actions=[
             action("attach", "seat side rail", "seat", "120925", "allen key 100001", "down",
                    "step 6-7: 2x seat side rail laid along the side edges of the seat, curved side down (info inset), fixed with 4x screw 120925"),
         ],
         final="seat with a side rail along each edge"),
    page(8, "assembly_step",
         parts=[SIDE_FRAME("left"), SEAT_SIDE_RAIL(1)],
         fasteners=[DOWEL(1), BOLT(1), WASHER(1)],
         tools=[ALLEN],
         actions=[
             action("insert", "", "seat side rail", "123786", "", "inward",
                    "step 8: dowel 123786 pushed into the seat side rail"),
             action("attach", "left side frame", "seat side rail", "146654", "allen key 100001", "down",
                    "step 8: chair upside down; left side frame laid over the seat side rail and fixed with 1x bolt 146654 and washer 102319 using allen key 100001"),
         ],
         final="left side frame on the upturned chair",
         unc=["The chair is turned upside down before step 8; not a join.", "Inset: use bolt 146654 here, not 122606."]),
    page(9, "assembly_step",
         parts=[SIDE_FRAME("left"), FRONT_RAIL, REAR_RAIL],
         fasteners=[LONG_BOLT(2), BARREL_NUT(2)],
         tools=[ALLEN],
         actions=[
             action("attach", "front rail", "left side frame", "122606", "allen key 100001", "up",
                    "step 9: front rail pushed up against the left side frame and fixed with bolt 122606 into barrel nut 100514"),
             action("attach", "rear base rail", "left side frame", "122606", "allen key 100001", "up",
                    "step 9: rear base rail pushed against the end of the left side frame's runner and fixed with bolt 122606 into barrel nut 100514"),
         ],
         final="front rail and rear base rail fixed to the left side frame",
         unc=["The chair is upside down, so the two crossbars are drawn pointing up."]),
    page(10, "assembly_step",
         parts=[SIDE_FRAME("right"), SEAT_SIDE_RAIL(1)],
         fasteners=[DOWEL(1), BOLT(1), WASHER(1)],
         tools=[ALLEN],
         actions=[
             action("attach", "right side frame", "seat side rail", "146654", "allen key 100001", "down",
                    "step 10: chair turned on its other side; right side frame fitted on dowel 123786 and fixed with 1x bolt 146654 and washer 102319"),
         ],
         final="both side frames on the seat side rails"),
    page(11, "assembly_step",
         parts=[SIDE_FRAME("right"), FRONT_RAIL, REAR_RAIL],
         fasteners=[LONG_BOLT(2), BARREL_NUT(2)],
         tools=[ALLEN],
         actions=[
             action("attach", "front rail", "right side frame", "122606", "allen key 100001", "down",
                    "step 11: bolt 122606 through the right side frame into the barrel nut 100514 in the front rail"),
             action("attach", "rear base rail", "right side frame", "122606", "allen key 100001", "down",
                    "step 11: bolt 122606 through the right side frame's runner into the barrel nut 100514 in the rear base rail"),
         ],
         final="chair frame complete"),
    page(12, "assembly_step",
         parts=[CUSHION, SEAT, SIDE_FRAME("left"), SIDE_FRAME("right")],
         tools=[ALLEN],
         actions=[
             action("place", "seat cushion", "seat", "", "", "down",
                    "chair upright; cushion laid on the seat and back, its strap pressed onto the hook-and-loop tape on the back"),
         ],
         final="finished POÄNG armchair with cushion",
         unc=["Top info: retighten all 6 bolts with allen key 100001 once the chair is upright."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled POÄNG armchair", (0.05, 0.1, 0.8, 0.85), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Allen key, no drill, soft floor, call IKEA if unsure", (0.05, 0.05, 0.95, 0.95),
                            parts=False, tools=True, action_="warning", complexity="low")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Fittings: bolt 122606 x4, bolt 146654 x2, dowel 123786 x2, screw 119046 x8, screw 120925 x6, barrel nut 100514 x4, washer 102319 x2",
                (0.03, 0.03, 0.97, 0.45), ["122606", "146654", "123786", "119046", "120925", "100514", "102319", "4x", "2x", "8x", "6x"],
                parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Allen key 100001 x1", (0.55, 0.03, 0.75, 0.3), ["100001", "1x"], parts=False, tools=True, complexity="low"),
        diagram("assembly_view", "Finished frame from the side", (0.03, 0.5, 0.97, 0.95), complexity="medium"),
    ], []),
    4: ("assembly_step", [
        diagram("exploded_view", "Step 1: back lying on its side, 4 back slats into the left back upright", (0.05, 0.05, 0.95, 0.48),
                arrows=True, action_="insert"),
        diagram("exploded_view", "Step 2: right back upright onto the slats", (0.05, 0.5, 0.95, 0.95), arrows=True, action_="attach"),
    ], []),
    5: ("assembly_step", [
        diagram("exploded_view", "Step 3: 4x screw 119046 through one back upright", (0.05, 0.05, 0.95, 0.48),
                ["119046", "100001", "4x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
        diagram("exploded_view", "Step 4: back turned over, 4x screw 119046 through the other back upright", (0.05, 0.5, 0.95, 0.95),
                ["119046", "100001", "4x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
    ], []),
    6: ("assembly_step", [diagram("exploded_view", "Step 5: seat screwed to the bottom of the back uprights with 2x screw 120925",
                                  (0.05, 0.05, 0.95, 0.95), ["120925", "100001", "2x"], fast=True, tools=True, arrows=True,
                                  action_="attach", complexity="high")], []),
    7: ("assembly_step", [
        diagram("exploded_view", "Step 6: seat side rails along the seat edges", (0.05, 0.05, 0.95, 0.48), arrows=True, action_="attach"),
        diagram("exploded_view", "Step 7: 4x screw 120925 through the seat side rails", (0.05, 0.5, 0.95, 0.95),
                ["120925", "100001", "4x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="high"),
    ], []),
    8: ("assembly_step", [diagram("exploded_view", "Step 8: chair upside down, left side frame on dowel 123786 with bolt 146654 and washer 102319",
                                  (0.05, 0.05, 0.95, 0.95), ["123786", "146654", "102319", "100001"], fast=True, tools=True,
                                  arrows=True, action_="attach", complexity="high")], []),
    9: ("assembly_step", [diagram("exploded_view", "Step 9: front rail and rear base rail, 2x bolt 122606 into barrel nut 100514",
                                  (0.05, 0.05, 0.95, 0.95), ["122606", "100514", "100001", "2x"], fast=True, tools=True,
                                  arrows=True, action_="attach", complexity="high")], []),
    10: ("assembly_step", [diagram("exploded_view", "Step 10: right side frame on dowel 123786 with bolt 146654 and washer 102319",
                                   (0.05, 0.05, 0.95, 0.95), ["123786", "146654", "102319", "100001"], fast=True, tools=True,
                                   arrows=True, action_="attach", complexity="high")], []),
    11: ("assembly_step", [diagram("exploded_view", "Step 11: 2x bolt 122606 through the right side frame into the crossbars",
                                   (0.05, 0.05, 0.95, 0.95), ["122606", "100514", "100001", "2x"], fast=True, tools=True,
                                   arrows=True, action_="attach", complexity="high")], []),
    12: ("assembly_step", [
        diagram("assembly_view", "Retighten all 6 bolts", (0.05, 0.05, 0.95, 0.48), ["100001", "6x"], tools=True, action_="tighten"),
        diagram("assembly_view", "Cushion fitted, strap on the hook-and-loop tape", (0.05, 0.5, 0.95, 0.95), arrows=True, action_="place"),
    ], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS)
