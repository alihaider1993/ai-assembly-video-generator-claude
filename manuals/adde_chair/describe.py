"""Vision results for the IKEA ADDE chair manual (12 pages, 11-12 blank).

A steel tube chair: two welded tube frames (each a front leg bent into a
seat rail, with a cross rail welded on) bolted to two straight back legs,
a plastic backrest pushed onto the back leg tops and screwed, and a plastic
seat clipped on. The manual prints no sizes; they are estimated from the
drawings and the ADDE's usual size (about 390 wide, 470 deep, 770 high,
seat 450 high).

Run: python manuals/adde_chair/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# Side view (y front to back, z up): the front leg rises from the floor and
# bends back into the seat rail.
SIDE_FRAME_PROFILE = {"path": [(0, 0), (10, 400), (40, 450), (420, 450)], "thickness": 22}
# Front view (x, z): the backrest shell, a rounded-top rectangle.
BACKREST_PROFILE = {"plane": "front", "closed": True,
                    "path": [(0, 0), (390, 0), (390, 190), (360, 220), (30, 220), (0, 190)]}

SIDE_FRAME = lambda side: part(
    "", f"{side} side frame", f"{side} welded steel tube frame: a front leg bent back into a seat rail, with a cross rail welded on and threaded bolt bosses",
    "frame", "metal", 1, [("hole", 2, "bolt bosses where the back legs are bolted on")], side, size=(22, 420, 450),
    profile=SIDE_FRAME_PROFILE)
BACK_LEG = lambda side: part(
    "", f"{side} back leg", f"{side} straight steel tube back leg, slightly curved, with a hex bolt hole at seat height",
    "tube", "metal", 1, [("hole", 1, "hex bolt hole at seat height")], side, size=(22, 22, 620))
BACKREST = lambda qty=1: part(
    "", "backrest", "perforated plastic backrest with sockets underneath that fit over the back leg tops",
    "panel", "plastic", qty, [("hole", 2, "sockets and screw holes for the back legs")], "top", size=(390, 20, 220), tilt=6,
    profile=BACKREST_PROFILE)
SEAT = lambda qty=1: part(
    "", "seat", "perforated plastic seat shell with hooks at the back and click catches underneath",
    "panel", "plastic", qty, [("slot", 6, "click catches underneath"), ("slot", 2, "hooks at the back edge")], "center",
    size=(390, 400, 25))
SIDES = ("left", "right")

CLIP = lambda qty: fastener("128671", "seat clip 128671", "bracket", qty)  # small plastic clip
BOLT = lambda qty: fastener("128654", "hex bolt 128654", "bolt", qty)
SCREW = lambda qty: fastener("106917", "screw 106917", "screw", qty)
NUT = lambda qty: fastener("104875", "flange nut 104875", "nut", qty)

DRIVER = tool("cross head screwdriver")
SPANNER = tool("adjustable spanner")

PAGES = [
    page(1, "cover", final="ADDE chair: four steel tube legs, perforated plastic seat and backrest",
         unc=["Cover page; product name ADDE and IKEA logo."]),
    page(2, "parts_list",
         fasteners=[CLIP(4), BOLT(4), SCREW(2), NUT(4)],
         tools=[DRIVER, SPANNER],
         unc=["Only the hardware is drawn; the tube frames, back legs, backrest and seat appear in the steps.",
              "Tools drawn: cross head screwdriver, hammer and adjustable spanner (not supplied); work on a soft floor; two people not required."]),
    page(3, "assembly_step",
         parts=[SIDE_FRAME("left"), BACK_LEG("left"), BACK_LEG("right")],
         actions=[
             action("attach", "left back leg", "left side frame", "", "", "down",
                    "step 1: frame laid on a rug; left back leg pushed onto the bolt boss of the left side frame, hex hole lined up (inset), curve the right way"),
             action("attach", "right back leg", "left side frame", "", "", "down",
                    "step 2: right back leg pushed onto the second bolt boss of the left side frame"),
         ],
         final="left side frame lying on a rug with both back legs standing up from it",
         unc=["The frame is drawn lying on its side; the inset shows which way the back leg curves.",
              "The left side frame also carries the welded cross rail, so both back legs fit on it."]),
    page(4, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACK_LEG("left"), BACK_LEG("right")],
         fasteners=[BOLT(2)],
         actions=[
             action("insert", "", "left side frame", "128654", "", "inward",
                    "step 3: 2x hex bolt 128654 pushed through the left back leg and right back leg into the left side frame"),
             action("attach", "right side frame", "left back leg", "", "", "down",
                    "step 4: right side frame turned over and laid on the free ends of the left back leg and right back leg"),
         ],
         final="both tube frames joined by the two back legs",
         unc=["Step 4 shows the right side frame being turned over before it goes on; this is not a join."]),
    page(5, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACK_LEG("left"), BACK_LEG("right")],
         fasteners=[BOLT(2), NUT(4)],
         actions=[
             action("insert", "", "right side frame", "128654", "", "inward",
                    "step 5: 2x hex bolt 128654 pushed through the back legs into the right side frame"),
             action("tighten", "", "left side frame", "104875", "", "clockwise",
                    "step 6: 4x flange nut 104875 screwed onto the bolt ends by hand, not tight yet"),
         ],
         final="chair frame upside down with all four bolts and nuts loosely fitted"),
    page(6, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACK_LEG("left"), BACK_LEG("right"), BACKREST()],
         fasteners=[SCREW(2)],
         tools=[DRIVER],
         actions=[
             action("attach", "backrest", "left back leg", "", "", "down",
                    "step 7: backrest pressed down onto the tops of the left back leg and right back leg"),
             action("tighten", "", "backrest", "106917", "cross head screwdriver", "clockwise",
                    "step 8: 2x screw 106917 driven through the back of the backrest into the back legs with a cross head screwdriver"),
         ],
         final="chair frame standing upright with the backrest on the back legs",
         unc=["Step 7 starts by turning the frame upright; not a join."]),
    page(7, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACK_LEG("left"), BACK_LEG("right"), BACKREST()],
         fasteners=[NUT(4)],
         tools=[SPANNER],
         actions=[
             action("tighten", "", "right side frame", "104875", "adjustable spanner", "clockwise",
                    "step 9: 4x flange nut 104875 tightened with an adjustable spanner in the order 1, 2, 3, 4 shown at the seat corners"),
         ],
         final="frame with all nuts tight",
         unc=["The chair is turned round to reach the nuts; not a join."]),
    page(8, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACK_LEG("left"), BACK_LEG("right"), BACKREST(), SEAT()],
         fasteners=[CLIP(4)],
         actions=[
             action("insert", "", "left side frame", "128671", "", "up",
                    "step 10: 2x seat clip 128671 pushed up over the flange nuts under the left side frame"),
             action("insert", "", "right side frame", "128671", "", "up",
                    "step 10: 2x seat clip 128671 pushed up over the flange nuts under the right side frame"),
             action("place", "seat", "left side frame", "", "", "down",
                    "step 11: seat hooked under the seat rails at the back (2x hooks), front edge still raised"),
         ],
         final="seat hooked on at the back, resting on the frame",
         unc=["Step 11 turns the chair round again; not a join."]),
    page(9, "assembly_step",
         parts=[SIDE_FRAME("left"), SIDE_FRAME("right"), BACKREST(), SEAT()],
         actions=[
             action("tighten", "", "seat", "", "", "down",
                    "step 12: seat pressed down until its 6x catches click into the clips fitted at step 10"),
         ],
         final="finished ADDE chair"),
    page(10, "info",
         parts=[SEAT()],
         fasteners=[CLIP(4), NUT(4)],
         tools=[SPANNER],
         final="finished ADDE chair",
         unc=["Information page: if the chair wobbles, pull off the 4 seat clips, retighten the nuts with a spanner and refit the clips. Not part of the build."]),
    page(11, "unknown", unc=["Blank page."]),
    page(12, "unknown", unc=["Blank page."]),
]

DIAGRAMS = {
    1: ("cover", [diagram("final_product", "Assembled ADDE chair", (0.08, 0.1, 0.85, 0.85), complexity="low", conf=0.95)], []),
    2: ("parts_list", [
        diagram("other", "Tools and safety: screwdriver, hammer, spanner; soft floor; ask IKEA if unsure",
                (0.06, 0.03, 0.94, 0.7), parts=False, tools=True, complexity="low"),
        diagram("part_inventory", "Fittings: seat clip 128671 x4, hex bolt 128654 x4, screw 106917 x2, flange nut 104875 x4",
                (0.06, 0.78, 0.62, 0.93), ["128671", "128654", "106917", "104875", "4x", "2x"], parts=False, fast=True, complexity="low", conf=0.9),
    ], []),
    3: ("assembly_step", [
        diagram("exploded_view", "Step 1: side frame on a rug, back leg on the boss; inset of correct leg curve",
                (0.03, 0.02, 0.97, 0.5), ["1"], arrows=False, action_="insert", complexity="medium"),
        diagram("exploded_view", "Step 2: second back leg pushed onto the frame", (0.03, 0.55, 0.97, 0.95), ["2"], arrows=True, action_="insert"),
    ], []),
    4: ("assembly_step", [
        diagram("exploded_view", "Step 3: 2x bolt 128654 into the back legs", (0.03, 0.05, 0.97, 0.5), ["3", "2x", "128654"], fast=True, arrows=True, action_="insert"),
        diagram("exploded_view", "Step 4: second frame turned over onto the back leg tops", (0.03, 0.55, 0.97, 0.95), ["4"], arrows=True, action_="attach"),
    ], []),
    5: ("assembly_step", [
        diagram("exploded_view", "Step 5: 2x bolt 128654 into the second frame", (0.03, 0.05, 0.97, 0.45), ["5", "2x", "128654"], fast=True, arrows=True, action_="insert"),
        diagram("detail_callout", "Step 6: 4x nut 104875 started by hand", (0.03, 0.52, 0.97, 0.95), ["6", "4x", "104875"], fast=True, arrows=True, action_="tighten"),
    ], []),
    6: ("assembly_step", [
        diagram("assembly_view", "Step 7: frame turned upright, backrest pressed onto the back legs", (0.03, 0.03, 0.97, 0.52), ["7"], arrows=True, action_="attach"),
        diagram("detail_callout", "Step 8: 2x screw 106917 with screwdriver", (0.03, 0.55, 0.97, 0.95), ["8", "2x", "106917"], fast=True, tools=True, arrows=True, action_="tighten"),
    ], []),
    7: ("assembly_step", [
        diagram("detail_callout", "Step 9: 4x nut tightened with a spanner in order 1-4", (0.03, 0.03, 0.97, 0.75), ["9", "1", "2", "3", "4", "4x"], fast=True, tools=True, arrows=True, action_="tighten"),
    ], []),
    8: ("assembly_step", [
        diagram("detail_callout", "Step 10: 4x seat clip 128671 pushed onto the nuts", (0.03, 0.03, 0.97, 0.5), ["10", "4x", "128671"], fast=True, arrows=True, action_="insert"),
        diagram("assembly_view", "Step 11: seat hooked on at the back (2x)", (0.03, 0.52, 0.97, 0.95), ["11", "2x"], arrows=True, action_="place"),
    ], []),
    9: ("assembly_step", [
        diagram("detail_callout", "Step 12: seat pressed down, 6x click", (0.1, 0.2, 0.9, 0.7), ["12", "6x"], fast=True, arrows=True, action_="place"),
    ], []),
    10: ("info", [
        diagram("detail_callout", "If the chair wobbles: remove clips, retighten nuts, refit clips", (0.05, 0.05, 0.95, 0.95), ["4x"], fast=True, tools=True, arrows=True, action_="tighten", complexity="low"),
    ], []),
    11: ("unknown", [], ["Blank page."]),
    12: ("unknown", [], ["Blank page."]),
}

if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA ADDE Chair")
