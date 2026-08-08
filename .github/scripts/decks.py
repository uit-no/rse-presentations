#!/usr/bin/env python3
"""Helpers for the slides CI: discover decks, validate assets, build the index page.

A deck is any top-level .md file starting with a cicero header block:

    <!-- cicero
    engine: remark
    js:
      - https://.../remark.min.js
    css:
      - slides.css
    -->
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CICERO = "https://cicero.pages.dev/github"


def parse_header(text):
    """Return the cicero header as {'engine': str, 'js': [...], 'css': [...]}, or None."""
    if not text.startswith("<!-- cicero"):
        return None
    end = text.find("-->")
    if end == -1:
        return None

    header = {"engine": None, "js": [], "css": []}
    key = None
    for line in text[len("<!-- cicero"):end].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if key in ("js", "css"):
                header[key].append(stripped[2:].strip())
        elif ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if key == "engine":
                header["engine"] = value
            elif key in ("js", "css") and value:
                header[key].append(value)
    return header


def title_of(text, fallback):
    """First markdown heading, used as the deck title on the index page."""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            # unwrap [text](url) links, which would otherwise show as raw markdown
            return re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", title)
    return fallback


def decks():
    """All decks, sorted by filename."""
    found = []
    for path in sorted(ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        header = parse_header(text)
        if header:
            found.append((path, header, title_of(text, path.stem)))
    return found


def cmd_list():
    """Print one deck filename per line, for the decktape loop in the workflow."""
    for path, _, _ in decks():
        print(path.name)


def cmd_check():
    """Fail if a deck declares a local asset that is not in the repo.

    decktape renders a deck with a missing stylesheet without complaining, so
    without this a broken css reference produces an unstyled PDF and a green CI run.
    """
    problems = []
    for path, header, _ in decks():
        if header["engine"] != "remark":
            print(f"note: {path.name} uses engine '{header['engine']}'")
        for asset in header["css"] + header["js"]:
            if asset.startswith(("http://", "https://", "//")):
                continue
            if not (ROOT / asset).is_file():
                problems.append(f"{path.name}: declares '{asset}', which does not exist")

    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"ok: {len(decks())} decks, all local assets present")
    return 0


def cmd_index(out_dir, repo, ref):
    """Write index.html listing every deck, linking to cicero and to the built PDF."""
    rows = []
    for path, _, title in decks():
        slides_url = f"{CICERO}/{repo}/{ref}/{path.name}/"
        rows.append(
            "    <li>\n"
            f"      <span class=\"title\">{html.escape(title)}</span>\n"
            f"      <span class=\"file\">{html.escape(path.name)}</span>\n"
            "      <span class=\"links\">"
            f"<a href=\"{html.escape(slides_url)}\">slides</a>"
            f"<a href=\"pdf/{path.stem}.pdf\">PDF</a></span>\n"
            "    </li>"
        )

    page = PAGE_TEMPLATE.replace("{{ROWS}}", "\n".join(rows)).replace(
        "{{REPO}}", html.escape(repo)
    )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {out / 'index.html'} with {len(rows)} decks")
    return 0


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RSE group presentations</title>
<style>
  :root { --ink: #222; --purple: #71137d; --muted: #666; --line: #e4e4e8; --bg: #fff; }
  @media (prefers-color-scheme: dark) {
    :root { --ink: #eee; --purple: #d9a6e0; --muted: #999; --line: #333; --bg: #16151a; }
  }
  body {
    margin: 0 auto; padding: 3rem 1.5rem; max-width: 46rem;
    font-family: system-ui, sans-serif; line-height: 1.5;
    color: var(--ink); background: var(--bg);
  }
  h1 { color: var(--purple); font-size: 1.9rem; margin: 0 0 .3rem; }
  p.lead { color: var(--muted); margin: 0 0 2.5rem; }
  ul { list-style: none; margin: 0; padding: 0; }
  li {
    display: flex; flex-wrap: wrap; gap: .25rem 1rem; align-items: baseline;
    padding: .9rem 0; border-top: 1px solid var(--line);
  }
  .title { flex: 1 1 16rem; font-weight: 600; }
  .file { color: var(--muted); font-family: ui-monospace, monospace; font-size: .85rem; }
  .links { display: flex; gap: .75rem; }
  .links a {
    color: var(--purple); text-decoration: none;
    border: 1px solid var(--line); border-radius: 999px; padding: .15rem .8rem;
    font-size: .9rem;
  }
  .links a:hover { border-color: var(--purple); }
  footer { margin-top: 3rem; color: var(--muted); font-size: .85rem; }
  footer a { color: inherit; }
</style>
</head>
<body>
  <h1>RSE group presentations</h1>
  <p class="lead">Slides are rendered by cicero. PDFs are rebuilt on every push to main.</p>
  <ul>
{{ROWS}}
  </ul>
  <footer>
    Source: <a href="https://github.com/{{REPO}}">github.com/{{REPO}}</a>
  </footer>
</body>
</html>
"""


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    if args[0] == "list":
        return cmd_list()
    if args[0] == "check":
        return cmd_check()
    if args[0] == "index":
        return cmd_index(args[1], args[2], args[3])
    print(f"unknown command: {args[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main() or 0)
