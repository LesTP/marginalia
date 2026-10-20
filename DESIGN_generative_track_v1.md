# DESIGN: Generative Track v1

**Status:** Experimental pilot completed 2026-10-02; reusable production tooling is
not built. The preserved scripts and evidence live under
`experiments/generative-track/pilot-2026-10/`. Results remain inconclusive pending
the diverse-text evidence gate in §8.
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

A world-fact needs an external source to be presented as established. A reading
needs only the poem, which is always a fully-consulted, public-domain source in the
corpus. Three terminal dispositions follow:

| Disposition | When | Epistemic status | Evidence | Where it goes |
|---|---|---|---|---|
| **backed -> normal** | A source was consulted that supports the claim as stated | Whatever the evidence warrants (`documented-fact`, `scholarly-consensus`, `attributed-interpretation`, `editorial-synthesis`) | The consulted source, with locator and quoted span | Continues through stages 5-7 |
| **reading -> proposal** | The claim is a reading/interpretation; no external scholarship, but the text supports it | `editorial-proposal` (or `conjecture` if deliberately speculative) | The base-text lines (`use: direct-evidence`, `relationship: supports`) | Published once a human reclassifies, points evidence at the text, and signs off |
| **fact -> unverified** | The claim asserts an externally checkable world-fact and a recorded search found no reachable source that backs it | `unverified`; **not presented as fact** | No supporting evidence; a required verification note records what was searched and which source would settle it | May be published inline only after human review, with a prominent **Unverified** warning; otherwise retained in `drafts/generative-track/` (D3) |

Notes:

- **The promotion the editor wants is `reading -> proposal`.** It is not
  "publish something unsourced"; it is "reclassify as a reading whose evidence is
  the text, and sign off." The invariant in section 1 holds: the reader sees
  "editorial proposal," never a fact in disguise. Precedent already in the Yeats
  corpus: `light-and-time` and `future-vow` are `editorial-proposal` records whose
  only evidence is the 1899 base text.
