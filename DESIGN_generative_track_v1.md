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
10. **Let the poem suggest its friction.** Participants are cast per poem from the
   tensions that poem actually raises, not from a fixed grid imposed in advance.
11. **A persona is a generation device, not a provenance claim.** What a staged voice
   produces re-enters the honesty machine (section 4.1): a text-as-evidence proposal,
   or an attributed-interpretation only with a real named source.

## 4. The pipeline

| # | Stage | Input | Output | Actor | Gate |
|---|---|---|---|---|---|
| 1 | **Explore** | Poem text | Topics, candidate claims and questions (never published) | Model | — |
| 2 | **Diverge** | Poem text, per passage | Readings and connections from several models, run blind | Several models | — |
| 3 | **Pool** | Stage 2 output | Candidates classed as shared (likely standard; find the critic) or singular (candidate proposal; check support and novelty) | Model + human | Human skim |
| 4 | **Gather sources** | Stage 1–3 candidates, *and* the poem independently | Source records with honest `access`, `quality`, `rights` | Model + human | Validator |
| 5 | **Regenerate as records** | Sources in context (optionally a second run without the draft, to check anchoring) | Annotation YAML: each claim with evidence, locator, quoted span and epistemic status; unsupported claims take a disposition (section 4.1), never a silent drop | Model | Validator |
| 6 | **Verify** | Stage 5 records and source texts | Per-evidence report: the span appears, the passage supports the claim, the locator is right | A different model | Report reviewed |
| 7 | **Edit** | Verified records | Wording revised; evidence, status and targets frozen | Editor and reader roles | Frozen-field check |
| 8 | **Select and review** | Edited records | Chosen notes, order, pathways, confidence, review state; one human reader pass | Human | Publication |

Stages 2-3 are the part the *Waste Land* barely used. Stages 6-7 correspond to its
debates, split so that checking facts and editing wording never happen in the same
pass.

### 4.1 Disposition at stages 4 and 6

Stage 4 (no source found) and stage 6 (verification fails) must **not silently
drop a claim**. They produce a *disposition*, resolved by a human at stage 8. The
disposition turns on one question:

> Does the claim assert something about the world outside the poem (a fact, date,
> event, influence, biography), or does it offer a way of *reading the text*?

A world-fact needs an external source. A reading needs only the poem, which is
always a fully-consulted, public-domain source in the corpus. Three terminal
dispositions follow:

| Disposition | When | Epistemic status | Evidence | Where it goes |
|---|---|---|---|---|
| **backed -> normal** | A source was consulted that supports the claim as stated | Whatever the evidence warrants (`documented-fact`, `scholarly-consensus`, `attributed-interpretation`, `editorial-synthesis`) | The consulted source, with locator and quoted span | Continues through stages 5-7 |
| **reading -> proposal** | The claim is a reading/interpretation; no external scholarship, but the text supports it | `editorial-proposal` (or `conjecture` if deliberately speculative) | The base-text lines (`use: direct-evidence`, `relationship: supports`) | Published once a human reclassifies, points evidence at the text, and signs off |
| **fact -> research-lead** | The claim asserts a world-fact and no reachable source backs it | none assignable; **not published as fact** | none | Retained as a flagged draft in `drafts/generative-track/` (D3), recording the claim, what was searched, and which source would settle it |

Notes:

- **The promotion the editor wants is `reading -> proposal`.** It is not
  "publish something unsourced"; it is "reclassify as a reading whose evidence is
  the text, and sign off." The invariant in section 1 holds: the reader sees
  "editorial proposal," never a fact in disguise. Precedent already in the Yeats
  corpus: `light-and-time` and `future-vow` are `editorial-proposal` records whose
  only evidence is the 1899 base text.
- **`fact -> research-lead` is the guardrail.** "Interesting" can promote a
  reading, but it cannot make a world-fact true. An unbackable factual claim stays
  a lead (this is the narrow D1 case), never published prose. This mirrors the
  *Waste Land* citation brief's rule: report the gap, do not invent a source
  (section 3, principle on novelty and the "report rather than fix" discipline).
- **Mechanical stage-6 failures are not dispositions.** A wrong locator or a
  mistyped quotation against the *right* source loops back to fix the record; only
  a genuine "the source does not support this" or "no source exists" triggers a
  disposition.
- **Confidence and review state are set by the human** at stage 8 (per
  `CLAUDE.md`: editorial confidence is a human assessment, not model confidence).

### 4.2 Discussion participants (casting stages 2-3)

