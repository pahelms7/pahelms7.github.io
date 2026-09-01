# helmsperformance.com

Static site for Helms Performance — sports chiropractic and physical therapy in Bethesda, MD.
Hosted on GitHub Pages with a custom domain.

## Stack
- Plain HTML / CSS / JS (no build step)
- GitHub Pages hosting
- Custom domain: helmsperformance.com

## Local preview
```bash
python3 -m http.server 8000
```
Visit http://localhost:8000

## Deploying changes
```bash
git add <changed-files>
git commit -m "describe the change"
git push
```
GitHub Pages redeploys automatically (~1 minute).

## Adding a new page
1. Create a folder with an `index.html` inside (e.g. `services/new-service/index.html`)
2. Add `<head>` tags: description, robots, canonical, Open Graph
3. Add a `<url>` entry to `sitemap.xml`
4. Link from the parent page (`/services/`)

## URL conventions
- Filenames: lowercase, hyphens (`back-pain`, not `Back_Pain`)
- Internal links: root-relative (`/assets/images/services/photo.webp`)
- Never use absolute URLs to helmsperformance.com inside the HTML — breaks local preview and the github.io staging URL

## Folder structure
```
/                          Home page, 404, robots.txt, sitemap.xml
/about/                    About Dr. Helms
/contact/                  Contact & booking
/blog/                     Blog index
/services/                 Services overview
/services/<slug>/          Individual service pages
/conditions/               Conditions overview
/conditions/<slug>/        Individual condition pages
/assets/images/services/   Service page images
/assets/images/conditions/ Condition page images
/assets/images/misc/       General photos (Dr. Helms, clinic)
```

## DNS
DNS is managed at the domain registrar. Do NOT modify MX, SPF, DKIM, or DMARC records — those handle email delivery.

## llms.txt is enforced, not remembered

`llms.txt` is how AI assistants enumerate this site. A page missing from it is invisible to them
even when it ranks normally in Google. It has no generator, so it used to drift silently: on
2026-09-01 it was found 10 blog posts behind, some published three weeks earlier.

Three layers now keep it honest, all calling the same script:

| Layer | When it runs | What it does |
|---|---|---|
| `scripts/llms-sync.py` | on demand | reports drift; `--fix` scaffolds the missing entries |
| `seo-audit` Check 9 | every site change | **errors** on any live page missing from llms.txt |
| `scripts/pre-commit` hook | every commit touching a page | **blocks** the commit |

Install the hook once per clone (git does not version `.git/hooks`):

```bash
cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

Bypass with `git commit --no-verify` when a page is deliberately unlisted. Deliberate omissions
belong in `IGNORE` at the top of `scripts/llms-sync.py`, which currently holds `/` (covered by the
file's header) and `/privacy-policy/`.
