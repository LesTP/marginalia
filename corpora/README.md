# Real Corpora

This directory keeps multiple literary corpora under one shared schema, validator, and
test suite. Each corpus is self-contained:

```text
corpora/<corpus-slug>/
  README.md
  corpus.yaml
  records/sources/*.yaml
  records/annotations/*.yaml
  review.html              Hand-authored, self-contained reading view
  drafts/                  Archived generated view and superseded prototypes
```

The paths inside each `corpus.yaml` are relative to that corpus directory. Source and
annotation files must remain under `records/sources/` and `records/annotations/` so the
validator can detect unlisted records. `review.html` embeds a snapshot of the validated
manifest; after any editorial change, validate and refresh that snapshot:

```powershell
reference-corpus-validate .\corpora\<corpus-slug>\corpus.yaml
python scripts\refresh-review.py .\corpora\<corpus-slug>\corpus.yaml
```

> `reference-corpus-render` writes the generated design to `review.html` by default and
> would overwrite the hand-authored view. Always pass `--output`, for example
> `--output .\corpora\<corpus-slug>\drafts\generated.html`.

## Presentation Checklist

A corpus can use the shared reading interface without adding another application or
folder structure:

1. Add one base-text annotation with a stable local key, normally `base-text`.
2. Add `presentation.base_text_annotation` to the manifest.
3. For multiple reading texts, declare one `canonical-target`, each `editorial-derivation`, and `default_text`; keep derived texts line- and stanza-aligned with the canonical text.
4. Add one `target.display_selectors` entry per derived view to every annotation so highlights resolve in each displayed text.
5. Omit `default_mode` for Plain reading, or explicitly choose a configured lens or pathway.
6. Define each lens once with a label, description, and tag; put that tag on participating annotations.
7. Define pathway order with annotation local keys rather than derived IDs or prose parsing.
8. Write every public title, lens description, pathway label, and claim for a general reader encountering the work for the first time.
9. Begin annotation prose with what the passage does and why it matters; introduce scholars, disputes, and source limitations afterward.
10. Keep pathway overview prose in an evidence-bearing annotation and its navigation order in the manifest.
11. Make `target.exact_text` the literal canonical passage to highlight inside the locator range; add prefix or suffix context only for repeated text.
12. Validate before refreshing or rendering. Broken references, ambiguous targets, misaligned text views, and cross-edition targets are rejected.

The Yeats corpus below is the single-text worked example; the Donne corpus demonstrates aligned edition-faithful and modernized views. Their lens labels belong to those corpora, and another text may define entirely different lenses and pathways.

## Catalog

| Corpus | Status | Base witness | Records |
|---|---|---|---|
| [W. B. Yeats, *The Song of Wandering Aengus*](yeats-song-of-wandering-aengus/) | Human-reviewed for sense; not source-verified | *The Wind Among the Reeds* (London: Elkin Mathews, 1899), pp. 15-16 | 12 sources, 15 annotations |
| [John Donne, *A Valediction: Forbidding Mourning*](donne-a-valediction-forbidding-mourning/) | Human-reviewed for sense; not source-verified; edition-faithful and modernized views | *Poems, by J. Donne* (London: Miles Flesher for John Marriot, 1633), pp. 193-194 | 4 sources, 12 annotations |

Files under `examples/valid/` are fictional contract fixtures. Files under `corpora/` are
real editorial projects and must not contain invented bibliography.
