"""Refresh the embedded data snapshot in a hand-authored review.html.

The published ``review.html`` for each corpus is a hand-authored reading view
(the "continuous note stream" design) whose layout, CSS, JavaScript, and fonts
are maintained by hand. Only its embedded presentation snapshot -- the
``<script id="corpus-data">`` block produced by
``reference_corpus.review.build_review_model`` -- is regenerated after editorial
changes to the YAML records.

This helper validates the corpus, rebuilds that snapshot, and replaces the block
in place, leaving the surrounding design untouched. It never rewrites the whole
page, so (unlike ``reference-corpus-render``) it will not replace the
hand-authored view with the generated accordion layout.

Usage:
    python scripts/refresh-review.py corpora/<corpus-slug>/corpus.yaml
    python scripts/refresh-review.py <manifest> --review <path/to/review.html>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from reference_corpus.review import build_review_model, serialize_for_html  # noqa: E402
from reference_corpus.validate import CorpusValidator  # noqa: E402

_START_TAG = '<script id="corpus-data" type="application/json">'
_END_TAG = "</script>"


def refresh(manifest: Path, review: Path) -> int:
    diagnostics = CorpusValidator().validate_manifest(manifest)
    if diagnostics:
        for diagnostic in diagnostics:
            print(diagnostic.render(), file=sys.stderr)
        return 1

    data = serialize_for_html(build_review_model(manifest))
    html = review.read_text(encoding="utf-8")
    if html.count(_START_TAG) != 1:
        print(f"error: expected exactly one {_START_TAG} block in {review}", file=sys.stderr)
        return 2

    start = html.index(_START_TAG) + len(_START_TAG)
    end = html.index(_END_TAG, start)
    review.write_text(html[:start] + data + html[end:], encoding="utf-8", newline="\n")
    print(f"refreshed {review} ({len(data)} chars of embedded data)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path, help="Path to a corpus.yaml manifest")
    parser.add_argument(
        "--review",
        type=Path,
        default=None,
        help="Path to review.html (default: review.html beside the manifest)",
    )
    args = parser.parse_args(argv)
    manifest = args.manifest.resolve()
    review = (args.review or manifest.with_name("review.html")).resolve()
    if not review.is_file():
        print(f"error: {review} does not exist", file=sys.stderr)
        return 2
    return refresh(manifest, review)


if __name__ == "__main__":
    raise SystemExit(main())
