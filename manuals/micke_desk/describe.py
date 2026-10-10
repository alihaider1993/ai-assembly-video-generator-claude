"""Vision results for the IKEA MICKE desk manual (24 pages).

Run: python manuals/micke_desk/describe.py

Pages 9-16 build the desk with the metal side frame on the right; pages 17-24
repeat them mirrored (frame on the left). Only the first branch is described.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "v2" / "agents"))

from manual_description import action, diagram, fastener, page, part, tool, write_description  # noqa: E402

# No sizes are printed; estimated for the 73 x 50 cm desk, 75 cm high.
DESKTOP = lambda desc: part(
    "", "desktop", desc, "panel", "wood", 1,
    [("hole", 1, "round cable outlet hole near the back"), ("hole", 4, "cam bolt holes in the underside")],
    "bottom", size=(730, 500, 18))
SIDE_PANEL = lambda desc, pos="center": part(
    "", "left side panel", desc, "panel", "wood", 1,
    [("hole", 6, "cam bolt holes along the top and back edges"), ("hole", 2, "drawer slide screw holes")],
    pos, size=(18, 500, 732))
SIDE_RAIL = lambda desc, pos="center": part(
    "", "right side rail", desc, "beam", "wood", 1,
    [("hole", 3, "bolt holes for the metal side frame"), ("hole", 2, "drawer slide screw holes")],
    pos, size=(500, 18, 130))
BACK_RAIL = lambda desc, pos="bottom": part(
    "", "back rail", desc, "beam", "wood", 1,
    [("hole", 4, "cam lock holes at both ends"), ("hole", 2, "dowel holes along one long edge")],
    pos, size=(694, 18, 150))
CABLE_SHELF = lambda desc, pos="center": part(
    "", "cable shelf", desc, "panel", "wood", 1,
    [("hole", 4, "dowel holes along both long edges")], pos, size=(694, 120, 18))
LIP_RAIL = lambda desc: part(
    "", "lip rail", desc, "beam", "wood", 1,
    [("hole", 2, "dowel holes"), ("hole", 2, "cam lock holes at the ends")], "top", size=(694, 18, 40))
SIDE_FRAME = lambda desc: part(
    "", "right side frame", desc, "frame", "metal", 1,
    [("hole", 3, "bolt holes in the upper bar")], "right", size=(25, 480, 732))
DRAWER_FRONT = lambda desc: part(
    "", "drawer front", desc, "panel", "wood", 1,
    [("slot", 1, "groove along the inner face for the drawer bottom"), ("hole", 2, "cam bolt holes at the ends")],
    "bottom", size=(660, 18, 100))
DRAWER_SIDE = lambda desc, qty=2: part(
    "", "drawer side", desc, "panel", "wood", qty,
    [("slot", 1, "groove for the drawer bottom"), ("hole", 1, "cam lock hole")], "center", size=(12, 430, 90))
DRAWER_BOTTOM = part("", "drawer bottom", "thin fibreboard drawer bottom slid into the grooves", "panel", "fibreboard", 1,
                     [], "center", size=(620, 420, 3))
DRAWER_BACK = part("", "drawer back", "narrow drawer back board slid in between the drawer sides", "panel", "wood", 1,
                   [("hole", 2, "nail holes at the ends")], "center", size=(616, 12, 75))
DRAWER_RUNNER = lambda qty=2: part(
    "112482", "drawer runner", "metal runner with a roller at its back end, fixed along a drawer side",
    "rail", "metal", qty, [("hole", 2, "screw holes")], "center")
DRAWER_SLIDE = lambda qty=1: part(
    "112482", "drawer slide", "metal carcass slide with a roller at its front end",
    "rail", "metal", qty, [("hole", 2, "screw holes")], "center")

PAGES = [
    page(1, "cover",
         final="MICKE desk: desktop on a full-height side panel on the left and a closed metal side frame on the right, with a drawer under the top",
         unc=["Cover shows the desk twice, with the drawer pulled out and pushed in."]),
    page(2, "warning",
         unc=["Tools needed (flat and cross-head screwdrivers, hammer) and general advice. No assembly action."]),
    page(3, "parts_list",
         fasteners=[
             fastener("100086", "frame bolt", "bolt", "3x"),
             fastener("110519", "drawer pin", "nail", "2x"),
             fastener("118331", "cam bolt", "bolt", "14x"),
             fastener("110126", "top cam lock", "cam", "4x"),
             fastener("103430", "cam lock", "cam", "8x"),
             fastener("103114", "drawer cam lock", "cam", "2x"),
             fastener("101344", "wooden dowel", "dowel", "12x"),
             fastener("100365", "runner screw", "screw", "8x"),
             fastener("153549", "floor glide", "other", "2x"),
             fastener("112519", "bumper", "other", "1x"),
             fastener("10081375", "frame foot pad", "other", "1x"),
         ],
         tools=[tool("allen key 100092"), tool("extension bar 121030")],
         unc=["Panels and the metal frame are not shown in the inventory; only hardware.",
              "112519 is one sheet of 4 adhesive bumpers; 10081375 one sheet of 2 hexagonal pads."]),
    page(4, "parts_list",
         parts=[DRAWER_RUNNER(2), DRAWER_SLIDE(2)],
         fasteners=[fastener("121304", "cable grommet", "other", "1x")],
         unc=["Runner set 112482: two drawer runners and two carcass drawer slides, drawn as one set (1x)."]),
    page(5, "assembly_step",
         parts=[DRAWER_FRONT("drawer front lying face down on a rug, groove up"),
                DRAWER_SIDE("two drawer sides held upright over the ends of the drawer front")],
         fasteners=[fastener("118331", "cam bolt", "bolt", 2), fastener("101344", "wooden dowel", "dowel", 2)],
         tools=[tool("screwdriver")],
         actions=[
             action("insert", "", "drawer front", "118331", "screwdriver", "clockwise",
                    "2x cam bolt 118331 screwed into the ends of the drawer front (step 1)"),
             action("insert", "", "drawer side", "101344", "", "down",
                    "2x wooden dowel 101344 pushed into the lower end of each drawer side (step 2)"),
             action("attach", "drawer side", "drawer front", "101344", "", "down",
                    "two drawer sides lowered onto the ends of the drawer front over the cam bolts (step 2)"),
         ],
         final="drawer front with both drawer sides standing on its ends",
         unc=["Step 1 inset shows the finished drawer and its parts (1x) to say which panels these are."]),
    page(6, "assembly_step",
         parts=[DRAWER_FRONT("drawer front with drawer sides fitted, lying face down"),
                DRAWER_SIDE("drawer sides upright on the drawer front"), DRAWER_BOTTOM],
         fasteners=[fastener("103114", "drawer cam lock", "cam", 2)],
         tools=[tool("screwdriver")],
         actions=[
             action("tighten", "drawer side", "drawer front", "103114", "screwdriver", "clockwise",
                    "2x drawer cam lock 103114 pushed into each drawer side and turned to lock onto the cam bolt; 110126 and 103430 crossed out (step 3)"),
             action("slide", "drawer bottom", "drawer side", "", "", "inward",
                    "drawer bottom slid into the grooves of the drawer sides and drawer front, decorative side down (step 4)"),
         ],
         final="drawer box of front, two sides and bottom",
         unc=["Step 4 shows the box turned over (curved arrow) before the bottom is slid in."]),
    page(7, "assembly_step",
         parts=[DRAWER_SIDE("drawer sides of the drawer box"), DRAWER_BACK],
         fasteners=[fastener("110519", "drawer pin", "nail", 2)],
         tools=[tool("hammer")],
         actions=[
             action("slide", "drawer back", "drawer side", "", "", "down",
                    "drawer back slid down between the drawer sides over the drawer bottom (step 5)"),
             action("insert", "drawer back", "drawer side", "110519", "hammer", "inward",
                    "2x drawer pin 110519 hammered through the drawer sides into the drawer back (step 6)"),
         ],
         final="closed drawer box",
         unc=["Info panel shows the drawer pin going straight into the end of the back."]),
    page(8, "assembly_step",
         parts=[DRAWER_SIDE("drawer sides of the drawer box"), DRAWER_RUNNER(2)],
         fasteners=[fastener("100365", "runner screw", "screw", 4)],
         tools=[tool("screwdriver")],
         actions=[
             action("place", "drawer runner", "drawer side", "", "", "down",
                    "2x drawer runner laid along the bottom edge of each drawer side (step 7)"),
             action("tighten", "drawer runner", "drawer side", "100365", "screwdriver", "clockwise",
                    "4x runner screw 100365 driven through the drawer runners into the drawer sides (step 8)"),
         ],
         final="drawer with a runner on each side"),
    page(9, "assembly_step",
         parts=[BACK_RAIL("back rail lying flat on a rug, holes up"),
                CABLE_SHELF("cable shelf held on its edge over the back rail"),
                LIP_RAIL("narrow lip rail with cam lock holes held over the cable shelf")],
         fasteners=[fastener("101344", "wooden dowel", "dowel", 4)],
         actions=[
             action("insert", "", "back rail", "101344", "", "down",
                    "2x wooden dowel 101344 pushed into the back rail (step 9)"),
             action("attach", "cable shelf", "back rail", "101344", "", "down",
                    "cable shelf pressed onto the dowels along the back rail (step 9)"),
             action("insert", "", "cable shelf", "101344", "", "down",
                    "2x wooden dowel 101344 pushed into the free edge of the cable shelf (step 10)"),
             action("attach", "lip rail", "cable shelf", "101344", "", "down",
                    "lip rail pressed onto the cable shelf, cam lock holes facing as the inset shows (step 10)"),
         ],
         final="back rail, cable shelf and lip rail joined into one I-shaped piece",
         unc=["Top insets: with the frame on the right continue here; with the frame on the left go to page 17 (mirrored steps).",
              "The I-shaped piece is drawn lying down; in the desk the back rail stands upright at the back under the desktop."]),
    page(10, "assembly_step",
         parts=[SIDE_PANEL("left side panel lying flat"), SIDE_RAIL("right side rail lying flat"), DRAWER_SLIDE(2)],
         fasteners=[fastener("118331", "cam bolt", "bolt", 8), fastener("100365", "runner screw", "screw", 4)],
         tools=[tool("screwdriver")],
         actions=[
             action("insert", "", "left side panel", "118331", "screwdriver", "clockwise",
                    "8x cam bolt 118331 screwed into the left side panel and the right side rail (step 11)"),
             action("insert", "", "right side rail", "118331", "screwdriver", "clockwise",
                    "cam bolt 118331 screwed into the right side rail (step 11)"),
             action("tighten", "drawer slide", "left side panel", "100365", "screwdriver", "clockwise",
                    "1x drawer slide screwed to the inner face of the left side panel with 2x runner screw 100365 (step 12)"),
             action("tighten", "drawer slide", "right side rail", "100365", "screwdriver", "clockwise",
                    "1x drawer slide screwed to the inner face of the right side rail with 2x runner screw 100365 (step 12)"),
         ],
         final="left side panel and right side rail each with cam bolts and a drawer slide"),
    page(11, "assembly_step",
         parts=[SIDE_PANEL("left side panel turned onto the end of the back rail piece"),
                SIDE_RAIL("right side rail swung up onto the other end"),
                BACK_RAIL("back rail of the I-shaped piece"), CABLE_SHELF("cable shelf of the I-shaped piece")],
         fasteners=[fastener("101344", "wooden dowel", "dowel", 2), fastener("103430", "cam lock", "cam", 8)],
         tools=[tool("screwdriver")],
         actions=[
             action("insert", "", "right side rail", "101344", "", "inward",
                    "2x wooden dowel 101344 pushed into the end of the right side rail (step 13)"),
             action("attach", "left side panel", "back rail", "", "", "inward",
                    "left side panel turned onto the end of the back rail and cable shelf (step 13, curved arrow)"),
             action("attach", "right side rail", "back rail", "101344", "", "inward",
                    "right side rail swung up onto the other end of the back rail (step 13, curved arrow)"),
             action("tighten", "left side panel", "back rail", "103430", "screwdriver", "clockwise",
                    "8x cam lock 103430 pushed into the back rail and lip rail and turned onto the cam bolts; 110126 crossed out (step 14)"),
         ],
         final="left side panel and right side rail joined by the back rail piece"),
    page(12, "assembly_step",
         parts=[SIDE_PANEL("left side panel"), SIDE_RAIL("right side rail"), SIDE_FRAME("closed rectangular metal tube frame")],
         fasteners=[fastener("101344", "wooden dowel", "dowel", 4), fastener("100086", "frame bolt", "bolt", 3)],
         tools=[tool("allen key 100092"), tool("extension bar 121030")],
         actions=[
             action("insert", "", "left side panel", "101344", "", "inward",
                    "4x wooden dowel 101344 pushed into the top edges of the left side panel and right side rail (step 15)"),
             action("attach", "right side frame", "right side rail", "100086", "allen key 100092", "clockwise",
                    "right side frame held against the right side rail and fixed with 3x frame bolt 100086 turned with allen key 100092 in extension bar 121030 (step 16)"),
         ],
         final="desk frame: left side panel, back rail piece, right side rail and metal side frame",
         unc=["Step 16 inset: allen key 100092 slots into extension bar 121030 at position 4."]),
    page(13, "assembly_step",
         parts=[DESKTOP("desktop lying face down"), SIDE_PANEL("left side panel of the upturned frame"),
                SIDE_RAIL("right side rail of the upturned frame")],
         fasteners=[fastener("118331", "cam bolt", "bolt", 4)],
         tools=[tool("screwdriver")],
         actions=[
             action("insert", "", "desktop", "118331", "screwdriver", "clockwise",
                    "4x cam bolt 118331 screwed into the underside of the desktop (step 17)"),
             action("attach", "desktop", "left side panel", "", "", "inward",
                    "desktop pushed onto the dowels at the top of the left side panel (step 18)"),
             action("attach", "desktop", "right side rail", "", "", "inward",
                    "desktop pushed onto the dowels at the top of the right side rail (step 18)"),
         ],
         final="desktop fitted to the frame, desk upside down",
         unc=["The frame is turned upside down onto the desktop; turning it is not a join."]),
    page(14, "assembly_step",
         parts=[DESKTOP("desktop"), SIDE_PANEL("left side panel"), SIDE_FRAME("right side frame")],
         fasteners=[fastener("110126", "top cam lock", "cam", 4), fastener("10081375", "frame foot pad", "other", 2)],
         tools=[tool("screwdriver")],
         actions=[
             action("tighten", "desktop", "left side panel", "110126", "screwdriver", "clockwise",
                    "4x top cam lock 110126 pushed into the left side panel and right side rail and turned onto the desktop cam bolts (step 19)"),
             action("insert", "", "right side frame", "10081375", "", "inward",
                    "2x frame foot pad 10081375 pressed onto the right side frame; adhesive bumper sheet crossed out (step 20)"),
         ],
         final="desktop locked to the frame"),
    page(15, "assembly_step",
         parts=[SIDE_PANEL("left side panel"), DRAWER_FRONT("drawer front of the finished drawer"), DRAWER_SLIDE(2)],
         fasteners=[fastener("153549", "floor glide", "other", 2)],
         actions=[
             action("insert", "", "left side panel", "153549", "", "inward",
                    "2x floor glide 153549 pressed into the bottom edge of the left side panel (step 21)"),
             action("slide", "drawer front", "drawer slide", "", "", "inward",
                    "drawer lifted onto the drawer slides and pushed in under the desktop (step 22)"),
         ],
         final="desk standing upright with the drawer in place",
         unc=["Step 22 inset shows the drawer runner roller dropping in behind the drawer slide roller."]),
    page(16, "assembly_step",
         parts=[DESKTOP("desktop of the finished desk"), SIDE_RAIL("right side rail")],
         fasteners=[fastener("121304", "cable grommet", "other", 1), fastener("112519", "bumper", "other", 4)],
         actions=[
             action("insert", "", "desktop", "121304", "", "down",
                    "1x cable grommet 121304 pressed into the hole in the desktop (step 23)"),
             action("insert", "", "right side rail", "112519", "", "inward",
                    "4x bumper 112519 stuck onto the front edges of the right side rail and left side panel as drawer stops (step 23)"),
         ],
         final="finished MICKE desk"),
    page(17, "unknown", unc=["Start of the mirrored branch (metal frame on the left): steps 9-10 repeated. Not described."]),
    page(18, "unknown", unc=["Mirrored branch: steps 11-12. Not described."]),
    page(19, "unknown", unc=["Mirrored branch: steps 13-14. Not described."]),
    page(20, "unknown", unc=["Mirrored branch: steps 15-16. Not described."]),
    page(21, "unknown", unc=["Mirrored branch: steps 17-18. Not described."]),
    page(22, "unknown", unc=["Mirrored branch: steps 19-20. Not described."]),
    page(23, "unknown", unc=["Mirrored branch: steps 21-22. Not described."]),
    page(24, "unknown", unc=["Mirrored branch: step 23. Not described."]),
]


def step_view(desc, labels, act, region=(0.03, 0.05, 0.97, 0.95), **kw):
    return diagram("assembly_view", desc, region, labels, action_=act, **kw)


DIAGRAMS = {
    1: ("cover", [diagram("final_product", "MICKE desk shown with the drawer out and in", (0.05, 0.05, 0.9, 0.9), complexity="low", conf=0.95)], []),
    2: ("warning", [diagram("warning", "Tools and general advice", (0.03, 0.02, 0.97, 0.98), parts=False, tools=True, complexity="low", action_="warning")], []),
    3: ("parts_list", [
        diagram("part_inventory", "Frame bolt 3x", (0.03, 0.03, 0.1, 0.27), ["100086", "3x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Drawer pin 2x", (0.11, 0.08, 0.19, 0.27), ["110519", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Cam bolt 14x", (0.2, 0.08, 0.27, 0.27), ["118331", "14x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Cam locks 4x / 8x / 2x", (0.28, 0.15, 0.6, 0.27), ["110126", "103430", "103114", "4x", "8x", "2x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Extension bar and allen key", (0.03, 0.33, 0.45, 0.5), ["121030", "100092", "1x"], parts=False, tools=True, complexity="low"),
        diagram("part_inventory", "Wooden dowel 12x, runner screw 8x", (0.45, 0.4, 0.6, 0.5), ["101344", "100365", "12x", "8x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Floor glide 2x, bumper sheet, foot pad sheet", (0.03, 0.57, 0.6, 0.73), ["153549", "112519", "10081375", "2x", "1x"], parts=False, fast=True, complexity="low"),
    ], []),
    4: ("parts_list", [
        diagram("part_inventory", "Cable grommet 1x", (0.05, 0.03, 0.8, 0.3), ["121304", "1x"], parts=False, fast=True, complexity="low"),
        diagram("part_inventory", "Drawer runner set 1x", (0.05, 0.35, 0.95, 0.75), ["112482", "1x"], complexity="low"),
    ], []),
    5: ("assembly_step", [step_view("Cam bolts into the drawer front; drawer sides lowered onto it with dowels", ["1", "2", "2x", "118331", "101344"], "attach", fast=True, arrows=True)], []),
    6: ("assembly_step", [step_view("Drawer cam locks turned; drawer bottom slid into the grooves", ["3", "4", "2x", "103114"], "slide", fast=True, tools=True, arrows=True)], []),
    7: ("assembly_step", [step_view("Drawer back slid in and pinned", ["5", "6", "2x", "110519"], "attach", fast=True, tools=True, arrows=True)], []),
    8: ("assembly_step", [step_view("Drawer runners screwed to the drawer sides", ["7", "8", "4x", "100365"], "attach", fast=True, tools=True, arrows=True)], []),
    9: ("assembly_step", [step_view("Back rail, cable shelf and lip rail joined with dowels", ["9", "10", "2x", "101344"], "attach", fast=True, arrows=True)], ["Branch choice insets at the top."]),
    10: ("assembly_step", [step_view("Cam bolts and drawer slides on the left side panel and right side rail", ["11", "12", "8x", "1x", "118331", "100365"], "attach", fast=True, tools=True, arrows=True)], []),
    11: ("assembly_step", [step_view("Side panel and end rail joined to the back rail piece; cam locks", ["13", "14", "2x", "8x", "101344", "103430"], "attach", fast=True, tools=True, arrows=True)], []),
    12: ("assembly_step", [step_view("Dowels in the top edges; metal side frame bolted to the end rail", ["15", "16", "4x", "3x", "101344", "100086", "100092", "121030"], "attach", fast=True, tools=True, arrows=True)], []),
    13: ("assembly_step", [step_view("Cam bolts into the desktop; desktop fitted", ["17", "18", "4x", "118331"], "attach", fast=True, arrows=True)], []),
    14: ("assembly_step", [step_view("Top cam locks turned; foot pads on the metal frame", ["19", "20", "4x", "2x", "110126", "10081375"], "tighten", fast=True, tools=True, arrows=True)], []),
    15: ("assembly_step", [step_view("Floor glides; drawer put on its slides", ["21", "22", "2x", "153549"], "slide", fast=True, arrows=True)], []),
    16: ("assembly_step", [step_view("Cable grommet and drawer bumpers", ["23", "1x", "4x", "121304", "112519"], "insert", fast=True, arrows=True)], []),
    **{n: ("unknown", [], ["Mirrored branch, not described."]) for n in range(17, 25)},
}


if __name__ == "__main__":
    write_description(HERE, PAGES, DIAGRAMS, title="IKEA MICKE Desk")
