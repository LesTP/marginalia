# Marginalia

Marginalia builds **annotated reading editions of individual poems**, grounded in cited
scholarship. Each human-reviewed note records the sources actually consulted, separates
documented fact and attributed scholarship from editorial reading, and says plainly what
remains uncertain.

The project is source-first and flat-file. Shared schemas, templates, validation, and tests
live once in this repository; individual poems live together under `corpora/`. Each record
states not only what an annotation says, but what kind of claim it is, which source supports
it, whether that source was actually consulted, where the evidence appears, and how far the
annotation has been reviewed.

Marginalia does **not** automate literary judgment. It gives editors and LLM-assisted
workflows a contract that prevents fluent synthesis from erasing attribution, uncertainty,
access gaps, or publication constraints.

## Inspiration

Marginalia grew out of the annotated edition of T. S. Eliot's *The Waste Land* by Ethan
Mollick and collaborators. That project showed how an LLM-assisted reading edition can make a
difficult poem approachable; Marginalia adapts the idea for other poems while adding an
explicit source-and-evidence discipline so commentary stays traceable to real scholarship.

- Reading edition: <https://the-waste-land.netlify.app/>
- Source repository: <https://github.com/emollick/wasteland-annotated>

Two poems are published so far:

- **W. B. Yeats, "The Song of Wandering Aengus"** (`corpora/yeats-song-of-wandering-aengus/`)
- **John Donne, "A Valediction: Forbidding Mourning"** (`corpora/donne-a-valediction-forbidding-mourning/`)

`index.html` is the landing page that links to each poem's reading view.

## What It Tracks

| Concern | Where it lives |
|---|---|
| Bibliographic identity and stable provenance | Source record |
| Scholarly authority and review status | `quality` in a source record |
| Full, excerpted, citation-only, or unavailable access | `access` in a source record |
| Quotation and reproduction constraints | `rights` in a source record |
| Exact annotated passage and edition | `target` in an annotation record |
| Aligned canonical and editorial reading texts | `presentation.texts`, `default_text`, and `target.display_selectors` |
| Reader-facing annotation heading | Optional `title` in an annotation record |
| Plain reading, lenses, and ordered pathways | Optional `presentation` in the corpus manifest |
| Fact, consensus, attributed reading, synthesis, proposal, or conjecture | `claim.epistemic_status` |
| Supporting, qualifying, disputing, or contextual evidence | `evidence` |
| Exact page, line, chapter, or archival locator | `evidence[].citation.locator` |
| Named scholarly positions | `claim.attributions` |
| Human assessment of evidentiary support | `claim.editorial_confidence` |
| Draft, source-verified, or editorially approved state | `review` |

Editorial confidence is never model confidence or a probability. It is an editor's
assessment of how well the recorded evidence supports the published claim.

## Project Layout

```text
index.html                   Landing page linking to each poem's reading view
corpus.yaml                  Empty starter manifest
corpora/                     Self-contained poem corpora and their reading views
schemas/                     Shared JSON Schema Draft 2020-12 contracts
templates/                   Copyable YAML starters
examples/valid/              Fictional contract examples
scripts/refresh-review.py    Refreshes the embedded data in a hand-authored review.html
src/reference_corpus/        Shared read-only validator, ID derivation, and renderer
tests/                       Contract, renderer, failure-mode, and real-corpus tests
```

Each poem uses `corpora/<corpus-slug>/corpus.yaml` with its own `records/sources/` and
`records/annotations/` directories, plus:

```text
corpora/<corpus-slug>/
  corpus.yaml                Manifest: sources, annotations, presentation
  records/sources/           Source records (and local-only source captures)
  records/annotations/       Annotation records
  review.html                Published hand-authored reading view (see below)
  drafts/                    Archived generated view and superseded prototypes
```

This avoids a separate repository for every poem while keeping source graphs and editorial
decisions isolated.

