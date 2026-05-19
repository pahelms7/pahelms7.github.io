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
