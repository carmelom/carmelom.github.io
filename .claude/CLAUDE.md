# carmelom.github.io

Personal/professional site + printable CV. Jinja2 + YAML/Markdown → `site/`; WeasyPrint renders the same `cv.html` to PDF.

## Project memory

`.claude/CLAUDE.md` (this file) and anything under `.claude/docs/` are the project's persistent memory for AI assistants. They travel with the repo. Keep CLAUDE.md short — a pointer index — and put detailed notes in focused docs under `.claude/docs/`.

When you (the AI) learn something durably useful about this project (a build quirk, a tool that needs special handling, a user preference about how to work), add it to the relevant doc under `.claude/docs/` or create a new one and link it from here. Per-host, per-user state (auth tokens, throwaway local notes) does not belong here.

## Quick reference

- Build site: `python build.py` → `site/`
- Build PDFs: `make pdf-wsl` (shells into WSL — required on Windows)

## Docs

- [`docs/build.md`](docs/build.md) — build commands, asset sources, WeasyPrint URL-fetcher detail
- [`docs/conventions.md`](docs/conventions.md) — working conventions for AI assistants (visual verification, Playwright artifacts, PDF inspection, permissions)
