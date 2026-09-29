from __future__ import annotations

from copy import deepcopy

from reference_corpus.identifiers import derive_annotation_id, derive_source_id


def test_source_id_is_deterministic() -> None:
    record = {
        "record_type": "source",
        "provenance": {
            "scheme": "bibliographic-key",
            "value": "example:river-poems-critical-edition:2024",
        },
    }

    assert derive_source_id(record) == "src_7b0f4b601ea6737c"
    assert derive_source_id(record) == derive_source_id(deepcopy(record))


def test_annotation_id_ignores_mutable_reader_facing_content() -> None:
    record = {
        "record_type": "annotation",
        "annotation_type": "textual-variant",
        "provenance": {"local_key": "line-12-variant"},
        "target": {
            "work_id": "work_example_river_poems",
            "edition_source_id": "src_7b0f4b601ea6737c",
            "locator": {"scheme": "line", "value": "12"},
        },
        "claim": {"body": "Original wording."},
    }
    revised = deepcopy(record)
    revised["title"] = "A Clear Title for Readers"
    revised["claim"]["body"] = "Rewritten without changing identity."

    assert derive_annotation_id(record) == "ann_b3584b6bff8f37cb"
    assert derive_annotation_id(record) == derive_annotation_id(revised)


def test_annotation_id_ignores_display_selectors() -> None:
    record = {
        "record_type": "annotation",
        "annotation_type": "formal",
        "provenance": {"local_key": "compass-conceit"},
        "target": {
            "work_id": "work_a_valediction_forbidding_mourning",
            "edition_source_id": "src_7b0f4b601ea6737c",
            "locator": {"scheme": "line", "value": "25-36"},
            "exact_text": "Canonical passage.",
        },
    }
    with_display = deepcopy(record)
    with_display["target"]["display_selectors"] = [
        {"text_id": "modernized", "exact_text": "Modernized passage."}
    ]
    revised_display = deepcopy(with_display)
    revised_display["target"]["display_selectors"][0]["exact_text"] = "Revised display."

    assert derive_annotation_id(record) == derive_annotation_id(with_display)
    assert derive_annotation_id(with_display) == derive_annotation_id(revised_display)


def test_identity_coordinate_change_changes_id() -> None:
    first = {
        "record_type": "source",
        "provenance": {"scheme": "doi", "value": "10.0000/example.one"},
    }
    second = deepcopy(first)
    second["provenance"]["value"] = "10.0000/example.two"

    assert derive_source_id(first) != derive_source_id(second)
