"""Resolve annotation text selectors against a corpus base text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping


_LINE_LOCATOR = re.compile(r"^(?P<start>[0-9]+)(?:-(?P<end>[0-9]+))?$")


class TargetResolutionError(ValueError):
    """Raised when a target cannot be resolved uniquely against its base text."""


@dataclass(frozen=True)
class BaseTextLine:
    """One displayed line and its character offsets in the canonical base text."""

    number: int
    text: str
    stanza_start: bool
    start: int
    end: int


@dataclass(frozen=True)
class BaseTextIndex:
    """Canonical base text indexed by displayed, nonblank lines."""

    text: str
    lines: tuple[BaseTextLine, ...]


def index_base_text(exact_text: str) -> BaseTextIndex:
    """Index nonblank display lines without discarding raw-text character offsets."""
    lines: list[BaseTextLine] = []
    stanza_start = True
    cursor = 0
    for raw_line in exact_text.splitlines(keepends=True):
        line_text = raw_line[:-1] if raw_line.endswith("\n") else raw_line
        if line_text:
            lines.append(
                BaseTextLine(
                    number=len(lines) + 1,
                    text=line_text,
                    stanza_start=stanza_start,
                    start=cursor,
                    end=cursor + len(line_text),
                )
            )
            stanza_start = False
        else:
            stanza_start = True
        cursor += len(raw_line)

    if exact_text and not exact_text.splitlines(keepends=True):
        lines.append(BaseTextLine(1, exact_text, True, 0, len(exact_text)))
    if not lines:
        raise TargetResolutionError("base-text annotation has no nonblank lines")
    return BaseTextIndex(exact_text, tuple(lines))


def parse_line_locator(value: str, line_count: int) -> dict[str, int] | None:
    """Parse a canonical line locator, returning None for other locator forms."""
    match = _LINE_LOCATOR.fullmatch(value)
    if not match:
        return None
    start = int(match.group("start"))
    end = int(match.group("end") or start)
    if start < 1 or start > end or end > line_count:
        raise TargetResolutionError(
            f"line locator {value!r} is outside the 1-{line_count} base text"
        )
    return {"start": start, "end": end}


def _candidate_bounds(
    target: Mapping[str, Any],
    base: BaseTextIndex,
) -> tuple[int, int, dict[str, int] | None]:
    locator = target["locator"]
    line_range = None
    if locator["scheme"] == "line":
        line_range = parse_line_locator(locator["value"], len(base.lines))
    if line_range is None:
        return 0, len(base.text), None
    first = base.lines[line_range["start"] - 1]
    last = base.lines[line_range["end"] - 1]
    return first.start, last.end, line_range


def _find_occurrences(text: str, needle: str, start: int, end: int) -> list[int]:
    positions: list[int] = []
    position = text.find(needle, start, end)
    while position != -1 and position + len(needle) <= end:
        positions.append(position)
        position = text.find(needle, position + 1, end)
    return positions


def resolve_target(
    target: Mapping[str, Any],
    base: BaseTextIndex,
) -> dict[str, Any]:
    """Resolve one target to an exact match and visible per-line fragments."""
    exact_text = target["exact_text"]
    candidate_start, candidate_end, line_range = _candidate_bounds(target, base)
    matches = _find_occurrences(base.text, exact_text, candidate_start, candidate_end)

    prefix = target.get("prefix")
    if prefix is not None:
        matches = [
            start for start in matches if base.text[:start].endswith(prefix)
        ]
    suffix = target.get("suffix")
    if suffix is not None:
        matches = [
            start
            for start in matches
            if base.text[start + len(exact_text) :].startswith(suffix)
        ]

    if not matches:
        raise TargetResolutionError("exact_text does not occur within the target locator")
    if len(matches) > 1:
        raise TargetResolutionError(
            "exact_text is ambiguous within the target locator; add prefix or suffix context"
        )

    match_start = matches[0]
    match_end = match_start + len(exact_text)
    fragments: list[dict[str, int]] = []
    for line in base.lines:
        fragment_start = max(match_start, line.start)
        fragment_end = min(match_end, line.end)
        if fragment_start < fragment_end:
            fragments.append(
                {
                    "line": line.number,
                    "start": fragment_start - line.start,
                    "end": fragment_end - line.start,
                }
            )

    if not fragments:
        raise TargetResolutionError("exact_text does not contain visible base-text characters")
    return {
        "line_range": line_range,
        "fragments": fragments,
    }
