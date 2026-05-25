#!/usr/bin/env bash
# One-time WSL setup for `make pdf-wsl`.
# Installs uv (if missing) and the WeasyPrint system libraries.
# Idempotent — safe to re-run.

set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
    echo ">> installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # make uv available for the rest of this script
    if [ -f "$HOME/.local/bin/env" ]; then
        . "$HOME/.local/bin/env"
    else
        export PATH="$HOME/.local/bin:$PATH"
    fi
else
    echo ">> uv already installed ($(uv --version))"
fi

echo ">> installing WeasyPrint system libraries (sudo required)"
sudo apt-get update
sudo apt-get install -y \
    libpango-1.0-0 libpangoft2-1.0-0 \
    libharfbuzz0b libfontconfig1 libcairo2 \
    fonts-dejavu

echo ">> done. From Windows you can now run: make pdf-wsl"
