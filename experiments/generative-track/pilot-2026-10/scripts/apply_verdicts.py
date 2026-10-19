"""Apply stage-6 verdicts to the three Donne drafts (human adjudication).

- abab-exact-rhyme (documented-fact): drop the "exact, nearly monosyllabic" over-claim;
  assert the strictly-checkable abab scheme + single end-rhymes.
- strain-as-tell / circle-no-progress (editorial-proposal): fold in the named competing
  reading so each proposal carries its counter-reading.

Only prose fields change; target/exact_text/ids are preserved (re-derived to confirm).
Each record is re-validated against the real annotation schema.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\apply_verdicts.py
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
DRAFTS = CORPUS / "drafts" / "generative-track"

EDITS = {
    "circle-no-progress.yaml": {
        "title": "The Closing Circle, Read Two Ways",
        "claim_body": (
            "The final line closes the figure by returning the speaker to his starting point: "
            "\"And makes me end, where I begunne.\" One reading hears a quiet melancholy here -- "
            "the long, \"obliquely\" running motion yields a completed circle but no advance, a "
            "consolation of form rather than of arrival. The lines equally support the opposite "
            "reading, in which \"just\" and \"firmnes\" give the circle's perfection a triumphant "
            "charge: closure as kept faith rather than stagnation. This note offers the melancholy "
            "reading as a possibility while recording that the text sustains the confident one."),
        "evidence_summary": (
            "The couplet states that the speaker's firmness-guided motion ends where it began -- the "
            "textual basis for both the 'return as completion' and the 'return as no-advance' readings."),
        "rationale": (
            "Offered as one reading of a line the text lets cut two ways; the competing confident "
            "reading is carried in the body. Status-aware stage-6 verification found it defensible "
            "but contested."),
        "notes": (
            "Stage-6 (status-aware) verified as defensible but contested; competing reading now "
            "carried in the body. Pending before promotion: novelty/attribution check and "
            "display_selectors for the modernized view."),
    },
    "strain-as-tell.yaml": {
        "title": "Does the Conceit's Elaborateness Betray Need?",
        "claim_body": (
            "The speaker meets the fact of parting not with open feeling but with an elaborate "
            "geometric proof, the twin compasses. One way to read that elaborateness is as a sign "
            "of need: were the union as secure as the argument claims, it might not require so "
            "intricate a machine to establish it, so that the strain of the conceit becomes part of "
            "its meaning. The lines equally support the opposite reading, in which the compass is a "
            "confident, even triumphant demonstration -- \"Thy firmnes makes my circle just\" -- and "
            "the ingenuity marks assurance rather than anxiety. This note offers the first reading as "
            "a possibility while recording that the text sustains both."),
        "evidence_summary": (
            "The compass argument sustained across the three stanzas is the textual basis for both "
            "readings: the elaborateness heard either as anxious need or as confident wit."),
        "rationale": (
            "Offered as a reading the text permits but does not compel; the competing confident "
            "reading is carried in the body. Status-aware stage-6 verification found it defensible "
            "but contested."),
        "notes": (
            "Stage-6 (status-aware) verified as defensible but contested; competing reading now "
            "carried in the body. Pending before promotion: novelty/attribution check and "
            "display_selectors for the modernized view."),
    },
    "abab-exact-rhyme.yaml": {
        "title": "The abab Rhyme Scheme",
        "claim_body": (
            "The three stanzas rhyme abab throughout, each quatrain closing on single end-rhymes "
            "(so/show, two/doe; sit/it, rome/home; must/just, runne/begunne). The regular "
            "alternating scheme is directly observable in the base text and lends the argument its "
            "measured, closed movement."),
        "evidence_summary": (
            "Each quatrain shows the abab pattern, the rhyme falling on the final word of every line "
            "(so/show, two/doe; sit/it, rome/home; must/just, runne/begunne)."),
        "rationale": (
            "A structural description strictly checkable against the base text; the 'exact' and "
            "'nearly monosyllabic' characterisations were removed after stage-6 flagged them as "
            "over-claims."),
        "notes": (
            "Stage-6 flagged 'exact, nearly monosyllabic' as an over-claim; tightened to the abab "
            "scheme and single end-rhymes, which are strictly checkable. Pending before promotion: "
            "display_selectors for the modernized view."),
    },
}

# base text index for a resolve check
manifest = load_yaml(CORPUS / "corpus.yaml")
base_lk = manifest["presentation"]["base_text_annotation"]
base_text = next(load_yaml(CORPUS / r)["target"]["exact_text"]
                 for r in manifest["annotations"]
                 if load_yaml(CORPUS / r)["provenance"]["local_key"] == base_lk)
idx = index_base_text(base_text)

schemas, registry = load_schemas(REPO / "schemas")
validator = Draft202012Validator(schemas["annotation.schema.json"], registry=registry)


def norm_write(path: pathlib.Path, rec: dict) -> None:
    text = yaml.safe_dump(rec, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=100)
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    path.write_bytes(text.encode("utf-8"))


for fname, e in EDITS.items():
    path = DRAFTS / fname
    rec = load_yaml(path)
    old_id = rec["id"]
    rec["title"] = e["title"]
    rec["claim"]["body"] = e["claim_body"]
    rec["claim"]["editorial_confidence"]["rationale"] = e["rationale"]
    rec["evidence"][0]["summary"] = e["evidence_summary"]
    rec["review"]["notes"] = e["notes"]
    new_id = derive_annotation_id(rec)
    rec["id"] = new_id
    errors = sorted(validator.iter_errors(rec), key=lambda x: list(x.path))
    resolve_target(rec["target"], idx)  # raises if the target no longer resolves
    norm_write(path, rec)
    print(f"{fname}: id {'UNCHANGED' if old_id == new_id else 'CHANGED!'} ({new_id}); "
          f"schema {'valid' if not errors else 'INVALID: ' + str(errors[:2])}; target resolves")

print("\ndone")
