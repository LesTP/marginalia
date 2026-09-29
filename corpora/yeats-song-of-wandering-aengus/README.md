# The Song of Wandering Aengus

A compact annotated reading of W. B. Yeats's 24-line poem for a general audience. It is
the first real corpus in this repository and tests how careful provenance can support
clear literary explanation without asking readers to know the scholarship in advance or
pretending that interpretation is mechanically decidable.

All annotations remain `draft`. Source locators and access states have been checked, but
no record is `editorially-approved` until a human editor reviews its wording and judgment.

For assembled reading and review, open `review.html` in a browser. It keeps the poem
visible, offers Plain reading plus corpus-configured lenses and a guided pathway, highlights
the selected annotation's exact target, and presents evidence and source access without
exposing the YAML structure.

`review-before-reading-model.html` is a byte-for-byte archival copy of the previous review
page, retained so the earlier interaction can still be compared with the reusable model.

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
- **Text and history** records the 1897 title reported by current scholarship and the directly inspected 1899 title and text. The 1897 periodical witness has not yet been obtained.

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

## Guided Reading

The page presents Guided Reading as one short introduction followed by five numbered
disclosure sections: the initiating fire, the trout's transformation, recognition by name,
a similar medieval Irish story, and the unfinished search with its apple imagery. The first
section is open by default; opening another closes the previous section so the current stage
stays visually connected to the poem.

The order remains an editorial route rather than a claim of scholarly consensus. Each
section points to existing evidence-bearing annotations, and sections with more than one
relevant note show those notes together instead of turning them into separate pages. The
three lenses and All Notes use the same numbered disclosure design, with one top-level
section open at a time and source detail expandable inside it.

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
- Rights fields document the working assessment used by this project and are not legal advice.

## Render and Validate

From the repository root:

```powershell
reference-corpus-validate .\corpora\yeats-song-of-wandering-aengus\corpus.yaml
reference-corpus-render .\corpora\yeats-song-of-wandering-aengus\corpus.yaml
python -m pytest
```

`review.html` is deterministic generated output. Make editorial changes in the YAML
records and rerun the renderer; do not edit the HTML by hand. The preserved
`review-before-reading-model.html` is a historical snapshot and is not regenerated.
