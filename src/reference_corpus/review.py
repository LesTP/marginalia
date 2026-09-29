"""Generate a self-contained review page from a validated corpus manifest."""

from __future__ import annotations

import argparse
import base64
from html import escape as html_escape
import json
import os
import sys
import tempfile
from importlib import resources
from pathlib import Path
from typing import Any, Mapping, Sequence

from reference_corpus.targets import (
    TargetResolutionError,
    index_base_text,
    parse_line_locator as _parse_line_locator,
    resolve_target,
)
from reference_corpus.validate import CorpusValidator, ValidatorConfigurationError
from reference_corpus.yaml_io import CorpusLoadError, load_yaml


_ASSET_DIRECTORY = "web"
_ASSETS = {
    "template": "review.html",
    "style": "review.css",
    "script": "review.js",
    "historical_style": "historical-forms.css",
}
_FONT_ROMAN_FILE = ("fonts", "IMFeENrm28P.ttf")
_FONT_ITALIC_FILE = ("fonts", "IMFeENit28P.ttf")
_FONT_LICENSE = ("fonts", "OFL.txt")
_FONT_ROMAN_DATA_MARKER = "@@IM_FELL_ENGLISH_ROMAN_DATA@@"
_FONT_ITALIC_DATA_MARKER = "@@IM_FELL_ENGLISH_ITALIC_DATA@@"
_FONT_ATTRIBUTION_MARKER = "@@REVIEW_FONT_ATTRIBUTION@@"


class ReviewError(ValueError):
    """Raised when a valid corpus cannot form a coherent review model."""


def _record_paths(manifest_path: Path, manifest: Mapping[str, Any], key: str) -> list[Path]:
    return [manifest_path.parent / Path(relative) for relative in manifest[key]]


