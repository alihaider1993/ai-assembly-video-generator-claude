---
name: describe-manual
description: Read a new assembly manual's pages and write its manuals/<name>/describe.py (the page-by-page vision results the pipeline starts from), then generate the video. Use when the user adds a manual, asks to "run the project on" a manual, or says /describe-manual <name>.
---

# Describe a manual

The pipeline has no vision model. You read the manual's page images and write `manuals/<name>/describe.py`. That file lists every page's parts, fasteners, tools and actions, and the part-list diagrams with sizes. Running it writes `page_states.json` and `diagram_analysis.json`, which the pipeline starts from.

Arguments: the manual's name (a folder under `manuals/`), or a path to a PDF.

## Steps

1. **Set up the folder.** For a PDF path, run `python utils/pdf_to_images.py <pdf> [name]`. This copies the PDF to `manuals/<name>/manual.pdf` and renders `manuals/<name>/pages/page_<n>.png`. If the folder exists but has no `pages/`, run it on `manuals/<name>/manual.pdf`.
2. **Get an overview, then read the details.** Run `python utils/page_sheets.py <name>`. It writes images to `manuals/<name>/sheets/`, each sized as large as the model can use, and lists any blank pages.
   - Read `contact.png` (all pages) to understand the product and the order of steps.
   - Read the two-page sheets `pages_NN_MM.png` for every step.
   - Where there is small print (part-list sizes, part numbers, quantities, "Repeat xN" notes, close-up insets), don't guess from the sheet: run `python utils/page_sheets.py <name> --page N --split 2` (or `--box x0 y0 x1 y1`) and read that at full detail. Always do this for the parts-list pages.
3. **Write `manuals/<name>/describe.py`.** Copy the structure of the existing examples: `manuals/banbury_chair/describe.py` (chair), `kaycie_bed` (bed), `melltorp_table` and `new_table_manual` (tables). Use the helpers from `v2/agents/manual_description.py`. End the file with `write_description(HERE, PAGES, DIAGRAMS)`.
4. **Run it.** Run `python manuals/<name>/describe.py`. Then fix every "action reference(s) could not be resolved" line: each fastener and tool an action uses must be listed on that page.
5. **Generate the video.** Run `python v2/run_mvp_pipeline.py <name> --quiet` in the background; it takes a few minutes, mostly the Blender render. `--quiet` leaves out only Blender's per-frame lines and progress bars; the full output is in `outputs/logs/pipeline.log`. Then run `python utils/layout_summary.py` and check `Layout mode`, the warnings, the steps, and each part's role, size and final position. Open the JSON files in `v2/outputs/json/` only when the summary shows a problem.
6. **Look at the result.** Run `python utils/sample_frames.py <name>` and read `outputs/checks/<name>_frames.png`. Check that parts end up where the manual shows them. If a frame is unclear, look at that moment with `--at <seconds>`. Fix the description or the layout and re-run if not.

## Naming parts so they get placed

The scene layout places parts by the **role** in their name (`PART_ROLES` in `v2/agents/part_shape_extractor_agent.py`). A part with no role ends up in the generic exploded ring, so use these words:

| Role | Name words | Placed as |
|---|---|---|
| top | "tabletop", "top panel", "worktop", "desktop" | table built upside down on it, turned over at the end |
| leg | "leg" | table corners, bed centre legs |
| post | "headboard foot/post", "footboard foot/post" | bed corners |
| leg_frame | "leg frame" | chair front U-frame |
| side_frame | "side frame" | chair side (front leg, back leg and rails); name them "left side frame" / "right side frame" |
| back | "chair back", "backrest" | chair back with its back legs |
| seat | "seat" | chair seat |
| slat | "slat" | bed base; on a side-frame chair, back slats standing on the back rail |
| rail | "rail", "apron" | Tables: "long"/"side" go along the long edges, "end"/"short" across the ends, "cross" across the inside, any other rail inside lengthways. Beds: "headboard rail" stacked in the headboard, "side rail" down the sides |
| stretcher | "stretcher" | low H-frame between table legs ("long stretcher" down the middle) |
| bracket | "bracket" | inside table corners |
| foot | "foot", "feet" | short feet under a sofa, cabinet or bed base |
| side_panel | "side panel", "end panel", "gable" | carcass sides at left/right |
| divider | "divider", "partition", "middle panel" | upright panels spaced evenly between the sides |
| back_panel / front_panel | "back panel", "hardboard", "front panel" | behind / in front of the sides, sized to cover them |
| shelf | "shelf", "bottom panel", "base panel" | bottom on the plinth or floor, shelves evenly up each compartment |
| lid | "lid" | on top, like a top panel; hinges go along its back edge |
| plinth | "plinth", "kickboard", "base rail" | on the floor at the front, under the bottom |
| door | "door" | front opening, side by side (one per compartment when counts match) |
| drawer_front / drawer_side / drawer_back / drawer_bottom | "drawer front" etc. | drawers in rows in the front opening (above the doors when both); one front, two sides, a back and a bottom per drawer |
| runner | "drawer runner", "drawer slide" | two per drawer, inside the carcass sides |
| handle / hinge | "handle", "knob", "pull" / "hinge" | on the fronts; two hinges per door at its outer edge |
| end_board | "headboard", "footboard" (not their rails or posts) | a bed end as one board |
| body | "sofa", "chaise", "armchair", "ottoman", "couch" | upholstered bodies side by side, feet under them, joining kit in the joint |
| cushion / back_cushion | "seat cushion", "cushion", "mattress" / "back cushion" | on top of the body / standing on its back edge |

