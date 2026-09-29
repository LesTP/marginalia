from __future__ import annotations

import base64
import hashlib
from html import escape as html_escape
from importlib import resources
from pathlib import Path
import re
import shutil

import pytest
import yaml

from reference_corpus.review import (
    ReviewError,
    build_review_model,
    main,
    parse_line_locator,
    render_review_html,
    serialize_for_html,
    write_review,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
YEATS_MANIFEST = PROJECT_ROOT / "corpora" / "yeats-song-of-wandering-aengus" / "corpus.yaml"
DONNE_MANIFEST = (
    PROJECT_ROOT
    / "corpora"
    / "donne-a-valediction-forbidding-mourning"
    / "corpus.yaml"
)
FONT_SHA256 = "fe9705bbde51af802719246d4608d08d37bde956ab99d9a590da996a5221a24c"


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )


def _dual_text_yeats(tmp_path: Path) -> Path:
    corpus = tmp_path / "dual-text-yeats"
    shutil.copytree(YEATS_MANIFEST.parent, corpus)
    manifest_path = corpus / "corpus.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
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
        annotation_path = corpus / relative
        annotation = yaml.safe_load(annotation_path.read_text(encoding="utf-8"))
        annotation["target"]["display_selectors"] = [
            {
                "text_id": "modernized",
                "exact_text": annotation["target"]["exact_text"].replace("a-flame", "aflame"),
            }
        ]
        _write_yaml(annotation_path, annotation)
    return manifest_path


def test_builds_yeats_review_model() -> None:
    model = build_review_model(YEATS_MANIFEST)

    assert model["corpus"]["source_count"] == 8
    assert model["corpus"]["annotation_count"] == 12
    assert model["corpus"]["authors"] == ["W. B. Yeats"]
    assert len(model["poem"]["lines"]) == 24
    assert [
        line["number"] for line in model["poem"]["lines"] if line["stanza_start"]
    ] == [1, 9, 17]
    assert model["presentation"]["default_state"] == {
        "text": "canonical",
        "mode": "pathway",
        "lens": None,
        "pathway": "guided-reading",
        "step": "initiating-fire",
        "annotation": "light-and-time",
    }
    assert model["presentation"]["default_text"] == "canonical"
    assert [text["id"] for text in model["texts"]] == ["canonical"]
    assert [lens["id"] for lens in model["presentation"]["lenses"]] == [
        "myth-folklore",
        "form-imagery",
        "text-history",
    ]
    pathway = model["presentation"]["pathways"][0]
    assert pathway["overview_annotation"] == "guided-reading"
    assert [step["id"] for step in pathway["steps"]] == [
        "initiating-fire",
        "transformation",
        "recognition",
        "medieval-parallel",
        "future-apples",
    ]


def test_builds_donne_review_model() -> None:
    model = build_review_model(DONNE_MANIFEST)

    assert (
        model["corpus"]["source_count"],
        model["corpus"]["annotation_count"],
        model["corpus"]["authors"],
        len(model["poem"]["lines"]),
    ) == (4, 10, ["John Donne"], 36)
    assert [text["id"] for text in model["texts"]] == [
        "edition-faithful",
        "modernized",
    ]
    assert model["texts"][0]["historical_forms"] is True
    assert "historical_forms" not in model["texts"][1]
    assert all("ſ" not in line["text"] for text in model["texts"] for line in text["lines"])
    assert model["presentation"]["default_state"] == {
        "text": "edition-faithful",
        "mode": "pathway",
        "lens": None,
        "pathway": "guided-reading",
        "step": "quiet-passing",
        "annotation": "quiet-passing",
    }
    assert 'id="text-view-selector"' in render_review_html(model)


def test_donne_embeds_scoped_historical_font_and_complete_license() -> None:
    rendered = render_review_html(build_review_model(DONNE_MANIFEST))
    matches = re.findall(r'data:font/ttf;base64,([^\"]+)', rendered)

    assert len(matches) == 1
    embedded = base64.b64decode(matches[0], validate=True)
    packaged = (
        resources.files("reference_corpus")
        .joinpath("web", "fonts", "IMFeENrm28P.ttf")
        .read_bytes()
    )
    license_text = (
        resources.files("reference_corpus")
        .joinpath("web", "fonts", "OFL.txt")
        .read_text(encoding="utf-8")
    )
    assert embedded == packaged
    assert hashlib.sha256(embedded).hexdigest() == FONT_SHA256
    assert "IM FELL English Roman by Igino Marini" in rendered
    assert "SIL Open Font License 1.1" in rendered
    assert html_escape(license_text, quote=False) in rendered
    assert '.poem-lines--historical-forms .poem-line__text' in rendered
    assert 'font-feature-settings: "hist" 1, "liga" 1' in rendered
    assert 'text.historical_forms === true' in rendered
    assert 'classList.toggle("poem-lines--historical-forms"' in rendered
    assert "https://fonts." not in rendered


