from __future__ import annotations

import shutil
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from reference_corpus.targets import index_base_text, resolve_target
from reference_corpus.validate import CorpusValidator
from reference_corpus.yaml_io import load_yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT_ROOT / "examples" / "valid"
CORPORA = PROJECT_ROOT / "corpora"
REAL_CORPUS_MANIFESTS = sorted(CORPORA.glob("*/corpus.yaml"))


def _copy_example(tmp_path: Path, name: str) -> Path:
    destination = tmp_path / name
    shutil.copytree(EXAMPLES / name, destination)
    return destination / "corpus.yaml"


def _copy_yeats(tmp_path: Path) -> Path:
    destination = tmp_path / "yeats"
    shutil.copytree(CORPORA / "yeats-song-of-wandering-aengus", destination)
    return destination / "corpus.yaml"


def _copy_dual_text_yeats(tmp_path: Path) -> Path:
    manifest_path = _copy_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    manifest["presentation"].update(
        {
            "texts": [
                {
                    "id": "edition-faithful",
                    "label": "Edition-faithful text",
                    "description": "The controlling historical transcription.",
                    "type": "canonical-target",
                },
                {
                    "id": "modernized",
                    "label": "Modernized text",
                    "description": "A conservative editorial derivation.",
                    "type": "editorial-derivation",
                    "derived_from": "edition-faithful",
                },
            ],
            "default_text": "edition-faithful",
        }
    )
    _write_yaml(manifest_path, manifest)
    for relative in manifest["annotations"]:
        annotation_path = manifest_path.parent / relative
        annotation = load_yaml(annotation_path)
        annotation["target"]["display_selectors"] = [
            {
                "text_id": "modernized",
                "exact_text": annotation["target"]["exact_text"],
            }
        ]
        _write_yaml(annotation_path, annotation)
    return manifest_path


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )


@pytest.mark.parametrize("name", ["basic", "limited-access", "contested-interpretation"])
def test_valid_examples(name: str) -> None:
    validator = CorpusValidator()

    assert validator.validate_manifest(EXAMPLES / name / "corpus.yaml") == []


def test_real_corpus_catalog_is_not_empty() -> None:
    assert REAL_CORPUS_MANIFESTS


@pytest.mark.parametrize(
    "manifest",
    REAL_CORPUS_MANIFESTS,
    ids=lambda path: path.parent.name,
)
def test_valid_real_corpora(manifest: Path) -> None:
    assert CorpusValidator().validate_manifest(manifest) == []


def test_wandering_aengus_targets_resolve_in_base_text() -> None:
    corpus_root = CORPORA / "yeats-song-of-wandering-aengus"
    manifest = load_yaml(corpus_root / "corpus.yaml")
    annotation_paths = [corpus_root / path for path in manifest["annotations"]]
    annotations = [load_yaml(path) for path in annotation_paths]
    base = next(item for item in annotations if item["provenance"]["local_key"] == "base-text")
    base_index = index_base_text(base["target"]["exact_text"])

    assert len(manifest["sources"]) == 12
    assert len(annotations) == 15
    assert len(base_index.lines) == 24

    for annotation in annotations:
        target = annotation["target"]
        resolved = resolve_target(target, base_index)

        assert target["work_id"] == "work_the_song_of_wandering_aengus"
        assert resolved["fragments"]
        assert annotation["review"]["state"] == "human-reviewed"


def test_dual_text_view_resolves_all_display_selectors(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)

    assert CorpusValidator().validate_manifest(manifest_path) == []


def test_witness_presentation_missing_author_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    manifest["presentation"]["texts"][0]["witness_presentation"] = {"show_author": True}
    _write_yaml(manifest_path, manifest)
    source_path = manifest_path.parent / "records" / "sources" / "base-text-witness.yaml"
    source = load_yaml(source_path)
    for contributor in source["bibliography"]["contributors"]:
        if contributor["role"] == "author":
            contributor["role"] = "editor"
    _write_yaml(source_path, source)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any(
        item.path == "$.presentation.texts[0].witness_presentation.show_author"
        and "base witness has none" in item.message
        for item in diagnostics
    )


def test_witness_presentation_missing_issued_date_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    manifest["presentation"]["texts"][0]["witness_presentation"] = {"show_issued": True}
    _write_yaml(manifest_path, manifest)
    source_path = manifest_path.parent / "records" / "sources" / "base-text-witness.yaml"
    source = load_yaml(source_path)
    source["bibliography"].pop("issued", None)
    _write_yaml(source_path, source)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any(
        item.path == "$.presentation.texts[0].witness_presentation.show_issued"
        and "base witness has none" in item.message
        for item in diagnostics
    )


def test_missing_display_selector_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "future-vow.yaml"
    annotation = load_yaml(annotation_path)
    annotation["target"].pop("display_selectors")
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("missing selector for editorial text 'modernized'" in item.message for item in diagnostics)


def test_misaligned_editorial_text_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    base_path = manifest_path.parent / "records" / "annotations" / "base-text.yaml"
    base = load_yaml(base_path)
    selector = base["target"]["display_selectors"][0]
    selector["exact_text"] = "\n".join(selector["exact_text"].splitlines()[:-1])
    _write_yaml(base_path, base)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("must preserve canonical line count and stanza boundaries" in item.message for item in diagnostics)


def test_unmatched_editorial_selector_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "future-vow.yaml"
    annotation = load_yaml(annotation_path)
    annotation["target"]["display_selectors"][0]["exact_text"] = "This is not in the poem."
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any(
        "text 'modernized': exact_text does not occur" in item.message for item in diagnostics
    )


