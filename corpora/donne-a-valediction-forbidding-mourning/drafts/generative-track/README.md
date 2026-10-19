# Generative-track stage 4-5 test drafts (unpublished)

These records are the output of a **stage 4-5 pipeline test** (see
`../../../../DESIGN_generative_track_v1.md`, sections 4 and 4.1). They are **not
published**: they live under `drafts/`, are absent from `../../corpus.yaml`, and the
validator does not scan them. They do not appear in the reading view or the tests.

## What is here

Three schema-valid annotation drafts, each produced from a top reading of the compass
conceit (last three stanzas) and routed by the section 4.1 disposition test:

- `strain-as-tell.yaml` -- reading -> proposal (`editorial-proposal`): the conceit's
  elaborateness read as a sign of emotional need.
- `circle-no-progress.yaml` -- reading -> proposal (`editorial-proposal`): "end where
  I begun" as form without progress, quietly melancholic.
- `abab-exact-rhyme.yaml` -- promoted 2026-10-02, then **retired** the same day. The
  abab scheme is uniform across all nine stanzas, so a note keyed to the compass
  stanzas was accurate but misplaced and without payoff (a stage-8 selection miss:
  verification confirms accuracy, not salience or scope). The content is recoverable
  from git history.

Plus `research-leads.md` -- the fact -> research-lead branch: a biographical
world-claim that was **not** turned into a record because no source was consulted.

`stage45-report.md` summarises the run.

## How they were generated

gpt-4.1-mini filled model-authored prose (title, claim body, rationale, evidence
summary, quotation) into a deterministic schema scaffold; the fixed structural fields
were restored defensively; ids were derived with `reference_corpus.identifiers`; and
each record was validated against the real `annotation.schema.json` + registry
(Draft 2020-12). Confabulation in this run: none.

## What remains before the surviving proposals could be promoted

Stage-6 verification is complete. Deterministic checks passed, and the status-aware
verifier found both surviving editorial proposals defensible but contested. Human
adjudication folded each competing reading into the draft. The factual abab note was
corrected, promoted, and then retired as accurate but mis-scoped and without editorial
payoff.

The two remaining proposals still need:

1. **Display selectors.** The Donne corpus has a modernized derived text view, so each
   annotation needs `target.display_selectors` before it can enter the manifest and
   pass full `reference-corpus-validate`.
2. **Novelty / attribution research.** `strain-as-tell` and `circle-no-progress` echo
   existing Donne criticism; if a named critic is found, they become
   `attributed-interpretation` rather than `editorial-proposal`.
3. **Prose / edit pass.** Their evidence and targets are frozen, but the prose remains
   draft quality.
4. **Human selection.** Verification establishes defensibility, not salience. A human
   editor must decide whether either note materially helps a reader.

The original throwaway generation harness lived outside the repository at
`_scratch/genpipe/`. Its scripts and evidence are now preserved as a non-production
pilot under `experiments/generative-track/pilot-2026-10/` at the repository root.
