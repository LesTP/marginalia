# Generative Track Pilot, October 2026

> **Status: preserved experiment, not production tooling.** The scripts and outputs in this directory document a manual pilot. They contain hardcoded passages, model IDs, filesystem paths, and references to Diplomat's runtime environment. They are retained as evidence and are not supported or expected to run from this location.

## Ownership

This pilot belongs to Reference Corpus Template. It explored the generative authoring track described in `../../../DESIGN_generative_track_v1.md`: a second route for discovering candidate literary annotations while preserving the same provenance, evidence, validation, and human-review contract as the source-first workflow.

The pilot borrowed:

- `toolkit.llm_client` and `toolkit.structured_llm` for provider-neutral model calls and structured output;
- Diplomat's Pirozhok virtual environment and API-key file as an expedient runtime;
- discussion, divergence, critic, and independent-judge patterns previously exercised by Diplomat;
- Reference Corpus schemas, identifiers, target resolution, YAML loading, and validation as the authoritative corpus gate.

It is not a Diplomat or Phosphene project. Those dependencies obscured ownership while the harness lived in `_scratch`.

## Why It Began Outside The Repository

The generative track entered the repository in commit `b4eab77` as a design proposal, not an accepted tooling surface. Several boundaries were still open:

- D1-D3: treatment of unsupported facts, what counts as a consulted source, and how generated provenance should be represented;
- D7: whether stages that write records should become repository tooling at all;
- D8: how discussion participants and model diversity should be configured;
- the rule in `CLAUDE.md` that an importer or editing surface requires a separate design decision.

The early scripts also hardcoded passages, prompts, model rosters, Pirozhok paths, output directories, and Diplomat's `.env` and venv. Keeping them in `_scratch/genpipe` let the experiment proceed without making those choices part of the corpus-neutral package or implying a stable API. Only reviewed findings, schema-valid drafts, and human-selected corpus changes entered Git.

The evidence is now retained here because the pilot produced durable design findings, but moving it into the repository does not change its status.

## Pipeline Under Test

| Stage | Purpose | Pilot coverage |
|---|---|---|
| 1. Explore | Generate topics, questions, and candidate claims | Partly represented by the blind-generation prompts |
| 2. Diverge | Run several models independently against the text | Donne at mid and quality tiers; Ecclesiastes at quality tier |
| 3. Pool / argue | Separate shared from singular readings and create productive friction | Donne strong-lines versus plain-style exchange plus neutral observer |
| 4. Gather sources | Find and record sources independently of generated claims | Existing Donne sources were reused; general source gathering was not built |
| 5. Regenerate as records | Convert surviving candidates into schema-valid annotations | Three Donne drafts and one research lead |
| 6. Verify | Run deterministic text checks and an independent status-aware judge | Donne strict and status-aware passes |
| 7. Edit | Revise prose while freezing evidence, status, and targets | Human verdicts applied manually to the Donne drafts |
| 8. Select / review | Decide what is useful enough to publish | One generated note promoted and then retired; two proposals remain drafts |

## Development Chronology

- `b4eab77` introduced the speculative track and the `drafts/generative-track` location rule.
- `a6a58d9` formalized claim dispositions, tooling ownership, and discussion design.
- `1695f76` committed the Donne stage 4-5 drafts and first-pass findings.
- `6818ba9` recorded deterministic and status-aware stage-6 findings.
- `0921fe9` applied human adjudication to the Donne drafts.
- `7b3c328` promoted the generated abab rhyme-scheme note.
- `d4d8aa0` retired that note because it was accurate but misplaced and without editorial payoff.
- `32c3d31` added a separate Ecclesiastes witness-presentation mock; that work did not complete the generative pipeline on Ecclesiastes.

## Donne Result

The Donne compass-conceit pilot reached a manual end-to-end cycle.

Blind divergence showed that model agreement mostly reproduced standard commentary. The quality tier improved novelty unevenly: Claude Opus produced the strongest singular readings, while Gemini was more useful for coverage and confirmation. No run invented a critic, source, or quotation.

The staged disagreement between a strong-lines/wit reader and a plain-style objector produced more useful ideas than divergence alone. It generated the `strain-as-tell` reading, sharpened the concession reading, exposed an agency asymmetry, and tested the melancholy reading against a triumphant account of circular return.

Three candidates became schema-valid records:

- `strain-as-tell`: an unpublished, contested `editorial-proposal`;
- `circle-no-progress`: an unpublished, contested `editorial-proposal`;
- `abab-exact-rhyme`: a `documented-fact` tightened after verification, promoted, then retired.

The rhyme note is the most important negative result. Verification established that the revised claim was accurate, but human selection found it scoped to the wrong passage and without interpretive payoff. Validation and verification do not establish salience.

The published compass-instrument gloss was hand-authored after a close-reading discussion. It is related follow-up work, not evidence that the generative pipeline produced a successful published note.

## Ecclesiastes Result

The Ecclesiastes run stopped after quality-tier blind divergence and a self-contained review preview. It tested whether the approach transferred from a metaphysical lyric to translated sacred prose-poetry, but did not perform source gathering, record production, verification, edit, or human selection.

Claims about Hebrew terms and translation choices remain unverified model observations. The separate 1611 witness-presentation mock in the corpus repository is presentation research, not completion of this pipeline.

## Preserved Material

- `scripts/` contains the 12 unique pilot and editorial-follow-up scripts, copied byte-for-byte.
- `evidence/` contains all raw model outputs, transcripts, verifier reports, JSON results, and the Ecclesiastes preview. Every file matched its source hash before deletion; the preview HTML was then normalized from CRLF to LF to satisfy repository text-file policy.
- `MANIFEST.json` records all 41 original files, their source hashes and sizes, destination paths and hashes for retained files, the one declared line-ending normalization, and reasons for the five intentional deletions.

The following were intentionally not retained:

- environment-presence, key-location, model-ID, and dependency preflight probes that described themselves as throwaway;
- `verify_input.json`, a regenerable intermediate handoff between the deterministic and model verification scripts.

## Known Limitations

- Passages, prompts, models, paths, and output directories are hardcoded.
- The scripts load API keys from Diplomat's environment and assume Pirozhok-specific paths.
- The blind runner is duplicated rather than generalized.
- Discussion and judge logic are inline prototypes rather than reusable Toolkit components.
- Source gathering, cached document fetching, source-span matching, and frozen-field edit checks are not implemented.
- The persona-versus-model diversity control was not run.
- Ecclesiastes did not progress beyond divergence and preview.
- D1-D3, D7, and D8 remain open design decisions.
- The pilot covers too little textual variety to establish that the method adds durable value over source-first editorial work.

## Decision Boundary

Do not convert these scripts directly into production tooling. The formal design now defines a diverse-text evidence gate that must first show useful human-selected output across at least three additional texts, including a full Ecclesiastes cycle, Yeats, and a structurally different text.

If that evidence justifies productionization, domain-free discussion, divergence, critic, judge, and document-fetch components should qualify through Toolkit's second-consumer rule. Corpus-specific verification, disposition, provenance, target, frozen-field, and YAML behavior should remain in Reference Corpus.

See `../../../DESIGN_generative_track_v1.md` for the evidence gate and productionization roadmap.