def test_duplicate_text_view_id_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_dual_text_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    duplicate = deepcopy(manifest["presentation"]["texts"][1])
    manifest["presentation"]["texts"].append(duplicate)
    _write_yaml(manifest_path, manifest)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("duplicate text ID 'modernized'" in item.message for item in diagnostics)


def test_missing_pathway_annotation_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    manifest["presentation"]["pathways"][0]["steps"][0]["annotation_keys"] = ["missing-note"]
    _write_yaml(manifest_path, manifest)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("unknown non-base annotation local key 'missing-note'" in item.message for item in diagnostics)


def test_duplicate_annotation_local_key_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "publication-history.yaml"
    annotation = load_yaml(annotation_path)
    annotation["provenance"]["local_key"] = "base-text"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("duplicate local key 'base-text'" in item.message for item in diagnostics)


def test_ambiguous_exact_target_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "future-vow.yaml"
    annotation = load_yaml(annotation_path)
    annotation["target"]["exact_text"] = "And"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("exact_text is ambiguous" in item.message for item in diagnostics)


def test_target_context_can_disambiguate_repeated_text(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "future-vow.yaml"
    annotation = load_yaml(annotation_path)
    annotation["target"]["exact_text"] = "And"
    annotation["target"]["suffix"] = " pluck"
    _write_yaml(annotation_path, annotation)

    assert CorpusValidator().validate_manifest(manifest_path) == []


def test_cross_work_target_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    annotation_path = manifest_path.parent / "records" / "annotations" / "future-vow.yaml"
    annotation = load_yaml(annotation_path)
    annotation["target"]["work_id"] = "work_another_text"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("target work differs from base text" in item.message for item in diagnostics)


def test_unmatched_lens_tag_is_reported(tmp_path: Path) -> None:
    manifest_path = _copy_yeats(tmp_path)
    manifest = load_yaml(manifest_path)
    manifest["presentation"]["lenses"][0]["tag"] = "lens-unused"
    _write_yaml(manifest_path, manifest)

    diagnostics = CorpusValidator().validate_manifest(manifest_path)

    assert any("matches no non-base annotation" in item.message for item in diagnostics)


def test_unknown_source_reference_is_reported(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "basic")
    annotation_path = manifest.parent / "records" / "annotations" / "line-12-variant.yaml"
    annotation = load_yaml(annotation_path)
    annotation["evidence"][0]["source_id"] = "src_0000000000000000"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any("unknown source ID" in diagnostic.message for diagnostic in diagnostics)


def test_citation_only_source_cannot_be_direct_evidence(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "limited-access")
    annotation_path = manifest.parent / "records" / "annotations" / "window-reading.yaml"
    annotation = load_yaml(annotation_path)
    annotation["evidence"][0]["use"] = "direct-evidence"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any("citation-only source cannot be used as direct-evidence" in item.message for item in diagnostics)


def test_citation_only_source_cannot_supply_quotation(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "limited-access")
    annotation_path = manifest.parent / "records" / "annotations" / "window-reading.yaml"
    annotation = load_yaml(annotation_path)
    annotation["evidence"][0]["quotation"] = "An unverified quotation."
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    messages = [item.message for item in diagnostics]
    assert any("quotation requires a consulted source" in message for message in messages)
    assert any("source quotation permission is unknown" in message for message in messages)


def test_consensus_requires_two_distinct_sources(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "basic")
    annotation_path = manifest.parent / "records" / "annotations" / "line-12-variant.yaml"
    annotation = load_yaml(annotation_path)
    annotation["claim"]["epistemic_status"] = "scholarly-consensus"
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any("at least two distinct sources" in item.message for item in diagnostics)


def test_attribution_must_reference_local_evidence(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "contested-interpretation")
    annotation_path = manifest.parent / "records" / "annotations" / "garden-dispute.yaml"
    annotation = load_yaml(annotation_path)
    annotation["claim"]["attributions"][0]["evidence_ids"] = ["ev_missing"]
    _write_yaml(annotation_path, annotation)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any("unknown evidence ID 'ev_missing'" in item.message for item in diagnostics)


def test_derived_id_mismatch_is_reported(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "basic")
    source_path = manifest.parent / "records" / "sources" / "river-poems-edition.yaml"
    source = load_yaml(source_path)
    source["provenance"]["value"] = "changed-coordinate"
    _write_yaml(source_path, source)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any("does not match derived ID" in item.message for item in diagnostics)


def test_unlisted_record_is_reported(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "basic")
    source_path = manifest.parent / "records" / "sources" / "river-poems-edition.yaml"
    extra_path = source_path.with_name("unlisted.yaml")
    shutil.copyfile(source_path, extra_path)

    diagnostics = CorpusValidator().validate_manifest(manifest)

    assert any(item.file == str(extra_path) and "not listed" in item.message for item in diagnostics)


def test_diagnostics_are_deterministically_sorted(tmp_path: Path) -> None:
    manifest = _copy_example(tmp_path, "basic")
    annotation_path = manifest.parent / "records" / "annotations" / "line-12-variant.yaml"
    annotation = load_yaml(annotation_path)
    annotation["review"] = {"state": "source-verified"}
    annotation["claim"]["body"] = ""
    _write_yaml(annotation_path, annotation)

    validator = CorpusValidator()
    first = validator.validate_manifest(manifest)
    second = validator.validate_manifest(manifest)

    assert first == second
    assert first == sorted(first)
    assert any(item.path.startswith("$.claim") for item in first)
    assert any(item.path.startswith("$.review") for item in first)