The discussion is meant to be a *source of ideas*, not only an error check. It does
two jobs: **generate** (stage 2 diverge) and **stress-test** (stage 3 argue). How the
participants are cast decides whether it produces anything worth reading.

**Two axes of difference.**

- *Facet* -- form, history/biography, sources and influence, reception, prosody,
  textual history. These map onto the corpus lenses and `annotation_type`s. They are
  parallel, not opposed, so they give *coverage* but little friction.
- *Stance* -- who holds a view and what is at stake. This is where genuine
  disagreement, and the better ideas, come from.

**On the stance axis, prefer period-contemporary friction over theory grids.**
Staging two contemporaries divided on a live, contentious question of the poem's own
moment (for Yeats c. 1899, the cultural-nationalist vs the cosmopolitan skeptic; for
Donne, the taste for "strong lines" and scholastic wit vs the plain-style objector)
tends to be historically anchored and to surface what was actually at stake. Imported
theoretical schools (marxist, feminist, freudian, and the like) are noted but not the
focus: they generate fluently but are the register most prone to ungrounded,
doctrine-driven readings, and they tend to make the note about the theory rather than
the poem.

**Do not over-specify the cast in advance (principle 10).** Each poem suggests its
own sources of friction. Prefer *discover then cast*: let an early pass name the live
tensions around this particular poem, then run the strongest one or two as a staged
disagreement, rather than applying one fixed roster to every poem.

**Personas are a generation device, not a provenance claim (principle 11).** A staged
voice is scaffolding to surface ideas; its output re-enters the honesty machine of
section 4.1:

- tied to a *real named critic with a real source* -> `attributed-interpretation`,
  and a two-sided cast maps onto the **contested** annotation type (two named
  attributions + evidence + contestation note);
- a defensible reading with no external scholarship -> `editorial-proposal`, the text
  as its evidence, optionally framed as "one way to read this was as a stake in debate
  X";
- an invented quotation or attribution -> caught at stage 6, demoted to a
  research-lead or dropped.

**Model diversity and persona diversity are orthogonal.** Different stances
decorrelate *perspective*; different model families decorrelate *training and error*.
Cast persona x model where possible, so the debate is not one model ventriloquizing
every voice (the *Waste Land* "model playing a critic" failure).

## 5. Open decisions

- **D1. Unsourced factual background (the `fact -> research-lead` case).** This is
  now scoped by section 4.1: it covers *only* world-facts that are probably true but
  that no reachable source supports. Readings and opinions are out of scope for D1 —
  they are handled by `reading -> proposal` and need no external source. What remains
  open for the factual case: (a) publish with a new visible status, (b) keep it as a
  flagged research-lead in `drafts/generative-track/` (the current default), or
  (c) never let it past stage 5. The schema still has no status that fits a
  probably-true-but-unbacked fact: `editorial-synthesis` needs recorded evidence and
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
- **D7. Tooling scope.** Stages 4-5 write records. `CLAUDE.md` forbids an importer
  or editing surface "without a separate design decision". This document is where
  that decision belongs, once scoped.
- **D8. Casting discussion participants.** How stages 2-3 are populated (section
  4.2): whether a small reusable persona set lives in the corpus manifest
  `presentation` block or is discovered fresh per poem per run; how the contention
  axis is chosen (bottom-up discovery vs top-down assignment); and how persona output
  is logged so a staged view is never later mistaken for a sourced one.

## 6. Infrastructure

Decisions settled 2026-10-02 (clarified with the operator):

1. **Substrate:** generate via `toolkit.llm_client` + `toolkit.structured_llm`
   (API/SDK providers producing schema-validated output); borrow i2c *patterns*
   (role->model routing, prompt purity, telemetry) but not its agent-CLI machinery.
2. **Debate primitives:** extract diplomat's generic critic / divergence /
   discussion / judge pieces into shared `toolkit`; reference-corpus becomes the
   second consumer that qualifies them under toolkit's second-consumer rule.
3. **Run location:** support both supervised laptop runs and autonomous headless
   sweeps on pirozhok (section 6.5).

### 6.1 In this repository (verified 2026-09-29)

- **Contracts:** JSON Schema 2020-12 for sources, annotations and manifests;
  vocabularies for `epistemicStatus`, `accessState`, `evidenceUse`,
  `authorityCategory`, `reviewState` and `editorialConfidence`.
- **Validator** (`reference-corpus-validate`): read-only, path-aware, enforces the
  access and quotation rules. It stays the **authoritative gate** at stages 4, 5 and
  7 even when an upstream tool pre-validates (see stage 5 below).
