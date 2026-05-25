# Build pipeline

Jinja2 + YAML/Markdown → static site under `site/`; the same `cv.html` template is rendered to PDF by WeasyPrint.

## Commands

**Always use the Makefile** — assume `make` and `uv` are present and let `make` handle the venv (`uv sync`) + python invocation. Don't call `python build.py` or `uv run python ...` directly; if you find yourself reaching for raw Python, add a Make target instead.

Some targets depend on the host OS. WeasyPrint needs GTK/Pango C libraries that are easy to install on Linux/macOS but painful on Windows, hence the WSL split for the PDF target.

| Goal | Linux / macOS | Windows |
|---|---|---|
| Build site (HTML only) | `make build` | same |
| Build all profile PDFs | `make pdf` | `make pdf-wsl` |
| One-time PDF env bootstrap | install GTK / poppler via apt or brew | `make setup-wsl` (one-time, prompts for sudo inside WSL) |
| Dev server (auto-reload) | `make serve` | same |
| Clean output | `make clean` | same |

### Why the PDF target splits by OS

`make pdf` runs WeasyPrint in the local uv venv; on Windows from PowerShell that fails with `OSError: cannot load library 'libgobject-2.0-0'` because WeasyPrint's GTK/Pango deps are not installed on the Windows host. `make pdf-wsl` shells into WSL, uses a Linux uv venv at `$HOME/.venvs/carmelom-site` (kept on ext4, not `/mnt/c`, because `uv` operations on NTFS-via-WSL fail at certain file steps), and runs the same `build.py --all-profiles`. Source files stay on `/mnt/c/...` so the Windows editor experience is unchanged.

The `make pdf-wsl` target shells into WSL, uses a Linux uv venv at `$HOME/.venvs/carmelom-site` (kept on ext4, not `/mnt/c`, because `uv` operations on NTFS-via-WSL fail at certain file steps), and runs `build.py --all-profiles`. Source files stay on `/mnt/c/...` so the Windows editor experience is unchanged.

## Asset sources

External CSS + fonts are loaded from jsDelivr (no local vendoring, no submodules):

- Font Awesome 4.7 — `https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/...`
- Academicons 1 — `https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/...`
- IBM Plex (Sans / Mono / Serif) — `https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-*@5/files/...`

## WeasyPrint URL fetcher

`build.py` ships a small `_site_url_fetcher` so WeasyPrint correctly resolves the root-relative `/css/*`, `/fonts/*`, `/favicon.svg` paths in the rendered HTML against the `site/` directory. Without it, WeasyPrint treats `/css/foo` as filesystem-absolute and silently falls back to DejaVu — the kind of failure that's invisible until you inspect the embedded fonts of the PDF.
