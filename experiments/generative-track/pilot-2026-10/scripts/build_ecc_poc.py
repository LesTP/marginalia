"""Build a quick, self-contained POC review page from the Ecclesiastes stage-1
divergence output. Not a corpus record -- a preview for human review of the raw
generated notes against the text. Reads results.md, emits poc.html.

  set PYTHONIOENCODING=utf-8
  python p:\\shared\\_scratch\\genpipe\\build_ecc_poc.py
"""
from __future__ import annotations

import html
import pathlib
import re

OUT = pathlib.Path(r"p:\shared\_scratch\genpipe\out\ecc_step1")
RESULTS = OUT / "results.md"
DEST = OUT / "poc.html"

PASSAGE = [
    ("2", "Vanity of vanities, saith the Preacher, vanity of vanities; all is vanity."),
    ("3", "What profit hath a man of all his labour which he taketh under the sun?"),
    ("4", "One generation passeth away, and another generation cometh: but the earth abideth for ever."),
    ("5", "The sun also ariseth, and the sun goeth down, and hasteth to his place where he arose."),
    ("6", "The wind goeth toward the south, and turneth about unto the north; it whirleth about "
          "continually, and the wind returneth again according to his circuits."),
    ("7", "All the rivers run into the sea; yet the sea is not full; unto the place from whence "
          "the rivers come, thither they return again."),
    ("8", "All things are full of labour; man cannot utter it: the eye is not satisfied with "
          "seeing, nor the ear filled with hearing."),
    ("9", "The thing that hath been, it is that which shall be; and that which is done is that "
          "which shall be done: and there is no new thing under the sun."),
    ("10", "Is there any thing whereof it may be said, See, this is new? it hath been already of "
           "old time, which was before us."),
    ("11", "There is no remembrance of former things; neither shall there be any remembrance of "
           "things that are to come with those that shall come after."),
]

MODEL_LABELS = {
    "openai": "GPT-5.5",
    "anthropic": "Claude Opus",
    "google": "Gemini 2.5 Pro",
}


def md_inline(text: str) -> str:
    """Escape, then convert **bold** and *italic* to HTML."""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    return t


def parse_results(md: str):
    """Return list of (model_key, [note_html, ...])."""
    blocks = []
    cur_key, cur_lines = None, []
    items: list[str] = []

    def flush_item():
        if cur_lines:
            joined = " ".join(l.strip() for l in cur_lines if l.strip())
            joined = re.sub(r"^\d+[.)]\s*", "", joined)
            if joined:
                items.append(md_inline(joined))
            cur_lines.clear()

    def flush_block():
        flush_item()
        if cur_key and items:
            blocks.append((cur_key, list(items)))
        items.clear()

    for line in md.splitlines():
        m = re.match(r"^##\s+(\w+)\s*/", line)
        if m:
            flush_block()
            cur_key = m.group(1)
            continue
        if cur_key is None:
            continue
        if re.match(r"^\s*\d+[.)]\s", line):   # new numbered item
            flush_item()
            cur_lines.append(line)
        elif re.match(r"^_tokens", line) or not line.strip():
            flush_item()
        else:
            cur_lines.append(line)
    flush_block()
    return blocks


def main():
    blocks = parse_results(RESULTS.read_text(encoding="utf-8"))

    verses = "\n".join(
        f'<p class="v"><span class="n">{n}</span> {html.escape(t)}</p>' for n, t in PASSAGE
    )
    note_sections = []
    for key, notes in blocks:
        label = MODEL_LABELS.get(key, key)
        cards = "\n".join(
            f'<li class="note"><span class="src">{html.escape(label)}</span>{n}</li>'
            for n in notes
        )
        note_sections.append(
            f'<section class="model"><h3>{html.escape(label)} '
            f'<span class="count">({len(notes)} observations)</span></h3>'
            f'<ol class="notes">{cards}</ol></section>'
        )

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ecclesiastes 1:2-11 - generative POC</title>
<style>
  :root {{ --paper:#F3EEE3; --ink:#1B1917; --violet:#4A3560; --rule:#d8cfbe; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font-family:"EB Garamond",Georgia,"Times New Roman",serif; line-height:1.5; }}
  .wrap {{ max-width:860px; margin:0 auto; padding:2.5rem 1.4rem 5rem; }}
  .tag {{ display:inline-block; font-family:"Courier Prime",monospace; font-size:.72rem;
    letter-spacing:.04em; text-transform:uppercase; color:var(--violet);
    border:1px solid var(--violet); border-radius:3px; padding:.12rem .45rem; }}
  h1 {{ font-variant:small-caps; letter-spacing:.03em; font-weight:400;
    font-size:2rem; margin:.6rem 0 .2rem; }}
  .caveat {{ background:#ece3d2; border-left:3px solid var(--violet); padding:.7rem 1rem;
    font-size:.9rem; margin:1.2rem 0 2rem; }}
  .passage {{ border-top:1px solid var(--rule); border-bottom:1px solid var(--rule);
    padding:1.4rem 0; margin-bottom:2rem; }}
  .passage .v {{ margin:.15rem 0; text-indent:-1.4rem; padding-left:1.4rem; }}
  .passage .n {{ font-family:"Courier Prime",monospace; font-size:.7rem; color:var(--violet);
    vertical-align:super; margin-right:.3rem; }}
  h2 {{ font-variant:small-caps; letter-spacing:.03em; font-weight:400; font-size:1.3rem;
    border-bottom:1px solid var(--rule); padding-bottom:.3rem; margin-top:2.5rem; }}
  .model h3 {{ font-weight:400; font-size:1.1rem; margin:1.8rem 0 .5rem; color:var(--violet); }}
  .model h3 .count {{ color:#9a8f7a; font-size:.85rem; }}
  ol.notes {{ list-style:none; margin:0; padding:0; }}
  li.note {{ border:1px solid var(--rule); border-radius:5px; background:#fbf7ef;
    padding:.8rem 1rem; margin:.6rem 0; position:relative; }}
  li.note .src {{ display:block; font-family:"Courier Prime",monospace; font-size:.68rem;
    text-transform:uppercase; letter-spacing:.05em; color:#9a8f7a; margin-bottom:.35rem; }}
  em {{ font-style:italic; }}
  footer {{ margin-top:3rem; padding-top:1rem; border-top:1px solid var(--rule);
    font-size:.82rem; color:#7c7465; }}
</style></head>
<body><div class="wrap">
  <span class="tag">Generative track - POC - unreviewed</span>
  <h1>Ecclesiastes 1:2-11</h1>
  <div class="caveat">
    <strong>Draft preview, not an edition.</strong> These are raw <em>stage-1 blind
    divergence</em> observations from three models (no context, no personas, no
    verification). They have not been dispositioned, sourced, fact-checked, or
    human-reviewed. Several claims about the Hebrew (e.g. <em>hevel</em>, <em>yitron</em>,
    the distribution of "under the sun") are plausible but <strong>must be verified in
    stage 6</strong> before any could be published. Base text: King James Version
    (public domain).
  </div>

  <h2>The passage</h2>
  <div class="passage">{verses}</div>

  <h2>Generated observations</h2>
  {''.join(note_sections)}

  <footer>
    Base text: KJV (public domain). Observations generated {len(blocks)} models x stage-1
    divergence; see <code>_scratch/genpipe/ecc_step1.py</code>. Self-contained, no network.
  </footer>
</div></body></html>"""

    DEST.write_text(doc, encoding="utf-8")
    total = sum(len(n) for _, n in blocks)
    print(f"wrote {DEST}  ({len(blocks)} models, {total} notes)")


if __name__ == "__main__":
    main()
