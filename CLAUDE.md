# Reference Corpus

## Purpose

This project defines a source-first, flat-file format and maintains multiple real literary
corpora beneath one shared toolchain. It codifies provenance, citations, epistemic status,
access limits, rights metadata, and editorial review without treating literary
interpretation as mechanically decidable.

## Project Rules

- Canonical corpus records are JSON-compatible YAML (`.yaml`, not `.yml`).
- Keep every real text self-contained under `corpora/<corpus-slug>/` with one manifest and `records/sources/` and `records/annotations/` directories.
- Keep schemas, validator behavior, templates, and tests corpus-neutral and shared at the repository root.
- Define corpus-specific lenses and ordered pathways in the manifest `presentation` block; never hardcode them in the shared renderer.
- Treat `corpus.yaml` at the repository root as an empty starter, not an umbrella manifest.
- Keep fictional records under `examples/` and never present them as real scholarship.
- Treat each corpus's `review.html` as deterministic generated output; edit YAML and rerun the renderer instead of hand-editing HTML.
- A deliberately named archival HTML snapshot may be retained when requested, but it is immutable and must not replace the canonical generated `review.html` workflow.
- Rendering must validate before writing and must remain self-contained, read-only, and free of network runtime dependencies.
- JSON Schema Draft 2020-12 files are the normative structural contracts.
- Keep files UTF-8, LF-only, and Unicode NFC.
- Write public titles, navigation copy, and annotations for a general reader who does not already know the scholarship or debate.
- In reader-facing prose, explain what the passage does and why it matters before introducing scholars, attribution, source limits, or editorial uncertainty.
- Never represent an unconsulted source as direct evidence.
- Distinguish documented facts, attributed interpretations, editorial synthesis, and conjecture in structured metadata rather than repeating those labels as prose openings.
- Editorial confidence is a human assessment of evidentiary support, not model confidence.
- Validation is read-only. Tools must not silently normalize or rewrite corpus records.
- Prefer explicit, path-aware errors and deterministic behavior.
- Use Python 3.10+ and PowerShell-compatible commands.
- Do not add a database, importer, editing UI, general publication system, or CRUD surface without a separate design decision.
- Do not commit or amend commits without explicit user confirmation.
