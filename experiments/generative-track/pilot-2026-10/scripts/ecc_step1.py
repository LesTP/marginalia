"""Stage 1 (quality tier): blind divergence on Ecclesiastes 1:2-11 (KJV).

Same pattern as the Donne step1_quality run: one prompt, three independent models,
no context, no personas. First test of the pipeline on a sacred/translated prose-poem.

  /home/claude/workspace/diplomat/.venv/bin/python \
    /home/claude/workspace/_scratch/genpipe/ecc_step1.py
"""
from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete

load_dotenv("/home/claude/workspace/diplomat/.env")
PROVIDER_KEY = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY", "openrouter": "OPENROUTER_API_KEY"}

MODELS = [
    ("openai", ["gpt-5.5"]),
    ("anthropic", ["claude-opus-4-6", "claude-sonnet-4-6"]),
    ("google", ["gemini-2.5-pro", "gemini-2.5-flash"]),
]
MAX_TOKENS = 4000

PASSAGE = """1:2 Vanity of vanities, saith the Preacher, vanity of vanities; all is vanity.
1:3 What profit hath a man of all his labour which he taketh under the sun?
1:4 One generation passeth away, and another generation cometh: but the earth abideth for ever.
1:5 The sun also ariseth, and the sun goeth down, and hasteth to his place where he arose.
1:6 The wind goeth toward the south, and turneth about unto the north; it whirleth about continually, and the wind returneth again according to his circuits.
1:7 All the rivers run into the sea; yet the sea is not full; unto the place from whence the rivers come, thither they return again.
1:8 All things are full of labour; man cannot utter it: the eye is not satisfied with seeing, nor the ear filled with hearing.
1:9 The thing that hath been, it is that which shall be; and that which is done is that which shall be done: and there is no new thing under the sun.
1:10 Is there any thing whereof it may be said, See, this is new? it hath been already of old time, which was before us.
1:11 There is no remembrance of former things; neither shall there be any remembrance of things that are to come with those that shall come after."""

SYSTEM = (
    "You are a close reader of literary and scriptural texts. Read this passage (the "
    "opening of Ecclesiastes in the 1611/standard King James Version, translated from "
    "Hebrew) and offer your own observations about how it works as a text: diction, "
    "syntax, sound, image, structure, argument, tone. You may note that it is a "
    "translation and flag a word whose rendering seems to carry weight, but do NOT "
    "invent Hebrew you are unsure of, and do NOT invent critics, sources, or dates; if "
    "unsure of a source, say so or leave it out. Give your own reading, not 'some say'. "
    "Be specific and concrete."
)
USER = ("Passage (King James Version):\n\n" + PASSAGE +
        "\n\nGive 6-8 distinct observations or readings, each 1-3 sentences. Number them. "
        "Prefer non-obvious noticings over generic praise.")

OUT = pathlib.Path("/home/claude/workspace/_scratch/genpipe/out/ecc_step1")
OUT.mkdir(parents=True, exist_ok=True)


def run_one(provider, candidates):
    key = os.environ.get(PROVIDER_KEY[provider])
    if not key:
        return {"provider": provider, "model": candidates[0], "error": "key missing"}
    msgs = [Message(role="system", content=SYSTEM), Message(role="user", content=USER)]
    last = None
    for model_id in candidates:
        cfg = LLMConfig(provider=provider, api_key=key, models={"default": model_id}, max_tokens=MAX_TOKENS)
        try:
            r = complete(msgs, cfg, ModelTier.DEFAULT, attribution="genpipe-ecc1", purpose="diverge")
            if r.content.strip():
                return {"provider": provider, "model": model_id, "content": r.content,
                        "in_tok": r.token_usage.input_tokens, "out_tok": r.token_usage.output_tokens}
            last = f"empty from {model_id}"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            print(f"  {model_id}: {last[:70]}, trying next", flush=True)
    return {"provider": provider, "model": candidates[0], "error": last or "all failed"}


def main():
    combined = ["# Ecclesiastes 1:2-11 (KJV) -- blind divergence (quality tier)\n",
                "Same prompt, three models, no context, no personas.\n"]
    for provider, candidates in MODELS:
        print(f"--- {provider} / {candidates} ---", flush=True)
        r = run_one(provider, candidates)
        if "error" in r:
            print("  ERROR:", r["error"], flush=True)
            combined.append(f"\n## {provider} / {candidates[0]}\n\n**ERROR:** {r['error']}\n")
            continue
        print(f"  ok {r['model']} ({r['in_tok']} in / {r['out_tok']} out)", flush=True)
        block = (f"\n## {provider} / {r['model']}\n\n_tokens: {r['in_tok']} in / {r['out_tok']} out_\n\n"
                 + r["content"] + "\n")
        combined.append(block)
        (OUT / f"{provider}.md").write_text(block, encoding="utf-8")
    (OUT / "results.md").write_text("\n".join(combined), encoding="utf-8")
    print("\nwrote", OUT / "results.md", flush=True)


if __name__ == "__main__":
    main()
