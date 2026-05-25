.PHONY: install build serve pdf pdf-wsl setup-wsl clean

install:
	uv sync

build:
	uv run python build.py

# Build all profile PDFs locally (Linux/macOS — WeasyPrint's C deps must be
# installed system-wide; on Debian/Ubuntu: libpango-1.0-0 libpangoft2-1.0-0
# libharfbuzz0b libfontconfig1 libcairo2 fonts-dejavu).
pdf:
	uv run python build.py --all-profiles

# Windows path: build PDFs inside WSL. The venv lives in the WSL home
# (ext4) because creating a Linux venv on /mnt/c (NTFS) fails on some
# file operations. The source repo stays on /mnt/c so editing on Windows
# keeps working as usual.
# bash -lc => login shell so ~/.profile is sourced and uv's ~/.local/bin is on PATH.
pdf-wsl:
	wsl bash -lc 'export UV_PROJECT_ENVIRONMENT=$$HOME/.venvs/carmelom-site && uv sync && uv run python build.py --all-profiles'

# One-time WSL bootstrap: install uv + WeasyPrint apt deps. Will prompt for sudo.
setup-wsl:
	wsl bash -l scripts/setup-wsl.sh

# Auto-reloading dev server at http://localhost:9997.
serve:
	uv run python serve.py

clean:
	rm -rf site