def test_builds_dual_text_review_model(tmp_path: Path) -> None:
    manifest = _dual_text_yeats(tmp_path)

    model = build_review_model(manifest)

    assert [text["id"] for text in model["texts"]] == ["edition-faithful", "modernized"]
    assert model["default_text"] == "edition-faithful"
    assert model["presentation"]["default_state"]["text"] == "edition-faithful"
    assert model["texts"][0]["provenance_note"].startswith("Base witness:")
    assert model["texts"][1]["provenance_note"].startswith("Editorial derivation:")
    assert model["texts"][0]["lines"][9]["text"].endswith("a-flame,")
    assert model["texts"][1]["lines"][9]["text"].endswith("aflame,")
    stanza = next(
        item for item in model["annotations"] if item["local_key"] == "stanzaic-progression"
    )
    assert set(stanza["target"]["fragments_by_text"]) == {
        "edition-faithful",
        "modernized",
    }

    rendered = render_review_html(model)
    assert 'id="text-view-selector"' in rendered
    assert "Editorial derivation" in rendered
    assert 'params.set("text", candidate.text)' in rendered


def test_annotation_targets_resolve_inside_the_base_poem() -> None:
    model = build_review_model(YEATS_MANIFEST)
    base_lines = {line["number"]: line["text"] for line in model["poem"]["lines"]}

    for annotation in model["annotations"]:
        line_range = annotation["target"]["line_range"]
        fragments = annotation["target"]["fragments"]
        assert line_range is not None
        assert fragments
        for fragment in fragments:
            assert line_range["start"] <= fragment["line"] <= line_range["end"]
            assert 0 <= fragment["start"] < fragment["end"] <= len(base_lines[fragment["line"]])

    future = next(
        item for item in model["annotations"] if item["local_key"] == "future-vow"
    )
    assert [fragment["line"] for fragment in future["target"]["fragments"]] == [19, 20, 21, 22]


def test_enriches_evidence_with_source_access_and_rights() -> None:
    model = build_review_model(YEATS_MANIFEST)
    apple_note = next(
        item for item in model["annotations"] if item["local_key"] == "apple-imagery-debate"
    )
    source = apple_note["evidence"][0]["source"]

    assert source["title"].startswith("Apple Imagery")
    assert source["access"]["state"] == "fully-consulted"
    assert source["quality"]["authority"] == "peer-reviewed-scholarship"
    assert source["rights"]["quotation"] == "limited"
    lens_memberships = {
        lens["id"] for lens in model["presentation"]["lenses"]
        if apple_note["local_key"] in lens["annotation_keys"]
    }
    assert lens_memberships == {"myth-folklore", "form-imagery"}
    assert apple_note["title"] == "Why the Apples Matter"
    assert apple_note["claim"]["body"].startswith("The apple images connect")
    assert apple_note["claim"]["contested"] is True
    assert len(apple_note["claim"]["attributions"]) == 2


def test_explicit_title_falls_back_to_humanized_local_key() -> None:
    model = build_review_model(YEATS_MANIFEST)
    base = next(item for item in model["annotations"] if item["local_key"] == "base-text")
    guided = next(item for item in model["annotations"] if item["local_key"] == "guided-reading")

    assert base["title"] == "Base Text"
    assert guided["title"] == "A Desire That Becomes a Search"


def test_parses_supported_line_locators() -> None:
    assert parse_line_locator("7", 24) == {"start": 7, "end": 7}
    assert parse_line_locator("7-16", 24) == {"start": 7, "end": 16}
    assert parse_line_locator("stanza-2", 24) is None


@pytest.mark.parametrize("value", ["0", "7-3", "24-25"])
def test_rejects_invalid_line_locators(value: str) -> None:
    with pytest.raises(ReviewError, match="line locator"):
        parse_line_locator(value, 24)


def test_unconfigured_manifest_uses_plain_generic_fallback(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    shutil.copytree(YEATS_MANIFEST.parent, corpus)
    manifest_path = corpus / "corpus.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("presentation")
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )

    model = build_review_model(manifest_path)

    assert model["presentation"] == {
        "default_text": "canonical",
        "default_state": {
            "text": "canonical",
            "mode": "plain",
            "lens": None,
            "pathway": None,
            "step": None,
            "annotation": None,
        },
        "lenses": [],
        "pathways": [],
    }


