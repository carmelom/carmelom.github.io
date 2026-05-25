# Working conventions for AI assistants

## Visual verification: ask, don't Playwright

For small CSS / spacing / color tweaks: make the edit, rebuild, and **ask the user to refresh their browser and confirm** — don't spin up Playwright. The user keeps the dev site open in their normal browser and can eyeball a tweak in seconds.

Reserve Playwright for:
- Initial-render debugging
- Capturing states the user can't easily reach (e.g. dark mode in a Playwright Chromium that doesn't inherit OS theme)
- Running interaction sequences a human would find tedious

Default phrasing after a tweak: *"Built — give it a refresh and tell me if it looks right."*

## Playwright artifacts go in `.playwright-mcp/`

When calling `mcp__playwright__browser_take_screenshot` (or any Playwright tool that writes a file via a `filename` argument), prefix the path with `.playwright-mcp/` — never write screenshots or snapshot files to the project root. `.playwright-mcp/` is gitignored and is already where the MCP server stores its own logs.

## PDF inspection via `Read`

The `Read` tool opens PDF files directly (one image per page) **as long as poppler-utils is on PATH**:

- Linux: `apt install poppler-utils`
- macOS: `brew install poppler`
- Windows: `scoop install poppler`

Pass `pages: "1"` (or a range up to 20) to limit output. If `Read site/cv.pdf` errors with `pdftoppm not found`, ask the user to install poppler for their OS — do not work around it with raw Python conversions.

## Permissions

`mcp__playwright__*`, `Bash(python build.py)`, and `Bash(make pdf-wsl *)` are auto-allowed via `.claude/settings.json` (committed, shared). If a new project-wide permission is needed for routine work, add it to `settings.json` so it travels with the repo. Reserve `.claude/settings.local.json` (gitignored — create on demand) for per-machine overrides only.