- **Identity** (`identifiers.py`): IDs derived from provenance and target, so edits
  to prose do not change identity. This supports the frozen-field check at stage 7.
- **Target resolution** (`targets.py`): `exact_text` must match the poem once. A
  similar matcher against *source* texts would serve stage 6.
- **Presentation** (`review.py`, `scripts/refresh-review.py`): the review model and
  reading view, unchanged by this track.
- **Evidence fields:** `evidence[].quotation`, `citation.locator` and
  `relationship` already hold what stage 5 must emit.

### 6.2 Reusable fleet tooling

**toolkit (generation substrate; a pure import library, no orchestration of its
own -- the consumer wires the pipeline).**

- `toolkit.llm_client` -- providers Anthropic/OpenAI/Gemini/OpenRouter, tiered
  (`ModelTier` QUALITY/DEFAULT/COMMODITY), `complete` / `complete_with_retry`
  (`src/toolkit/llm_client/providers.py`, `types.py`).
- `toolkit.structured_llm.structured_call` -- prompt assembly + JSON-Schema
  validation + bounded retry with error feedback (`src/toolkit/structured_llm/core.py`).
  Keystone reuse for stage 5.
- `toolkit.cost_accountant` -- per-call/operation/session budgets + JSONL ledger
  with `attribution` tags (`src/toolkit/cost_accountant/`).
- `toolkit.source_ingestion.normalization` -- `fetch_url_text`, `html_to_text`,
  `extract_urls`, `build_content_item` (fetch without cache/retry).
- `toolkit.embedding` + `toolkit.clustering` -- content-addressed embedding cache
  and HDBSCAN/RAPTOR grouping.
- `toolkit.edit_classifier` -- LLM-as-judge edit categorizer; an existing
  judge-factory precedent in toolkit.

**diplomat (discussion engine; negotiation-domain scoring is discarded -- patterns
extracted per 6.4).**

- Per-role model assignment `--per-faction-providers`
  (`tests/self_play/run_simulation.py:88-100`, `game_environment.py:253-337`).
- Round loop with broadcast/react (`src/flows/round_stepped.py:25-70`) -- the actual
  discussion mechanic.
- Standalone adversarial critic (`src/modules/adversarial/`).
- analyst `compare()` two-model divergence (`src/modules/analyst/divergence.py`).
- `mechanism_classifier` LLM-as-judge with binary-question decomposition and the
  guardrail "judge must be a fixed independent model, not a contestant scoring
  itself" (`ARCH_mechanism_classifier.md:13-37`).
- `rank_aggregator` + `aggregate_stats.bootstrap_ci` for pooling and CIs.
- `LoggingLLMClient` / `DryRunLLMClient` for free provenance and zero-cost dry runs.

**i2c (patterns only, not machinery).** An i2c "backend" is an agent CLI that edits
code and writes `.state/` -- the wrong runtime for producing annotation YAML. Borrow
three patterns: (a) the per-action role->model routing table (`[run.backends]`,
`i2c/config.py:34-55`) as pipeline config; (b) pure/deterministic prompt assembly +
`prompt_hash` for reproducible generation (`DESIGN_provenance_v1.md` section 3);
(c) runner-owned telemetry jsonl as a provenance substrate distinct from
worker-authored records. The Devmate built-in `/council` (3-model blind peer review
+ ranked vote) is a ready manual stand-in for stage 2 during early experiments.

### 6.3 Pipeline stage -> tooling map

| Stage | Reuse | Build / extract |
|---|---|---|
| 1 Explore | `llm_client.complete` (QUALITY), `cost_accountant` | - |
| 2 Diverge (blind) | per-model `LLMConfig`s run independently; role->model routing (i2c pattern); `/council` for quick manual runs | thin blind-runner wiring -- **no cross-talk** |
| 3 Pool | diplomat `analyst.compare` divergence; `rank_aggregator` + `bootstrap_ci`; `embedding` + `clustering` to group overlapping readings | extract divergence -> toolkit (6.4) |
| 3 -> argue | **diplomat round loop (`round_stepped.py`): contest singular readings against the text** | extract round engine -> toolkit, shed negotiation scoring (6.4) |
| 4 Gather sources | `source_ingestion.normalization.fetch_url_text` / `html_to_text` | `toolkit.doc_fetch` (fetch+cache+retry) -- gap |
| 5 Regenerate as records | `structured_call(schema=annotation.schema.json)` -> dict -> `yaml_io`; then `reference-corpus-validate` (authoritative) | map structured output -> repo YAML conventions; disposition routing (section 4.1) |
| 6 Verify | diplomat adversarial critic; `mechanism_classifier` judge (fixed independent model) | source-span matcher (`targets.py`-style, against fetched source text) |
| 7 Edit | `edit_classifier` to categorize edits; `identifiers.py` identity stability | frozen-field diff between rounds |
| 8 Select and review | human; optional `gateway` + `feedback_collector` for HITL delivery/edits | - |