Canonical records use `.yaml`, UTF-8 without a BOM, LF line endings, Unicode NFC, and only
JSON-compatible YAML values. Quote dates such as `"2026-09-22"`; an unquoted YAML date
becomes a non-JSON Python date and is rejected. A YAML scalar that begins with `"` must be a
block scalar (`>-`) or it will be misparsed as a quoted string.

The internal Python package is still named `reference_corpus`, with the console commands
`reference-corpus-validate` and `reference-corpus-render`. Renaming the package is deferred;
it is invisible to the published pages.

## Two Presentation Views

Each corpus has one published page, `review.html`, but the repository supports two distinct
presentation tracks.

- **Generated view (the renderer).** `reference-corpus-render` turns a validated manifest
  into a self-contained accordion review page. It is deterministic output: edit the YAML and
  rerun the renderer. The archived generated page for each corpus lives in its `drafts/`
  folder.
- **Published reading view (hand-authored).** The current `review.html` for each poem is a
  hand-authored "continuous note stream" design: a sticky poem synchronized with a single
  scroll of notes, subject **Focus** filters, one note open at a time, short citations that
  link to full records under **Sources**, and period typography for historical texts. Its
  layout, CSS, JavaScript, and embedded fonts are maintained by hand.

The reading view embeds a snapshot of the same validated presentation model the renderer
builds (the `<script id="corpus-data">` block from
`reference_corpus.review.build_review_model`), so the poem text, notes, evidence, and
line highlighting stay faithful to the YAML while the design stays hand-authored. After any
editorial change, refresh that snapshot:

```powershell
$env:PYTHONPATH = "src"
reference-corpus-validate .\corpora\<corpus-slug>\corpus.yaml
python scripts\refresh-review.py .\corpora\<corpus-slug>\corpus.yaml
```

`scripts/refresh-review.py` validates first, then rebuilds and replaces only the embedded
data block, leaving the surrounding page intact.

> **Caveat.** Running `reference-corpus-render` writes the *generated* accordion design to
> `review.html` and would overwrite the hand-authored reading view. If you want the generated
> page, send it elsewhere with `--output` (for example into `drafts/`).

## Install

From the repository root in PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Any Python 3.10 or newer interpreter may be used if the `py -3.10` launcher is not
available.

## Editorial Workflow

1. Create or select `corpora/<corpus-slug>/`, then copy `templates/source.yaml` into its `records/sources/` directory.
2. Record the source's bibliographic identity and a stable provenance coordinate.
3. State exactly how much of the source was consulted.
4. Record why the source is authoritative for its intended use.
5. Track quotation and reproduction constraints without treating them as legal advice.
6. Derive the source ID and put it in the record.
7. Copy `templates/annotation.yaml` into that corpus's `records/annotations/` directory.
8. Identify the exact work, edition, locator, and passage being annotated.
9. Write for a general reader: explain what the passage does and why it matters before introducing scholars, debate, or source limitations.
10. Add an optional public `title` when the stable local key would make an awkward heading, then select the claim's epistemic status.
11. Attach evidence with source IDs and exact citation locators.
12. Attribute scholar-specific or contested readings explicitly after the reader-facing explanation.
13. Record editorial confidence and its rationale.
14. Keep the annotation in `draft` until the required source review has occurred.
15. Add the relative record paths to that corpus's `corpus.yaml`.
16. Optionally configure Plain reading, lenses, and guided pathways in `presentation`.
17. When presenting an aligned editorial derivation, declare the canonical and derived text views and add an exact display selector for every annotation in every derived view.
18. Validate before review or publication.
19. Refresh the reading view's embedded data with `scripts/refresh-review.py` (or render a generated view to a scratch path).

Generate IDs without modifying a record:

```powershell
reference-corpus-validate --show-derived-id .\records\sources\example.yaml
reference-corpus-validate --show-derived-id .\records\annotations\example.yaml
```

Source IDs derive from the provenance scheme and value. Annotation IDs derive from the
work, edition, target locator, annotation type, and `provenance.local_key`. Editing the
public `title`, claim prose, confidence, or review metadata does not change an annotation's
identity.

