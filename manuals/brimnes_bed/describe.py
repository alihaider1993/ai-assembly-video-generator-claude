"""Vision results for the IKEA BRIMNES bed frame with storage manual (36 pages).

A box bed: a plain end board at the head and foot, two long side panels with
two drawer openings each, inside them two cross-shaped divider units on floor
rails, long inner rails, metal slat ledges, a metal centre support beam and
four drawers on runners.

Run: python manuals/brimnes_bed/describe.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 160 x 200 cm bed, 47 cm high.
# Beams are length first: size=(length, thickness, height).
HEAD = part("", "headboard", "plain end board at the head of the bed", "panel", "wood", 1,
            [("hole", 6, "cam and dowel holes")], "center", size=(1680, 18, 470))
FOOT = part("", "footboard", "plain end board at the foot of the bed", "panel", "wood", 1,
            [("hole", 6, "cam and dowel holes")], "center", size=(1680, 18, 470))
SIDE = lambda side: part("", f"{side} side panel", f"{side} long side panel with two drawer openings", "panel", "wood", 1,
                         [("hole", 8, "cam and dowel holes"), ("slot", 2, "drawer openings")], side, size=(18, 2040, 470))
CROSS = lambda qty=4, side="left": part("", f"{side} box cross rail", f"short divider panel across the {side} half of the bed, from the side panel to the centre divider",
                           "beam", "wood", qty, [("hole", 4, "cam and runner holes")], "center", size=(780, 18, 300))
CENTRE = lambda qty=1: part("", "centre divider", "long board down the middle of the bed, the stem of the cross units (two boards end to end, drawn as one)",
                            "panel", "wood", 1, [("hole", 4, "cam holes"), ("hole", 2, "runner screw holes")], "center", size=(18, 2000, 300))
FLOOR_RAIL = lambda qty=2: part("", "bottom rail", "narrow floor rail under the cross units, with glides", "beam", "wood", qty,
                                [("hole", 6, "dowel and cam bolt holes")], "center", size=(1600, 18, 60))
LONG_RAIL = lambda qty=2: part("", "long rail", "long inner rail along the top of the drawer compartments", "beam", "wood", qty,
                               [("hole", 6, "dowel holes"), ("hole", 2, "bracket holes")], "center", size=(2000, 18, 100))
LEDGE = lambda qty=4: part("118301", "side ledge", "metal angle ledge for the slatted base along a side panel", "beam", "metal", qty,
                           [("hole", 4, "screw slots")], "center", size=(1000, 20, 20))
SUPPORT = part("117228", "centre support rail", "metal centre beam from the headboard to the footboard", "beam", "metal", 1,
               [("hole", 2, "bracket holes")], "center", size=(2000, 30, 60))
DRAWER = lambda qty=4: part("", "drawer front", "finished drawer seen by its front, in a side panel opening", "panel", "wood", qty,
                            [], "center", size=(780, 18, 200))
RUNNER = lambda qty=8: part("139505", "drawer runner", "metal drawer runner", "rail", "metal", qty, [("hole", 3, "screw holes")], "center")

PAGES = [
    page(1, "cover", final="BRIMNES bed frame with storage: low box bed, two drawers in each long side"),
    page(2, "warning", unc=["Tools, soft surface, two people, ask IKEA."]),
    page(3, "parts_list",
         fasteners=[fastener("118331", "cam bolt", "bolt", "14x"), fastener("110630", "cam lock", "cam", "14x"),
                    fastener("101345", "wooden dowel", "dowel", "12x"), fastener("101359", "large dowel", "dowel", "8x"),
                    fastener("122628", "floor glide", "other", "6x"), fastener("110115", "connector bolt", "bolt", "4x")],
         tools=[tool("allen key 100049")],
         unc=["Bag 1 hardware."]),
    page(4, "parts_list",
         fasteners=[fastener("110789", "ledge screw", "screw", "20x"), fastener("100365", "bracket screw", "screw", "12x"),
                    fastener("191315", "slat stop", "other", "8x"), fastener("116791", "beam bracket", "bracket", "2x")],
         unc=["Bags 2 and 3 hardware."]),
    page(5, "parts_list", parts=[LEDGE(4), SUPPORT, RUNNER(8)],
         unc=["Metal parts: 4x slat ledge, 4x runner set, 4x support strip; drawer handles 4x."]),
    page(6, "assembly_step",
         parts=[CROSS(1, "left"), CROSS(1, "right"), CENTRE(1)],
         fasteners=[fastener("110630", "cam lock", "cam", 2), fastener("110115", "connector bolt", "bolt", 2)],
         actions=[action("insert", "", "centre divider", "110115", "", "inward",
                         "step 1: 2x cam lock 110630 and 2x connector bolt 110115 fitted to the centre divider and box cross rails")],
         final="first cross unit parts ready",
         unc=["Info: the finished box frame. The two cross units are built the same way (steps 1-6 and 10-11)."]),
    page(7, "assembly_step", parts=[CROSS(2, "left"), CROSS(2, "right"), RUNNER(8)],
         fasteners=[fastener("139505", "runner screw", "screw", 8)],
         actions=[action("attach", "drawer runner", "left box cross rail", "139505", "", "clockwise",
                         "steps 2-4: drawer runner screwed to each left box cross rail"),
             action("attach", "drawer runner", "right box cross rail", "139505", "", "clockwise",
                         "steps 2-4: drawer runner screwed to each right box cross rail")],
         final="runners on the cross rails"),
    page(8, "assembly_step", parts=[CROSS(2, "left"), CROSS(2, "right"), RUNNER(8)],
         actions=[action("attach", "drawer runner", "right box cross rail", "", "", "clockwise", "step 4: runners on the other right box cross rails")],
         final="all cross rails with runners"),
    page(9, "assembly_step",
         parts=[CROSS(1, "left"), CROSS(1, "right"), CENTRE(1)],
         fasteners=[fastener("110115", "connector bolt", "bolt", 2)],
         actions=[action("attach", "left box cross rail", "centre divider", "110115", "", "inward",
                         "step 5: left box cross rail pushed onto the connector bolts of the centre divider"),
             action("attach", "right box cross rail", "centre divider", "110115", "", "inward",
                         "step 5: right box cross rail pushed on from the other side, forming a cross")],
         final="first cross unit"),
    page(10, "assembly_step",
         parts=[CROSS(1, "left"), CROSS(1, "right"), CENTRE(1), FLOOR_RAIL(2)],
         fasteners=[fastener("110630", "cam lock", "cam", 2), fastener("122628", "floor glide", "other", 4)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("tighten", "left box cross rail", "centre divider", "110630", "flat screwdriver", "clockwise", "step 6: 2x cam lock 110630 turned"),
             action("insert", "", "bottom rail", "122628", "", "down", "step 7: 2x floor glide 122628 under each bottom rail"),
         ],
         final="cross unit and floor rails"),
    page(11, "assembly_step",
         parts=[FLOOR_RAIL(2)],
         fasteners=[fastener("118331", "cam bolt", "bolt", 4), fastener("101345", "wooden dowel", "dowel", 6)],
         actions=[action("insert", "", "bottom rail", "118331", "", "clockwise",
                         "steps 8-9: cam bolts 118331 and wooden dowels 101345 into the bottom rails")],
         final="floor rails ready"),
    page(12, "assembly_step",
         parts=[CROSS(1, "left"), CROSS(1, "right"), CENTRE(1), FLOOR_RAIL(2)],
         fasteners=[fastener("110630", "cam lock", "cam", 2)],
         tools=[tool("flat screwdriver")],
         actions=[
             action("attach", "centre divider", "bottom rail", "", "", "down", "step 10: cross unit lowered onto the bottom rails"),
             action("tighten", "centre divider", "bottom rail", "110630", "flat screwdriver", "clockwise", "step 11: 2x cam lock 110630 turned"),
         ],
         final="first cross unit on the floor rails"),
    *[page(n, "assembly_step",
           parts=[CROSS(1, "left"), CROSS(1, "right"), CENTRE(1), FLOOR_RAIL(2)],
           actions=[action("attach", "centre divider", "bottom rail", "", "", "down",
                           f"steps on page {n}: the second cross unit built the same way and set on the bottom rails")],
           final="second cross unit on the floor rails") for n in (13, 14, 15, 16)],
    page(17, "assembly_step",
         parts=[LONG_RAIL(2)],
         fasteners=[fastener("101359", "large dowel", "dowel", 4), fastener("100365", "bracket screw", "screw", 2)],
         actions=[action("insert", "", "long rail", "101359", "", "inward",
                         "steps 19-20: 4x large dowel 101359 in the long rails and a bracket 121370 screwed to each with bracket screw 100365")],
         final="long rails ready"),
    page(18, "assembly_step",
         parts=[HEAD, CENTRE(2), FLOOR_RAIL(2), LONG_RAIL(2)],
         actions=[
             action("attach", "headboard", "bottom rail", "", "", "inward",
                    "step 21: headboard set against the ends of the bottom rails and cross units"),
             action("attach", "headboard", "centre divider", "", "", "inward", "step 21: headboard against the centre dividers"),
         ],
         final="headboard against the inner frame"),
    page(19, "assembly_step",
         parts=[LONG_RAIL(2), HEAD],
         fasteners=[fastener("110115", "connector bolt", "bolt", 1)],
         tools=[tool("allen key 100049")],
         actions=[action("attach", "long rail", "headboard", "110115", "allen key 100049", "clockwise",
                         "step 22: long rail fixed to the headboard with the connector turned by allen key 100049")],
         final="first long rail on"),
    page(20, "assembly_step",
         parts=[LONG_RAIL(2), CROSS(2, "left"), CROSS(2, "right")],
         fasteners=[fastener("100365", "bracket screw", "screw", 2)],
         actions=[action("attach", "long rail", "left box cross rail", "100365", "", "clockwise",
                         "steps 23-24: long rails screwed to the box cross rails with bracket screw 100365, both sides")],
         final="long rails on both sides"),
    page(21, "assembly_step",
         parts=[LONG_RAIL(2), HEAD],
         tools=[tool("allen key 100049")],
         actions=[action("tighten", "long rail", "headboard", "", "allen key 100049", "clockwise", "step 25: connectors tightened")],
         final="frame tightened"),
    page(22, "assembly_step",
         parts=[FOOT, LONG_RAIL(2), CENTRE(2)],
         fasteners=[fastener("100365", "bracket screw", "screw", 2)],
         actions=[
             action("attach", "footboard", "long rail", "", "", "inward", "step 27: footboard pushed onto the far ends of the long rails"),
             action("attach", "footboard", "centre divider", "100365", "", "inward", "step 26: bracket screwed; footboard against the centre divider"),
         ],
         final="footboard on"),
    page(23, "assembly_step",
         parts=[SIDE("left"), HEAD, FOOT],
         actions=[
             action("attach", "left side panel", "headboard", "", "", "inward",
                    "step 28: left side panel fitted between the headboard and footboard"),
             action("attach", "left side panel", "footboard", "", "", "inward", "step 28: left side panel against the footboard"),
         ],
         final="left side panel on"),
    page(24, "assembly_step",
         parts=[SIDE("right"), HEAD, FOOT],
         actions=[
             action("attach", "right side panel", "headboard", "", "", "inward", "step 29: right side panel fitted"),
             action("attach", "right side panel", "footboard", "", "", "inward", "step 29: right side panel against the footboard"),
         ],
         final="box frame closed"),
    page(25, "assembly_step",
         parts=[LEDGE(4), SIDE("left"), SIDE("right")],
         fasteners=[fastener("110789", "ledge screw", "screw", 16)],
         tools=[tool("cross head screwdriver")],
         actions=[
             action("attach", "side ledge", "left side panel", "110789", "cross head screwdriver", "clockwise",
                    "step 30: 2x side ledge screwed inside the left side panel with ledge screws 110789"),
             action("attach", "side ledge", "right side panel", "110789", "cross head screwdriver", "clockwise",
                    "step 30: 2x side ledge screwed inside the right side panel; 16x screw in all"),
         ],
         final="slat ledges along both sides",
         unc=["Info: the mattress must sit inside the frame."]),
    page(26, "assembly_step",
         parts=[HEAD, FOOT],
         fasteners=[fastener("116791", "beam bracket", "bracket", 2), fastener("110789", "ledge screw", "screw", 4)],
         actions=[
             action("insert", "", "headboard", "116791", "", "clockwise", "step 31: beam bracket 116791 screwed to the middle of the headboard"),
             action("insert", "", "footboard", "116791", "", "clockwise", "step 31: beam bracket 116791 screwed to the middle of the footboard"),
         ],
         final="beam brackets at both ends"),
    *[page(n, "assembly_step", unc=["Steps 32-33: support strips and runner adjustments. No new join."]) for n in (27, 28)],
    page(29, "assembly_step",
         parts=[SUPPORT, HEAD, FOOT],
         actions=[
             action("attach", "centre support rail", "headboard", "", "", "down",
                    "steps 34-35: metal centre support rail lowered into the beam bracket at the headboard"),
             action("attach", "centre support rail", "footboard", "", "", "down", "steps 34-35: and into the beam bracket at the footboard"),
         ],
         final="centre support rail in place"),
    page(30, "assembly_step",
         parts=[SIDE("left")],
         fasteners=[fastener("191315", "slat stop", "other", 8)],
         actions=[action("insert", "", "left side panel", "191315", "", "down", "step 36: 8x slat stop 191315 screwed onto the ledges")],
         final="frame ready for a slatted base",
         unc=["Info: the slatted base is sold separately."]),
    page(31, "assembly_step", unc=["Step 37: slatted base (not included) rolled out. Steps 38: drawer building begins; 4 drawers."]),
    *[page(n, "assembly_step", unc=["Steps 38-46: each drawer built from a front, two sides, a back and a bottom (4x)."]) for n in (32, 33, 34)],
    page(35, "assembly_step",
         parts=[DRAWER(4), RUNNER(8)],
         actions=[action("slide", "drawer front", "drawer runner", "", "", "inward",
                         "step 47: 4x finished drawer put on the drawer runners and pushed into the side panel openings")],
         final="drawers in"),
    page(36, "assembly_step", unc=["Finished BRIMNES storage bed; do not sit on open drawers."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "BRIMNES storage bed", (0.05, 0.1, 0.9, 0.8), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Tools and advice", (0.03, 0.03, 0.97, 0.97), parts=False, tools=True, complexity="low", action_="warning")], []),
    3: ("parts_list", [diagram("part_inventory", "Bag 1 hardware", (0.03, 0.03, 0.97, 0.97), ["118331", "110630", "101345", "101359", "122628", "110115"], parts=False, fast=True, complexity="medium")], []),
    4: ("parts_list", [diagram("part_inventory", "Bags 2 and 3", (0.03, 0.03, 0.97, 0.97), ["110789", "100365", "191315", "116791"], fast=True, complexity="medium")], []),
    5: ("parts_list", [diagram("part_inventory", "Metal parts", (0.03, 0.03, 0.97, 0.97), ["118301", "117228", "139505", "4x"], complexity="medium")], []),
    **{n: ("assembly_step", [step_view(f"Steps on page {n}", [], "attach", fast=True, tools=True, arrows=True)], []) for n in range(6, 37)},
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA BRIMNES Storage Bed")
