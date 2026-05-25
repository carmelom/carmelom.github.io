#!/usr/bin/env python3
"""Build carmelom.github.io.

Usage:
    python build.py                       # default profile -> site/
    python build.py --profile academic    # builds cv-academic.pdf if --pdf
    python build.py --pdf                 # also generate PDF for current profile
    python build.py --all-profiles        # build PDFs for every profile in profiles/
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CONTENT = ROOT / "content"
PROFILES = ROOT / "profiles"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "site"


# ---------- data loading ---------------------------------------------------

def load_data() -> dict:
    return {
        p.stem: yaml.safe_load(p.read_text(encoding="utf-8"))
        for p in sorted(DATA.glob("*.yaml"))
    }


def load_content() -> dict:
    return {
        p.stem: p.read_text(encoding="utf-8")
        for p in sorted(CONTENT.glob("*.md"))
    }


def load_profile(name: str) -> dict:
    return yaml.safe_load((PROFILES / f"{name}.yaml").read_text(encoding="utf-8"))


# ---------- profile filtering ----------------------------------------------

def _year_of(entry: dict) -> int | None:
    if "year" in entry:
        return entry["year"]
    for key in ("start", "date", "end"):
        v = entry.get(key)
        if isinstance(v, str) and len(v) >= 4 and v[:4].isdigit():
            return int(v[:4])
        if hasattr(v, "year"):
            return v.year
    return None


def apply_filter(entries: list, flt: dict | None) -> list:
    if not flt or not isinstance(entries, list):
        return entries
    out = entries
    if "since" in flt:
        out = [e for e in out if (y := _year_of(e)) is not None and y >= flt["since"]]
    if "exclude_ids" in flt:
        skip = set(flt["exclude_ids"])
        out = [e for e in out if e.get("id") not in skip]
    if "tags_any" in flt:
        wanted = set(flt["tags_any"])
        out = [e for e in out if wanted & set(e.get("tags", []))]
    if "contribution_any" in flt:
        opts = set(flt["contribution_any"])
        out = [e for e in out if e.get("contribution") in opts]
    return out


def resolve_profile(profile: dict, data: dict) -> list:
    sections = []
    for spec in profile["sections"]:
        sid = spec["id"]
        entries = data.get(sid)
        if isinstance(entries, list):
            entries = apply_filter(entries, spec.get("filter"))
        sections.append({"id": sid, "entries": entries})
    return sections


# ---------- Jinja env ------------------------------------------------------

def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["markdown"] = lambda s: md.markdown(s, extensions=["extra"])
    env.filters["doi_url"] = lambda d: f"https://doi.org/{d}" if d else None
    env.filters["arxiv_url"] = lambda a: f"https://arxiv.org/abs/{a}" if a else None
    env.filters["join_authors"] = lambda authors: ", ".join(authors)
    return env


# ---------- static copy ----------------------------------------------------

def _copy_tree(src: Path, dst: Path) -> None:
    """Copy directory tree without preserving metadata.

    Avoids shutil.copytree's copystat() calls, which raise EPERM when
    running under WSL against /mnt/c (NTFS doesn't accept Linux-style
    chmod/utime). Plain content copy works on all platforms.
    """
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.rglob("*"):
        rel = entry.relative_to(src)
        target = dst / rel
        if entry.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry, target)


def copy_static() -> None:
    OUT.mkdir(exist_ok=True)
    if STATIC.exists():
        _copy_tree(STATIC, OUT)


# ---------- rendering ------------------------------------------------------

def render_site(env: Environment, data: dict, content: dict, profile: dict) -> None:
    sections = resolve_profile(profile, data)
    current = next(
        (c for c in data.get("career", []) if c.get("current")),
        None,
    )

    (OUT / "index.html").write_text(
        env.get_template("index.html").render(
            bio=content.get("bio", ""),
            current=current,
            profile=profile,
            page="home",
        ),
        encoding="utf-8",
    )

    (OUT / "cv").mkdir(exist_ok=True)
    (OUT / "cv" / "index.html").write_text(
        env.get_template("cv.html").render(
            sections=sections,
            data=data,
            profile=profile,
            page="cv",
        ),
        encoding="utf-8",
    )


def _site_url_fetcher(url, **kwargs):
    """Map root-relative `file:///foo` URLs into the built ``site/`` tree.

    WeasyPrint resolves ``<link href="/css/x.css">`` against the base URL's
    *host*, not its path — which for a filesystem base_url means filesystem
    root. This fetcher intercepts file:// URLs and re-roots them under OUT,
    while letting CDN (https://) URLs pass through to the default fetcher.
    """
    from urllib.parse import urlparse, unquote

    from weasyprint import default_url_fetcher

    parsed = urlparse(url)
    if parsed.scheme == "file":
        local = OUT / unquote(parsed.path).lstrip("/")
        if local.is_file():
            mime = {
                ".css": "text/css",
                ".woff2": "font/woff2",
                ".woff": "font/woff",
                ".svg": "image/svg+xml",
                ".png": "image/png",
                ".jpg": "image/jpeg",
            }.get(local.suffix.lower())
            return {"file_obj": local.open("rb"), "mime_type": mime}
    return default_url_fetcher(url, **kwargs)


def render_pdf(env: Environment, data: dict, profile: dict, out_path: Path) -> None:
    from weasyprint import HTML

    sections = resolve_profile(profile, data)
    html = env.get_template("cv.html").render(
        sections=sections,
        data=data,
        profile=profile,
        page="cv",
        for_pdf=True,
    )
    HTML(
        string=html,
        base_url=str(OUT),
        url_fetcher=_site_url_fetcher,
    ).write_pdf(str(out_path))


# ---------- public entry points --------------------------------------------

def build_site(profile_name: str = "default") -> None:
    """Build the HTML site into OUT. Used by build.py CLI and serve.py."""
    if OUT.exists():
        shutil.rmtree(OUT)
    copy_static()
    env = make_env()
    data = load_data()
    content = load_content()
    render_site(env, data, content, load_profile(profile_name))


def build_pdfs(profile_names: list[str]) -> list[Path]:
    """Render PDFs for the given profile names. Returns the output paths."""
    env = make_env()
    data = load_data()
    outputs = []
    for name in profile_names:
        prof = load_profile(name)
        suffix = "" if name == "default" else f"-{name}"
        out_path = OUT / f"cv{suffix}.pdf"
        render_pdf(env, data, prof, out_path)
        outputs.append(out_path)
    return outputs


# ---------- main -----------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="default")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument(
        "--all-profiles",
        action="store_true",
        help="Build PDFs for every profiles/*.yaml",
    )
    args = ap.parse_args()

    build_site("default")
    print("  built site/  (profile: default)")

    if args.pdf or args.all_profiles:
        names = (
            [p.stem for p in sorted(PROFILES.glob("*.yaml"))]
            if args.all_profiles
            else [args.profile]
        )
        for out_path in build_pdfs(names):
            print(f"  built {out_path.name}")


if __name__ == "__main__":
    main()
