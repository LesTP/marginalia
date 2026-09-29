from __future__ import annotations

import shutil
from pathlib import Path

from reference_corpus.validate import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_validates_manifest(capsys) -> None:
    code = main([str(PROJECT_ROOT / "examples" / "valid" / "basic" / "corpus.yaml")])

    assert code == 0
    assert "valid:" in capsys.readouterr().out


def test_cli_returns_one_for_invalid_corpus(tmp_path: Path, capsys) -> None:
    source = PROJECT_ROOT / "examples" / "valid" / "basic"
    destination = tmp_path / "basic"
    shutil.copytree(source, destination)
    (destination / "records" / "sources" / "river-poems-edition.yaml").unlink()

    code = main([str(destination / "corpus.yaml")])

    assert code == 1
    assert "does not exist" in capsys.readouterr().err


def test_cli_returns_two_for_missing_schema_directory(tmp_path: Path, capsys) -> None:
    code = main(["--check-schemas", str(tmp_path / "missing")])

    assert code == 2
    assert "missing schemas" in capsys.readouterr().err


def test_cli_shows_derived_id_without_writing(capsys) -> None:
    record = PROJECT_ROOT / "examples" / "valid" / "basic" / "records" / "sources" / "river-poems-edition.yaml"
    before = record.read_bytes()

    code = main(["--show-derived-id", str(record)])

    assert code == 0
    assert capsys.readouterr().out.strip() == "src_7b0f4b601ea6737c"
    assert record.read_bytes() == before
