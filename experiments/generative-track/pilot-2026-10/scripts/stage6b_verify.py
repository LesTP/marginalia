"""Stage 6, Part B -- independent-model verification against the source lines.

An independent verifier (Claude sonnet-4-6, a different family from the gpt-4.1-mini
that generated the drafts) judges each claim ONLY against the source lines, via binary
questions; the label is derived deterministically from the answers (not by the model).

  /home/claude/workspace/diplomat/.venv/bin/python \
    /home/claude/workspace/_scratch/genpipe/stage6b_verify.py
"""
from __future__ import annotations

import json
import os
import pathlib

from dotenv import load_dotenv

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete
from toolkit.structured_llm import parse_json_response

load_dotenv("/home/claude/workspace/diplomat/.env")
VERIFIER = ("anthropic", "claude-sonnet-4-6")  # independent of the gpt-4.1-mini generator

SCRATCH = pathlib.Path("/home/claude/workspace/_scratch/genpipe")
records = json.loads((SCRATCH / "verify_input.json").read_text(encoding="utf-8"))
OUT = SCRATCH / "out" / "step6"
OUT.mkdir(parents=True, exist_ok=True)

SYS = ("You are an independent verifier of an annotation about a poem. Judge ONLY "
       "against the SOURCE LINES provided. Do not use outside knowledge, do not infer "
       "beyond the lines, and invent nothing. Be strict.")

QUESTIONS = (
    "Answer these about the claim, judged only against the source lines:\n"
    "- quotation_is_exact: the quotation is copied verbatim from the source lines.\n"
    "- claim_grounded_in_lines: every assertion the claim makes about the text is "
    "borne out by these lines (no over-reach, nothing absent from the lines).\n"
    "- claim_adds_no_external_facts: the claim asserts no fact, source, context, or "
    "biography not present in these lines.\n"
    "- status_appropriate: given the claim is labelled '{status}', that label fits -- "
    "for 'documented-fact' the claim must be strictly checkable from the lines (not "
    "interpretation); for 'editorial-proposal' it must be a defensible reading grounded "
    "in the lines and not over-stated as fact.\n"
    "- issues: a short, specific note of any problem (e.g. an over-claim or a borderline "
    "word), or 'none'.\n"
    "Return JSON only: {{\"quotation_is_exact\":bool, \"claim_grounded_in_lines\":bool, "
    "\"claim_adds_no_external_facts\":bool, \"status_appropriate\":bool, \"issues\":str}}"
)
KEYS = ["quotation_is_exact", "claim_grounded_in_lines", "claim_adds_no_external_facts",
        "status_appropriate"]


def verify(rec: dict) -> dict:
    user = (f"SOURCE LINES:\n{rec['source_lines']}\n\n"
            f"CLAIM (epistemic_status = {rec['epistemic_status']}):\n{rec['claim_body']}\n\n"
            f"EVIDENCE SUMMARY:\n{rec['evidence_summary']}\n\n"
            f"QUOTATION:\n{rec['quotation']}\n\n" + QUESTIONS.format(status=rec["epistemic_status"]))
    cfg = LLMConfig(provider=VERIFIER[0], api_key=os.environ[PROVIDER_KEY[VERIFIER[0]]],
                    models={"default": VERIFIER[1]}, max_tokens=1500)
    err = None
    for _ in range(2):
        u = user if err is None else user + f"\n\nYour previous output was unparseable ({err}). Return JSON only."
        resp = complete([Message(role="system", content=SYS), Message(role="user", content=u)],
                        cfg, ModelTier.DEFAULT, attribution="genpipe-step6", purpose="verify")
        try:
            return parse_json_response(resp.content)
        except Exception as e:  # noqa: BLE001
            err = str(e)
    raise RuntimeError(f"verifier unparseable for {rec['local_key']}: {err}")


PROVIDER_KEY = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY", "openrouter": "OPENROUTER_API_KEY"}

report = ["# Stage 6 -- verification against source text\n",
          f"Deterministic checks (repo targets machinery) + independent verifier "
          f"({VERIFIER[1]}, different family from the gpt-4.1-mini generator). "
          f"Label derived deterministically from the binary answers.\n"]
results = []
for rec in records:
    print(f"--- {rec['local_key']} ---", flush=True)
    v = verify(rec)
    det = rec["deterministic"]
    det_ok = det["target_resolves"] and det["quotation_in_base_text"] and det["quotation_in_target"]
    model_ok = all(bool(v.get(k)) for k in KEYS)
    label = "VERIFIED" if (det_ok and model_ok) else "FLAGGED"
    failed = [k for k in KEYS if not bool(v.get(k))]
    if not det_ok:
        failed = ["deterministic"] + failed
    print(f"  {label}" + (f" (failed: {', '.join(failed)})" if failed else ""), flush=True)
    print(f"  issues: {v.get('issues')}", flush=True)
    results.append({"local_key": rec["local_key"], "label": label, "failed": failed,
                    "deterministic": det, "verifier": v})
    report.append(
        f"## {rec['local_key']} -- {label}\n\n"
        f"- status: `{rec['epistemic_status']}`\n"
        f"- deterministic: target_resolves={det['target_resolves']}, "
        f"quotation_in_base_text={det['quotation_in_base_text']}, "
        f"quotation_in_target={det['quotation_in_target']}\n"
        f"- verifier: " + ", ".join(f"{k}={bool(v.get(k))}" for k in KEYS) + "\n"
        f"- issues: {v.get('issues')}\n")

(OUT / "verify_report.md").write_text("\n".join(report), encoding="utf-8")
(OUT / "verify_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nwrote", OUT / "verify_report.md", flush=True)
