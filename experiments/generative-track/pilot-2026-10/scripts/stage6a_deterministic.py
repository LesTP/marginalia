"""Stage 6, Part A -- deterministic verification against the source text.

Uses the repo's own targets machinery to check, for each stage-5 draft:
  - target.exact_text resolves uniquely within its locator in the base text;
  - evidence.quotation appears verbatim in the base text (and within the target).
Writes verify_input.json (records + source lines + deterministic results) for the
independent-model judgment in Part B.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\stage6a_deterministic.py
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(r"p:\shared\reference-corpus-template")
sys.path.insert(0, str(REPO / "src"))
from reference_corpus.targets import TargetResolutionError, index_base_text, resolve_target  # noqa: E402
from reference_corpus.yaml_io import load_yaml  # noqa: E402

CORPUS = REPO / "corpora" / "donne-a-valediction-forbidding-mourning"
DRAFTS = CORPUS / "drafts" / "generative-track"
DRAFT_FILES = ["strain-as-tell.yaml", "circle-no-progress.yaml", "abab-exact-rhyme.yaml"]

manifest = load_yaml(CORPUS / "corpus.yaml")
base_lk = manifest["presentation"]["base_text_annotation"]
base_text = None
for rel in manifest["annotations"]:
    rec = load_yaml(CORPUS / rel)
    if rec["provenance"]["local_key"] == base_lk:
        base_text = rec["target"]["exact_text"]
        break
assert base_text, "base-text annotation not found"
idx = index_base_text(base_text)
print(f"base text: {len(idx.lines)} lines; first line: {idx.lines[0].text!r}\n")

out = []
for fname in DRAFT_FILES:
    rec = load_yaml(DRAFTS / fname)
    tgt, claim = rec["target"], rec["claim"]
    ev = rec["evidence"][0]
    quote = (ev.get("quotation") or "").strip()

    try:
        resolve_target(tgt, idx)
        resolves, rerr = True, ""
    except TargetResolutionError as e:
        resolves, rerr = False, str(e)

    q_in_base = quote in base_text
    q_in_target = quote in tgt["exact_text"]

    print(f"--- {rec['provenance']['local_key']} ({claim['epistemic_status']}) ---")
    print(f"  target resolves in base text: {resolves}{(' -- ' + rerr) if rerr else ''}")
    print(f"  quotation verbatim in base text: {q_in_base}")
    print(f"  quotation within target span:    {q_in_target}")

    out.append({
        "local_key": rec["provenance"]["local_key"],
        "epistemic_status": claim["epistemic_status"],
        "annotation_type": rec["annotation_type"],
        "source_lines": tgt["exact_text"],
        "claim_body": claim["body"],
        "evidence_summary": ev.get("summary", ""),
        "quotation": quote,
        "deterministic": {
            "target_resolves": resolves,
            "resolve_error": rerr,
            "quotation_in_base_text": q_in_base,
            "quotation_in_target": q_in_target,
        },
    })

dest = pathlib.Path(r"p:\shared\_scratch\genpipe\verify_input.json")
dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nwrote {dest}")
