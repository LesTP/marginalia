"""Step 3: Stage 3 argue -- period-persona friction on Donne's compass conceit.

Two reconstructed period stances, each on a DIFFERENT strong model (so neither is
one model ventriloquizing both), contest the stanza and the standout readings from
the divergence runs. Opening (blind) + one rebuttal round, then a neutral observer
names what the clash surfaced and flags any confabulation.

Personas are a GENERATION device, not a provenance claim: no invented quotations,
critics, or sources; the text is the evidence.

  /home/claude/workspace/diplomat/.venv/bin/python \
    /home/claude/workspace/_scratch/genpipe/step3_argue.py
"""
from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv

from toolkit.llm_client import LLMConfig, Message, ModelTier, complete

load_dotenv("/home/claude/workspace/diplomat/.env")

PROVIDER_KEY = {
    "openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY", "openrouter": "OPENROUTER_API_KEY",
}
A_MODEL = ("anthropic", "claude-opus-4-6")   # wit / strong-lines admirer
B_MODEL = ("openai", "gpt-5.5")               # plain-style objector
OBS_MODEL = ("google", "gemini-2.5-pro")      # neutral observer

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

READINGS = """Readings already on the table (from earlier close readings):
R1. The compass simile is a concession, not an assertion: "If they be two" concedes
    that separation may be real, so the famous image is really a fallback position
    after the claim that the souls are already one.
R2. "End where I begun" yields no progress, only form -- a quietly melancholic note
    beneath the reassurance: the roaming amounts to the shape of fidelity and nothing
    gained.
R3. "Hearkens" makes the fixed foot listen rather than watch -- attention, not
    surveillance.
R4. "Grows erect, as that comes home" fuses geometric closure and erotic reunion in
    one phrase.
R5. "Just" means both geometrically exact and morally right."""

HONESTY = (
    " Rules: argue about what is on the page; the text is your evidence. Do NOT invent "
    "quotations, critics, dates, or sources, and do not impersonate or quote any real "
    "person. Argue the position in your own voice. Be specific and concrete."
)
A_SYS = ("You hold the 'strong lines' taste of Donne's own circle: you prize wit, the "
         "daring conceit, intellectual compression, and argument made to feel like "
         "passion. You think the compass conceit is a triumph -- thought made into "
         "feeling." + HONESTY)
B_SYS = ("You hold the plain-style taste: you distrust far-fetched conceits and value "
         "decorum, clarity, and feeling that is not strained through geometry. You "
         "suspect the compass conceit is frigid or indecorous -- wit displacing grief "
         "at a parting." + HONESTY)
OBS_SYS = ("You are a neutral editor observing a disagreement between two readers of a "
           "poem. Report plainly; take no side.")


def call(model, system, user, max_tokens=4000, name=None):
    """Cached, empty-resilient single turn. Caches to OUT/<name>.md so re-runs skip
    turns that already succeeded; retries at a larger budget if a reasoning model
    returns empty."""
    if name:
        f = OUT / f"{name}.md"
        if f.exists() and f.read_text(encoding="utf-8").strip():
            print(f"  [cached] {name}", flush=True)
            return f.read_text(encoding="utf-8")
    provider, model_id = model
    msgs = [Message(role="system", content=system), Message(role="user", content=user)]
    last = None
    for mt in (max_tokens, max_tokens * 2):
        cfg = LLMConfig(provider=provider, api_key=os.environ[PROVIDER_KEY[provider]],
                        models={"default": model_id}, max_tokens=mt)
        try:
            r = complete(msgs, cfg, ModelTier.DEFAULT, attribution="genpipe-step3",
                         purpose="argue")
            if r.content.strip():
                if name:
                    (OUT / f"{name}.md").write_text(r.content, encoding="utf-8")
                return r.content
            last = "empty content"
            print(f"  {name or model_id}: empty at {mt}, retrying", flush=True)
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            print(f"  {name or model_id}: {last[:70]} at {mt}, retrying", flush=True)
    raise RuntimeError(f"{name or model_id} failed: {last}")


CONTEXT = f"Passage (John Donne):\n\n{PASSAGE}\n\n{READINGS}\n\n"
OPEN = CONTEXT + ("Give your opening reading of this stanza from your stance (4-6 "
                  "points). Engage the readings on the table where they bear on your view.")

OUT = pathlib.Path("/home/claude/workspace/_scratch/genpipe/out/step3")
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("A opening (wit/opus)...", flush=True)
    a1 = call(A_MODEL, A_SYS, OPEN, name="a1")
    print("B opening (plain/gpt-5.5)...", flush=True)
    b1 = call(B_MODEL, B_SYS, OPEN, name="b1")

    print("A rebuttal...", flush=True)
    a2 = call(A_MODEL, A_SYS, CONTEXT + "Your interlocutor (plain-style) argued:\n\n"
              + b1 + "\n\nRespond: where are they right, where wrong, and what does the "
              "clash reveal about the stanza? Concede where fair; stay on the text.",
              name="a2")
    print("B rebuttal...", flush=True)
    b2 = call(B_MODEL, B_SYS, CONTEXT + "Your interlocutor (strong-lines) argued:\n\n"
              + a1 + "\n\nRespond: where are they right, where wrong, and what does the "
              "clash reveal about the stanza? Concede where fair; stay on the text.",
              name="b2")

    print("Observer synthesis (gemini-pro)...", flush=True)
    obs = call(OBS_MODEL, OBS_SYS,
               f"Passage:\n\n{PASSAGE}\n\nStrong-lines opening:\n{a1}\n\n"
               f"Plain-style opening:\n{b1}\n\nStrong-lines rebuttal:\n{a2}\n\n"
               f"Plain-style rebuttal:\n{b2}\n\n"
               "Report, in three numbered sections: (1) the genuine points of "
               "disagreement; (2) any NEW readings this exchange produced that are NOT "
               "already in the five readings on the table above or in the openings; "
               "(3) any statement that looks like an invented quotation, critic, date, "
               "or source (flag for verification), or 'none'.", max_tokens=6000, name="obs")

    transcript = (
        "# Step 3 -- period-persona argue on Donne's compass conceit\n\n"
        f"A = strong-lines/wit ({A_MODEL[1]})  |  B = plain-style ({B_MODEL[1]})  |  "
        f"observer = {OBS_MODEL[1]}\n\n"
        "## A opening (strong-lines)\n\n" + a1 + "\n\n"
        "## B opening (plain-style)\n\n" + b1 + "\n\n"
        "## A rebuttal\n\n" + a2 + "\n\n"
        "## B rebuttal\n\n" + b2 + "\n\n"
        "## Observer synthesis\n\n" + obs + "\n"
    )
    (OUT / "transcript.md").write_text(transcript, encoding="utf-8")
    print("\nwrote", OUT / "transcript.md", flush=True)


if __name__ == "__main__":
    main()
