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

Layout modes: **table** needs a top and legs, **chair** needs a leg frame and a back, or side frames (then "front rail", "back rail" and "top rail" are placed by name), **bed** needs posts. Anything else gets the generic layout. If a new kind of product needs its own layout, add one in `v2/rendering/scene_layout_engine.py` next to the existing three. Don't hard-code a single product.

## Rules that matter

- **Quantities.** `quantity_visible` on a parts-list page sets how many copies exist. On a step page, a quantity over 1 caps how many copies the action applies to. Use 1 for a close-up that stands for all copies.
- **"Repeat xN".** Put it in the action's `visual_evidence` exactly like that; it multiplies the copies.
- **Sizes.** Write them into a parts-list `diagram("part_inventory", "Side rail (310 x 60mm) x4", ..., ["1", "4x"])`. The description needs `(A x B mm)` and `visible_labels` needs the part's numeric label. Manuals that print no sizes get default sizes by role.
- **References.** `moving_part_ref` and `target_part_ref` use part names. Every fastener and tool an action names must also be listed on that page.
- **Pre-fitting fasteners.** For dowels or cam bolts going into one part, use action type `insert` with an empty moving ref and the fastener as `fastener_ref`. Insert actions never create part-to-part links.
- **Sub-assemblies.** For a part attached to an already assembled frame, target one of the frame's parts by name (e.g. "long side rail"), not "assembled frame".
- **Product boxes holding several items** (e.g. a pair of chairs): describe one item and say so in the parts-list page's uncertainties.
- **Name parts in full in `visual_evidence`.** Write "left corner bracket", not "bracket": a part named by only some of its words can be matched to a similar part (e.g. the other side frame) and create a link the manual doesn't show.
- **Record what you can't see.** Ambiguities go in `unc=[...]` on that page.
