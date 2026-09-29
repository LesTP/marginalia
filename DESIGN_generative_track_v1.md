# DESIGN: Generative Track v1

**Status:** Draft — 2026-09-29. A proposal for discussion; nothing is built. §6
(infrastructure) is a first inventory, to be elaborated.
**Scope:** a second way of producing corpus records, alongside the existing
source-first workflow. Same project, same schemas, validator and renderer.
**Depends on:** `schemas/`, `src/reference_corpus/`, the Editorial Workflow in
`README.md`, the rules in `CLAUDE.md`.
**Origin:** a discussion of the annotated *Waste Land* (see `README.md`,
"Inspiration") and how its commentary was produced.

---

## 0. Summary

Marginalia today is **source-first**: a source record exists before any claim
rests on it, and annotations are written within what was consulted. Models may
help draft (current Donne records carry `created_by: Devmate-assisted editorial
draft`), but the sources set the agenda.

The **generative track** starts from the other end. Models generate commentary
broadly: background, biography, period context, parallels, influence, readings.
The pipeline then sources, verifies, edits and selects until what survives is
publishable under the same contract. The aim is breadth that the source-first
track cannot reach on its own, in service of the project's purpose: helping a
reader think about the poem.

The two tracks produce the same kind of record and must pass the same validator.
The generative track relaxes no rule in `CLAUDE.md`. It adds a way of *finding*
things to say, not a lower bar for *saying* them.

## 1. Two tracks, one contract

| | Source-first track (existing) | Generative track (new) |
|---|---|---|
| Starting point | Consulted sources | Model-generated drafts and readings |
| Who sets the agenda | The sources | The models, then the sources |
| Main risk | Narrow coverage | Unsourced or wrong detail passing as fact; anchoring on the draft |
| Model role | Drafting assistant | Generator, verifier, editor (distinct roles, ideally distinct models) |
| Human role | Author and reviewer | Selector, orderer, final reviewer |
| Output | Records under `corpora/<slug>/` | The same records, the same validator |

Invariant: a reader can see the standing of every published claim, whichever
track produced it.

## 2. Background: what the *Waste Land* pipeline did

From the repository history of `emollick/wasteland-annotated` (20 Sept 2026, UTC):

1. 03:43: poem text fetched from the 1922 Boni & Liveright scans (sourced).
2. 04:52: the whole commentary, together with research files (verified links to
   primary texts, media, image licences), committed in one model session. The
   prose carried no per-claim evidence.
3. 05:46: a self-check pass by the same session (about forty corrections).
4. 17:30–19:20: six debates (editor, scholar agent, reader agent; the scholar
   decides substance and the reader wording). Mostly correction, cutting and
   hedging: "the text takes the safer reading".
5. Evening: a `sources:` field added to existing claims (citation retrofit), with
   unverifiable claims listed in reports rather than cited.

Lessons carried into this design:

- **Retrofit sourcing checks claims but cannot widen them.** Coverage and framing
  stay the model's.
- **Provenance was reconstructable only from process files**, not from the records.
  A reader cannot tell a claim checked against page images from one resting on a
  search-inside snippet.
- **Editing rounds polish prose, not provenance.** A Wikipedia-sourced detail
  passed through the debates; the ban on Wikipedia came later, in the citation brief.
- **The debates were convergent review, not idea generation.** Same-model roles
  share priors, so their errors are correlated.
- **What worked:** strict citation rules (no guessed page numbers; report errors
  rather than fixing them; leave uncited rather than invent), fixed fields frozen
  across edit rounds, and explicit role asymmetry.

## 3. Principles

1. **Provenance is captured when a claim is written**, never reconstructed later.
2. **Edit rounds change wording only.** Evidence, status and targets are frozen once
   verified.
3. **Verify against the source text**, not against another model's knowledge.
4. **Agreement between models is a signal, not evidence.** They share training data.
   Disagreement is a flag to verify.
5. **Disagreement between models is not scholarly contestation.** A contested
   annotation still needs named scholars and evidence. Model debate only shows
   where to look.
6. **Models point at experience; they do not report it.** "Count the ANDs in lines
   7–12 and read them aloud" rather than "the ANDs propel the poem forward".
7. **Novelty is a factual claim.** Before a reading is published as an
   `editorial-proposal`, search for prior attribution.
8. **Humans select, order and judge.** Editorial confidence and review state are
   human assessments (`CLAUDE.md`); the pipeline never sets them above `unassessed`
   / `draft`.
9. **Divergent before convergent.** Generate readings independently and blind, then
   argue, then verify.

## 4. The pipeline

| # | Stage | Input | Output | Actor | Gate |
|---|---|---|---|---|---|
| 1 | **Explore** | Poem text | Topics, candidate claims and questions (never published) | Model | — |
| 2 | **Diverge** | Poem text, per passage | Readings and connections from several models, run blind | Several models | — |
| 3 | **Pool** | Stage 2 output | Candidates classed as shared (likely standard; find the critic) or singular (candidate proposal; check support and novelty) | Model + human | Human skim |
| 4 | **Gather sources** | Stage 1–3 candidates, *and* the poem independently | Source records with honest `access`, `quality`, `rights` | Model + human | Validator |
| 5 | **Regenerate as records** | Sources in context (optionally a second run without the draft, to check anchoring) | Annotation YAML: each claim with evidence, locator, quoted span and epistemic status; unsupported claims demoted or flagged | Model | Validator |
| 6 | **Verify** | Stage 5 records and source texts | Per-evidence report: the span appears, the passage supports the claim, the locator is right | A different model | Report reviewed |
| 7 | **Edit** | Verified records | Wording revised; evidence, status and targets frozen | Editor and reader roles | Frozen-field check |
| 8 | **Select and review** | Edited records | Chosen notes, order, pathways, confidence, review state; one human reader pass | Human | Publication |

