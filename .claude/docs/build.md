# Build pipeline

Jinja2 + YAML/Markdown → static site under `site/`; the same `cv.html` template is rendered to PDF by WeasyPrint.

## Commands

| Goal | Command | Notes |
|---|---|---|
| Build site (HTML only) | `python build.py` | Outputs into `site/` |
| Build a single CV PDF | `make pdf-wsl` | Shells into WSL; uses uv venv at `$HOME/.venvs/carmelom-site` |
| Build all profile PDFs | `make pdf-wsl` | Already runs `--all-profiles`; each `profiles/*.yaml` → `site/cv-<name>.pdf` |

### Why not direct WeasyPrint on Windows

`python build.py --pdf` from PowerShell fails with `OSError: cannot load library 'libgobject-2.0-0'` — WeasyPrint's GTK/Pango deps live only inside WSL. Always use `make pdf-wsl` on Windows.

## Asset sources

External CSS + fonts are loaded from jsDelivr (no local vendoring, no submodules):

- Font Awesome 4.7 — `https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/...`
- Academicons 1 — `https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/...`
- IBM Plex (Sans / Mono / Serif) — `https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-*@5/files/...`

## WeasyPrint URL fetcher

`build.py` ships a small `_site_url_fetcher` so WeasyPrint correctly resolves the root-relative `/css/*`, `/fonts/*`, `/favicon.svg` paths in the rendered HTML against the `site/` directory. Without it, WeasyPrint treats `/css/foo` as filesystem-absolute and silently falls back to DejaVu — the kind of failure that's invisible until you inspect the embedded fonts of the PDF.
