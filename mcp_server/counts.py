"""Counts read from an action's visual_evidence text (vision output, not the manual).

Digit counts only: "repeat x4" and "24x screw B". Counts written as words are not
captured, and nothing here guesses which part or fastener a count belongs to.
"""

from __future__ import annotations

import re
from typing import Optional

REPEAT = re.compile(r"\brepeat\s*x\s*(\d+)", re.IGNORECASE)
REPEAT_QUALIFIER = re.compile(r"\b(total|each|per|across)\b", re.IGNORECASE)
# "24x screw B": digits glued to x, then a space. Not "M6x" or "1.5x" (lookbehind).
QUANTITY = re.compile(r"(?<![\w./])(\d+)x\s+", re.IGNORECASE)
CLAUSE_END = re.compile(r"[,;]| and ", re.IGNORECASE)
MAX_TEXT = 40


def parse_repeat(evidence: Optional[str]) -> Optional[int]:
    """N from "repeat xN", or None when absent, qualified, or contradictory."""
    if not evidence:
        return None
    counts = set()
    for match in REPEAT.finditer(evidence):
        clause = CLAUSE_END.split(evidence[match.end():], maxsplit=1)[0]
        if REPEAT_QUALIFIER.search(clause):
            return None
        counts.add(int(match.group(1)))
    return counts.pop() if len(counts) == 1 else None


def parse_quantities(evidence: Optional[str]) -> list[tuple[int, str]]:
    """(count, short text) for each "Nx <words>"; dimensions such as "4 x 35mm" are skipped."""
    if not evidence:
        return []
    matches = list(QUANTITY.finditer(evidence))
    found = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(evidence)
        rest = evidence[match.end():end]
        if rest[:1].isdigit():  # "4x 35mm", "2x 1/4 in": a size, not a thing
            continue
        text = CLAUSE_END.split(rest, maxsplit=1)[0][:MAX_TEXT].strip()
        if text:
            found.append((int(match.group(1)), text))
    return found
