from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest

from reference_corpus.yaml_io import CorpusLoadError, load_yaml


def test_loads_json_compatible_mapping(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_text('name: Example\ncount: 2\nactive: true\n', encoding="utf-8", newline="\n")

    assert load_yaml(path) == {"name": "Example", "count": 2, "active": True}


def test_preserves_multiline_poem_text(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_text(
        "exact_text: |-\n  First stanza.\n\n  Second stanza.\n",
        encoding="utf-8",
        newline="\n",
    )

    assert load_yaml(path)["exact_text"] == "First stanza.\n\nSecond stanza."


def test_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_text("name: first\nname: second\n", encoding="utf-8", newline="\n")

    with pytest.raises(CorpusLoadError, match="duplicate mapping key"):
        load_yaml(path)


def test_rejects_yaml_native_date(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_text("consulted_on: 2026-09-22\n", encoding="utf-8", newline="\n")

    with pytest.raises(CorpusLoadError, match="not JSON-compatible"):
        load_yaml(path)


def test_rejects_crlf(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_bytes(b"name: Example\r\n")

    with pytest.raises(CorpusLoadError, match="line endings must be LF"):
        load_yaml(path)


def test_rejects_non_nfc_text(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    decomposed = unicodedata.normalize("NFD", "Caf\u00e9")
    path.write_text(f'name: "{decomposed}"\n', encoding="utf-8", newline="\n")

    with pytest.raises(CorpusLoadError, match="Unicode NFC"):
        load_yaml(path)


def test_rejects_yml_extension(tmp_path: Path) -> None:
    path = tmp_path / "record.yml"
    path.write_text("name: Example\n", encoding="utf-8", newline="\n")

    with pytest.raises(CorpusLoadError, match=".yaml extension"):
        load_yaml(path)
