# Profiles

Each YAML file in this directory defines a **profile**: a named selection
and ordering of CV sections, optionally filtered. The site itself is
always built from `default.yaml`. Additional profiles produce alternate
CV PDFs (`site/cv-<name>.pdf`) on demand.

## Building

```sh
uv run python build.py --profile=academic --pdf   # → site/cv-academic.pdf
make pdf                                          # → all profiles
```

## Schema

```yaml
name: academic              # used in the output filename: cv-<name>.pdf
tagline: ...                # currently unused in templates; descriptive
sections:                   # output order = listed order; omit a section to drop it
  - id: education           # section id matches a file in data/<id>.yaml
  - id: career
  - id: publications
    filter:                 # optional, applied per section
      since: 2018
      tags_any: [cold-atoms, trapped-ions]
  - id: teaching
```

Section `id` must match a data file under `data/` (e.g. `id: publications`
reads `data/publications.yaml`). Missing data files for a listed section
result in an empty section in the output.

## Filter keys

All filters are optional; an entry passes if **all** declared keys
accept it.

| Key | Meaning |
|---|---|
| `since: <year>` | Keep entries whose effective year is ≥ N. Year is taken from the entry's `year`, `start`, `date`, or `end` field, whichever appears first. |
| `exclude_ids: [...]` | Drop entries whose `id` is in the list. Useful to suppress one-offs from an otherwise blanket section. |
| `tags_any: [...]` | Keep entries whose `tags:` field intersects the given list (set union). |
| `contribution_any: [...]` | Conference-section helper: keep entries whose `contribution` field is in the list (e.g. `[invited talk, talk]`). |

If a section has no filter, all of its entries pass through.

## Conventions

- Tag values are free-form strings in entries' `tags:` arrays. Pick consistent slugs
  (`cold-atoms`, `trapped-ions`, `integrated-photonics`, `padua`, `eth`, `trento`,
  `invited`, `organization`) and reuse them across profiles.
- `default.yaml` lists every section in the site order. Don't filter it — the
  site is meant to show everything.
- Treat profile YAML as the source of truth for CV variant output. The
  template files don't know about profiles; only `build.py`'s
  `resolve_profile` does.
