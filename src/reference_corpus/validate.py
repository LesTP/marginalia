"""Read-only validation for reference corpus manifests and records."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from .identifiers import IdentifierError, derive_record_id
from .targets import TargetResolutionError, index_base_text, resolve_target
from .yaml_io import CorpusLoadError, load_yaml


SCHEMA_BY_RECORD_TYPE = {
    "corpus-manifest": "manifest.schema.json",
    "source": "source.schema.json",
    "annotation": "annotation.schema.json",
}


@dataclass(frozen=True, order=True)
class Diagnostic:
    """One deterministic validation diagnostic."""

    file: str
    path: str
    message: str

    def render(self) -> str:
        location = self.file if self.path == "$" else f"{self.file}:{self.path}"
        return f"{location}: {self.message}"


class ValidatorConfigurationError(RuntimeError):
    """Raised for malformed or incomplete validator configuration."""


def default_schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"


def _format_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif str(part).isidentifier():
            result += f".{part}"
        else:
            result += f"[{json.dumps(str(part))}]"
    return result


def load_schemas(schema_dir: str | Path) -> tuple[dict[str, dict[str, Any]], Registry[Any]]:
    directory = Path(schema_dir)
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []

    for path in sorted(directory.glob("*.schema.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except (OSError, json.JSONDecodeError, SchemaError) as error:
            raise ValidatorConfigurationError(f"{path}: invalid schema: {error}") from error

        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            raise ValidatorConfigurationError(f"{path}: schema has no non-empty $id")
        schemas[path.name] = schema
        resources.append((schema_id, Resource.from_contents(schema)))

    required = set(SCHEMA_BY_RECORD_TYPE.values()) | {"vocabularies.schema.json"}
    missing = required - set(schemas)
    if missing:
        raise ValidatorConfigurationError(
            f"{directory}: missing schemas: {', '.join(sorted(missing))}"
        )

    return schemas, Registry().with_resources(resources)


class CorpusValidator:
    """Validate schemas, records, and cross-record corpus invariants."""

    def __init__(self, schema_dir: str | Path | None = None) -> None:
        self.schema_dir = Path(schema_dir) if schema_dir else default_schema_dir()
        self.schemas, self.registry = load_schemas(self.schema_dir)
        self.validators = {
            record_type: Draft202012Validator(
                self.schemas[filename],
                registry=self.registry,
                format_checker=FormatChecker(),
            )
            for record_type, filename in SCHEMA_BY_RECORD_TYPE.items()
        }

    def validate_record(
        self,
        record: Mapping[str, Any],
        label: str,
        expected_type: str | None = None,
    ) -> list[Diagnostic]:
        record_type = record.get("record_type")
        if not isinstance(record_type, str) or record_type not in self.validators:
            return [Diagnostic(label, "$.record_type", "unknown or missing record_type")]
        if expected_type is not None and record_type != expected_type:
            return [
                Diagnostic(
                    label,
                    "$.record_type",
                    f"expected {expected_type!r}, found {record_type!r}",
                )
            ]

        errors = self.validators[record_type].iter_errors(record)
        return sorted(
            Diagnostic(label, _format_path(error.absolute_path), error.message)
            for error in errors
        )

    def validate_manifest(self, manifest_path: str | Path) -> list[Diagnostic]:
        path = Path(manifest_path).resolve()
        diagnostics: list[Diagnostic] = []

        try:
            manifest = load_yaml(path)
        except (OSError, CorpusLoadError) as error:
            return [Diagnostic(str(path), "$", str(error))]

        diagnostics.extend(self.validate_record(manifest, str(path), "corpus-manifest"))
        if diagnostics:
            return sorted(diagnostics)

        root = path.parent
        source_records, source_paths = self._load_manifest_records(
            root, manifest["sources"], "source", diagnostics
        )
        annotation_records, annotation_paths = self._load_manifest_records(
            root, manifest["annotations"], "annotation", diagnostics
        )
        self._check_manifest_completeness(root, source_paths, annotation_paths, diagnostics)

        if any(diagnostic.message.startswith("record failed schema validation") for diagnostic in diagnostics):
            return sorted(diagnostics)

        self._check_unique_ids(source_records, annotation_records, diagnostics)
        self._check_derived_ids(source_records, annotation_records, diagnostics)
        self._check_annotations(source_records, annotation_records, diagnostics)
        self._check_presentation_and_targets(
            str(path), manifest, annotation_records, diagnostics
        )
        return sorted(diagnostics)

    def _load_manifest_records(
        self,
        root: Path,
        relative_paths: Sequence[str],
        expected_type: str,
        diagnostics: list[Diagnostic],
    ) -> tuple[list[tuple[Path, dict[str, Any]]], set[str]]:
        records: list[tuple[Path, dict[str, Any]]] = []
        listed: set[str] = set()

        for relative in relative_paths:
            listed.add(relative)
            candidate = (root / Path(*relative.split("/"))).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                diagnostics.append(Diagnostic(str(candidate), "$", "manifest path escapes corpus root"))
                continue
            if not candidate.is_file():
                diagnostics.append(Diagnostic(str(candidate), "$", "manifest record does not exist"))
                continue
            try:
                record = load_yaml(candidate)
            except (OSError, CorpusLoadError) as error:
                diagnostics.append(Diagnostic(str(candidate), "$", str(error)))
                continue

            record_errors = self.validate_record(record, str(candidate), expected_type)
            if record_errors:
                diagnostics.extend(record_errors)
                diagnostics.append(
                    Diagnostic(str(candidate), "$", "record failed schema validation")
                )
                continue
            records.append((candidate, record))

        return records, listed

    def _check_manifest_completeness(
        self,
        root: Path,
        source_paths: set[str],
        annotation_paths: set[str],
        diagnostics: list[Diagnostic],
    ) -> None:
        for directory, listed in (
            (root / "records" / "sources", source_paths),
            (root / "records" / "annotations", annotation_paths),
        ):
            if not directory.is_dir():
                continue
            for record_path in sorted(directory.rglob("*.yaml")):
                relative = record_path.relative_to(root).as_posix()
                if relative not in listed:
                    diagnostics.append(
                        Diagnostic(str(record_path), "$", "record is not listed in corpus manifest")
                    )

    def _check_unique_ids(
        self,
        sources: Sequence[tuple[Path, dict[str, Any]]],
        annotations: Sequence[tuple[Path, dict[str, Any]]],
        diagnostics: list[Diagnostic],
    ) -> None:
        seen: dict[str, Path] = {}
        for path, record in (*sources, *annotations):
            record_id = record["id"]
            if record_id in seen:
                diagnostics.append(
                    Diagnostic(
                        str(path),
                        "$.id",
                        f"duplicate ID {record_id!r}; first declared in {seen[record_id]}",
                    )
                )
            else:
                seen[record_id] = path

    def _check_derived_ids(
        self,
        sources: Sequence[tuple[Path, dict[str, Any]]],
        annotations: Sequence[tuple[Path, dict[str, Any]]],
        diagnostics: list[Diagnostic],
    ) -> None:
        for path, record in (*sources, *annotations):
            try:
                expected = derive_record_id(record)
            except IdentifierError as error:
                diagnostics.append(Diagnostic(str(path), "$.id", str(error)))
                continue
            if record["id"] != expected:
                diagnostics.append(
                    Diagnostic(
                        str(path),
                        "$.id",
                        f"stored ID {record['id']!r} does not match derived ID {expected!r}",
                    )
                )

    def _check_annotations(
        self,
        sources: Sequence[tuple[Path, dict[str, Any]]],
        annotations: Sequence[tuple[Path, dict[str, Any]]],
        diagnostics: list[Diagnostic],
    ) -> None:
        source_by_id = {record["id"]: record for _, record in sources}

        for path, annotation in annotations:
            label = str(path)
            edition_id = annotation["target"]["edition_source_id"]
            if edition_id not in source_by_id:
                diagnostics.append(
                    Diagnostic(label, "$.target.edition_source_id", f"unknown source ID {edition_id!r}")
                )

            evidence_by_id: dict[str, dict[str, Any]] = {}
            for index, evidence in enumerate(annotation["evidence"]):
                evidence_id = evidence["id"]
                if evidence_id in evidence_by_id:
                    diagnostics.append(
                        Diagnostic(label, f"$.evidence[{index}].id", f"duplicate evidence ID {evidence_id!r}")
                    )
                evidence_by_id[evidence_id] = evidence

                source_id = evidence["source_id"]
                source = source_by_id.get(source_id)
                if source is None:
                    diagnostics.append(
                        Diagnostic(label, f"$.evidence[{index}].source_id", f"unknown source ID {source_id!r}")
                    )
                    continue
                self._check_evidence_access(label, index, evidence, source, diagnostics)

            for attribution_index, attribution in enumerate(annotation["claim"]["attributions"]):
                for evidence_index, evidence_id in enumerate(attribution["evidence_ids"]):
                    if evidence_id not in evidence_by_id:
                        diagnostics.append(
                            Diagnostic(
                                label,
                                f"$.claim.attributions[{attribution_index}].evidence_ids[{evidence_index}]",
                                f"unknown evidence ID {evidence_id!r}",
                            )
                        )

            if annotation["claim"]["epistemic_status"] == "scholarly-consensus":
                distinct_sources = {item["source_id"] for item in annotation["evidence"]}
                if len(distinct_sources) < 2:
                    diagnostics.append(
                        Diagnostic(
                            label,
                            "$.claim.epistemic_status",
                            "scholarly-consensus requires evidence from at least two distinct sources",
                        )
                    )

    def _check_presentation_and_targets(
        self,
        manifest_label: str,
        manifest: Mapping[str, Any],
        annotations: Sequence[tuple[Path, dict[str, Any]]],
        diagnostics: list[Diagnostic],
    ) -> None:
        annotations_by_key: dict[str, tuple[Path, dict[str, Any]]] = {}
        for path, annotation in annotations:
            local_key = annotation["provenance"]["local_key"]
            if local_key in annotations_by_key:
                first_path = annotations_by_key[local_key][0]
                diagnostics.append(
                    Diagnostic(
                        str(path),
                        "$.provenance.local_key",
                        f"duplicate local key {local_key!r}; first declared in {first_path}",
                    )
                )
            else:
                annotations_by_key[local_key] = (path, annotation)

        presentation = manifest.get("presentation")
        base_entry: tuple[Path, dict[str, Any]] | None = None
        if presentation is not None:
            base_key = presentation["base_text_annotation"]
            base_entry = annotations_by_key.get(base_key)
            if base_entry is None:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        "$.presentation.base_text_annotation",
                        f"unknown annotation local key {base_key!r}",
                    )
                )
            self._check_presentation_references(
                manifest_label,
                presentation,
                annotations_by_key,
                base_key,
                diagnostics,
            )
        else:
            base_matches = [
                entry
                for entry in annotations
                if entry[1]["provenance"]["local_key"] == "base-text"
                or "base-text" in entry[1].get("tags", [])
            ]
            if len(base_matches) == 1:
                base_entry = base_matches[0]
            elif len(base_matches) > 1:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        "$.annotations",
                        f"multiple base-text annotations found ({len(base_matches)})",
                    )
                )

        if base_entry is None:
            return
        base_path, base_annotation = base_entry
        try:
            base = index_base_text(base_annotation["target"]["exact_text"])
        except TargetResolutionError as error:
            diagnostics.append(Diagnostic(str(base_path), "$.target.exact_text", str(error)))
            return

        base_target = base_annotation["target"]
        for path, annotation in annotations:
            target = annotation["target"]
            if target["work_id"] != base_target["work_id"]:
                diagnostics.append(
                    Diagnostic(
                        str(path),
                        "$.target.work_id",
                        f"target work differs from base text {base_target['work_id']!r}",
                    )
                )
            if target["edition_source_id"] != base_target["edition_source_id"]:
                diagnostics.append(
                    Diagnostic(
                        str(path),
                        "$.target.edition_source_id",
                        "target edition source differs from the base text",
                    )
                )
            try:
                resolve_target(target, base)
            except TargetResolutionError as error:
                diagnostics.append(Diagnostic(str(path), "$.target.exact_text", str(error)))

        if presentation is not None and presentation.get("texts"):
            self._check_text_views(
                manifest_label,
                presentation,
                base_entry,
                base,
                annotations,
                diagnostics,
            )

    @staticmethod
    def _check_text_views(
        manifest_label: str,
        presentation: Mapping[str, Any],
        base_entry: tuple[Path, dict[str, Any]],
        canonical_base: Any,
        annotations: Sequence[tuple[Path, dict[str, Any]]],
        diagnostics: list[Diagnostic],
    ) -> None:
        text_views = presentation["texts"]
        views_by_id: dict[str, tuple[int, Mapping[str, Any]]] = {}
        for index, view in enumerate(text_views):
            text_id = view["id"]
            if text_id in views_by_id:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.texts[{index}].id",
                        f"duplicate text ID {text_id!r}",
                    )
                )
            else:
                views_by_id[text_id] = (index, view)

        canonical_views = [view for view in text_views if view["type"] == "canonical-target"]
        if len(canonical_views) != 1:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.texts",
                    f"text views require exactly one canonical-target, found {len(canonical_views)}",
                )
            )
        canonical_id = canonical_views[0]["id"] if len(canonical_views) == 1 else None

        default_text = presentation["default_text"]
        if default_text not in views_by_id:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.default_text",
                    f"unknown text ID {default_text!r}",
                )
            )

        derived_ids: list[str] = []
        for index, view in enumerate(text_views):
            if view["type"] != "editorial-derivation":
                continue
            text_id = view["id"]
            derived_ids.append(text_id)
            if canonical_id is not None and view["derived_from"] != canonical_id:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.texts[{index}].derived_from",
                        f"editorial derivation must reference canonical text {canonical_id!r}",
                    )
                )

        selector_maps: dict[str, dict[str, tuple[int, Mapping[str, Any]]]] = {}
        for path, annotation in annotations:
            selectors: dict[str, tuple[int, Mapping[str, Any]]] = {}
            for index, selector in enumerate(annotation["target"].get("display_selectors", [])):
                text_id = selector["text_id"]
                selector_path = f"$.target.display_selectors[{index}].text_id"
                if text_id in selectors:
                    diagnostics.append(
                        Diagnostic(str(path), selector_path, f"duplicate selector for text {text_id!r}")
                    )
                    continue
                selectors[text_id] = (index, selector)
                if text_id not in views_by_id:
                    diagnostics.append(
                        Diagnostic(str(path), selector_path, f"unknown text ID {text_id!r}")
                    )
                elif text_id == canonical_id:
                    diagnostics.append(
                        Diagnostic(
                            str(path),
                            selector_path,
                            "canonical text uses target.exact_text and cannot have a display selector",
                        )
                    )
            selector_maps[annotation["provenance"]["local_key"]] = selectors
            for text_id in derived_ids:
                if text_id not in selectors:
                    diagnostics.append(
                        Diagnostic(
                            str(path),
                            "$.target.display_selectors",
                            f"missing selector for editorial text {text_id!r}",
                        )
                    )

        base_path, base_annotation = base_entry
        base_key = base_annotation["provenance"]["local_key"]
        base_selectors = selector_maps[base_key]
        display_bases: dict[str, Any] = {}
        canonical_stanzas = tuple(line.stanza_start for line in canonical_base.lines)
        for text_id in derived_ids:
            selector_entry = base_selectors.get(text_id)
            if selector_entry is None:
                continue
            selector_index, selector = selector_entry
            selector_path = f"$.target.display_selectors[{selector_index}].exact_text"
            try:
                display_base = index_base_text(selector["exact_text"])
            except TargetResolutionError as error:
                diagnostics.append(Diagnostic(str(base_path), selector_path, str(error)))
                continue
            display_stanzas = tuple(line.stanza_start for line in display_base.lines)
            if display_stanzas != canonical_stanzas:
                diagnostics.append(
                    Diagnostic(
                        str(base_path),
                        selector_path,
                        "editorial text must preserve canonical line count and stanza boundaries",
                    )
                )
                continue
            display_bases[text_id] = display_base

        for path, annotation in annotations:
            target = annotation["target"]
            selectors = selector_maps[annotation["provenance"]["local_key"]]
            for text_id, display_base in display_bases.items():
                selector_entry = selectors.get(text_id)
                if selector_entry is None:
                    continue
                selector_index, selector = selector_entry
                display_target = {
                    "locator": target["locator"],
                    "exact_text": selector["exact_text"],
                }
                if "prefix" in selector:
                    display_target["prefix"] = selector["prefix"]
                if "suffix" in selector:
                    display_target["suffix"] = selector["suffix"]
                try:
                    resolve_target(display_target, display_base)
                except TargetResolutionError as error:
                    diagnostics.append(
                        Diagnostic(
                            str(path),
                            f"$.target.display_selectors[{selector_index}].exact_text",
                            f"text {text_id!r}: {error}",
                        )
                    )

    @staticmethod
    def _check_presentation_references(
        manifest_label: str,
        presentation: Mapping[str, Any],
        annotations_by_key: Mapping[str, tuple[Path, dict[str, Any]]],
        base_key: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        lenses = presentation["lenses"]
        pathways = presentation["pathways"]
        lens_ids: dict[str, int] = {}
        for index, lens in enumerate(lenses):
            lens_id = lens["id"]
            if lens_id in lens_ids:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.lenses[{index}].id",
                        f"duplicate lens ID {lens_id!r}",
                    )
                )
            else:
                lens_ids[lens_id] = index
            if not any(
                local_key != base_key and lens["tag"] in annotation.get("tags", [])
                for local_key, (_, annotation) in annotations_by_key.items()
            ):
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.lenses[{index}].tag",
                        f"lens tag {lens['tag']!r} matches no non-base annotation",
                    )
                )

        pathway_ids: dict[str, int] = {}
        for pathway_index, pathway in enumerate(pathways):
            pathway_id = pathway["id"]
            if pathway_id in pathway_ids:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.pathways[{pathway_index}].id",
                        f"duplicate pathway ID {pathway_id!r}",
                    )
                )
            else:
                pathway_ids[pathway_id] = pathway_index

            overview = pathway["overview_annotation"]
            if overview == base_key or overview not in annotations_by_key:
                diagnostics.append(
                    Diagnostic(
                        manifest_label,
                        f"$.presentation.pathways[{pathway_index}].overview_annotation",
                        f"unknown non-base annotation local key {overview!r}",
                    )
                )

            step_ids: dict[str, int] = {}
            for step_index, step in enumerate(pathway["steps"]):
                step_id = step["id"]
                if step_id in step_ids:
                    diagnostics.append(
                        Diagnostic(
                            manifest_label,
                            f"$.presentation.pathways[{pathway_index}].steps[{step_index}].id",
                            f"duplicate pathway step ID {step_id!r}",
                        )
                    )
                else:
                    step_ids[step_id] = step_index
                for key_index, annotation_key in enumerate(step["annotation_keys"]):
                    if annotation_key == base_key or annotation_key not in annotations_by_key:
                        diagnostics.append(
                            Diagnostic(
                                manifest_label,
                                f"$.presentation.pathways[{pathway_index}].steps[{step_index}].annotation_keys[{key_index}]",
                                f"unknown non-base annotation local key {annotation_key!r}",
                            )
                        )

        default_mode = presentation.get("default_mode", "plain")
        default_lens = presentation.get("default_lens")
        default_pathway = presentation.get("default_pathway")
        if default_mode == "lens" and default_lens not in lens_ids:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.default_lens",
                    f"unknown default lens {default_lens!r}",
                )
            )
        elif default_lens is not None and default_lens not in lens_ids:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.default_lens",
                    f"unknown lens ID {default_lens!r}",
                )
            )
        if default_mode == "pathway" and default_pathway not in pathway_ids:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.default_pathway",
                    f"unknown default pathway {default_pathway!r}",
                )
            )
        elif default_pathway is not None and default_pathway not in pathway_ids:
            diagnostics.append(
                Diagnostic(
                    manifest_label,
                    "$.presentation.default_pathway",
                    f"unknown pathway ID {default_pathway!r}",
                )
            )

    @staticmethod
    def _check_evidence_access(
        label: str,
        index: int,
        evidence: Mapping[str, Any],
        source: Mapping[str, Any],
        diagnostics: list[Diagnostic],
    ) -> None:
        access = source["access"]["state"]
        evidence_use = evidence["use"]

        allowed_uses = {
            "fully-consulted": {"direct-evidence", "reported-evidence", "context-only"},
            "excerpt-consulted": {"direct-evidence", "reported-evidence", "context-only"},
            "citation-only": {"reported-evidence", "context-only"},
            "unavailable": {"context-only"},
        }
        if evidence_use not in allowed_uses[access]:
            diagnostics.append(
                Diagnostic(
                    label,
                    f"$.evidence[{index}].use",
                    f"{access} source cannot be used as {evidence_use}",
                )
            )

        if "quotation" not in evidence:
            return
        if access not in {"fully-consulted", "excerpt-consulted"}:
            diagnostics.append(
                Diagnostic(
                    label,
                    f"$.evidence[{index}].quotation",
                    f"quotation requires a consulted source, not {access}",
                )
            )
        quotation_permission = source["rights"]["quotation"]
        if quotation_permission not in {"permitted", "limited"}:
            diagnostics.append(
                Diagnostic(
                    label,
                    f"$.evidence[{index}].quotation",
                    f"source quotation permission is {quotation_permission}",
                )
            )


def _print_diagnostics(diagnostics: Sequence[Diagnostic]) -> None:
    for diagnostic in sorted(diagnostics):
        print(diagnostic.render(), file=sys.stderr)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reference-corpus-validate",
        description="Validate source-first literary annotation corpora without modifying them.",
    )
    parser.add_argument("manifest", nargs="?", help="Path to corpus.yaml")
    parser.add_argument("--schemas", type=Path, default=None, help="Override the schema directory")
    parser.add_argument(
        "--check-schemas",
        type=Path,
        metavar="DIRECTORY",
        help="Meta-validate schemas and exit",
    )
    parser.add_argument(
        "--show-derived-id",
        type=Path,
        metavar="RECORD",
        help="Print the deterministic ID for a source or annotation record",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.check_schemas:
            schemas, _ = load_schemas(args.check_schemas)
            print(f"valid: {len(schemas)} schemas")
            return 0

        if args.show_derived_id:
            record = load_yaml(args.show_derived_id)
            print(derive_record_id(record))
            return 0

        if not args.manifest:
            parser.error("manifest is required unless --check-schemas or --show-derived-id is used")

        validator = CorpusValidator(args.schemas)
        diagnostics = validator.validate_manifest(args.manifest)
        if diagnostics:
            _print_diagnostics(diagnostics)
            return 1
        print(f"valid: {Path(args.manifest)}")
        return 0
    except (CorpusLoadError, IdentifierError, OSError, ValidatorConfigurationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