- **`fact -> unverified` is the guardrail.** "Interesting" can promote a reading,
  but it cannot make a world-fact true. In the narrow D1 case, an unresolved factual
  claim may appear inline only with an **Unverified** label and warning that no
  supporting source was found. The warning must expose the search scope and name the
  kind of source that would settle the claim. An `unverified` record cannot support
  another claim, contribute to `scholarly-consensus`, or be paraphrased elsewhere as
  established. This mirrors the *Waste Land* citation brief's rule: report the gap,
  do not invent a source (section 3, principle on novelty and the "report rather than
  fix" discipline).
- **Mechanical stage-6 failures are not dispositions.** A wrong locator or a
  mistyped quotation against the *right* source loops back to fix the record; only
  a genuine "the source does not support this" or "no source exists" triggers a
  disposition.
- **Confidence and review state are set by the human** at stage 8 (per
  `CLAUDE.md`: editorial confidence is a human assessment, not model confidence).
  For `unverified`, publication requires human review of its reader value, wording,
  warning, and search account, while `editorial_confidence` remains `unassessed`;
  review of the presentation does not verify the underlying claim.

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
- an unsupported but externally checkable claim -> `unverified` under D1 after a
  recorded source search; an invented quotation or attribution -> dropped.

**Model diversity and persona diversity are orthogonal.** Different stances
decorrelate *perspective*; different model families decorrelate *training and error*.
Cast persona x model where possible, so the debate is not one model ventriloquizing
every voice (the *Waste Land* "model playing a critic" failure).

## 5. Decisions and open questions

- **D1. Unsourced factual background (resolved 2026-10-19).** Add `unverified` to
  the controlled `epistemicStatus` vocabulary for the narrow `fact -> unverified`
  disposition in section 4.1. It covers externally checkable world-claims for which
  a recorded search found no reachable supporting source; it does not mean "probably
  true." Readings and opinions remain out of scope because `reading -> proposal`
  handles them using the text as evidence. An `unverified` record may appear inline
  only after human selection and with a prominent reader-facing warning; it cannot
  serve as evidence for another claim. Schema work must add the status, allow no
  supporting evidence only for that status, and require a verification note recording
  the search scope and the kind of source that would settle the claim. Renderer and
  hand-authored reading views must present the warning before the claim rather than
  relying on color or a metadata drawer.
- **D2. What counts as "consulted" (resolved 2026-10-19).** Access describes how
  much source material was actually inspected by the research process, not
  exclusively by a human. Complete model inspection qualifies as
  `fully-consulted`. Source records must identify whether consultation was by a
  model, human, or both through a controlled `access.consulted_by` field. Human
  source verification is optional and remains a separate annotation review state;
  `review.state: source-verified` is authoritative, and the interface may render it
  as an `H` badge. The access state must describe what was actually supplied: a
  truncated source remains `excerpt-consulted`, and a citation or search snippet
  remains `citation-only`, regardless of what the model reports having read.
- **D3. Where generative-track records live and how they are marked (resolved
  2026-10-19).** Use one corpus and one annotation schema for both tracks. Add a
  required, immutable `provenance.origin_track` with controlled values
  `source-first` and `generative-track`. The value records what set the candidate's
  agenda, not who drafted the final prose: a generated candidate remains
  `generative-track` after sourcing and human editing, while model assistance on a
  source-led annotation remains `source-first`. Do not add a `hybrid` value unless
  real cases show that this rule cannot classify them. Keep free-text
  `provenance.created_by` for descriptive authorship, and allow an optional future
  `provenance.process_ref` to link a preserved run or experiment manifest.
  Published records live in the ordinary corpus and satisfy the same evidence,
  validation, and review contract. The reading interface exposes `origin_track` in
  provenance details, not as an epistemic warning or headline badge; claim standing
  continues to come from evidence, status, confidence, and review, including D2's
  optional `H` badge.
  - **Finding (2026-09-29, Yeats "irish-identity" pilot).** *Unpublished* drafts must
    live in `corpora/<slug>/drafts/generative-track/`, not in the corpus `records/`
    tree. The validator requires every file under `records/sources/` and
    `records/annotations/` to be listed in the manifest ("record is not listed in
    corpus manifest"), and the real-corpus tests pin exact source/annotation counts
    plus a current `review.html` snapshot. So there is no "loose draft" slot inside
    `records/`: a draft placed there fails validation and breaks the pinned tests.
    Keeping drafts under `drafts/generative-track/` leaves them beside the poem,
    out of the validator's `records/` scan, and out of the published reading view.
  - **One-schema boundary.** A file represented as a source or annotation draft must
    validate against the same record schema used for publication; there is no relaxed
    generative-record schema. Earlier prompts, candidates, debates, and reports are
    process evidence rather than corpus records and may use experiment-specific
    formats.
  - **Validation of a draft in that location.** The corpus validator only checks
    records reachable from the manifest, so a draft in `drafts/generative-track/` is
    not validated in place. To validate it, temporarily add its relative paths to the
    manifest `sources`/`annotations`, run `reference-corpus-validate`, then revert the
    manifest. (Done for the Yeats pilot: exit 0.) A future standalone-record validation
    path may remove this temporary-manifest step without changing the schema.
  - **Promotion path (verified).** Move the source files into `records/sources/` and
    the annotation into `records/annotations/`, add all three to `corpus.yaml`, set
    `review.state` (e.g. `human-reviewed` with reviewer and date), refresh the reading
    view (`python scripts/refresh-review.py <corpus.yaml>`), and update the pinned
    counts in `tests/test_validation.py` and `tests/test_review.py`. Promotion never
    erases or changes `provenance.origin_track`.
- **D4. Tertiary sources (resolved 2026-10-19).** Wikipedia and similar sources
  may be retained in the source graph rather than hidden as finding aids, but their
  standing and limits must be explicit. Classify them with the existing
  `quality.authority` flag (`established-reference` or `informal-resource`), record
  the applicable `quality.peer_review_status` and an honest `quality.rationale`, and
  restrict annotation evidence drawn from them to `use: context-only`. They may
  orient research, surface candidate connections, and point to underlying sources;
  they do not by themselves support a published factual or scholarly claim. When a
  claim depends on material encountered through a tertiary source, consult and cite
  the strongest reachable underlying source. This keeps the actual discovery path
  visible without silently upgrading tertiary material into scholarship.
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
| 6 Verify | **deterministic first** (`targets.resolve_target` + verbatim-quotation check); then an independent judge (`mechanism_classifier` pattern, fixed independent model) with a **status-aware rubric** | source-span matcher against *fetched* source text (gap); the status-aware verifier prompt |
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

Stage-6 findings (first run on the Donne drafts, 2026-10-02):

- **Run the deterministic checks first; they carry the reliable weight.** The repo's
  `targets.resolve_target` (unique target resolution) plus a verbatim-quotation check
  need no model and cannot hallucinate; the model judgment is advisory on top. In the
  first run all three drafts passed the deterministic checks (no fabricated or
  misquoted text).
- **The verifier rubric must be status-aware.** Holding an `editorial-proposal` to the
  documented-fact standard ("every assertion borne out by the lines, no over-reach")
  flags all genuine interpretation. Switch rubric on the epistemic status: a
  `documented-fact` must be strictly checkable from the text (this correctly caught an
  "exact, nearly monosyllabic rhymes" over-claim); an `editorial-proposal` need only be
  defensible / not contradicted by the lines, free of external facts, and honestly
  labelled as a proposal. The verifier must receive the status and pick its test.
- **The verifier itself errs; humans adjudicate (principle 8).** The independent model
  miscalled exact rhymes (so/show, two/doe, rome/home) as near rhymes -- over-correcting
  on the very point it flagged. Verifier output is a candidate for human review, not a
  verdict; no model is the final authority, which is why the deterministic checks hold
  the reliable weight.
- **A flag on a proposal often means 'contested', not 'wrong'.** The verifier reproduced
  the stage-3 strong-lines position against the anxious/melancholy readings. Such a flag
  should route the proposal to carry its counter-reading (or the `contested` annotation
  type), not to deletion.
- **Confirmed by a status-aware re-run (2026-10-02).** With the rubric switched on
  epistemic status, both editorial-proposals verified as defensible -- the verifier
  marking each as *contested* and naming its competing reading (the confident/triumphant
  reading of the compass) -- while the documented-fact stayed flagged for the "exact,
  nearly monosyllabic" over-claim. The status split stops over-flagging genuine
  interpretation without weakening the catch on factual over-claims. The verifier again
  miscalled exact rhymes as slant, confirming that human adjudication remains required.

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
- implementation of resolved D1: the `unverified` status, its conditional
  evidence/verification-note rules, and the mandatory inline warning;
- implementation of resolved D2: add controlled `access.consulted_by` values
  (`model`, `human`, `both`) to source records and derive the optional `H` badge
  from annotation `review.state: source-verified`;
- implementation of resolved D3: add and backfill required
  `provenance.origin_track`, validate generative record drafts against the same schema
  without publishing them, and expose origin in provenance details.

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

### 7.1 Results, first pass (2026-10-02)

First pass on the Donne compass conceit (the last three stanzas), run on pirozhok via
diplomat's venv and `.env` keys (the API path, not the FU-28 `claude -p` path). The
original throwaway harness and evidence are now preserved, unchanged and explicitly
non-production, under `experiments/generative-track/pilot-2026-10/`. One stanza only
-- treat as indicative, not general.

**Stage 2, blind divergence** (same prompt, no context, no personas), at mid tier
(gpt-4.1-mini, claude-sonnet-4-6, gemini-2.5-flash-lite) and quality tier (gpt-5.5,
claude-opus-4-6, gemini-2.5-pro):

- Readings shared across models matched the standard commentary already in the corpus
  (interdependent feet, oblique path, turn to direct address, circular closure),
  confirming that the shared-vs-singular split is a usable signal.
- **Tier matters, unevenly by provider.** OpenAI mid -> quality was a large jump;
  Anthropic Opus led on novelty and produced the only two genuinely new divergence
  readings (the conceit as a concession/fallback, not the main claim; "end where I
  begun" as no progress, only form -- quietly melancholic). Gemini was the weakest
  idea-generator at both tiers (competent but standard).
- **Confabulation: 0** at either tier -- no invented critics, sources, or quotations.
- Practical: reasoning models (gpt-5*, gemini pro) need a large token budget or they
  return empty/truncated; the harness retries at a higher budget.

**Stage 3, argue** (strong-lines/wit on Opus vs plain-style on gpt-5.5, each on a
different model, neutral observer on gemini-pro, seeded with the standout divergence
readings):

- **Friction out-produced divergence.** The clash generated a reading neither opening
  had -- the elaborate conceit as a symptom of emotional need ("if the union were as
  serene as the argument wants, the poem would not need so elaborate a machine to
  prove it"), the strain itself the tell. It also adjudicated the seeded readings: the
  concession reading sharpened from "fallback" to the logician's "even if"; the
  melancholy reading was diagnosed as depending on an imported Romantic expectation of
  growth. It surfaced an agency-asymmetry reading (the beloved praised for constancy
  but cast as reactive).
- **Confabulation: 0 even in persona mode** -- the framing most likely to invent a
  period quotation produced none (observer's check: "None"). Key safety result.
- The neutral observer worked as the stage-3 pool/judge: it separated genuine
  disagreements, named the new readings, and ran the confabulation check.
- The debate did not collapse into hedging (the *Waste Land* failure mode); concession
  plus counter developed claims rather than averaging them.

**Validated / still open.** The idea-generation half (stages 1-3) held on first
contact: variety was real, quality tier lifted novelty, friction developed and tested
ideas, and the honesty rule survived throughout. The pilot then exercised record
production and verification manually: three schema-valid Donne drafts, deterministic
text checks, a strict verifier, a corrected status-aware verifier, and human
adjudication. General source gathering was not built, and config C (persona x model
swap, the ventriloquism control) remains untested. D1-D3 were open at the time of
this pilot; D1-D3 were resolved on 2026-10-19.

**Roster finding.** Weight toward the strong idea-generators (Opus led; gpt-5.5
strong), but keep >= 2 models so the shared-vs-singular split still works; Gemini
earns a place for coverage/confirmation, not novelty.

### 7.2 Outcome after verification and human selection

The manual pipeline did not establish that generative authoring should become a
supported production workflow.

Two interpretive candidates (`strain-as-tell` and `circle-no-progress`) survived
status-aware verification as defensible but contested editorial proposals. They remain
unpublished drafts pending novelty/attribution research, prose work, selectors, and a
human decision that they add enough value.

The factual abab rhyme-scheme note was corrected, verified, promoted, and then retired
one hour later. Its description was accurate after correction, but the feature was
uniform across all nine stanzas, so a note attached to the compass passage was
mis-scoped and without editorial payoff. This is the pilot's load-bearing negative
result: verification can establish accuracy and defensibility, but not salience,
scope, or whether a note helps a reader.

The published compass-instrument gloss was hand-authored after a close-reading
discussion and is not a generative-track product. No generated pilot note is currently
published.

A later Ecclesiastes run tested blind divergence and produced an unreviewed preview,
but did not proceed through sources, record production, verification, edit, or human
selection. The 1611 witness mock is separate presentation research, not evidence that
the generative pipeline was completed on Ecclesiastes.

## 8. Diverse-text evidence gate

Do not build a production runner merely because the Donne drafts validated. Before
productionization, run the complete pipeline on at least three additional, diverse
texts:

1. Complete Ecclesiastes through source gathering, record production, verification,
   edit, and human selection.
2. Run the existing Yeats corpus through the complete track, using its mature
   source-first annotations as a comparison set.
3. Choose one structurally different text -- longer prose, drama, or a translated or
   non-English work -- before that future phase begins.

For each text, record:

- novelty relative to existing annotations and consulted criticism;
- candidate survival through human selection and actual promotion;
- confabulation and unverifiable-world-fact rate;
- salience and scope rejection rate, not only factual verification;
- the human "sends me back to the text" judgment;
- cost, latency, and model/provider variability;
- the persona-versus-model diversity control, including the unrun config C swap.

Productionization requires useful human-selected output across the matrix, acceptable
provenance failure rates, and evidence that the workflow adds value beyond ordinary
source-first editorial work. A high validation pass rate alone is insufficient.

## 9. Productionization roadmap

This is a prerequisite list, not approved implementation work.

1. Replace hardcoded passages, prompts, model IDs, paths, and output directories with
   explicit per-text configuration and a corpus-neutral runner.
2. Generalize blind divergence while preserving prompt/model provenance, cost, and a
   deterministic output layout.
3. Extract domain-free components into Toolkit only when Reference Corpus qualifies as
   a real second consumer: critic, divergence comparison, discussion/argue loop,
   independent judge pattern, and cached/retrying document fetch.
4. Keep corpus-specific behavior here: deterministic target and quotation checks,
   epistemic-status-aware rubrics, reading/fact disposition routing, source-span
   matching, frozen-field checks, and canonical JSON-compatible YAML writing.
5. Reuse existing `toolkit.structured_llm.structured_call`,
   `toolkit.cost_accountant.CostAccountant`, `toolkit.source_ingestion.normalization`,
   `toolkit.prompt_regression`, and the existing `reference_corpus` identifiers,
   targets, validator, and YAML loader rather than rebuilding them.
6. Implement D1's controlled `unverified` status and inline warning, D2's
   consultation-actor metadata and optional human-verification badge, and D3's
   immutable origin metadata; resolve D7 and D8 before accepting a supported write
   path or publishing a controlled generated-provenance vocabulary.
7. Add hermetic unit tests, prompt-regression cases, multi-corpus acceptance tests,
   frozen-field tests, and an explicit human promotion workflow before calling the
   track production-ready.