## Audience and Voice

The public page is written for a general reader, not for someone already familiar with the
author's scholarship or the latest critical debate. An annotation should normally proceed
in this order:

1. Say what happens in the selected passage or identify the pattern a reader can notice.
2. Explain why it changes or deepens the reading of the work.
3. Introduce a named scholar, competing interpretation, source limitation, or editorial uncertainty only when it helps clarify that meaning.

Do not begin reader-facing prose with labels such as "Editorial synthesis," with a scholar's
name, or with a summary of research procedure. Those facts belong in the structured status,
attribution, confidence, evidence, and citation fields, which remain visible after the
explanation. Explicit attribution is still required; it should support an intelligible
account rather than substitute for one.

Use `title` for a concise public heading and `provenance.local_key` for stable internal
references. A missing title falls back to a humanized local key for backward compatibility.

## Access Discipline

Access state constrains evidence use:

| Source access | Allowed evidence use |
|---|---|
| `fully-consulted` | Direct, reported, or contextual |
| `excerpt-consulted` | Direct within the recorded scope, reported, or contextual |
| `citation-only` | Reported or contextual only |
| `unavailable` | Contextual only |

A citation-only source must say how the citation was encountered and what remains
unverified. An unavailable source can remain in the research map, but it cannot support a
claim as though it had been read. Quotations require a fully or excerpt-consulted source
and a rights record that marks quotation as `permitted` or `limited`.

## Epistemic Status

- `documented-fact`: directly established by textual, archival, bibliographic, or historical evidence.
- `scholarly-consensus`: supported by at least two distinct scholarly sources.
- `attributed-interpretation`: a reading assigned to a named scholar and linked to evidence.
- `editorial-synthesis`: the corpus editor's synthesis of recorded evidence.
- `editorial-proposal`: a new reading offered for consideration rather than as established scholarship.
- `conjecture`: a deliberately speculative possibility with uncertainty kept visible.

A contested annotation keeps positions separate. It requires a contestation note and at
least two named attributions, each connected to evidence within the annotation.

## Validate

```powershell
reference-corpus-validate --check-schemas .\schemas
reference-corpus-validate .\corpora\yeats-song-of-wandering-aengus\corpus.yaml
reference-corpus-validate .\corpora\donne-a-valediction-forbidding-mourning\corpus.yaml
python -m pytest
```

The command is read-only and deterministic. It reports all discovered errors with paths
such as `$.evidence[1].citation.locator`.

Exit codes:

- `0`: schemas and corpus are valid.
- `1`: record, canonicalization, reference, or cross-record validation failed.
- `2`: operational failure or invalid validator/schema configuration.

## Real Corpora

- `corpora/yeats-song-of-wandering-aengus/` is the first pilot: a verified public-domain base text, ten source records, eleven public notes, and an explicitly editorial guided reading.
- `corpora/donne-a-valediction-forbidding-mourning/` demonstrates an edition-faithful 1633 transcription and a line-aligned modernized derivation, both resolved against the same human-reviewed annotations, with commentary drawn from Grierson (1912) and Freccero (1963).
- `corpora/README.md` is the catalog and layout guide for future poems.

The root `corpus.yaml` remains an empty starter manifest; it is not an umbrella manifest and does not embed child corpora.

## Configure Reading Modes

A corpus may add an optional `presentation` block to its manifest. The shared renderer
always supplies **Plain reading**, **All notes**, and **Sources**. A configured corpus may
also define its own lenses and ordered pathways without changing renderer code. The
hand-authored reading view reuses the same presentation model, exposing lenses as **Focus**
filters over one continuous note stream.