Stages 2–3 are the part the *Waste Land* barely used. Stages 6–7 correspond to its
debates, split so that checking facts and editing wording never happen in the same
pass.

## 5. Open decisions

- **D1. Unsourced factual background.** A claim that is probably true but that no
  source reachable here supports: (a) publish with a new visible status, (b) mark it
  in provenance and keep it unpublished, or (c) never let it past stage 5. The schema
  has no status for it today: `editorial-synthesis` needs recorded evidence and
  `conjecture` mislabels it.
- **D2. What counts as "consulted".** If a model read the full source text in
  context, is that `fully-consulted`? Or does `access` describe what a human
  editor consulted? This affects every stage 4–6 record.
- **D3. Where generative-track records live and how they are marked.** The options:
  mixed into existing corpora, kept as separate corpora, or distinguished by a field
  (the free-text `provenance.created_by` exists; a controlled vocabulary would make
  it checkable). Is the origin shown to readers?
  - **Finding (2026-09-29, Yeats "irish-identity" pilot).** *Unpublished* drafts must
    live in `corpora/<slug>/drafts/generative-track/`, not in the corpus `records/`
    tree. The validator requires every file under `records/sources/` and
    `records/annotations/` to be listed in the manifest ("record is not listed in
    corpus manifest"), and the real-corpus tests pin exact source/annotation counts
    plus a current `review.html` snapshot. So there is no "loose draft" slot inside
    `records/`: a draft placed there fails validation and breaks the pinned tests.
    Keeping drafts under `drafts/generative-track/` leaves them beside the poem,
    out of the validator's `records/` scan, and out of the published reading view.
  - **Validation of a draft in that location.** The corpus validator only checks
    records reachable from the manifest, so a draft in `drafts/generative-track/` is
    not validated in place. To validate it, temporarily add its relative paths to the
    manifest `sources`/`annotations`, run `reference-corpus-validate`, then revert the
    manifest. (Done for the Yeats pilot: exit 0.)
  - **Promotion path (verified).** Move the source files into `records/sources/` and
    the annotation into `records/annotations/`, add all three to `corpus.yaml`, set
    `review.state` (e.g. `human-reviewed` with reviewer and date), refresh the reading
    view (`python scripts\refresh-review.py <corpus.yaml>`), and update the pinned
    counts in `tests/test_validation.py` and `tests/test_review.py`.
  - **Still open:** whether *published* generative-track records are marked in a
    controlled `provenance.created_by` vocabulary (the pilot uses free text,
    `"Devmate generative-track draft"`), and whether that origin is shown to readers.
- **D4. Tertiary sources.** Wikipedia and similar: either recorded honestly
  (`authority: established-reference` or `informal-resource`, context-only), or
  used as finding aids only, with the underlying source cited instead.
- **D5. Model roster and independence.** Which models fill which roles; blind first
  rounds; which additions need new adapters (for example Grok).
- **D6. Process records.** Keep every round (the *Waste Land* keeps 198 debate
  files) or only the decisions for each annotation.
- **D7. Tooling scope.** Stages 4–5 write records. `CLAUDE.md` forbids an importer
  or editing surface "without a separate design decision". This document is where
  that decision belongs, once scoped.

## 6. Infrastructure (first inventory, to be elaborated)

### 6.1 In this repository (verified 2026-09-29)

- **Contracts:** JSON Schema 2020-12 for sources, annotations and manifests;
  vocabularies for `epistemicStatus`, `accessState`, `evidenceUse`,
  `authorityCategory`, `reviewState` and `editorialConfidence`.
- **Validator** (`reference-corpus-validate`): read-only, path-aware, enforces the
  access and quotation rules. This is the gate at stages 4, 5 and 7.
- **Identity** (`identifiers.py`): IDs derived from provenance and target, so edits
  to prose do not change identity. This supports the frozen-field check at stage 7.
- **Target resolution** (`targets.py`): `exact_text` must match the poem once. A
  similar matcher against *source* texts would serve stage 6.
- **Presentation** (`review.py`, `scripts/refresh-review.py`): the review model and
  reading view, unchanged by this track.
- **Evidence fields:** `evidence[].quotation`, `citation.locator` and
  `relationship` already hold what stage 5 must emit.

### 6.2 Elsewhere in the fleet (to inventory)

- i2c: `[run.backends]` already routes different actions to different models, which
  is a precedent for assigning roles to models. Could the pipeline run as i2c phases?
- pirozhok: where autonomous multi-model runs would execute (the laptop cannot run
  them; FU-28).
- Other projects' fetching, caching or model-adapter code: to be surveyed.

### 6.3 Gaps (preliminary)

- Orchestrating several models for blind rounds.
- Storing source texts for verification (only local captures exist today, and they
  are git-ignored for rights reasons).
- Matching evidence spans against source texts.
- A frozen-field diff between edit rounds.
- A schema decision for D1–D3.

## 7. First experiment

On the Donne corpus: three models, one stanza, no context, run blind (stages 2–3
only). Compare their output with Grierson (1912), Freccero (1963) and the existing
annotations. The question is whether variety between models is real or superficial,
before anything is built.
