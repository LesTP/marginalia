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
- `abab-exact-rhyme.yaml` -- **promoted 2026-10-02** to
  `../../records/annotations/abab-exact-rhyme.yaml` (backed -> normal,
  `documented-fact`); tightened to the abab scheme and given a modernized display
  selector before promotion, so it is no longer in this folder.

Plus `research-leads.md` -- the fact -> research-lead branch: a biographical
world-claim that was **not** turned into a record because no source was consulted.

`stage45-report.md` summarises the run.

## How they were generated

gpt-4.1-mini filled model-authored prose (title, claim body, rationale, evidence
summary, quotation) into a deterministic schema scaffold; the fixed structural fields
were restored defensively; ids were derived with `reference_corpus.identifiers`; and
each record was validated against the real `annotation.schema.json` + registry
(Draft 2020-12). Confabulation in this run: none.

## What remains before any of these could be promoted

1. **Display selectors.** The Donne corpus has a modernized derived text view, so each
   annotation needs `target.display_selectors` for it before it can enter the manifest
   and pass full `reference-corpus-validate`. (These drafts were validated against the
   schema only, not the full corpus cross-checks.)
2. **Stage-6 verification.** An independent model should check each quotation and claim
   against the source text -- e.g. the `documented-fact` says the rhymes are "exact,"
   which is borderline on period pronunciation and should be verified.
3. **Novelty / attribution check.** `strain-as-tell` and `circle-no-progress` echo
   existing Donne criticism; if a named critic is found, they become
   `attributed-interpretation` rather than `editorial-proposal`.
4. **Prose / edit pass.** Mid-tier prose; a stage-7 edit (evidence frozen) would lift it.

The generation harness itself is throwaway and lives outside the repo
(`_scratch/genpipe/`), not committed.