- `base_text_annotation` names the base record by `provenance.local_key`.
- Optional `texts` declares exactly one `canonical-target` view and one or more `editorial-derivation` views; `default_text` selects the initial view. Derived views must name the canonical view in `derived_from`.
- Every derived view requires a matching `target.display_selectors` entry on every annotation. Display selectors do not change annotation identity, and the validator resolves them independently while requiring aligned nonblank lines and stanza boundaries.
- A text view may set `historical_forms: true` to display period spelling with vendored IM FELL English Roman and Italic faces for that view only; other views and all notes use the reading serif.
- Optional `witness_presentation` metadata may supply an exact printed heading, request source-backed author and issued-year display, indent selected one-based lines within each stanza, and enlarge the first initial. These are DOM/CSS presentation instructions: stored text, selectors, copied text, and annotation identity remain unchanged.
- `default_mode` may be `plain`, `lens`, `pathway`, `all`, or `sources`; omission means `plain`.
- Each lens supplies an ID, label, description, and annotation tag.
- Each pathway supplies a short introductory annotation and ordered steps; a step may contain one or more existing annotations.
- Presentation references use local keys rather than derived annotation IDs, so normal prose and exact-target edits do not break navigation.

For line-based annotations, `target.locator` defines the candidate range and
`target.exact_text` identifies the precise passage inside it. The validator requires one
literal match. Use `target.prefix` or `target.suffix` only to disambiguate repeated text.

See `templates/manifest.yaml` for a generic configuration,
`corpora/yeats-song-of-wandering-aengus/corpus.yaml` for the single-text worked example, and
`corpora/donne-a-valediction-forbidding-mourning/corpus.yaml` for aligned canonical and
editorial text views.

## Render a Review Page

The renderer turns a valid manifest into one self-contained HTML file. It works through
`file://`: there is no server, JavaScript build, external stylesheet, external font request,
or runtime data request. A text view may opt into a vendored OFL font embedded directly in
the file with its attribution and license.

```powershell
reference-corpus-render .\corpora\yeats-song-of-wandering-aengus\corpus.yaml --output .\corpora\yeats-song-of-wandering-aengus\drafts\generated.html
```

Rendering always validates first and refuses to replace the output if the corpus is invalid.
As noted above, the default output path is `review.html` beside the manifest, which is the
hand-authored reading view; pass `--output` to avoid overwriting it.

## Publish (GitHub Pages)

Every `review.html` and `index.html` is a self-contained static file with embedded fonts and
data and **no external requests**, so GitHub Pages can serve the repository as-is with no
build step.

1. Push the repository (suggested repo name: `marginalia`).
2. In the repository settings, enable Pages from the `main` branch root.
3. The landing page is served at `https://<user>.github.io/marginalia/`, and each poem at
   `https://<user>.github.io/marginalia/corpora/<corpus-slug>/review.html`.

### Publishing and copyright

`.gitignore` excludes local-only **source captures** — page images or screenshots of
copyrighted sources (for example, journal-article scans under `records/sources/`). These are
consulted locally to write paraphrased, cited notes but must not be redistributed. The
paraphrases and citation records that depend on them are tracked and published.

Everything else is safe to publish: the poem texts are public domain (Donne, 1633; Yeats,
1899), and the bundled fonts (Libre Caslon; IM FELL English Roman and Italic) are under the
SIL Open Font License, with their `OFL.txt` files kept alongside them.

## Examples

- `examples/valid/basic/` shows a fully consulted critical edition supporting a documented textual fact.
- `examples/valid/limited-access/` shows a citation-only article used as reported evidence without quotation.
- `examples/valid/contested-interpretation/` preserves two directly consulted scholarly positions without collapsing them into consensus.

All names, works, publishers, identifiers, and arguments in the examples are fictional.
They demonstrate the contract without presenting invented bibliography as real scholarship.

## Scope and Limitations

Marginalia validates editorial declarations; it cannot determine whether a citation is true,
a page was genuinely consulted, an interpretation is persuasive, or a proposed use is legally
permissible. Human source checking and editorial judgment remain required.

The project intentionally has no database, document importer, annotation editor, general
publication system, or CRUD CLI. The renderer and the refresh helper are narrow, read-only
presentations of existing records; broader publishing or editing features require a separate
design decision.