def test_serialization_cannot_terminate_data_script() -> None:
    serialized = serialize_for_html({"claim": "</script><tag>\u2028\u2029&"})

    assert "</script>" not in serialized
    assert "<tag>" not in serialized
    assert "\u2028" not in serialized
    assert "\u2029" not in serialized
    assert "\\u003c/script\\u003e" in serialized
    assert "\\u2028" in serialized
    assert "\\u2029" in serialized
    assert "\\u0026" in serialized


def test_render_is_deterministic_and_self_contained() -> None:
    model = build_review_model(YEATS_MANIFEST)

    first = render_review_html(model)
    second = render_review_html(model)

    assert first == second
    assert first.startswith("<!doctype html>")
    assert "@@REVIEW_" not in first
    assert '<script id="corpus-data" type="application/json">' in first
    assert 'class="poem-sticky"' in first
    assert "<link " not in first
    assert "<script src=" not in first
    assert "fetch(" not in first
    assert "innerHTML" not in first
    assert "https://fonts." not in first
    assert "data:font/ttf;base64," not in first
    assert "IM FELL English Roman by Igino Marini" not in first
    assert "SIL OPEN FONT LICENSE Version 1.1" not in first
    assert "Myth and folklore" in first
    assert 'id="pathway-detail"' in first
    assert 'id="annotation-collection"' in first
    assert 'makeElement("details", "reading-section pathway-step")' in first
    assert 'makeElement("details", "reading-section annotation-section")' in first
    assert "renderAnnotationContent(annotation, note, true)" in first
    assert "renderAnnotationContent(annotation, note, true, false)" in first
    assert "closeSiblingReadingSections(details)" in first
    assert "details.parentElement.children" in first
    assert 'sibling.classList.contains("reading-section")' in first
    assert 'details.setAttribute("name", `pathway-${pathway.id}`)' in first
    assert 'details.setAttribute("name", `annotations-${state.mode}-${state.lens || "all"}`)' in first
    assert 'id="annotation-nav"' not in first
    assert 'id="annotation-detail"' not in first
    assert "annotation: null" in first
    assert "Sources and editorial notes" in first
    assert "Pathway overview" not in first
    assert 'id="pathway-previous"' not in first
    assert 'id="pathway-next"' not in first
    assert "Read without commentary" not in first
    assert 'id="plain-detail"' not in first
    assert 'id="poem-heading"' not in first
    assert 'id="active-mode-label"' not in first
    assert ">The text<" not in first
    assert "Annotated reading edition" in first
    content_renderer = first[
        first.index("function renderAnnotationContent") : first.index("function highlightedAnnotations")
    ]
    assert content_renderer.index("renderRichText(annotation.claim.body") < content_renderer.index(
        "renderAnnotationApparatus(annotation, container)"
    )


@pytest.mark.parametrize("manifest", [YEATS_MANIFEST, DONNE_MANIFEST])
def test_checked_in_review_data_is_current(manifest: Path) -> None:
    """The published review.html is a hand-authored reading view, not the generated
    accordion page, so it is not expected to equal ``render_review_html``. The invariant
    that must hold is that its embedded data snapshot -- the ``corpus-data`` block that
    ``scripts/refresh-review.py`` regenerates -- matches the current model.
    """
    review = manifest.with_name("review.html").read_text(encoding="utf-8")
    start_tag = '<script id="corpus-data" type="application/json">'
    end_tag = "</script>"
    assert review.count(start_tag) == 1
    start = review.index(start_tag) + len(start_tag)
    end = review.index(end_tag, start)
    assert review[start:end] == serialize_for_html(build_review_model(manifest))


def test_cli_writes_requested_output(tmp_path: Path, capsys) -> None:
    output = tmp_path / "edition.html"

    code = main([str(YEATS_MANIFEST), "--output", str(output)])

    assert code == 0
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>")
    assert "rendered:" in capsys.readouterr().out


def test_invalid_corpus_does_not_write_output(tmp_path: Path, capsys) -> None:
    corpus = tmp_path / "corpus"
    shutil.copytree(YEATS_MANIFEST.parent, corpus)
    (corpus / "records" / "sources" / "base-text-witness.yaml").unlink()
    output = tmp_path / "should-not-exist.html"

    code = main([str(corpus / "corpus.yaml"), "--output", str(output)])

    assert code == 1
    assert not output.exists()
    assert "corpus validation failed" in capsys.readouterr().err


def test_default_output_sits_beside_manifest(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    shutil.copytree(YEATS_MANIFEST.parent, corpus)
    existing_output = corpus / "review.html"
    if existing_output.exists():
        existing_output.unlink()

    output = write_review(corpus / "corpus.yaml")

    assert output == existing_output
    assert output.exists()
