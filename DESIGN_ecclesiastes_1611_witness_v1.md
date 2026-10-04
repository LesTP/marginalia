# DESIGN: Ecclesiastes 1611 Witness Presentation v1

**Status:** Draft - 2026-10-04. Presentation proposal only; nothing is
implemented by this document.

**Scope:** A historically grounded witness view for an annotated corpus of
Ecclesiastes based on the 1611 first edition of the King James Bible, paired
with a more spacious reading view for annotation.

**Depends on:** the source-first rules in `CLAUDE.md`, the dual-text model and
witness-presentation work already used by the Donne corpus, the corpus schemas,
target validation, and the hand-authored review-shell workflow documented in
`README.md`.

**Origin:** A discussion prompted by an image of the 1611 Ecclesiastes opening
page, with its running header, ornamental headpiece, mixed roman and blackletter
type, chapter synopsis, two-column setting, decorated initial, marginal
references, and the beginning of chapter II in the lower right column.

---

## 0. Summary

Ecclesiastes should be able to offer two aligned presentations:

1. A **1611 witness view** that reconstructs the selected printed witness's
   textual and typographic organization: original spelling and punctuation,
   blackletter biblical text, roman and italic ancillary matter, two columns,
   running header, rules, synopsis, marginal references, ornament, and a
   decorated initial.
2. A **reading view** that presents the same indexed passage in a spacious,
   accessible single column suited to sustained reading and annotation.

The witness view is not produced by applying an old-looking font to a modern
KJV text. Its controlling source must be an identified and directly consulted
1611 witness. Edition-faithful wording, spelling, punctuation, supplied words,
chapter matter, marginalia, and page transitions must come from that witness.
Font features may change glyph presentation, but they must not silently change
the stored text.