One layout (`v2/rendering/general_layout.py`) places every product as a box frame from these roles, the parts each part is joined to, and name words: front/back/head/foot, left/right, side/long, end/short, cross, top, bottom. Parts with no role are classed by their proportions. Panels named "side" stand at the sides, and panels joined between two sides (shelves, a bottom) lie flat. So get the joins right. If a new kind of product comes out wrong, improve that layout. Don't add a layout for one product.

## Rules that matter

- **Quantities.** `quantity_visible` on a parts-list page sets how many copies exist. On a step page, a quantity over 1 caps how many copies the action applies to. Use 1 for a close-up that stands for all copies.
- **"Repeat xN".** Put it in the action's `visual_evidence` exactly like that; it multiplies the copies.
- **Sizes.** Write them into a parts-list `diagram("part_inventory", "Side rail (310 x 60mm) x4", ..., ["1", "4x"])`. The description needs `(A x B mm)` and `visible_labels` needs the part's numeric label. Manuals that print no sizes get default sizes by role.
- **References.** `moving_part_ref` and `target_part_ref` use part names. Every fastener and tool an action names must also be listed on that page.
- **Pre-fitting fasteners.** For dowels or cam bolts going into one part, use action type `insert` with an empty moving ref and the fastener as `fastener_ref`. Insert actions never create part-to-part links.
- **Sub-assemblies.** For a part attached to an already assembled frame, target one of the frame's parts by name (e.g. "long side rail"), not "assembled frame".
- **Product boxes holding several items** (e.g. a pair of chairs): describe one item and say so in the parts-list page's uncertainties.
- **Name parts in full in `visual_evidence`.** Write "left corner bracket", not "bracket": a part named by only some of its words can be matched to a similar part (e.g. the other side frame) and create a link the manual doesn't show.
- **Only real parts of the finished piece.** Don't list temporary jigs, spacing templates, packaging or tools as parts; mention them in `unc=[...]`.
- **Turning the piece over is not a join.** Don't make a flip or rotate action between two parts; note the turn in `unc=[...]`.
- **Use the plainest role word.** A rail across the top of a chair back is a "top rail", not a "chair back"; "chair back" is a whole backrest with its back legs.
- **Record what you can't see.** Ambiguities go in `unc=[...]` on that page.
- **Drawings can be rotated.** Early steps often show a sub-assembly lying down or on its side. Name each part by how it sits in the **finished** piece (check the cover and final pages): a long piece that ends up upright is an upright, not a rail, and pieces that end up running across are slats or rails.
- **Parts that come off and go back on** (an armrest moved from a sofa to a new section): list the part, note the removal in `unc=[...]`, and record the refit as normal actions.
- **Count every bar and rail** against the fastener counts: 4 long bolts in pairs usually mean two crossbars.
- **Sizes when none are printed.** Give `size=(width, depth, height)` in mm, as the part sits in the finished piece, estimated from the drawings and the product's usual proportions (a chaise longue is long, an armchair seat is about 400 mm high). Without it every part of a role gets the same default and proportions are lost.
- **Leaning and curved parts.** `tilt=` (degrees) leans a fitted part back: a reclined chair back, or a seat sloping to the back. `profile={"path": [(y, z), ...], "thickness": mm}` traces a bent or curved part in its side view (y from front to back, z up, mm) for bentwood frames, curved uprights and armrests; `"plane": "front"` traces it in the front view (x, z). The renderer draws the outline instead of a box.
