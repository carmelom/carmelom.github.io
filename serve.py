#!/usr/bin/env python3
"""Dev server: build, serve, watch, auto-reload.

Replaces browser-sync. Uses livereload (Python + Tornado) to:
  - serve site/ at http://localhost:9997
  - watch source dirs and rebuild on change
  - inject a tiny JS snippet that auto-refreshes the browser
"""

from __future__ import annotations

from livereload import Server

from build import OUT, build_site


def rebuild() -> None:
    build_site()
    print("  rebuilt site/")


def main() -> None:
    build_site()
    server = Server()
    watch_paths = [
        "templates/*.html",
        "templates/partials/*.html",
        "data/*.yaml",
        "content/*.md",
        "content/**/*.md",
        "profiles/*.yaml",
        "static/**/*",
        "build.py",
    ]
    for path in watch_paths:
        server.watch(path, rebuild, delay=0.2)

    server.serve(root=str(OUT), host="localhost", port=9997, open_url_delay=None)


if __name__ == "__main__":
    main()
