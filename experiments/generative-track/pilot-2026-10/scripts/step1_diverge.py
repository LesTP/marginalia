"""Step 1 of the generative pipeline: Stage 2 blind divergence.

Run the SAME prompt against several models independently (no cross-talk, no
context, no personas) on the compass conceit from Donne's "A Valediction:
Forbidding Mourning", and collect each model's candidate readings.

Run on pirozhok with diplomat's venv python so toolkit + SDKs + keys are present:
  /home/claude/workspace/diplomat/.venv/bin/python \
    /home/claude/workspace/_scratch/genpipe/step1_diverge.py

Throwaway experiment. Writes results under _scratch/genpipe/out/step1/.
"""
from __future__ import annotations

import os
import pathlib
import traceback

from dotenv import load_dotenv

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete

# Keys live in diplomat's .env on pirozhok.
load_dotenv("/home/claude/workspace/diplomat/.env")

PROVIDER_KEY = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

# Three independent families (ids reused from diplomat, known-good).
MODELS = [
    ("openai", "gpt-4.1-mini"),
    ("anthropic", "claude-sonnet-4-6"),
    ("google", "gemini-2.5-flash-lite"),
]

PASSAGE = """If they be two, they are two so
As stiff twin compasses are two,
Thy soul the fixed foot, makes no show
To move, but doth, if th'other do.

And though it in the center sit,
Yet when the other far doth roam,
It leans, and hearkens after it,
And grows erect, as that comes home.

Such wilt thou be to me, who must
Like th'other foot, obliquely run;
Thy firmness makes my circle just,
And makes me end, where I begun."""

SYSTEM = (
    "You are a close reader of poetry. Read the passage and offer your own "
    "observations about how it works as a text. Focus on what is on the page: "
    "diction, syntax, sound, image, structure, argument. You may note a possible "
    "connection or context, but do NOT invent quotations, critics, dates, or "
    "sources; if you are unsure of a source, say so or leave it out. Do not hedge "
    "into 'some readers say' -- give your own reading. Be specific and concrete."
)

USER = (
    "Passage (John Donne):\n\n"
    + PASSAGE
    + "\n\nGive 6-8 distinct observations or readings, each 1-3 sentences. "
    "Number them. Prefer non-obvious noticings over generic praise."
)

OUT = pathlib.Path("/home/claude/workspace/_scratch/genpipe/out/step1")
OUT.mkdir(parents=True, exist_ok=True)


def run_one(provider: str, model_id: str) -> dict:
    key = os.environ.get(PROVIDER_KEY[provider])
    if not key:
        return {"provider": provider, "model": model_id, "error": f"{PROVIDER_KEY[provider]} missing"}
    config = LLMConfig(provider=provider, api_key=key, models={"default": model_id}, max_tokens=900)
    messages = [Message(role="system", content=SYSTEM), Message(role="user", content=USER)]
    try:
        resp = complete(messages, config, ModelTier.DEFAULT,
                        attribution="genpipe-step1", purpose="diverge")
        return {
            "provider": provider, "model": model_id, "content": resp.content,
            "in_tok": resp.token_usage.input_tokens, "out_tok": resp.token_usage.output_tokens,
        }
    except Exception as e:  # noqa: BLE001
        return {"provider": provider, "model": model_id,
                "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()}


def main() -> None:
    combined = ["# Step 1 -- blind divergence on Donne's compass conceit\n",
                "Same prompt, three models, no context, no personas.\n"]
    for provider, model_id in MODELS:
        print(f"--- {provider} / {model_id} ---", flush=True)
        r = run_one(provider, model_id)
        slug = f"{provider}_{model_id}".replace("/", "_").replace(".", "-")
        if "error" in r:
            print("  ERROR:", r["error"], flush=True)
            block = f"## {provider} / {model_id}\n\n**ERROR:** {r['error']}\n"
        else:
            print(f"  ok ({r['in_tok']} in / {r['out_tok']} out tokens)", flush=True)
            block = (f"## {provider} / {model_id}\n\n"
                     f"_tokens: {r['in_tok']} in / {r['out_tok']} out_\n\n{r['content']}\n")
            (OUT / f"{slug}.md").write_text(block, encoding="utf-8")
        combined.append("\n" + block)
    (OUT / "results.md").write_text("\n".join(combined), encoding="utf-8")
    print("\nwrote", OUT / "results.md", flush=True)


if __name__ == "__main__":
    main()