The preferred biblical-text font is
[KJV1611](https://github.com/ctrlcctrlv/kjv1611), Fredrick Brennan's direct
digital restoration from a 1611 facsimile. It is available as OTF, WOFF, and
WOFF2 under the SIL Open Font License 1.1 and includes historical forms,
ligatures, contextual alternates, stylistic alternates, and special handling
for long `s`.

The original page is a typographic system, not a single font. KJV1611 supplies
the main blackletter face but does not supply the roman hierarchy, engraved
headpiece, decorated initial, rules, page proportions, marginal apparatus, or
paper and ink behavior. Those elements require separate, source-backed design
and rights decisions.

## 1. Goals

- Give readers a meaningful encounter with the 1611 witness rather than a
  generic "old Bible" theme.
- Preserve the source-first distinction between textual evidence and visual
  reconstruction.
- Reproduce the witness's mixed typographic hierarchy, including the semantic
  contrast between blackletter and roman text.
- Keep the indexed text selectable, searchable, copyable, and available to
  assistive technology.
- Align the witness and reading views so the same annotations resolve exactly
  in both.
- Keep annotation controls outside the simulated page and visually subordinate
  highlights within it.
- Remain self-contained at runtime, including fonts, licenses, ornamental
  assets, and embedded corpus data.
- Reflow intelligently on narrow screens instead of shrinking a two-column
  folio into illegibility.
- Describe the result honestly as an edition-faithful digital reconstruction,
  not a facsimile.

## 2. Non-goals

- A pixel-for-pixel photographic facsimile.
- Simulation of foxing, stains, torn edges, page curvature, or arbitrary
  distress for atmosphere.
- Use of Gutenberg-era Textura or a generic Fraktur face merely because it
  looks old.
- Silent substitution of the common 1769-standardized KJV text for the 1611
  text.
- Encoding long `s`, ligatures, `r` rotunda, or other contextual glyph forms as
  arbitrary replacement characters in the canonical transcription.
- Treating ornamental art or marginal references as decoration when they carry
  source or interpretive information.
- Allowing the historical presentation to impair ordinary reading,
  annotation, keyboard navigation, copying, or screen-reader order.
- Generalizing the shared renderer around one biblical page before a concrete
  corpus establishes the smallest reusable contract.

## 3. Source-critical rule

A 1611 visual presentation commits the corpus to a 1611 textual witness.

The corpus must not place later standardized KJV wording into 1611 dress. The
commonly circulated KJV text normally reflects eighteenth-century editorial
standardization, especially the 1769 Oxford revision. Its spelling,
punctuation, italics, and sometimes wording cannot be assumed to represent the
first edition.

Before implementation, the editor must:

1. Identify the exact physical or digitized 1611 copy used as the controlling
   witness.
2. Record the stable URL, holding institution, shelfmark or scan identifier,
   page or leaf locators, access date, access method, and reproduction terms.
3. Inspect the page images directly rather than relying on OCR.
4. Transcribe the selected passage from the page images.
5. Determine whether the corpus covers a chapter, a selection, or the complete
   book, and how page-spanning ancillary matter will be represented.
6. Record any departure from the witness as an explicit editorial derivation.

The discussion image is a design reference, not yet an identified source
record. It cannot become the controlling witness until its edition, copy,
location, and rights status are established.

## 4. Two aligned text views

### 4.1 The 1611 witness view

The witness view should preserve, as applicable to the selected pages:

- wording;
- lexical spelling, including forms such as `vanitie`, `vnto`, and `bee`;
- capitalization;
- punctuation;
- verse numbering;
- chapter boundaries and chapter synopsis;
- line and column sequence;
- supplied-word typography;
- marginal cross-references and notes;
- running headers and page furniture;
- page transitions that affect the reader's understanding of the artifact.

Historical glyph behavior is presentation. For example, ordinary stored `s`
may render as long `s` where the font's historical-form logic calls for it.
The copied text should remain ordinary Unicode and should not acquire visual
substitutions that obscure search or exact selector resolution.

### 4.2 The reading view

The reading view should be a single-column presentation designed for close
reading. It may modernize glyphs and typographic conventions, but its textual
policy must be named precisely.

Possible policies include:

- the same 1611 wording and spelling in modern typography;
- conservative modernization of spelling and typography derived from 1611;
- a separately sourced later KJV edition.

These are not interchangeable. If a later edition is displayed, it is a second
edition source, not merely a modernization. Its selectors, provenance, and
textual differences must be represented accordingly.

Every public annotation must include an exact selector for every displayed
text. The validator must independently resolve both the witness passage and the
reading-view passage.

## 5. Typographic system

The 1611 page derives much of its meaning from contrast among typographic
roles. The implementation should model those roles explicitly rather than
flattening the page into one font.

| Witness role | Proposed treatment | Notes |
|---|---|---|
| Biblical text | KJV1611 blackletter | Primary historical face; use verified OpenType features |
| Book title | Widely spaced roman capitals | `ECCLESIASTES,` should not be blackletter |
| Subtitle | Centered roman | `or the Preacher.` |
| Running header | Roman with three-part alignment | For example, `The vanitie of` / `Chap. j. ij.` / `worldly things.` |
| Chapter heading | Roman capitals with tracking | For example, `CHAP. I.` |
| Chapter synopsis | Compact roman | Visually and semantically distinct from scripture |
| Supplied words | Roman within blackletter text | Preserve the original convention; do not silently convert to later italic practice |
| Marginal commentary | Small italic or roman according to witness | Exact role must be transcribed from the selected copy |
| Cross-references | Very small roman | Keep legible and expose semantically to assistive technology |
| Verse numbers | Small roman or witness-matched figures | Must remain addressable as verse metadata |
| Catchwords, signatures, page numbers | Witness-matched ancillary type | Include only when relevant to the chosen fidelity level |
| Ornament and decorated initial | Rights-cleared image or reconstructed vector | Not supplied by KJV1611 |

### 5.1 KJV1611

KJV1611 is the recommended main face because it is tied directly to the target
edition and has a clear embedding license. Its repository describes it as a
complete digital OpenType restoration traced from microscope images of a 1611
facsimile.

The font provides these relevant feature tags:

- `hist`: historical forms, including contextual long `s`, historical `I`/`J`
  and `U`/`V` behavior, and `r` rotunda;
- `kern`: special kerning, including combinations involving long `s`;
- `calt`: contextual alternates;
- `liga`: ligatures, including historical combinations and a `LORD` ligature;
- `salt`: stylistic alternates;
- `ss01`: all stylistic alternates;
- `ss02`: selected historically accurate alternates;
- `ss03`: historical forms.

Initial CSS exploration may use a declaration equivalent to:

```css
.witness-scripture {
  font-family: "KJV1611", serif;
  font-feature-settings:
    "hist" 1,
    "kern" 1,
    "calt" 1,
    "liga" 1;
}
```

Feature combinations must be checked against the selected page. Enabling every
alternate is not automatically more faithful. The final configuration should
be based on direct glyph-by-glyph comparison at representative passages.

The OFL text must be packaged in full and surfaced in the reading page's font
credits, following the precedent established for IM FELL.

### 5.2 Roman and italic companions

The KJV1611 designer recommends pairing the font with EB Garamond. EB Garamond
is therefore the leading roman and italic candidate, subject to visual
comparison with the selected witness.

IM FELL is already packaged by this project and may harmonize with the wider
Marginalia design, but the Fell types are later than 1611. If used, they must be
described as a compatible historical approximation rather than a reconstruction
of the witness's roman face.

The choice should be made by comparing:

- the book title and subtitle;
- running headers;
- the chapter synopsis;
- marginal notes;
- roman supplied words embedded in blackletter;
- numeral proportions and small-size readability.

A single companion family is preferable if it can cover roman, italic, small
sizes, and display capitals without distorting the hierarchy.

### 5.3 Fonts that should not be used for this witness

- **Gutenberg Textura or B42 reconstructions:** Gutenberg's Bible predates the
  KJV by roughly a century and uses fifteenth-century `textura quadrata`.
- **UnifrakturMaguntia:** despite its OFL license and useful web features, it is
  based on a 1901 Fraktur design, not the 1611 KJV.
- **Generic Old English display fonts:** visual resemblance is not evidence of
  historical relation.
- **Kingthings Petrock:** its own documentation says it is based on lettering
  found in a church display about bell ringing, not the King James Bible.

A future Gutenberg Bible corpus would require a separate witness and design
specification. It should not share a typeface decision with Ecclesiastes merely
because both witnesses use forms of blackletter.

## 6. Page composition

### 6.1 Desktop witness

At wide viewports, the witness should appear as a centered folio page or page
region with notes alongside it. The composition should reproduce the logic of
the source without pretending to reproduce every physical accident.

From top to bottom, the reference page contains:

1. A three-part running header bounded by rules.
2. A floral or vegetal headpiece.
3. A centered book title in spaced roman capitals.
4. A centered subtitle in roman.
5. A horizontal rule.
6. A chapter heading and compact chapter synopsis.
7. Two justified text columns separated by a vertical rule.
8. Marginal references outside the scripture columns.
9. A decorated opening `T` spanning several lines.
10. The beginning of chapter II in the lower right column, with its own heading,
    synopsis, and decorated initial.
11. Bottom-of-page furniture such as a catchword, signature, or page number if
    present and relevant in the controlling witness.

The outer page should use a warm ivory ground and dark brown-black ink. Any
paper texture should be low-contrast, non-repeating at visible scale, and
subordinate to the type. Avoid artificial stains, torn edges, dark vignettes,
or exaggerated print damage.

The column width, line height, justification, paragraph starts, verse-number
placement, and initial dimensions matter more than decorative aging.

### 6.2 Running header

The header should be modeled as three semantic regions rather than a single
string spaced with manual blanks:

- left topic;
- centered chapter range;
- right topic.

This allows faithful alignment at desktop sizes and accessible linear reading.
The exact wording must come from the selected witness.

### 6.3 Headpiece and rules

The headpiece may be:

- a crop from a rights-cleared page image;
- a vector reconstruction traced from a public-domain original under documented
  reproduction terms;
- a newly drawn, clearly labeled approximation derived from the witness.

It should not be replaced by a generic stock flourish without disclosure.
Decorative rules may be CSS when they represent simple geometry. They should
not be baked into a background image that also contains text.

### 6.4 Decorated initial

The large initial must remain textual in reading order. A decorative image or
SVG may surround or overlay it, but screen readers and copied text should
encounter one `T`, not a missing letter or a duplicate.

The design must specify:

- how many lines the initial spans;
- whether its ornament is a sourced crop or reconstruction;
- how the adjacent blackletter wraps;
- its fallback when images or custom fonts fail;
- its simplified form on narrow screens.

### 6.5 Columns and reading order

CSS multi-column layout is visually tempting but can complicate stable anchors,
selection, annotation highlights, and screen-reader order. A structured pair of
column containers may provide more deterministic behavior if the original
column break is itself part of the witness.

The implementation must preserve a single logical reading order:

1. left scripture column from top to bottom;
2. right scripture column from top to bottom;
3. associated marginal matter in an order announced or linked semantically.

The visible page in the reference image spans chapter I and part of chapter II.
The corpus must decide whether preserving that page composition requires
including the beginning of chapter II even if the initial annotation scope is
chapter I. A fabricated blank lower-right area is not an edition-faithful
solution.

### 6.6 Marginal references

Marginal notes and cross-references should remain outside the main columns on
wide screens. They must be represented as structured text connected to the
relevant verse or phrase, not flattened into the page background.

At narrow widths, marginal matter may become:

- verse-linked expandable notes;
- an end-of-verse apparatus;
- an end-of-chapter apparatus.

The relationship between reference and target must remain available to keyboard
and screen-reader users.

## 7. Annotation interaction

The annotation interface should remain outside the simulated witness page.
Opening notes must not push individual lines around or insert modern cards
inside the historical columns.

Recommended behavior:

- Keep the witness page in the primary reading region.
- Keep annotations in a neighboring panel at wide widths and below the text at
  narrow widths.
- Use a restrained translucent ochre or muted gold wash for active text.
- Consider a thin gutter mark where background highlighting reduces
  blackletter legibility.
- Preserve sufficient contrast between ink, active highlight, and paper.
- Scroll the smallest necessary amount when activating a note.
- Keep the selected annotation and selected text view in the URL state.
- Never use color alone to communicate selection.

Highlights should follow exact textual fragments, not absolute image
coordinates. The visual system may imitate a page, but annotation resolution
must remain text-based and deterministic.

## 8. Responsive behavior

The witness should not be uniformly scaled down on mobile. A complete
side-by-side folio at phone width would make both scripture and marginalia
unreadable.

### Wide screens

- Centered page or page region.
- Two scripture columns.
- Outer marginal references.
- Annotation panel beside the page.
- Full running header and headpiece.

### Intermediate screens

- Preserve two columns only while the minimum readable type size and column
  width can be maintained.
- Move the annotation panel below or into a controlled drawer.
- Reduce outer whitespace before reducing type size.
- Keep margins and references from overlapping scripture.

### Narrow screens

- Reflow scripture into one column in canonical reading order.
- Preserve blackletter, roman role changes, verse numbers, chapter headings,
  synopsis, and decorated initial.
- Convert marginal references to linked apparatus entries.
- Simplify the running header without concatenating its parts ambiguously.
- Reduce the ornament rather than allowing it to force horizontal scrolling.
- Keep body type at a comfortable fixed size; do not scale text with viewport
  width.

The reading view remains the default escape hatch for readers who find dense
blackletter difficult. Switching views should preserve the active annotation
and approximate reading position.

## 9. Data and schema implications

The existing dual-text and `witness_presentation` facilities establish useful
precedents but do not yet express all features of a biblical folio.

Potential new structured requirements include:

- page and column boundaries;
- running-header regions;
- chapter headings and synopses;
- typographic-role spans within the indexed text;
- supplied-word ranges;
- verse numbers independent of the copied verse text;
- marginal notes and cross-references linked to exact anchors;
- ornaments and decorated initials with source and rights metadata;
- catchwords, signatures, and page numbers;
- continuation of a second chapter on the same witness page.

These concerns must not be encoded as opaque HTML inside the canonical text.
The base text and annotation selectors must remain plain, deterministic, and
schema-valid.

Before extending shared schemas, implementers should classify each element as:

1. **Indexed textual content:** part of the text against which annotations
   resolve.
2. **Ancillary witness text:** meaningful textual matter linked to the indexed
   content but not necessarily part of annotation selectors.
3. **Presentation metadata:** layout and typographic roles.
4. **Decorative asset:** non-textual material with provenance and rights.

A hand-authored review shell may be appropriate for the first implementation,
as with the current Donne page, but its embedded corpus-data snapshot must
remain deterministic. Corpus-specific shell code must not silently become the
only record of textual or source decisions.

Any shared schema extension requires a separate design decision, fixtures,
validation rules, path-aware errors, and tests across existing corpora.

## 10. Sources, provenance, and rights

### 10.1 Controlling witness

The final source record must document:

- bibliographic identity of the 1611 edition;
- exact copy and holding institution;
- stable scan URL or identifier;
- relevant leaf and page-image locators;
- direct inspection date and method;
- OCR use, if any, limited to discovery rather than authority;
- image reproduction terms;
- known defects or missing matter in the selected copy;
- comparison sources used to resolve uncertain readings.

### 10.2 Font

KJV1611 should be obtained from its canonical repository rather than a font
aggregation site. Record the exact upstream commit or release and the SHA-256
hash of every packaged binary. Include the complete OFL 1.1 text.

If the font is modified or subset, confirm and document the OFL naming and
redistribution requirements. Prefer an unmodified upstream WOFF2 unless file
size or glyph coverage creates a demonstrated need for subsetting.

### 10.3 Ornament and initial

The underlying 1611 printing is public domain, but a modern scan or photograph
may carry provider-specific terms or a rights statement. Public-domain age does
not eliminate the need to record how the digital image was obtained and what
reproduction conditions the holding institution states.

Each reproduced or reconstructed asset should record:

- source page and crop location;
- creator of the digital reconstruction;
- whether it is a direct crop, trace, or new approximation;
- creation date;
- license and redistribution status;
- transformations such as cleanup, thresholding, redrawing, or recoloring.

## 11. Accessibility

- All scripture and ancillary text must remain real text, not an image.
- DOM order must match reading order even when the visual layout uses two
  columns and outer margins.
- Decorative images must be hidden from assistive technology unless they carry
  relevant content.
- The decorated initial must not remove or duplicate its letter in accessible
  text.
- Font loading failure must leave a complete, readable fallback.
- Historical glyph substitution must not corrupt copied text or accessible
  names.
- Controls for text view, focus lens, pathway, notes, and sources must remain
  keyboard reachable with visible focus.
- Highlights must meet contrast requirements and use a non-color cue.
- Zoom to 200 percent must not cause overlap or horizontal page scrolling in
  the normal reading workflow.
- The reading view must remain available without requiring users to decipher
  blackletter.
- Marginal references moved at narrow widths must retain explicit links to the
  verses they annotate.

## 12. Performance and self-containment

The published page must have no network runtime dependency. It should embed or
package locally:

- KJV1611;
- the selected roman and italic companion;
- complete font licenses;
- ornament and initial assets;
- CSS and JavaScript;
- deterministic corpus data.

Font and image sizes should be measured before deciding whether to inline them
as data URLs or package them as adjacent static assets. The existing project
rule that generated reading pages are self-contained remains the default;
departure from it requires a documented project-level decision.

Layout should not shift materially after font load. Font metrics, fallbacks,
and explicit dimensions for decorative assets should be chosen accordingly.

## 13. Visual direction

The design should feel like a carefully reconstructed working book page, not a
museum-themed interface.

- Warm ivory rather than beige decoration across the whole application.
- Brown-black ink with restrained variation.
- Fine rules and exact alignment.
- Dense but ordered page typography.
- Ornament concentrated at the headpiece and initial rather than distributed
  as generic decoration.
- Modern controls outside the page, quiet and utilitarian.
- No ornamental gradient blobs, fake candlelight, leather textures, or gothic
  display type in the interface chrome.
- No cards nested inside the witness page.

The witness may be visually dense because the source is dense. The surrounding
interface should compensate with calm spacing, clear controls, and an immediate
route to the reading view.

## 14. Acceptance criteria

The design is ready for implementation only when all of the following are true:

### Source and text

- The controlling 1611 copy is identified and directly consulted.
- The exact Ecclesiastes pages are transcribed and checked.
- The relation between chapter I and the chapter II continuation is decided.
- The reading-view textual policy is named and sourced.
- All annotations resolve exactly in every displayed text.

### Typography and assets

- KJV1611 is obtained from canonical upstream, hashed, packaged, and accompanied
  by its full license.
- OpenType feature choices are checked against representative witness words.
- The roman and italic companion is selected through witness comparison.
- Supplied-word typography is represented structurally.
- Ornament and initial assets have recorded provenance and rights.
- The page is described as a reconstruction, not a facsimile.

### Layout and interaction

- Wide layout reproduces the two-column hierarchy without image-based text.
- Narrow layout reflows to one readable column.
- Marginal references remain linked and accessible.
- Active annotations highlight deterministic text fragments.
- Note controls do not disrupt witness lineation.
- View switching preserves annotation and reading state.

### Quality

- Schema validation passes.
- Existing corpora continue to validate and render unchanged unless a shared
  change was intentionally approved.
- Tests cover text alignment, historical-form opt-in, font integrity and
  licenses, structured witness furniture, and snapshot freshness.
- Desktop and narrow browser checks cover the witness and reading views.
- Keyboard, zoom, copy, and screen-reader reading order are verified.
- The final page remains self-contained and works with network access disabled.

## 15. Proposed implementation sequence

1. **Identify the witness.** Establish the exact scan, source record, rights,
   and page range.
2. **Transcribe and align.** Produce the edition-faithful text and decide the
   reading-view source or derivation.
3. **Inventory witness furniture.** Record headers, synopsis, references,
   columns, ornaments, initials, chapter transitions, catchwords, and page
   marks.
4. **Prototype typography.** Package KJV1611 and compare companion roman faces,
   feature combinations, column widths, and supplied-word spans.
5. **Decide the data contract.** Determine what current schemas can express and
   write a separate schema proposal for anything genuinely reusable.
6. **Build the witness shell.** Implement semantic text and layout before paper
   texture or ornamental refinement.
7. **Integrate annotations.** Resolve aligned selectors and add non-disruptive
   highlights and note navigation.
8. **Implement responsive apparatus.** Reflow columns and marginalia without
   losing associations.
9. **Verify accessibility and fidelity.** Compare representative passages with
   the scan and test keyboard, zoom, copy, screen-reader order, and fallback
   behavior.
10. **Document and publish.** Record fonts, hashes, licenses, visual limits,
    editorial decisions, and refresh workflow before deployment.

## 16. Open decisions

- Which exact 1611 copy and scan controls the corpus?
- Does the corpus cover chapter I, the full book, or a selected passage?
- Must the witness page include the visible opening of chapter II to preserve
  the original page composition?
- Is the reading view a typographic normalization of 1611, a conservative
  modernization, or a separately sourced later KJV edition?
- Which roman and italic face best matches the selected copy while retaining
  an embeddable license?
- Are supplied words encoded as inline typographic-role ranges, and if so where
  does that structured data live?
- Are marginal references part of the corpus's indexed text, ancillary witness
  records, or a new apparatus structure?
- Are the headpiece and decorated initials direct crops, traced vectors, or new
  approximations?
- Should desktop preserve exact historical column breaks or allow text to flow
  dynamically between two columns?
- What is the smallest reusable schema addition, if any, that does not force
  biblical page furniture onto unrelated corpora?
- Which aspects of the physical page are essential evidence and which are
  presentation atmosphere?

## 17. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Later KJV text is presented as 1611 | Require a directly inspected 1611 base witness and exact transcription |
| Blackletter becomes decorative rather than evidentiary | Limit historical styling to the witness view and document every approximation |
| Font features silently alter textual identity | Keep canonical text in ordinary Unicode and test copied text and selectors |
| Dense two-column page is unreadable on mobile | Reflow to one column and move marginalia into linked apparatus |
| Commercial or ambiguous font rights enter a public repository | Prefer canonical OFL sources and retain full license and hashes |
| Scan crops are assumed public domain without checking provider terms | Record digital-source rights separately from underlying work rights |
| CSS columns scramble anchors or reading order | Use deterministic semantic containers and test selection and assistive technology |
| Ornament dominates the reading experience | Concentrate it at historically supported locations and keep interface chrome restrained |
| Corpus-specific needs overcomplicate shared schemas | Prototype locally, classify data roles, and require a separate shared-schema decision |
| Historical glyphs make annotation highlights inaccurate | Resolve targets against stored text and apply glyph substitution only after resolution |

## 18. Reference material

- KJV1611 canonical repository and OFL source:
  <https://github.com/ctrlcctrlv/kjv1611>
- KJV1611 Font Library catalog entry:
  <https://fontlibrary.org/en/font/kjv-1611/>
- Specialist overview of 1611 mixed typography:
  <https://blackletterkingjamesbible.com/Library/Typography>
- National Diet Library overview of Gutenberg's `textura quadrata` and the
  approximately 300 sorts used for the 42-line Bible:
  <https://www.ndl.go.jp/incunabula/e/chapter2/index.html>
- Commercial Gutenberg-specific comparison, not proposed for this witness:
  <https://www.myfonts.com/collections/1456-gutenberg-b42-pro-font-glc>
- Permissively licensed generic Textura comparison, not a B42 or KJV
  reconstruction:
  <https://github.com/MihailJP/TexturaLibera>

These links are research starting points. Any claim or asset promoted into a
real corpus must be represented through the project's normal source,
evidence, access, rights, and review records.

## 19. Implementation brief

Add an edition-faithful 1611 witness view using the OFL-licensed KJV1611 font
and verified historical OpenType features. Reproduce the selected witness's
mixed blackletter and roman hierarchy, two-column measure, running header,
chapter synopsis, marginal references, supplied-word roman, ornament, and
decorated initial. Keep ornaments source-backed, keep the stored transcription
free of presentation-glyph substitutions, and provide a separate readable
single-column view for annotations. Do not claim fidelity until the exact 1611
copy, transcription, ancillary matter, font behavior, and asset rights have
been checked directly.
