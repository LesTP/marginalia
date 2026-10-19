"""Stage 4-5 test on Donne: turn top readings into annotation YAML, exercising the
section 4.1 dispositions (reading -> proposal, fact -> research-lead, backed -> normal).

Runs on the laptop: gpt-4.1-mini fills model-authored prose into a deterministic
schema scaffold; each record is validated against the REAL annotation schema +
registry; ids are derived with the repo's own deriver. Drafts (unpublished) and a
research-lead stub are written to the Donne corpus's drafts/generative-track/.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\stage45.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete
from toolkit.structured_llm import parse_json_response

REPO = pathlib.Path(r"p:\shared\reference-corpus-template")
sys.path.insert(0, str(REPO / "src"))
from reference_corpus.identifiers import derive_annotation_id  # noqa: E402
from reference_corpus.validate import load_schemas  # noqa: E402

OUT = REPO / "corpora" / "donne-a-valediction-forbidding-mourning" / "drafts" / "generative-track"
OUT.mkdir(parents=True, exist_ok=True)

WORK = "work_a_valediction_forbidding_mourning"
SRC = "src_d933303080412160"  # 1633 base-text witness
MODEL = ("openai", "gpt-4.1-mini")

S3 = (
    "If they be two; they are two so\n"
    "As stiffe twin compasses are two,\n"
    "Thy soule the fixt foot, makes no show\n"
    "To move, but doth, if th'other doe.\n\n"
    "And though it in the center sit,\n"
    "Yet when the other far doth rome,\n"
    "It leanes, and hearkens after it,\n"
    "And growes erect, as that comes home.\n\n"
    "Such wilt thou be to mee, who must\n"
    "Like th'other foot, obliquely runne,\n"
    "Thy firmnes makes my circle just,\n"
    "And makes me end, where I begunne."
)
COUPLET = "Thy firmnes makes my circle just,\nAnd makes me end, where I begunne."

# Each spec carries its section-4.1 disposition, assigned by the fact/reading test:
# does the claim assert something about the world (needs a source) or read the text?
ANNOTATION_SPECS = [
    {
        "local_key": "strain-as-tell",
        "disposition": "reading -> proposal",
        "epistemic_status": "editorial-proposal",
        "annotation_type": "thematic",
        "locator": "25-36",
        "exact_text": S3,
        "reading": ("The very elaborateness of the compass conceit can be read as a sign "
                    "of emotional need: if the lovers' union were as secure as the argument "
                    "claims, the poem would not need so intricate a machine to prove it. The "
                    "strain of the figure is itself the tell."),
    },
    {
        "local_key": "circle-no-progress",
        "disposition": "reading -> proposal",
        "epistemic_status": "editorial-proposal",
        "annotation_type": "thematic",
        "locator": "35-36",
        "exact_text": COUPLET,
        "reading": ("'And makes me end, where I begunne' yields no progress, only form: the "
                    "roaming produces a completed circle but no advance, a quietly melancholic "
                    "note beneath the reassurance that depends on reading the closure as mere "
                    "return."),
    },
    {
        "local_key": "abab-exact-rhyme",
        "disposition": "backed -> normal",
        "epistemic_status": "documented-fact",
        "annotation_type": "formal",
        "locator": "25-36",
        "exact_text": S3,
        "reading": ("The three stanzas rhyme abab throughout, on exact, almost entirely "
                    "monosyllabic rhymes (so/show, two/doe; sit/it, rome/home; must/just, "
                    "runne/begunne), a formal regularity directly observable in the base text."),
    },
]

# A world-fact with no source consulted here -> section 4.1 fact -> research-lead
# (NOT published as an annotation).
RESEARCH_LEADS = [
    {
        "local_key": "composed-for-anne-1611",
        "claim": ("Donne wrote 'A Valediction: Forbidding Mourning' for his wife Anne before "
                  "a journey to the Continent, around 1611."),
        "why_lead": ("A biographical claim about the world, not a reading of the text, and no "
                     "source was consulted here. It would be settled (or corrected) by Izaak "
                     "Walton's Life of Donne and by Grierson's headnote (already a corpus "
                     "source, grierson-commentary). Until consulted, it stays a lead and is "
                     "not published as fact."),
    },
]

FIXED_PROSE_FIELDS = (
    "title, claim.body, claim.editorial_confidence.rationale, evidence[0].summary, "
    "evidence[0].quotation, review.notes"
)


def scaffold(spec: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "record_type": "annotation",
        "id": "ann_PENDING",
        "title": "<FILL: short public heading, no author name>",
        "provenance": {
            "local_key": spec["local_key"],
            "created_by": "Devmate generative-track (stage 5 test)",
            "created_on": "2026-10-02",
        },
        "target": {
            "work_id": WORK,
            "edition_source_id": SRC,
            "locator": {"scheme": "line", "value": spec["locator"]},
            "exact_text": spec["exact_text"],
        },
        "annotation_type": spec["annotation_type"],
        "claim": {
            "body": "<FILL: the reading, text-first, 2-4 sentences, a general reader>",
            "epistemic_status": spec["epistemic_status"],
            "editorial_confidence": {
                "level": "unassessed",
                "rationale": "<FILL: why unassessed / what review is still pending>",
            },
            "contested": False,
            "attributions": [],
        },
        "evidence": [
            {
                "id": "ev_base_text",
                "source_id": SRC,
                "relationship": "supports",
                "use": "direct-evidence",
                "summary": "<FILL: how the quoted lines support the claim>",
                "citation": {"locator": f"lines {spec['locator']}, 1633 text"},
                "quotation": "<FILL: a short exact quotation from the passage>",
            }
        ],
        "review": {
            "state": "draft",
            "notes": "<FILL: one line on what remains before promotion>",
        },
    }


def generate(spec: dict, validator: Draft202012Validator) -> dict:
    scaf = scaffold(spec)
    sys_p = (
        "You convert a literary reading into one annotation record. You are given a JSON "
        "scaffold. Return the SAME object with every <FILL: ...> replaced and all other "
        f"values unchanged. Fill only: {FIXED_PROSE_FIELDS}. Rules: the text is your only "
        "evidence; invent no critics, sources, dates, or quotations; the quotation must be "
        "copied verbatim from the passage. Lead the claim body with what the passage does. "
        "Output JSON only."
    )
    usr_p = (f"Reading to record ({spec['disposition']}, epistemic_status="
             f"{spec['epistemic_status']}):\n{spec['reading']}\n\n"
             f"Passage:\n{spec['exact_text']}\n\nScaffold:\n{json.dumps(scaf, indent=2)}")
    cfg = LLMConfig(provider=MODEL[0], api_key=os.environ["OPENAI_API_KEY"],
                    models={"default": MODEL[1]}, max_tokens=1500)
    err = None
    for attempt in range(2):
        u = usr_p if err is None else usr_p + f"\n\nYour previous output failed validation: {err}\nFix it."
        resp = complete([Message(role="system", content=sys_p), Message(role="user", content=u)],
                        cfg, ModelTier.DEFAULT, attribution="genpipe-stage5", purpose="record")
        try:
            rec = parse_json_response(resp.content)
        except Exception as e:  # noqa: BLE001
            err = f"not valid JSON: {e}"
            continue
        # Defensive: restore fixed structural fields, then derive the id.
        base = scaffold(spec)
        for k in ("schema_version", "record_type", "provenance", "target", "annotation_type"):
            rec[k] = base[k]
        rec["claim"]["epistemic_status"] = spec["epistemic_status"]
        rec["claim"]["contested"] = False
        rec["claim"]["attributions"] = []
        rec["claim"]["editorial_confidence"]["level"] = "unassessed"
        rec["evidence"][0]["source_id"] = SRC
        rec["evidence"][0]["relationship"] = "supports"
        rec["evidence"][0]["use"] = "direct-evidence"
        rec["review"]["state"] = "draft"
        rec["id"] = derive_annotation_id(rec)
        errors = sorted(validator.iter_errors(rec), key=lambda e: list(e.path))
        if not errors:
            return rec
        err = "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:4])
    raise RuntimeError(f"{spec['local_key']} failed schema validation: {err}")


def main() -> None:
    schemas, registry = load_schemas(REPO / "schemas")
    validator = Draft202012Validator(schemas["annotation.schema.json"], registry=registry)

    report = ["# Stage 4-5 test -- Donne compass conceit\n",
              "Dispositions assigned by the section 4.1 fact/reading test; records validated "
              "against the real annotation schema + registry.\n"]
    for spec in ANNOTATION_SPECS:
        print(f"--- {spec['local_key']} ({spec['disposition']}) ---", flush=True)
        rec = generate(spec, validator)
        path = OUT / f"{spec['local_key']}.yaml"
        path.write_text(yaml.safe_dump(rec, sort_keys=False, allow_unicode=True,
                                       default_flow_style=False, width=100), encoding="utf-8")
        print(f"  VALID -> {path.name}  id={rec['id']}  status={rec['claim']['epistemic_status']}",
              flush=True)
        report.append(f"- **{spec['local_key']}** ({spec['disposition']}): VALID, "
                      f"`{rec['claim']['epistemic_status']}`, id `{rec['id']}`\n"
                      f"  - title: {rec['title']}\n"
                      f"  - claim: {rec['claim']['body']}")

    leads = ["# Research leads (fact -> research-lead; NOT published)\n"]
    for lead in RESEARCH_LEADS:
        print(f"--- {lead['local_key']} (fact -> research-lead) ---", flush=True)
        leads.append(f"## {lead['local_key']}\n\n- claim: {lead['claim']}\n- why a lead: {lead['why_lead']}\n")
        report.append(f"- **{lead['local_key']}** (fact -> research-lead): NOT a record; "
                      f"written to research-leads.md")
    (OUT / "research-leads.md").write_text("\n".join(leads), encoding="utf-8")
    (OUT / "stage45-report.md").write_text("\n".join(report), encoding="utf-8")
    print("\nwrote", OUT, flush=True)


if __name__ == "__main__":
    main()
