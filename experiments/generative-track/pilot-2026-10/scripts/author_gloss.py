"""Author a hand-written gloss identifying the drawing-compass instrument.

Not a generative-track product -- it comes from a close-reading discussion -- so it
is created as a draft under drafts/ (outside records/, so the validator ignores it)
with created_by marking it hand-authored. Documented-fact, targeting line 26 where
"twin compasses" is first named, with a modernized display selector so it is
promotion-ready.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\author_gloss.py
"""
from __future__ import annotations

import pathlib
import sys
import unicodedata

import yaml
from jsonschema import Draft202012Validator

REPO = pathlib.Path(r"p:\shared\reference-corpus-template")
sys.path.insert(0, str(REPO / "src"))
from reference_corpus.identifiers import derive_annotation_id  # noqa: E402
from reference_corpus.targets import index_base_text, resolve_target  # noqa: E402
from reference_corpus.validate import load_schemas  # noqa: E402
from reference_corpus.yaml_io import load_yaml  # noqa: E402

CORPUS = REPO / "corpora" / "donne-a-valediction-forbidding-mourning"
DEST = CORPUS / "drafts" / "compass-instrument-gloss.yaml"
BASE_SRC = "src_d933303080412160"       # 1633 base-text witness
GRIERSON = "src_95a01a8318fcf5d6"       # Grierson 1912 commentary

rec = {
    "schema_version": "1.0.0",
    "record_type": "annotation",
    "id": "ann_PENDING",
    "title": "What the \u201cTwin Compasses\u201d Are",
    "provenance": {
        "local_key": "compass-instrument",
        "created_by": "Devmate-assisted editorial draft",
        "created_on": "2026-10-02",
    },
    "target": {
        "work_id": "work_a_valediction_forbidding_mourning",
        "edition_source_id": BASE_SRC,
        "locator": {"scheme": "line", "value": "26"},
        "exact_text": "As stiffe twin compasses are two,",
        "display_selectors": [
            {"text_id": "modernized", "exact_text": "As stiff twin compasses are two,"}
        ],
    },
    "annotation_type": "linguistic",
    "claim": {
        "body": (
            "These \u201ctwin compasses\u201d are the two-legged instrument for drawing a circle, "
            "not a magnetic compass for finding direction. The poem works from the tool itself: "
            "its two \u201cfeet\u201d (the legs) are joined at the top, and one stays fixed at the "
            "centre while the other swings round to draw the circle. Seeing the instrument is what "
            "makes the rest legible \u2014 the \u201cfixt foot\u201d that sits \u201cin the center,\u201d "
            "the \u201cother\u201d that \u201cdoth rome,\u201d and the \u201ccircle\u201d they trace together."
        ),
        "epistemic_status": "documented-fact",
        "editorial_confidence": {
            "level": "unassessed",
            "rationale": (
                "The identification is strictly checkable from the poem's own details (two joined "
                "feet, one fixed at the centre, a circle drawn) and is confirmed by Grierson's "
                "commentary."
            ),
        },
        "contested": False,
        "attributions": [],
    },
    "evidence": [
        {
            "id": "ev_base_text",
            "source_id": BASE_SRC,
            "relationship": "supports",
            "use": "direct-evidence",
            "summary": (
                "The poem's own details \u2014 two joined \u201cfeet,\u201d one fixed at the "
                "\u201ccenter,\u201d the other drawing a \u201ccircle\u201d \u2014 identify the "
                "two-legged drawing instrument."
            ),
            "citation": {"locator": "line 26 (and ll. 25-36)"},
            "quotation": "As stiffe twin compasses are two,",
        },
        {
            "id": "ev_grierson",
            "source_id": GRIERSON,
            "relationship": "supports",
            "use": "reported-evidence",
            "summary": (
                "Grierson's commentary treats the simile as the drawing compass, citing a parallel "
                "that describes twin compasses as one body with two points making the round of a "
                "circle."
            ),
            "citation": {
                "locator": "commentary on ll. 25-36 (vol. II, pp. 49-50)",
                "citation_text": "Grierson, The Poems of John Donne, vol. II, 49-50.",
            },
        },
    ],
    "review": {
        "state": "draft",
        "notes": (
            "Hand-authored gloss from a close-reading discussion (not a generative-track product). "
            "Ready to promote: documented-fact with a modernized display selector, targeting the "
            "instrument's first naming at line 26."
        ),
    },
    "tags": ["lens-geometry-cosmology", "gloss", "compass"],
}

rec["id"] = derive_annotation_id(rec)

# base-text indices (canonical + modernized) for resolution checks
manifest = load_yaml(CORPUS / "corpus.yaml")
base_lk = manifest["presentation"]["base_text_annotation"]
base_rec = next(load_yaml(CORPUS / r) for r in manifest["annotations"]
                if load_yaml(CORPUS / r)["provenance"]["local_key"] == base_lk)
idx = index_base_text(base_rec["target"]["exact_text"])
modern_full = next(s["exact_text"] for s in base_rec["target"]["display_selectors"]
                   if s["text_id"] == "modernized")

schemas, registry = load_schemas(REPO / "schemas")
errors = sorted(Draft202012Validator(schemas["annotation.schema.json"], registry=registry)
                .iter_errors(rec), key=lambda e: list(e.path))
resolve_target(rec["target"], idx)  # canonical resolves (raises otherwise)
sel_ok = rec["target"]["display_selectors"][0]["exact_text"] in modern_full


class BlockDumper(yaml.SafeDumper):
    pass


BlockDumper.add_representer(
    str, lambda d, x: d.represent_scalar("tag:yaml.org,2002:str", x, style="|" if "\n" in x else None)
)
text = yaml.dump(rec, Dumper=BlockDumper, sort_keys=False, allow_unicode=True,
                 default_flow_style=False, width=1000)
text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
if not text.endswith("\n"):
    text += "\n"
DEST.write_bytes(text.encode("utf-8"))

print(f"id {rec['id']}")
print(f"schema {'valid' if not errors else 'INVALID: ' + str(errors[:3])}")
print(f"canonical target resolves: True; modernized selector resolves: {sel_ok}")
print(f"wrote {DEST}")
