"""Stage 6, Part B v2 -- STATUS-AWARE independent verification.

Same independent verifier (Claude sonnet-4-6) and deterministic inputs, but the rubric
now switches on epistemic status:
  - documented-fact  -> strictly checkable from the lines AND accurate (flag over-claims)
  - editorial-proposal -> defensible / not contradicted by the lines, free of external
    facts, and honestly labelled as a reading (NOT held to the fact standard)
Label derived deterministically from the binary answers.

  /home/claude/workspace/diplomat/.venv/bin/python \
    /home/claude/workspace/_scratch/genpipe/stage6b_statusaware.py
"""
from __future__ import annotations

import json
import os
import pathlib

from dotenv import load_dotenv

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete
from toolkit.structured_llm import parse_json_response

load_dotenv("/home/claude/workspace/diplomat/.env")
VERIFIER = ("anthropic", "claude-sonnet-4-6")
PROVIDER_KEY = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY", "openrouter": "OPENROUTER_API_KEY"}

SCRATCH = pathlib.Path("/home/claude/workspace/_scratch/genpipe")
records = json.loads((SCRATCH / "verify_input.json").read_text(encoding="utf-8"))
OUT = SCRATCH / "out" / "step6_v2"
OUT.mkdir(parents=True, exist_ok=True)

SYS = ("You are an independent verifier of an annotation about a poem. Judge ONLY against "
       "the SOURCE LINES provided. Do not use outside knowledge, and invent nothing. "
       "Apply the rubric for the stated epistemic status exactly; do not import a stricter "
       "standard than the rubric asks for.")

COMMON = (
    "- quotation_is_exact: the quotation is copied verbatim from the source lines.\n"
    "- claim_adds_no_external_facts: the claim asserts no fact, source, context, or "
    "biography not present in these lines.\n"
)
FACT_RUBRIC = (
    "This claim is labelled documented-fact. A documented-fact must be strictly checkable "
    "from the lines alone. Answer:\n" + COMMON +
    "- fact_strictly_checkable: the claim is strictly checkable from these lines (not "
    "interpretation) AND accurate -- any structural or quantitative detail (counts, rhyme, "
    "metre, wording) must be correct for these lines, with no over-statement.\n"
    "- issues: a short specific note of any inaccuracy or over-claim, or 'none'.\n"
    "Return JSON only: {\"quotation_is_exact\":bool, \"claim_adds_no_external_facts\":bool, "
    "\"fact_strictly_checkable\":bool, \"issues\":str}"
)
PROPOSAL_RUBRIC = (
    "This claim is labelled editorial-proposal -- an interpretation offered for "
    "consideration, NOT a fact. A proposal may go beyond the literal sense; it must only "
    "be defensible. Do NOT flag it merely for being interpretive or not fully grounded. "
    "Answer:\n" + COMMON +
    "- reading_defensible: the source lines can plausibly support this reading and do NOT "
    "flatly contradict it. (Going beyond the literal is allowed; being contradicted by the "
    "lines is not.)\n"
    "- honestly_labelled: the claim is offered as a reading/interpretation, not asserted as "
    "established fact.\n"
    "- issues: a short specific note, or 'none'. If the lines also support a strong "
    "competing reading, say so briefly (this marks the proposal as contested, not wrong).\n"
    "Return JSON only: {\"quotation_is_exact\":bool, \"claim_adds_no_external_facts\":bool, "
    "\"reading_defensible\":bool, \"honestly_labelled\":bool, \"issues\":str}"
)
KEYS = {
    "documented-fact": ["quotation_is_exact", "claim_adds_no_external_facts", "fact_strictly_checkable"],
    "editorial-proposal": ["quotation_is_exact", "claim_adds_no_external_facts",
                           "reading_defensible", "honestly_labelled"],
}


def verify(rec: dict) -> dict:
    status = rec["epistemic_status"]
    rubric = FACT_RUBRIC if status == "documented-fact" else PROPOSAL_RUBRIC
    user = (f"SOURCE LINES:\n{rec['source_lines']}\n\n"
            f"CLAIM (epistemic_status = {status}):\n{rec['claim_body']}\n\n"
            f"EVIDENCE SUMMARY:\n{rec['evidence_summary']}\n\n"
            f"QUOTATION:\n{rec['quotation']}\n\n{rubric}")
    cfg = LLMConfig(provider=VERIFIER[0], api_key=os.environ[PROVIDER_KEY[VERIFIER[0]]],
                    models={"default": VERIFIER[1]}, max_tokens=1500)
    err = None
    for _ in range(2):
        u = user if err is None else user + f"\n\nPrevious output unparseable ({err}). JSON only."
        resp = complete([Message(role="system", content=SYS), Message(role="user", content=u)],
                        cfg, ModelTier.DEFAULT, attribution="genpipe-step6v2", purpose="verify")
        try:
            return parse_json_response(resp.content)
        except Exception as e:  # noqa: BLE001
            err = str(e)
    raise RuntimeError(f"verifier unparseable for {rec['local_key']}: {err}")


report = ["# Stage 6 (status-aware) -- verification against source text\n",
          f"Independent verifier {VERIFIER[1]}; rubric switches on epistemic status. "
          f"Label = deterministic checks AND all rubric answers true.\n"]
results = []
for rec in records:
    status = rec["epistemic_status"]
    print(f"--- {rec['local_key']} ({status}) ---", flush=True)
    v = verify(rec)
    det = rec["deterministic"]
    det_ok = det["target_resolves"] and det["quotation_in_base_text"] and det["quotation_in_target"]
    keys = KEYS[status]
    failed = [k for k in keys if not bool(v.get(k))]
    if not det_ok:
        failed = ["deterministic"] + failed
    label = "VERIFIED" if not failed else "FLAGGED"
    print(f"  {label}" + (f" (failed: {', '.join(failed)})" if failed else ""), flush=True)
    print(f"  issues: {v.get('issues')}", flush=True)
    results.append({"local_key": rec["local_key"], "status": status, "label": label,
                    "failed": failed, "deterministic": det, "verifier": v})
    report.append(
        f"## {rec['local_key']} -- {label}\n\n"
        f"- status: `{status}`\n"
        f"- deterministic: resolves={det['target_resolves']}, "
        f"quote_in_base={det['quotation_in_base_text']}, quote_in_target={det['quotation_in_target']}\n"
        f"- verifier: " + ", ".join(f"{k}={bool(v.get(k))}" for k in keys) + "\n"
        f"- issues: {v.get('issues')}\n")

(OUT / "verify_report.md").write_text("\n".join(report), encoding="utf-8")
(OUT / "verify_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nwrote", OUT / "verify_report.md", flush=True)
