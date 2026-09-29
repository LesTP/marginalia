"""Deterministic identifiers derived from stable provenance coordinates."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any


class IdentifierError(ValueError):
    """Raised when a record lacks the coordinates needed to derive its ID."""


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n")).strip()


def _digest(prefix: str, components: Iterable[str]) -> str:
    normalized = [_normalize(component) for component in components]
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    suffix = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{suffix}"


def derive_source_id(record: Mapping[str, Any]) -> str:
    try:
        provenance = record["provenance"]
        scheme = provenance["scheme"]
        value = provenance["value"]
    except (KeyError, TypeError) as error:
        raise IdentifierError("source provenance.scheme and provenance.value are required") from error

    if not isinstance(scheme, str) or not isinstance(value, str):
        raise IdentifierError("source provenance coordinates must be strings")
    return _digest("src", (scheme.casefold(), value))


def derive_annotation_id(record: Mapping[str, Any]) -> str:
    try:
        provenance = record["provenance"]
        target = record["target"]
        locator = target["locator"]
        components = (
            target["work_id"],
            target["edition_source_id"],
            locator["scheme"],
            locator["value"],
            record["annotation_type"],
            provenance["local_key"],
        )
    except (KeyError, TypeError) as error:
        raise IdentifierError(
            "annotation work, edition, locator, type, and provenance.local_key are required"
        ) from error

    if not all(isinstance(component, str) for component in components):
        raise IdentifierError("annotation identity coordinates must be strings")
    return _digest("ann", components)


def derive_record_id(record: Mapping[str, Any]) -> str:
    record_type = record.get("record_type")
    if record_type == "source":
        return derive_source_id(record)
    if record_type == "annotation":
        return derive_annotation_id(record)
    raise IdentifierError("record_type must be source or annotation to derive an ID")
