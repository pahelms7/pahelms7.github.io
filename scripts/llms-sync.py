#!/usr/bin/env python3
"""
Keep llms.txt in sync with the pages that actually exist on the site.

llms.txt is how AI assistants enumerate this site. A page missing from it is
invisible to them even when it ranks normally in Google. The file has no
generator and nothing used to validate it, so it drifted silently: on
2026-09-01 it was found 10 blog posts behind the live site, some of them
published three weeks earlier.

Usage:
    python3 scripts/llms-sync.py            # report drift, exit 1 if any
    python3 scripts/llms-sync.py --fix      # append the missing entries, then report

--fix scaffolds each entry from the page's own og:title and meta description,
both of which are already written and voice-checked. Read what it wrote before
committing: a meta description is aimed at a searcher, and the llms.txt line is
aimed at a model deciding whether the page answers a question. They are usually
close enough, but not always.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLMS = os.path.join(ROOT, "llms.txt")
DOMAIN = "https://helmsperformance.com"

# Pages deliberately left out of llms.txt.
#   /                deja described by the file's own header block
#   /privacy-policy/ legal boilerplate, nothing an assistant should cite
IGNORE = {"/", "/privacy-policy/"}

# Which section a new entry belongs in, longest prefix first.
SECTIONS = [
    ("/blog/",       "## Articles"),
    ("/services/",   "## Services"),
    ("/conditions/", "## Conditions Treated"),
]
DEFAULT_SECTION = "## About"


def indexable_pages():
    """Every real page on disk, as a site-root-relative URL path."""
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "scripts")]
        if "index.html" not in files:
            continue
        full = os.path.join(base, "index.html")
        with open(full, encoding="utf-8") as f:
            head = f.read(2000)
        if 'http-equiv="refresh"' in head:      # legacy WordPress redirect stub
            continue
        rel = os.path.relpath(base, ROOT)
        out.append("/" if rel == "." else f"/{rel}/")
    return sorted(out)


def listed_paths():
    with open(LLMS, encoding="utf-8") as f:
        text = f.read()
    found = set()
    for path in re.findall(re.escape(DOMAIN) + r"(/[A-Za-z0-9\-/]*)", text):
        found.add(path if path.endswith("/") else path + "/")
    return found


def page_meta(url_path):
    """Pull a title and one-line description from the page itself."""
    with open(os.path.join(ROOT, url_path.strip("/"), "index.html"), encoding="utf-8") as f:
        html = f.read()

    def grab(pattern):
        m = re.search(pattern, html, re.I)
        return m.group(1).strip() if m else ""

    title = (grab(r'<meta property="og:title" content="([^"]*)"')
             or grab(r"<title>([^<]*)</title>"))
    title = re.sub(r"\s*\|\s*Dr\. Helms\s*$", "", title)
    title = re.sub(r"\s*\|\s*Helms Performance\s*$", "", title)

    desc = (grab(r'<meta property="og:description" content="([^"]*)"')
            or grab(r'<meta name="description" content="([^"]*)"'))
    # first sentence only, so the line stays scannable
    first = re.split(r"(?<=[.!?])\s+", desc)[0] if desc else ""
    if first and not first.endswith((".", "!", "?")):
        first += "."
    return title, first


def entry_for(url_path):
    title, desc = page_meta(url_path)
    if not title:
        title = url_path.strip("/").split("/")[-1].replace("-", " ").title()
    line = f"- [{title}]({DOMAIN}{url_path})"
    return f"{line}: {desc}" if desc else line + ":"


def section_for(url_path):
    for prefix, section in SECTIONS:
        if url_path.startswith(prefix):
            return section
    return DEFAULT_SECTION


def insert(text, section, lines):
    """Append lines to the end of `section`, before the next '## ' header."""
    start = text.index(section) + len(section)
    nxt = text.find("\n## ", start)
    end = len(text) if nxt == -1 else nxt
    block = text[start:end].rstrip("\n")
    return text[:start] + block + "\n" + "\n".join(lines) + "\n" + text[end:]


def main():
    fix = "--fix" in sys.argv
    missing = [p for p in indexable_pages() if p not in listed_paths() and p not in IGNORE]

    if not missing:
        print(f"llms.txt is in sync ({len(indexable_pages())} pages on disk, none missing).")
        return 0

    if not fix:
        print(f"llms.txt is missing {len(missing)} page(s):")
        for m in missing:
            print(f"   {m}")
        print("\nRun:  python3 scripts/llms-sync.py --fix")
        return 1

    with open(LLMS, encoding="utf-8") as f:
        text = f.read()

    by_section = {}
    for path in missing:
        by_section.setdefault(section_for(path), []).append(entry_for(path))

    for section, lines in by_section.items():
        if section not in text:
            print(f"ERROR: section {section!r} not found in llms.txt; add it by hand.")
            return 2
        text = insert(text, section, lines)
        for line in lines:
            print(f"  + {section}: {line}")

    with open(LLMS, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nAdded {len(missing)} entry(ies). Read them before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
