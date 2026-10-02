# The Song of Wandering Aengus

A compact annotated reading of W. B. Yeats's 24-line poem for a general audience. It is
the first real corpus in this repository and tests how careful provenance can support
clear literary explanation without asking readers to know the scholarship in advance or
pretending that interpretation is mechanically decidable. The corpus contains 13 annotation
records, including 11 reader-facing notes.

All annotation records are `human-reviewed`: read for sense, but not yet verified against
their sources. None is `editorially-approved`, and editorial confidence remains `unassessed`.

For assembled reading and review, open `review.html` in a browser. It keeps the poem
visible beside one poem-ordered stream of notes, offers the corpus lenses as **Focus**
filters, highlights the selected note's exact target, and presents evidence and source
access without exposing the YAML structure.

Earlier review pages and prototypes are archived in `drafts/` (see `drafts/README.md`).

## Base Text

The base witness is the first London edition of *The Wind Among the Reeds*, published by
Elkin Mathews in 1899. The transcription follows the printed page images on pages 15-16,
including punctuation, the hyphen in `a-flame`, and three stanzas of eight lines each.
OCR was used only to find pages.

A Project Gutenberg transcription of the 1903 fourth edition was consulted as a second
witness. Where OCR or later transcription could obscure punctuation, the 1899 page image
controls this corpus.

Stable work identifier:

```text
work_the_song_of_wandering_aengus
```

## Three Lenses

- **Myth and folklore** starts with Yeats's own note on pages 87-89. He names a Greek folk song as the poem's prompt while describing Irish beliefs about spirits that appear as fish or women. The medieval *Aislinge Óenguso* is treated as a revealing comparison, not an unquestioned genetic source.
- **Form and imagery** examines the three-stanza progression, repeated `And`, light imagery, repeated naming, the future-tense vow, and the scholarly disagreement over the apples.
- **Text and history** records the 1897 title reported by current scholarship and the directly inspected 1899 title and text. The 1897 periodical witness has not yet been obtained. It also places the poem's Irish god, written in English, within Yeats's stated cultural program of the 1890s, drawing on his own prose.

## Source Map

| Source | Role | Access | Evidentiary limit |
|---|---|---|---|
| Yeats, *The Wind Among the Reeds* (1899) | Base text and authorial note | Fully consulted | Primary witness for pages 15-16 and 87-89 |
| Project Gutenberg ebook 32233 | 1903 fourth-edition cross-check | Fully consulted | Corroboration, not the controlling witness |
| Shaw/Murray, *Aislinge Oenguso*, University College Cork | Medieval text and English translation | Fully consulted | Comparative context; not proof of direct derivation |
| Bodsworth, “Meet Me in My World” (2024) | Scholarship on the medieval tale | Excerpt consulted | Only pages 87-91 and 121 are used |
| Bodsworth, “Changing the story” (2023) | Publication-title report and interpretive argument | Fully consulted abstract | Claims are limited to the university-hosted abstract |
| Mazzaro, “Apple Imagery” (1957) | Direct poem-specific scholarship | Fully consulted | Pages 342-343; preserves a debate rather than settling it |
| McDonald, “The Song of Wandering Aengus” (2020) | Priority modern commentary | Citation only | Supplies no evidence until the chapter is obtained |
| LiederNet text 28583 | Curated title and publication-history record | Fully consulted | Useful corroboration, not a critical edition |
| Yeats, *The Celtic Twilight* (1902 ed.), Project Gutenberg 10459 | Yeats's stated aims for his folklore work | Fully consulted | Dedicatory preface only; transcription not checked against page images, so no page numbers |
| Yeats, *Ideas of Good and Evil* (1903 ed.), Project Gutenberg 32884 | Yeats's stated cultural-nationalist program | Fully consulted | "The Celtic Element in Literature" and "Ireland and the Arts"; located by essay, not page |

## Guided Reading

The manifest defines Guided Reading as one short introduction followed by five ordered
steps: the initiating fire, the trout's transformation, recognition by name, a similar
medieval Irish story, and the unfinished search with its apple imagery.

The current hand-authored `review.html` does not present the pathway: it treats the
`guided-reading` annotation as route metadata and omits it from the note stream. The
pathway appears in the generated view archived in `drafts/`.

The order remains an editorial route rather than a claim of scholarly consensus. Each
step points to existing evidence-bearing annotations.

## Acquisition Priorities

1. Peter McDonald's poem-specific chapter in *The Poems of W. B. Yeats*, pages 518-529. Its bibliographic record is already present as `citation-only`.
2. The 4 August 1897 issue of *The Sketch*, page 52, reported by the LiederNet record and other current references to contain the first printing under the title “A Mad Song.” This is needed to verify the first witness and its revisions directly.
3. Margaret Rudd's *Divided Image*, page 144, which Mazzaro quotes when describing the Maud Gonne interpretation of the apple imagery.
4. A. Norman Jeffares's *A New Commentary on the Poems of W. B. Yeats* for comparison with the present source map.
5. A modern critical edition edited by Richard J. Finneran for a systematic textual collation beyond the two public-domain witnesses.

Until these are obtained, the corpus does not quote them or treat their arguments as
directly consulted.

## Known Limits

- The first 1897 periodical printing has not been inspected.
- No comprehensive modern variorum has been consulted.
- The connection with *Aislinge Óenguso* is deliberately qualified: Yeats's own note identifies a Greek folk-song prompt and Irish folkloric associations, while later scholarship argues over the medieval tale's relevance.
- Formal notes based only on the poem are labeled editorial synthesis or proposal, not scholarship.
- The Irish-identity note links Yeats's own prose program to this poem as editorial synthesis; it has not been checked against secondary Yeats scholarship.
- The two Yeats prose sources are Project Gutenberg transcriptions not yet checked against printed page images.
- Rights fields document the working assessment used by this project and are not legal advice.

## Render and Validate

From the repository root:

```powershell
reference-corpus-validate .\corpora\yeats-song-of-wandering-aengus\corpus.yaml
python .\scripts\refresh-review.py .\corpora\yeats-song-of-wandering-aengus\corpus.yaml
python -m pytest
```

`review.html` is a hand-authored continuous reading shell with a deterministic embedded
corpus-data snapshot. Make editorial changes in YAML, then run `refresh-review.py`; do not
replace the shell with the generic renderer. To produce the generated view, pass `--output`
to `reference-corpus-render` (for example, `drafts\review-generated-shared-renderer.html`).
