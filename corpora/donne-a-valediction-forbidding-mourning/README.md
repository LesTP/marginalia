# A Valediction: Forbidding Mourning

A compact annotated reading of John Donne's 36-line poem for a general audience. This corpus presents two aligned reading texts: an edition-faithful transcription of the 1633 first edition and a conservative modernized text derived from it. Both remain editorial drafts.

All annotations are `draft`. The source locations and access states have been checked, but neither transcription nor the interpretive wording is `editorially-approved` until a human editor reviews it.

## Base Witness

The controlling witness is the first edition of *Poems, by J. Donne. With Elegies on the Authors Death*, printed in London by Miles Flesher for John Marriot in 1633. The poem appears on printed pages 193-194, corresponding to scan leaves 208-209 in Internet Archive item `donnepoems`.

The transcription was made from the page images themselves. OCR was used only to locate the poem. Herbert J. C. Grierson's 1912 edition was then consulted as a cross-check and as a record of variants; it does not replace the 1633 witness.

Stable work identifier:

```text
work_a_valediction_forbidding_mourning
```

## Two Reading Texts

- **1633 text** preserves the printed wording, spelling, capitalization, punctuation, lineation, and nine quatrains. Long s remains ordinary `s` in the stored transcription, selectors, and copied text, while the review page uses IM FELL English's contextual historical forms to display non-final `s` as `ſ`. This is period-appropriate typography rather than a facsimile of Miles Flesher's type. The decorated opening capital is recorded as `AS`; ornamental indentation and catchwords are not encoded.
- **Modernized text** preserves wording, syntax, lineation, and stanza structure while modernizing spelling and typography. It follows Grierson's punctuation at four points: the colon after `no`, the comma after `less`, the comma after the first `two`, and the semicolon after `run`. It adds the possessive apostrophe in `lovers' love`, but it does not import Grierson's manuscript-supported `and` before `hands`.

Every annotation contains an exact selector for both texts. The validator requires both versions to retain the same line count and stanza boundaries and verifies each highlighted passage independently.

## Four Lenses

- **Form and argument** follows the poem's movement from a quiet departure to images that redefine distance as expansion and return.
- **Bodies and souls** examines the distinction between sense-dependent love and a bond described as inwardly assured.
- **Geometry and cosmology** treats the earthquake, celestial trepidation, beaten gold, and twin compasses as working models in the argument.
- **Text and history** distinguishes the 1633 witness, the editorial modernization, and later critical choices.

## Source Map

| Source | Role | Access | Evidentiary limit |
|---|---|---|---|
| Donne, *Poems* (1633) | Controlling base witness | Fully consulted | Printed pages 193-194 and relevant scan metadata |
| Grierson, *The Poems of John Donne*, vol. I (1912) | Critical text and variant apparatus | Excerpt consulted | Title matter, editorial-method preface, poem on page 49, and immediate apparatus |
| Grierson, *The Poems of John Donne*, vol. II (1912) | Poem-specific commentary | Excerpt consulted | Title matter and commentary on pages 49-50 |

The Grierson volumes were consulted through Project Gutenberg ebooks 48688 and 48772. Claims attributed by Grierson to another scholar remain reported evidence unless that scholar's original work is obtained.

## Guided Reading

The generated page presents six ordered sections:

1. A quiet model for parting.
2. Why display would profane the love.
3. Earthquake and celestial motion.
4. What physical absence removes.
5. A breach becomes an expansion.
6. The compasses and return.

The sequence follows the poem's own stanza order. It is an editorial route, not a claim of scholarly consensus.

## Textual Decisions

The 1633 page and Grierson's edited text differ in several instructive places:

- The 1633 witness reads `eyes, lips, hands`; Grierson adds `and` before `hands` and reports support from all manuscripts.
- The 1633 witness ends `runne.`; Grierson prints `runne;` and records the full-stop reading for the early editions.
- Grierson records later-edition and manuscript variants for the poem's title, line 4, the compass passage, and the final lines.

This corpus retains the 1633 wording in both displayed texts while identifying the modern view's four punctuation changes explicitly. Modernization changes presentation, not textual authority.

## Acquisition Priorities

1. A current scholarly edition or variorum for comparison with Grierson's 1912 apparatus.
2. Direct inspection of representative manuscript witnesses, especially for line 20 and the poem's titles.
3. The original Chambers commentary behind the astronomical gloss reported by Grierson.
4. Izaak Walton's *Life of Donne* for the early biographical framing and its version of the poem.
5. Modern poem-specific scholarship on departure, cosmology, gender, and the compass conceit.

Until those sources are obtained, the corpus does not treat their arguments as directly consulted scholarship.

## Known Limits

- The corpus controls its text from one copy of the 1633 edition and does not yet collate another physical copy.
- No manuscript witness has been inspected directly.
- The modernized text is an editorial derivation, not a critical edition.
- Most interpretive notes are explicitly editorial syntheses grounded in the poem; modern scholarship has not yet been added.
- Grierson's attribution of the astronomical gloss to Chambers is recorded as reported evidence.
- Rights fields document the working assessment used by this project and are not legal advice.

## Render and Validate

From the repository root:

```powershell
reference-corpus-validate .\corpora\donne-a-valediction-forbidding-mourning\corpus.yaml
reference-corpus-render .\corpora\donne-a-valediction-forbidding-mourning\corpus.yaml
python -m pytest
```

`review.html` is deterministic generated output. Make editorial changes in the YAML records and rerun the renderer; do not edit the HTML by hand.
