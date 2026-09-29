from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

from reference_corpus.validate import CorpusValidator, default_schema_dir
from reference_corpus.yaml_io import load_yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


EXPECTED_EPISTEMIC_STATUSES = {
    "documented-fact",
    "scholarly-consensus",
    "attributed-interpretation",
    "editorial-synthesis",
    "editorial-proposal",
    "conjecture",
}


PRESENTATION_MANIFEST = {
    "schema_version": "1.0.0",
    "record_type": "corpus-manifest",
    "corpus_id": "corpus_presentation_example",
    "title": "Presentation example",
    "sources": ["records/sources/base.yaml"],
    "annotations": ["records/annotations/base.yaml", "records/annotations/note.yaml"],
    "presentation": {
        "base_text_annotation": "base-text",
        "default_mode": "pathway",
        "default_pathway": "first-reading",
        "lenses": [
            {
                "id": "context",
                "label": "Context",
                "description": "Context for the text.",
                "tag": "lens-context",
            }
        ],
        "pathways": [
            {
                "id": "first-reading",
                "label": "First reading",
                "description": "An ordered route.",
                "overview_annotation": "guided-reading",
                "steps": [
                    {
                        "id": "opening",
                        "label": "The opening",
                        "annotation_keys": ["opening-note"],
                    }
                ],
            }
        ],
    },
}


def test_all_schemas_meta_validate() -> None:
    paths = sorted(default_schema_dir().glob("*.schema.json"))
    assert len(paths) == 4
    for path in paths:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_epistemic_vocabulary_is_explicit_and_complete() -> None:
    path = default_schema_dir() / "vocabularies.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))

    assert set(schema["$defs"]["epistemicStatus"]["enum"]) == EXPECTED_EPISTEMIC_STATUSES


def test_manifest_schema_accepts_optional_complete_presentation() -> None:
    validator = CorpusValidator()

    assert validator.validate_record(PRESENTATION_MANIFEST, "corpus.yaml", "corpus-manifest") == []
    without_presentation = deepcopy(PRESENTATION_MANIFEST)
    without_presentation.pop("presentation")
    assert validator.validate_record(without_presentation, "corpus.yaml", "corpus-manifest") == []


def test_manifest_schema_rejects_partial_or_malformed_presentation() -> None:
    validator = CorpusValidator()
    partial = deepcopy(PRESENTATION_MANIFEST)
    partial["presentation"].pop("base_text_annotation")
    malformed = deepcopy(PRESENTATION_MANIFEST)
    malformed["presentation"]["pathways"][0]["steps"][0]["id"] = "Not Stable"
    unknown = deepcopy(PRESENTATION_MANIFEST)
    unknown["presentation"]["lenses"][0]["color"] = "blue"

    assert validator.validate_record(partial, "corpus.yaml", "corpus-manifest")
    assert validator.validate_record(malformed, "corpus.yaml", "corpus-manifest")
    assert validator.validate_record(unknown, "corpus.yaml", "corpus-manifest")


def test_manifest_schema_accepts_complete_text_views() -> None:
    validator = CorpusValidator()
    manifest = deepcopy(PRESENTATION_MANIFEST)
    manifest["presentation"].update(
        {
            "texts": [
                {
                    "id": "edition-faithful",
                    "label": "Edition-faithful text",
                    "description": "The controlling historical transcription.",
                    "type": "canonical-target",
                    "historical_forms": True,
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

    assert validator.validate_record(manifest, "corpus.yaml", "corpus-manifest") == []

    missing_default = deepcopy(manifest)
    missing_default["presentation"].pop("default_text")
    assert validator.validate_record(missing_default, "corpus.yaml", "corpus-manifest")

    canonical_with_parent = deepcopy(manifest)
    canonical_with_parent["presentation"]["texts"][0]["derived_from"] = "modernized"
    assert validator.validate_record(canonical_with_parent, "corpus.yaml", "corpus-manifest")

    malformed_historical_forms = deepcopy(manifest)
    malformed_historical_forms["presentation"]["texts"][0]["historical_forms"] = "yes"
    assert validator.validate_record(
        malformed_historical_forms,
        "corpus.yaml",
        "corpus-manifest",
    )


def test_annotation_schema_accepts_display_selectors() -> None:
    validator = CorpusValidator()
    path = (
        PROJECT_ROOT
        / "examples"
        / "valid"
        / "contested-interpretation"
        / "records"
        / "annotations"
        / "garden-dispute.yaml"
    )
    annotation = load_yaml(path)
    annotation["target"]["display_selectors"] = [
        {"text_id": "modernized", "exact_text": annotation["target"]["exact_text"]}
    ]

    assert validator.validate_record(annotation, path, "annotation") == []

    malformed = deepcopy(annotation)
    malformed["target"]["display_selectors"][0]["text_id"] = "Not Stable"
    assert validator.validate_record(malformed, path, "annotation")


def test_annotation_title_is_optional_but_must_be_non_empty() -> None:
    validator = CorpusValidator()
    path = (
        PROJECT_ROOT
        / "examples"
        / "valid"
        / "contested-interpretation"
        / "records"
        / "annotations"
        / "garden-dispute.yaml"
    )
    annotation = load_yaml(path)

    assert validator.validate_record(annotation, path, "annotation") == []
    without_title = deepcopy(annotation)
    without_title.pop("title")
    assert validator.validate_record(without_title, path, "annotation") == []

    for invalid_title in ["", 42]:
        invalid = deepcopy(annotation)
        invalid["title"] = invalid_title
        assert validator.validate_record(invalid, path, "annotation")


def test_schema_format_checker_rejects_impossible_date() -> None:
    validator = CorpusValidator()
    source = {
        "schema_version": "1.0.0",
        "record_type": "source",
        "id": "src_0000000000000000",
        "provenance": {"scheme": "bibliographic-key", "value": "example"},
        "bibliography": {
            "title": "Example",
            "contributors": [{"name": "A. Editor", "role": "editor"}],
            "citation": "A. Editor, Example.",
        },
        "source_type": "critical-edition",
        "quality": {
            "authority": "scholarly-edition",
            "peer_review_status": "editorially-reviewed",
            "rationale": "Example rationale.",
        },
        "access": {"state": "fully-consulted", "consulted_on": "2026-99-99"},
        "rights": {
            "status": "copyrighted",
            "quotation": "limited",
            "reproduction": "prohibited",
            "notes": "Example constraints.",
        },
    }

    errors = validator.validate_record(source, "source.yaml", "source")
    assert any(error.path == "$.access.consulted_on" for error in errors)