Two placements to note:

- **The discussion engine is used at exactly one spot: the stage-3 "argue"
  sub-step.** Stage 2 is deliberately blind (principle 9: diverge before converge),
  and stage 6 is critique/judgment by one independent model, not a round. Starting
  the argument earlier forces premature convergence; running it as a debate at stage
  6 just produces hedging (the failure mode that weakened the *Waste Land* notes).
- **structured_llm pre-validates; the repo validator stays authoritative.**
  `structured_call` validates the model's JSON against `schemas/annotation.schema.json`
  as a pre-filter; derived-ID, target-resolution, access/quotation and cross-record
  checks still run through `reference-corpus-validate`.

### 6.4 What to extract into toolkit

Each is a separate toolkit-repo change under its second-consumer rule
(`PROJECT.md:40`) and `API.md` contract; reference-corpus consumes them as imports
and does not fork them.

- `toolkit.critic` <- diplomat adversarial module (reskin prompt to a literary rubric).
- `toolkit.divergence` <- diplomat `analyst.compare` (pure compare of two structured outputs).
- `toolkit.discussion` <- diplomat round loop (`round_stepped.py`), negotiation
  scoring shed; this is the stage-3 "argue" engine.
- `toolkit.judge` <- `mechanism_classifier` pattern (fixed independent judge), or
  document `edit_classifier` as the reusable judge-factory plus a corpus rubric.
- `toolkit.doc_fetch` <- new fetch+cache+retry loader (reference-corpus is the
  qualifying second consumer alongside source_ingestion's fetcher).

### 6.5 Run model

- **Laptop (supervised):** API/SDK calls run locally (not the `claude -p` FU-28
  path), good for single-poem interactive iteration.
- **pirozhok (headless):** multi-model sweeps/batch, pattern after diplomat's
  `tools/ablation_multi.sh` + `cost_accountant` budgets; results land on the shared
  disk (`p:\shared` == container `/home/claude/workspace`).
- **Auth out-of-band:** provider keys (`ANTHROPIC_/OPENAI_/GOOGLE_/OPENROUTER_API_KEY`)
  as host env vars, never in config -- mirrors i2c D-be-2 and diplomat's
  `_PROVIDER_API_KEY_ENV` (`game_environment.py:159-164`).

### 6.6 Remaining gaps / to build

After reuse, what truly remains:

- blind-runner wiring (stage 2);
- `toolkit.doc_fetch` fetch+cache+retry module (stage 4);
- the source-span matcher (stage 6);
- the frozen-field diff (stage 7);
- schema decisions D1-D3, especially whether generative drafts validate against
  `annotation.schema.json` as-is or a relaxed draft schema (ties to the D3
  `drafts/generative-track/` finding and the section 4.1 dispositions).

## 7. First experiments

Run a small matrix on one poem -- Donne's compass stanza is a good test (rich
contention; Grierson (1912) and Freccero (1963) already in the corpus) -- to see what
casting actually produces good ideas before building anything.

- **A (coverage baseline):** facet participants (form, history, sources, reception),
  several models, blind, then pool. The original plan's "three models, one stanza, no
  context, run blind" is this baseline.
- **B (friction):** two opposed period-contemporary stances, blind diverge, then an
  argue round.
- **C (diversity control):** B again, but each persona on a *different* model vs all
  personas on one model -- to see whether model variety pulls weight or the personas
  alone do.

Define "good" up front so the configs are comparable:

- **novelty** -- readings not already in the notes or standard commentary;
- **survival** -- how many candidates pass section 4.1 to publishable (proposal or
  backed) rather than dying as confabulated attributions;
- **confabulation rate** -- invented quotations or attributions caught at stage 6
  (lower is better);
- the human **"sends me back to the text"** test.

Compare each config against Grierson, Freccero and the existing annotations. A high
confabulation rate in B is not a reason to drop staged friction; it is a reason to
tighten the persona prompt's rule that the text is the only evidence unless a real
named source can be given.
