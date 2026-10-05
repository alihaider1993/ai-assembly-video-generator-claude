"""Read-only loader for the pipeline's per-product JSON (manuals/<id>/page_states.json).

The pipeline is a black box: this module only reads its output files from disk.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, ValidationError

log = logging.getLogger(__name__)

DATA_DIR_ENV = "ASSEMBLY_DATA_DIR"
PAGE_STATES = "page_states.json"
PRODUCT_INFO = "product.json"


class _Model(BaseModel):
    model_config = ConfigDict(extra="ignore")


class VisiblePart(_Model):
    part_uid: Optional[str] = None
    name: Optional[str] = None
    manual_label: Optional[str] = None
    quantity_visible: Optional[int] = None


class VisibleFastener(_Model):
    fastener_uid: Optional[str] = None
    name: Optional[str] = None
    manual_label: Optional[str] = None
    quantity_visible: Optional[int] = None


class VisibleTool(_Model):
    tool_uid: Optional[str] = None
    name: Optional[str] = None


class ObservedAction(_Model):
    action_uid: Optional[str] = None
    action_type: Optional[str] = None
    moving_part_ref: Optional[str] = None
    target_part_ref: Optional[str] = None
    fastener_ref: Optional[str] = None
    tool_ref: Optional[str] = None
    direction_hint: Optional[str] = None
    visual_evidence: Optional[str] = None


class PageState(_Model):
    page_number: Optional[int] = None
    page_type: Optional[str] = None
    visible_parts: list[VisiblePart] = []
    visible_fasteners: list[VisibleFastener] = []
    visible_tools: list[VisibleTool] = []
    observed_actions: list[ObservedAction] = []
    uncertainties: list[str] = []


class ProductSummary(_Model):
    id: str
    title: str
    pages_with_actions: int = 0
    status: Literal["ok", "invalid"]
    reason: Optional[str] = None


class Ref(_Model):
    ref: str
    name: Optional[str] = None


class Step(_Model):
    action_uid: Optional[str] = None
    action_type: Optional[str] = None
    moving_part: Optional[Ref] = None
    target_part: Optional[Ref] = None
    fastener: Optional[Ref] = None
    tool: Optional[Ref] = None
    direction_hint: Optional[str] = None
    visual_evidence: Optional[str] = None


class PageSteps(_Model):
    page_number: Optional[int] = None
    actions: list[Step]
    uncertainties: list[str] = []


class AssemblySteps(_Model):
    id: str
    title: str
    pages: list[PageSteps]


class LoaderError(Exception):
    """An expected failure, reported to clients as a structured error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def data_root() -> Path:
    """ASSEMBLY_DATA_DIR if set, else the repo root containing this package."""
    env = os.environ.get(DATA_DIR_ENV)
    return Path(env) if env else Path(__file__).resolve().parents[1]


def discover_products(root: Path) -> dict[str, Path]:
    """Map product id -> folder for every manuals/<id>/ that has a page_states.json."""
    manuals = root / "manuals"
    if not manuals.is_dir():
        log.warning("no manuals directory under %s", root)
        return {}
    return {
        folder.name: folder
        for folder in sorted(manuals.iterdir())
        if folder.is_dir() and (folder / PAGE_STATES).is_file()
    }


def _title(folder: Path) -> str:
    try:
        title = json.loads((folder / PRODUCT_INFO).read_text(encoding="utf-8")).get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    except (OSError, ValueError, AttributeError):
        pass
    return folder.name.replace("_", " ")


def _load_pages(folder: Path) -> list[PageState]:
    try:
        raw = json.loads((folder / PAGE_STATES).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LoaderError("invalid_product", f"{PAGE_STATES} unreadable: {exc.__class__.__name__}") from exc
    if not isinstance(raw, list):
        raise LoaderError("invalid_product", f"{PAGE_STATES} is not a list of pages")
    try:
        return [PageState.model_validate(page) for page in raw]
    except ValidationError as exc:
        raise LoaderError("invalid_product", f"{PAGE_STATES} has {exc.error_count()} schema error(s)") from exc


def list_products(root: Path) -> list[ProductSummary]:
    summaries = []
    for product_id, folder in discover_products(root).items():
        title = _title(folder)
        try:
            pages = _load_pages(folder)
        except LoaderError as exc:
            log.warning("product %s invalid: %s", product_id, exc.message)
            summaries.append(ProductSummary(id=product_id, title=title, status="invalid", reason=exc.message))
            continue
        count = sum(1 for page in pages if page.observed_actions)
        summaries.append(ProductSummary(id=product_id, title=title, pages_with_actions=count, status="ok"))
    return summaries


def _resolve(ref: Optional[str], names: dict[str, Optional[str]]) -> Optional[Ref]:
    if not ref:
        return None
    return Ref(ref=ref, name=names.get(ref))


def get_assembly_steps(root: Path, product_id: str, include_evidence: bool = False) -> AssemblySteps:
    products = discover_products(root)
    # Only ids found on disk are accepted; raw input is never joined into a path.
    folder = products.get(product_id) if isinstance(product_id, str) else None
    if folder is None:
        raise LoaderError("unknown_product", f"Unknown product_id {product_id!r}. Call list_products for valid ids.")

    pages = []
    for page in _load_pages(folder):
        if not page.observed_actions:
            continue
        parts = {p.part_uid: p.name for p in page.visible_parts if p.part_uid}
        fasteners = {f.fastener_uid: f.name for f in page.visible_fasteners if f.fastener_uid}
        tools = {t.tool_uid: t.name for t in page.visible_tools if t.tool_uid}
        steps = [
            Step(
                action_uid=a.action_uid,
                action_type=a.action_type,
                moving_part=_resolve(a.moving_part_ref, parts),
                target_part=_resolve(a.target_part_ref, parts),
                fastener=_resolve(a.fastener_ref, fasteners),
                tool=_resolve(a.tool_ref, tools),
                direction_hint=a.direction_hint or None,
                visual_evidence=a.visual_evidence if include_evidence else None,
            )
            for a in page.observed_actions
        ]
        pages.append(PageSteps(page_number=page.page_number, actions=steps, uncertainties=page.uncertainties))
    return AssemblySteps(id=product_id, title=_title(folder), pages=pages)
