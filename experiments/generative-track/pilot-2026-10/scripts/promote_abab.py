"""Promote abab-exact-rhyme from the generative-track drafts into the Donne corpus.

Adds the modernized display selector (reused verbatim from twin-compasses-return, same
line range), sets a human-reviewed state, and writes the record into records/annotations
in the repo's block-scalar YAML style. The derived id must stay unchanged.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\promote_abab.py
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
from reference_corpus.validate import load_schemas  # noqa: E402
from reference_corpus.yaml_io import load_yaml  # noqa: E402

CORPUS = REPO / "corpora" / "donne-a-valediction-forbidding-mourning"
SRC_DRAFT = CORPUS / "drafts" / "generative-track" / "abab-exact-rhyme.yaml"
DEST = CORPUS / "records" / "annotations" / "abab-exact-rhyme.yaml"

MODERNIZED = (
    "If they be two, they are two so\n"
    "As stiff twin compasses are two,\n"
    "Thy soul the fixed foot, makes no show\n"
    "To move, but doth, if th'other do.\n"
    "And though it in the center sit,\n"
    "Yet when the other far doth roam,\n"
    "It leans, and hearkens after it,\n"
    "And grows erect, as that comes home.\n"
    "Such wilt thou be to me, who must\n"
    "Like th'other foot, obliquely run;\n"
    "Thy firmness makes my circle just,\n"
    "And makes me end, where I begun."
)

rec = load_yaml(SRC_DRAFT)
old_id = rec["id"]

rec["provenance"]["created_by"] = "Devmate generative-track"
rec["target"]["display_selectors"] = [{"text_id": "modernized", "exact_text": MODERNIZED}]
rec["review"] = {
    "state": "human-reviewed",
    "reviewer": "LesTP",
    "reviewed_on": "2026-10-02",
    "notes": ("Rhyme scheme is strictly checkable against the base text; the 'exact' and "
              "'nearly monosyllabic' wording was removed after stage-6 flagged it as an "
              "over-claim. Generative-track origin; promoted after deterministic and "
              "status-aware verification."),
}
rec["tags"] = ["lens-form-argument", "rhyme-scheme"]

new_id = derive_annotation_id(rec)
rec["id"] = new_id

schemas, registry = load_schemas(REPO / "schemas")
errors = sorted(Draft202012Validator(schemas["annotation.schema.json"], registry=registry)
                .iter_errors(rec), key=lambda e: list(e.path))


class BlockDumper(yaml.SafeDumper):
    pass


def _str_rep(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


BlockDumper.add_representer(str, _str_rep)

text = yaml.dump(rec, Dumper=BlockDumper, sort_keys=False, allow_unicode=True,
                 default_flow_style=False, width=1000)
text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
if not text.endswith("\n"):
    text += "\n"
DEST.write_bytes(text.encode("utf-8"))

print(f"id {'UNCHANGED' if old_id == new_id else 'CHANGED!'} ({new_id})")
print(f"schema {'valid' if not errors else 'INVALID: ' + str(errors[:3])}")
print(f"wrote {DEST}")
