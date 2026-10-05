# Golden data

Golden files are the ground truth for evaluating the assembly-video pipeline.
They are filled in by hand from the manual PDFs, independently of any model or
pipeline output.

## Rules

1. Golden data records what the MANUAL says, never what the pipeline outputs.
2. A "step" means the manual's numbered step, not a PDF page. Several steps can
   share a page, and some pages have none.
3. Part and fastener ids are the manual's own labels (e.g. dowel A), not
   pipeline ids like P006_001.
4. Washers and accessories belong to the step of the fastener they accompany,
   and are not separate steps.
5. Quantities are per step as printed (e.g. "x4"), plus a separate total from
   the parts list.

## Layout

- `checklists/<product>.md`: a blank checklist per product, filled in while
  reading `manuals/<product>/manual.pdf`.