def _load_records(manifest_path: Path, manifest: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    return [load_yaml(path) for path in _record_paths(manifest_path, manifest, key)]


def _base_annotation(
    manifest: Mapping[str, Any],
    annotations: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    presentation = manifest.get("presentation")
    if presentation is not None:
        local_key = presentation["base_text_annotation"]
        matches = [
            annotation
            for annotation in annotations
            if annotation["provenance"]["local_key"] == local_key
        ]
    else:
        matches = [
            annotation
            for annotation in annotations
            if annotation["provenance"]["local_key"] == "base-text"
            or "base-text" in annotation.get("tags", [])
        ]
    if len(matches) != 1:
        raise ReviewError(f"expected exactly one base-text annotation, found {len(matches)}")
    return matches[0]


def parse_line_locator(value: str, line_count: int) -> dict[str, int] | None:
    """Parse a canonical line locator, returning None for unsupported locator forms."""
    try:
        return _parse_line_locator(value, line_count)
    except TargetResolutionError as error:
        raise ReviewError(str(error)) from error


def _humanize(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _presentation_source(source: Mapping[str, Any]) -> dict[str, Any]:
    bibliography = source["bibliography"]
    return {
        "id": source["id"],
        "title": bibliography["title"],
        "contributors": bibliography.get("contributors", []),
        "issued": bibliography.get("issued"),
        "publisher": bibliography.get("publisher"),
        "container_title": bibliography.get("container_title"),
        "volume": bibliography.get("volume"),
        "issue": bibliography.get("issue"),
        "pages": bibliography.get("pages"),
        "citation": bibliography["citation"],
        "canonical_url": bibliography.get("canonical_url"),
        "source_type": source["source_type"],
        "source_type_detail": source.get("source_type_detail"),
        "quality": source["quality"],
        "access": source["access"],
        "rights": source["rights"],
        "notes": source.get("notes"),
    }


def _presentation_lines(base_index: Any) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    stanza_line = 0
    for line in base_index.lines:
        stanza_line = 1 if line.stanza_start else stanza_line + 1
        lines.append(
            {
                "number": line.number,
                "text": line.text,
                "stanza_start": line.stanza_start,
                "stanza_line": stanza_line,
            }
        )
    return lines


def _resolved_witness_presentation(
    view: Mapping[str, Any],
    base_source: Mapping[str, Any],
) -> dict[str, Any] | None:
    configured = view.get("witness_presentation")
    if configured is None:
        return None

    resolved = dict(configured)
    if configured.get("show_author"):
        authors = [
            contributor["name"]
            for contributor in base_source["contributors"]
            if contributor["role"] == "author"
        ]
        if not authors:
            raise ReviewError(
                f"text {view['id']!r}: witness presentation requests an author, "
                "but the base witness has none"
            )
        resolved["author"] = ", ".join(authors)
    if configured.get("show_issued"):
        issued = base_source.get("issued")
        if not issued:
            raise ReviewError(
                f"text {view['id']!r}: witness presentation requests an issued date, "
                "but the base witness has none"
            )
        resolved["issued"] = issued
    return resolved


def _text_views(
    manifest: Mapping[str, Any],
    base: Mapping[str, Any],
    canonical_index: Any,
    base_source: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], str, str]:
    presentation = manifest.get("presentation") or {}
    configured = presentation.get("texts")
    if not configured:
        text_id = "canonical"
        return (
            [
                {
                    "id": text_id,
                    "label": "Base text",
                    "description": "The corpus's controlling text.",
                    "type": "canonical-target",
                    "derived_from": None,
                    "provenance_note": f"Base witness: {base_source['citation']}",
                    "lines": _presentation_lines(canonical_index),
                }
            ],
            {text_id: canonical_index},
            text_id,
            text_id,
        )

    selectors = {
        selector["text_id"]: selector
        for selector in base["target"].get("display_selectors", [])
    }
    views: list[dict[str, Any]] = []
    indexes: dict[str, Any] = {}
    canonical_id = next(view["id"] for view in configured if view["type"] == "canonical-target")
    for view in configured:
        text_id = view["id"]
        if view["type"] == "canonical-target":
            text_index = canonical_index
            provenance_note = f"Base witness: {base_source['citation']}"
        else:
            selector = selectors.get(text_id)
            if selector is None:
                raise ReviewError(f"base text is missing display selector for {text_id!r}")
            try:
                text_index = index_base_text(selector["exact_text"])
            except TargetResolutionError as error:
                raise ReviewError(f"text {text_id!r}: {error}") from error
            provenance_note = f"Editorial derivation: {view['description']}"
        indexes[text_id] = text_index
        rendered_view = {
            **view,
            "derived_from": view.get("derived_from"),
            "provenance_note": provenance_note,
            "lines": _presentation_lines(text_index),
        }
        witness_presentation = _resolved_witness_presentation(view, base_source)
        if witness_presentation is not None:
            rendered_view["witness_presentation"] = witness_presentation
        views.append(rendered_view)
    return views, indexes, presentation["default_text"], canonical_id


def _normalized_presentation(
    manifest: Mapping[str, Any],
    annotations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    configured = manifest.get("presentation")
    if configured is None:
        return {
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

    non_base = {
        annotation["local_key"]: annotation
        for annotation in annotations
        if not annotation["is_base_text"]
    }
    lenses: list[dict[str, Any]] = []
    for lens in configured["lenses"]:
        lenses.append(
            {
                "id": lens["id"],
                "label": lens["label"],
                "description": lens["description"],
                "annotation_keys": [
                    annotation["local_key"]
                    for annotation in annotations
                    if not annotation["is_base_text"] and lens["tag"] in annotation["tags"]
                ],
            }
        )

    pathways = [
        {
            "id": pathway["id"],
            "label": pathway["label"],
            "description": pathway["description"],
            "overview_annotation": pathway["overview_annotation"],
            "steps": [
                {
                    "id": step["id"],
                    "label": step["label"],
                    "annotation_keys": list(step["annotation_keys"]),
                }
                for step in pathway["steps"]
            ],
        }
        for pathway in configured["pathways"]
    ]

    mode = configured.get("default_mode", "plain")
    default_text = configured.get("default_text", "canonical")
    default_state: dict[str, Any] = {
        "text": default_text,
        "mode": mode,
        "lens": None,
        "pathway": None,
        "step": None,
        "annotation": None,
    }
    if mode == "lens":
        lens_id = configured["default_lens"]
        lens = next(item for item in lenses if item["id"] == lens_id)
        default_state["lens"] = lens_id
        default_state["annotation"] = lens["annotation_keys"][0]
    elif mode == "pathway":
        pathway_id = configured["default_pathway"]
        pathway = next(item for item in pathways if item["id"] == pathway_id)
        first_step = pathway["steps"][0]
        default_state["pathway"] = pathway_id
        default_state["step"] = first_step["id"]
        default_state["annotation"] = first_step["annotation_keys"][0]
    elif mode not in {"plain", "all", "sources"}:
        raise ReviewError(f"unsupported default presentation mode {mode!r}")

    for pathway in pathways:
        if pathway["overview_annotation"] not in non_base:
            raise ReviewError(
                f"pathway {pathway['id']!r} references unknown overview annotation"
            )
    return {
        "default_text": default_text,
        "default_state": default_state,
        "lenses": lenses,
        "pathways": pathways,
    }


def build_review_model(manifest_path: str | Path) -> dict[str, Any]:
    """Build the reduced browser presentation model from canonical records."""
    path = Path(manifest_path).resolve()
    manifest = load_yaml(path)
    sources = _load_records(path, manifest, "sources")
    annotations = _load_records(path, manifest, "annotations")
    source_views = [_presentation_source(source) for source in sources]
    sources_by_id = {source["id"]: source for source in source_views}

    base = _base_annotation(manifest, annotations)
    try:
        base_index = index_base_text(base["target"]["exact_text"])
    except TargetResolutionError as error:
        raise ReviewError(str(error)) from error

    base_source = sources_by_id[base["target"]["edition_source_id"]]
    text_views, text_indexes, default_text, canonical_text = _text_views(
        manifest, base, base_index, base_source
    )
    base_key = base["provenance"]["local_key"]
    annotation_views: list[dict[str, Any]] = []
    for annotation in annotations:
        provenance = annotation["provenance"]
        target = annotation["target"]
        evidence_views: list[dict[str, Any]] = []
        for evidence in annotation["evidence"]:
            source_id = evidence["source_id"]
            source = sources_by_id.get(source_id)
            if source is None:
                raise ReviewError(f"annotation evidence references unknown source {source_id!r}")
            evidence_views.append({**evidence, "source": source})

        try:
            resolved = resolve_target(target, base_index)
        except TargetResolutionError as error:
            local_key = provenance["local_key"]
            raise ReviewError(f"annotation {local_key!r}: {error}") from error

        fragments_by_text = {canonical_text: resolved["fragments"]}
        selectors = {
            selector["text_id"]: selector
            for selector in target.get("display_selectors", [])
        }
        for text_id, text_index in text_indexes.items():
            if text_id == canonical_text:
                continue
            selector = selectors.get(text_id)
            if selector is None:
                raise ReviewError(
                    f"annotation {provenance['local_key']!r} is missing display selector for {text_id!r}"
                )
            display_target = {
                "locator": target["locator"],
                "exact_text": selector["exact_text"],
            }
            if "prefix" in selector:
                display_target["prefix"] = selector["prefix"]
            if "suffix" in selector:
                display_target["suffix"] = selector["suffix"]
            try:
                display_resolved = resolve_target(display_target, text_index)
            except TargetResolutionError as error:
                raise ReviewError(
                    f"annotation {provenance['local_key']!r}, text {text_id!r}: {error}"
                ) from error
            fragments_by_text[text_id] = display_resolved["fragments"]

        local_key = provenance["local_key"]
        annotation_views.append(
            {
                "id": annotation["id"],
                "local_key": local_key,
                "title": annotation.get("title", _humanize(local_key)),
                "annotation_type": annotation["annotation_type"],
                "is_base_text": local_key == base_key,
                "target": {
                    "work_id": target["work_id"],
                    "locator": target["locator"],
                    "line_range": resolved["line_range"],
                    "fragments": resolved["fragments"],
                    "fragments_by_text": fragments_by_text,
                    "exact_text": target["exact_text"],
                },
                "claim": annotation["claim"],
                "evidence": evidence_views,
                "review": annotation["review"],
                "tags": annotation.get("tags", []),
            }
        )

    presentation = _normalized_presentation(manifest, annotation_views)
    authors = [
        item["name"] for item in base_source["contributors"] if item["role"] == "author"
    ]
    review_states = sorted({item["review"]["state"] for item in annotation_views})
    return {
        "corpus": {
            "id": manifest["corpus_id"],
            "title": manifest["title"],
            "description": manifest.get("description", ""),
            "authors": authors,
            "source_count": len(source_views),
            "annotation_count": len(annotation_views),
            "review_states": review_states,
            "base_witness": {
                "title": base_source["title"],
                "citation": base_source["citation"],
                "issued": base_source.get("issued"),
            },
        },
        "poem": {
            "work_id": base["target"]["work_id"],
            "lines": _presentation_lines(base_index),
        },
        "texts": text_views,
        "default_text": default_text,
        "annotations": annotation_views,
        "sources": source_views,
        "presentation": presentation,
    }


def serialize_for_html(model: Mapping[str, Any]) -> str:
    """Serialize JSON for a script data block without permitting tag termination."""
    serialized = json.dumps(
        model,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _asset_resource(*parts: str):
    return resources.files("reference_corpus").joinpath(_ASSET_DIRECTORY, *parts)


def _asset_text(name: str) -> str:
    return _asset_resource(_ASSETS[name]).read_text(encoding="utf-8")


def _historical_font_assets(model: Mapping[str, Any]) -> tuple[str, str]:
    if not any(text.get("historical_forms") is True for text in model.get("texts", [])):
        return "", ""

    font_payloads = {
        _FONT_ROMAN_DATA_MARKER: base64.b64encode(
            _asset_resource(*_FONT_ROMAN_FILE).read_bytes()
        ).decode("ascii"),
        _FONT_ITALIC_DATA_MARKER: base64.b64encode(
            _asset_resource(*_FONT_ITALIC_FILE).read_bytes()
        ).decode("ascii"),
    }
    stylesheet = _asset_text("historical_style")
    for marker, font_data in font_payloads.items():
        if marker not in stylesheet:
            raise ReviewError(f"historical font stylesheet is missing marker {marker}")
        stylesheet = stylesheet.replace(marker, font_data)

    license_text = _asset_resource(*_FONT_LICENSE).read_text(encoding="utf-8")
    attribution = (
        '<section class="font-attribution" aria-labelledby="font-attribution-heading">\n'
        '      <p id="font-attribution-heading" class="font-attribution__credit">'
        'IM FELL English Roman and Italic by Igino Marini, Copyright (c) 2010. '
        'Licensed under the SIL Open Font License 1.1.</p>\n'
        '      <details class="font-attribution__license">\n'
        '        <summary>Font attribution and complete license</summary>\n'
        f'        <pre>{html_escape(license_text, quote=False)}</pre>\n'
        '      </details>\n'
        '    </section>'
    )
    return stylesheet, attribution


def render_review_html(model: Mapping[str, Any]) -> str:
    """Render a complete offline review page."""
    template = _asset_text("template")
    historical_style, font_attribution = _historical_font_assets(model)
    review_style = _asset_text("style")
    if historical_style:
        review_style = f"{review_style}\n\n{historical_style}"
    replacements = {
        "@@REVIEW_STYLE@@": review_style,
        "@@REVIEW_DATA@@": serialize_for_html(model),
        "@@REVIEW_SCRIPT@@": _asset_text("script"),
        _FONT_ATTRIBUTION_MARKER: font_attribution,
    }
    for marker, value in replacements.items():
        if marker not in template:
            raise ReviewError(f"review template is missing marker {marker}")
        template = template.replace(marker, value)
    return template


def write_review(manifest_path: str | Path, output_path: str | Path | None = None) -> Path:
    """Validate and atomically write a corpus review page."""
    manifest = Path(manifest_path).resolve()
    diagnostics = CorpusValidator().validate_manifest(manifest)
    if diagnostics:
        rendered = "\n".join(diagnostic.render() for diagnostic in diagnostics)
        raise ReviewError(f"corpus validation failed:\n{rendered}")

    output = Path(output_path).resolve() if output_path else manifest.with_name("review.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    content = render_review_html(build_review_model(manifest))
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_name = temporary.name
        os.replace(temporary_name, output)
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reference-corpus-render",
        description="Render a validated corpus as a self-contained review page.",
    )
    parser.add_argument("manifest", type=Path, help="Path to corpus.yaml")
    parser.add_argument(
        "--output", type=Path, help="Output HTML path (default: review.html beside manifest)"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        output = write_review(args.manifest, args.output)
        print(f"rendered: {output}")
        return 0
    except ReviewError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except (CorpusLoadError, OSError, ValidatorConfigurationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
