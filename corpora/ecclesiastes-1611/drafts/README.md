# Ecclesiastes 1611 witness prototype

This directory contains an isolated, non-canonical interaction prototype for the
witness presentation proposed in
`../../../DESIGN_ecclesiastes_1611_witness_v1.md`.

Open `review-witness-mockup.html` directly in a browser. It is a self-contained
file with embedded CSS, JavaScript, fonts, licenses, demonstration data, and an
original inline SVG ornament. It makes no runtime network requests and does not
require a build step.

## Status and boundary

The prototype tests one architectural principle:

> Marginalia owns the frame; the witness owns the page.

The Marginalia frame supplies the masthead, view and focus controls, URL-backed
state, external note stream, provenance disclosure, responsive behavior, and
accessibility conventions. The witness-specific canvas supplies the running
header, headpiece, mixed roman and blackletter type, chapter synopsis, explicit
columns, marginal references, decorated initial, and page furniture.

This directory intentionally has no `corpus.yaml`, `records/`, canonical
`review.html`, or catalog entry. The prototype is not included in a manifest,
not validated as a corpus, and not published as an edition. It does not replace
a sibling `../review.html`; no such canonical page exists yet.

The shared renderer, schemas, tests, Donne corpus, Yeats corpus, and repository
landing page are unchanged. Witness-specific presentation remains local until a
real Ecclesiastes corpus establishes the smallest reusable contract.

## Demonstration text

The sample includes Ecclesiastes 1:1-18 and 2:1-2 from:

- Project Gutenberg ebook 10, *The King James Version of the Bible*;
- `https://www.gutenberg.org/cache/epub/10/pg10.txt`;
- release date 1989-08-01;
- most recent source update 2024-10-29;
- retrieved 2026-10-04.

This normalized Project Gutenberg copy is used only to make the layout and
interaction testable. It has not been collated against a 1611 page image. The
blackletter setting, supplied-word sample, marginal references, running header,
chapter synopsis, page number, catchword, and column break are design
reconstructions, not source-critical claims. Typography does not establish a
historical reading.

The discussion image that prompted the design remains an unidentified reference
image. A canonical implementation still requires the controlling copy, holding
institution, shelfmark or scan identifier, page locators, access method,
reproduction terms, and direct transcription described in the root design spec.

## Font assets

The HTML embeds exact upstream binaries as base64 data URLs. Historical forms
are OpenType presentation; the stored and copied sample text remains ordinary
Unicode.

| Asset | Canonical upstream | Pinned commit | Bytes | SHA-256 |
|---|---|---|---:|---|
| `KJV1611.woff2` | `https://github.com/ctrlcctrlv/kjv1611` | `f957694f8eef31f997ae3ff17880c76292441774` | 136532 | `0a327e72a0f4bd29e732172de04c01276ba4a934405a334a2a21e6042da0511a` |
| `EBGaramond[wght].ttf` | `https://github.com/google/fonts/tree/main/ofl/ebgaramond` | `9710da1eacb3be272583c3224dcb70f9da6eadbb` | 851176 | `ef9512f92f6d579e5dc75af59a5a4b1b8b47d2eda89e00b954d44520e5369027` |
| `EBGaramond-Italic[wght].ttf` | `https://github.com/google/fonts/tree/main/ofl/ebgaramond` | `9710da1eacb3be272583c3224dcb70f9da6eadbb` | 754468 | `bba2c4499c93c9612b90b9825d32b07da52fce2fe57562a1eb6b833553f93c4e` |

Both projects distribute their fonts under the SIL Open Font License 1.1. The
complete upstream license texts are embedded in visible, collapsible sections
inside the HTML; line endings and trailing whitespace are normalized for HTML
display. The downloaded license-file hashes were:

- KJV1611 `LICENSE.txt`: `0ea667fb557836c9a1f7c802fcced24d781cfcb8696e1a57cab1b0a727957a9c`
- EB Garamond `OFL.txt`: `0985066662eb755ed3683ae5482a81a9195b49ce3f7e165cc2388b3dbece7dd7`

The headpiece SVG and decorated-initial CSS were made for this prototype. They
do not copy artwork from the discussion image or another scan.

## What the mock exercises

- witness and reading views rendered from one inline demonstration model;
- explicit semantic left and right columns in logical reading order;
- scoped KJV1611 historical forms over ordinary Unicode text;
- roman hierarchy and a representative supplied-word role;
- linked desktop marginal references and a mobile apparatus;
- external mock notes with focus filters and phrase highlighting;
- view, focus, active-note, and note-visibility state stored in the URL hash;
- browser Back/Forward and reload restoration;
- keyboard-accessible controls, visible focus, skip navigation, and Escape close;
- two-column desktop presentation and one-column narrow-screen reflow;
- reduced-motion and increased-contrast preferences;
- offline font, license, CSS, JavaScript, data, and ornament packaging.

## Known gaps before promotion

Promotion requires source work, not merely visual polish:

1. Identify and directly inspect the exact 1611 witness.
2. Transcribe the selected page or passage from images rather than OCR alone.
3. Verify wording, spelling, punctuation, supplied words, marginalia, synopsis,
   running header, ornament, column break, chapter-II continuation, and page
   furniture against that witness.
4. Decide the reading-view textual policy and source it separately when needed.
5. Classify each element as indexed text, ancillary text, presentation metadata,
   or decorative asset.
6. Create canonical source and annotation records with independently resolving
   selectors for every displayed text.
7. Record image-provider reproduction terms separately from the public-domain
   status of the underlying printing.
8. Add corpus validation, rendering tests, asset-integrity tests, accessibility
   checks, and the normal human review trail.

Do not run the shared renderer or `scripts/refresh-review.py` against this draft.
Those workflows apply only after an actual manifest and hand-authored canonical
review shell exist.
