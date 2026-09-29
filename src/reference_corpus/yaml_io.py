"""Strict, read-only loading for canonical corpus YAML records."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

import yaml


class CorpusLoadError(ValueError):
    """Raised when a corpus record is unsafe or non-canonical."""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeySafeLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise CorpusLoadError("mapping keys must be strings")
        if key in mapping:
            raise CorpusLoadError(f"duplicate mapping key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _require_json_compatible(value: Any, path: str = "$", seen: set[int] | None = None) -> None:
    if seen is None:
        seen = set()

    if value is None or isinstance(value, (str, bool, int, float)):
        return

    if isinstance(value, dict):
        identity = id(value)
        if identity in seen:
            raise CorpusLoadError(f"{path}: cyclic YAML aliases are not allowed")
        seen.add(identity)
        try:
            for key, child in value.items():
                if not isinstance(key, str):
                    raise CorpusLoadError(f"{path}: mapping keys must be strings")
                _require_json_compatible(child, f"{path}.{key}", seen)
        finally:
            seen.remove(identity)
        return

    if isinstance(value, list):
        identity = id(value)
        if identity in seen:
            raise CorpusLoadError(f"{path}: cyclic YAML aliases are not allowed")
        seen.add(identity)
        try:
            for index, child in enumerate(value):
                _require_json_compatible(child, f"{path}[{index}]", seen)
        finally:
            seen.remove(identity)
        return

    raise CorpusLoadError(
        f"{path}: {type(value).__name__} is not JSON-compatible; quote YAML dates and special values"
    )


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load one canonical YAML mapping without modifying the source file."""

    record_path = Path(path)
    if record_path.suffix != ".yaml":
        raise CorpusLoadError("corpus records must use the .yaml extension")

    raw = record_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CorpusLoadError("UTF-8 BOM is not allowed")

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise CorpusLoadError(f"file is not valid UTF-8: {error}") from error

    if "\r" in text:
        raise CorpusLoadError("line endings must be LF, not CRLF or CR")
    if unicodedata.normalize("NFC", text) != text:
        raise CorpusLoadError("text must use Unicode NFC normalization")

    try:
        parsed = yaml.load(text, Loader=UniqueKeySafeLoader)
    except CorpusLoadError:
        raise
    except yaml.YAMLError as error:
        raise CorpusLoadError(f"invalid YAML: {error}") from error

    if not isinstance(parsed, dict):
        raise CorpusLoadError("YAML document root must be a mapping")

    _require_json_compatible(parsed)
    try:
        json.dumps(parsed, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise CorpusLoadError(f"record is not strict JSON-compatible: {error}") from error

    return parsed
