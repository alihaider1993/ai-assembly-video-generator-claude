"""Vision results for the IKEA POÄNG rocking chair frame manual (12 pages).

A cantilevered bentwood armchair: four slats across between two S-curved
back uprights make the back, a fabric seat is screwed to the bottom of the
uprights with a side rail along each of its edges, and two bentwood
rocker frames (armrest bending down into the front leg and a curved
rocker) are fixed to the seat side rails and joined by one front rail. The manual prints no sizes; sizes and outlines are estimated.

Run: python manuals/poang_rocking/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# Sizes are estimated from the drawings and the usual size of this chair
# (about 680 wide, 820 deep, 1000 high, seat about 400 high). Outlines are
# traced in the side view: y from front to back, z up, in mm.
SIDE_PROFILE = {"path": [(700, 560), (150, 600), (60, 540), (90, 380), (200, 120), (60, 60), (-60, 40),
                         (150, 10), (450, 0), (750, 30), (900, 90)],
                "thickness": 45}
BACK_PROFILE = {"path": [(0, 0), (70, 250), (40, 480), (120, 740), (250, 960)], "thickness": 40}
# A back slat seen from above (x across, y front to back): a shallow arc.
SLAT_PROFILE = {"path": [(0, 0), (130, 25), (260, 35), (390, 25), (520, 0)], "thickness": 15, "plane": "top"}

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
                               f"{side} bentwood side frame: armrest bending down into the front leg and a long curved rocker",
                               "frame", "wood", 1, [("hole", 3, "bolt and dowel holes")], side,
                               size=(60, 960, 600), profile=SIDE_PROFILE)
FRONT_RAIL = part("", "front rail", "straight wooden crossbar joining the two side frames at the front, under the seat", "beam", "wood", 1,
                  [("hole", 2, "bolt holes in the ends"), ("hole", 2, "barrel nut holes")], "bottom", size=(560, 40, 60))

LONG_BOLT = lambda qty: fastener("122606", "bolt 122606", "bolt", qty)
BOLT = lambda qty: fastener("146654", "bolt 146654", "bolt", qty)
DOWEL = lambda qty: fastener("10056347", "dowel 10056347", "dowel", qty)
SLAT_SCREW = lambda qty: fastener("119046", "screw 119046", "screw", qty)
SEAT_SCREW = lambda qty: fastener("120925", "screw 120925", "screw", qty)
BARREL_NUT = lambda qty: fastener("100514", "barrel nut 100514", "nut", qty)

ALLEN = tool("allen key 100001")

PAGES = [
    page(1, "cover", final="POÄNG rocking chair: bentwood rocker frames, slatted back and seat",
         unc=["Cover page; cushion sold separately."]),
    page(2, "warning", unc=["Use the supplied allen key, no power drill; soft floor; call IKEA if unsure."]),
    page(3, "parts_list",
         fasteners=[LONG_BOLT(2), BOLT(4), DOWEL(2), SLAT_SCREW(8), SEAT_SCREW(6), BARREL_NUT(2)],
         tools=[ALLEN],
         unc=["Only the hardware is drawn; the info box shows the finished rocking frame."]),
    page(4, "assembly_step",
         parts=[SLAT(4), BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         actions=[
             action("insert", "back slat", "left back upright", "", "", "down",
                    "step 1: back lying on its side; 4x back slat pushed into the holes of the left back upright"),
             action("attach", "right back upright", "back slat", "", "", "down",
                    "step 2: right back upright pressed onto the other ends of the 4 back slats"),
         ],
         final="back lying on its side",
         unc=["The back is drawn lying on its side; in the chair the uprights stand and the slats run across."]),
    page(5, "assembly_step",
         parts=[SLAT(4), BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         fasteners=[SLAT_SCREW(8)],
         tools=[ALLEN],
         actions=[
             action("tighten", "", "right back upright", "119046", "allen key 100001", "clockwise",
                    "step 3: 4x screw 119046 through the right back upright into the back slats"),
             action("tighten", "", "left back upright", "119046", "allen key 100001", "clockwise",
                    "step 4: back turned over; 4x screw 119046 through the left back upright"),
         ],
         final="back screwed together"),
    page(6, "assembly_step",
         parts=[SEAT, BACK_UPRIGHT("left"), BACK_UPRIGHT("right")],
         fasteners=[SEAT_SCREW(2)],
         tools=[ALLEN],
         actions=[action("attach", "seat", "left back upright", "120925", "allen key 100001", "inward",
                         "step 5: seat screwed to the bottom ends of the back uprights with 2x screw 120925")],
         final="seat hanging from the bottom of the back"),
    page(7, "assembly_step",
         parts=[SEAT, SEAT_SIDE_RAIL(2)],
         fasteners=[SEAT_SCREW(4)],
         tools=[ALLEN],
         actions=[action("attach", "seat side rail", "seat", "120925", "allen key 100001", "down",
                         "steps 6-7: 2x seat side rail laid along the side edges of the seat, curved side down, fixed with 4x screw 120925")],
         final="seat with a side rail along each edge"),
    page(8, "assembly_step",
         parts=[SIDE_FRAME("left"), SEAT_SIDE_RAIL(1)],
         fasteners=[DOWEL(1), BOLT(1)],
         tools=[ALLEN],
         actions=[
             action("insert", "", "seat side rail", "10056347", "", "inward",
                    "step 8: dowel 10056347 pushed into the seat side rail up to its collar"),
             action("attach", "left side frame", "seat side rail", "146654", "allen key 100001", "down",
                    "steps 8-9: chair upside down; left side frame laid over the seat side rail and fixed with bolt 146654"),
         ],
         final="left rocker frame on the upturned chair",
         unc=["The chair is turned upside down before step 8; not a join."]),
    page(9, "assembly_step",
         parts=[SIDE_FRAME("left"), FRONT_RAIL, SEAT_SIDE_RAIL(1)],
         fasteners=[BOLT(1), LONG_BOLT(1), BARREL_NUT(1)],
         tools=[ALLEN],
         actions=[
             action("tighten", "left side frame", "seat side rail", "146654", "allen key 100001", "clockwise",
                    "step 10: second bolt 146654 through the left side frame into the seat side rail"),
             action("attach", "front rail", "left side frame", "122606", "allen key 100001", "up",
                    "step 11: front rail pushed up against the left side frame and fixed with bolt 122606 into barrel nut 100514"),
         ],
         final="front rail fixed to the left side frame"),
    page(10, "assembly_step",
         parts=[SIDE_FRAME("right"), SEAT_SIDE_RAIL(1)],
         fasteners=[DOWEL(1), BOLT(1)],
         tools=[ALLEN],
         actions=[action("attach", "right side frame", "seat side rail", "146654", "allen key 100001", "down",
                         "steps 12-13: chair turned on its other side; right side frame fitted on dowel 10056347 and fixed with bolt 146654")],
         final="both rocker frames on the seat side rails"),
    page(11, "assembly_step",
         parts=[SIDE_FRAME("right"), FRONT_RAIL],
         fasteners=[BOLT(1), LONG_BOLT(1), BARREL_NUT(1)],
         tools=[ALLEN],
         actions=[action("attach", "front rail", "right side frame", "122606", "allen key 100001", "down",
                         "steps 14-15: second bolt 146654 and bolt 122606 through the right side frame into the front rail's barrel nut 100514")],
         final="rocking chair frame complete"),
    page(12, "assembly_step",
         unc=["Retighten all 6 bolts with allen key 100001 once upright; the cushion (sold separately) is laid on. No join."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "POÄNG rocking chair", (0.05, 0.1, 0.8, 0.85), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Allen key, soft floor, call IKEA", (0.05, 0.05, 0.95, 0.95), parts=False, tools=True,
                            action_="warning", complexity="low")], []),
    3: ("parts_list", [diagram("part_inventory", "Fittings and allen key", (0.03, 0.03, 0.97, 0.48),
                               ["122606", "146654", "10056347", "119046", "100514", "120925", "100001", "2x", "4x", "8x", "6x"],
                               parts=False, fast=True, tools=True, complexity="low")], []),
    **{n: ("assembly_step", [diagram("exploded_view", f"Steps on page {n}", (0.05, 0.05, 0.95, 0.95), [], fast=True, tools=True,
                                     arrows=True, action_="attach", complexity="high")], []) for n in range(4, 12)},
    12: ("assembly_step", [diagram("assembly_view", "Retighten bolts; cushion", (0.05, 0.05, 0.95, 0.95), ["6x", "100001"],
                                   tools=True, action_="tighten")], []),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA POÄNG Rocking Chair")
