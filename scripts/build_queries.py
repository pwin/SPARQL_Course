#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write queries/**/*.rq from the catalogue, plus a per-module README."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json

import querycat
from querycat import CATALOGUE, MODULE_INFO, QUERIES
import specs

# Importing these registers their queries with the catalogue.
import queries_core          # noqa: F401
try:
    import queries_paths     # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_geo       # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_rdf12     # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_forms     # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_debug     # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_extensions  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_federation  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_blanknodes  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_update  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_toolkit  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import queries_inference  # noqa: F401
except ModuleNotFoundError:
    pass


def load_measured_counts() -> None:
    """Fold the cross-engine row counts into each header, so a reader knows
    what the query should return before running it.  Written by
    check_queries.py; absent on a first build, which is fine."""
    path = QUERIES.parent / "build" / "results.json"
    if not path.exists():
        return
    measured = json.loads(path.read_text(encoding="utf-8"))
    for item in CATALOGUE:
        got = measured.get(item.qid, {})
        counts = {v["rows"] for v in got.values() if v.get("ok")}
        if len(counts) == 1:
            n = counts.pop()
            item.expect = f"{n} row{'' if n == 1 else 's'}, on every engine that runs it"
        elif counts:
            item.expect = ", ".join(
                f"{k} {v['rows']}" for k, v in sorted(got.items()) if v.get("ok")
            ) + "  (see the note above)"


# Modules whose folder holds hand-written material as well as generated
# queries.  The build must not remove these.
EXTRA_READING = {
    "13-planning-and-debugging": [
        ("PLANS.md", "Getting the plan out of each engine, and the debugging "
                     "playbook"),
    ],
}


def main() -> None:
    load_measured_counts()
    QUERIES.mkdir(parents=True, exist_ok=True)
    # Remove only what this script generates.  queries/00-the-lab/README.md and
    # queries/13-planning-and-debugging/PLANS.md are written by hand, and an
    # earlier version of this function deleted them by removing the whole tree.
    for pattern in ("*/*.rq", "*/*.ru"):
        for stale in QUERIES.glob(pattern):
            stale.unlink()

    grouped: dict[str, list] = {}
    for item in CATALOGUE:
        grouped.setdefault(item.module, []).append(item)
    # By module number, not by the order the query files happened to import.
    by_module = dict(sorted(grouped.items(), key=lambda kv: kv[0]))

    for module, items in by_module.items():
        folder = QUERIES / module
        folder.mkdir(parents=True, exist_ok=True)
        title, blurb = MODULE_INFO[module]
        num = module.split("-", 1)[0]
        lines = [f"# Module {num} · {title}", "", blurb, "",
                 "Each `.rq` file carries its own explanation: what it asks, how it "
                 "works, a diagram of the mechanism, and what to take away. Read the "
                 "header before running the query.", ""]
        for extra, why in EXTRA_READING.get(module, []):
            lines += [f"**Read first: [{extra}]({extra})** — {why}.", ""]
        sections = specs.MODULE_SPECS.get(module, [])
        if sections:
            lines += ["**In the standards.** The sections this module is "
                      "defined by:", ""]
            lines += [f"- [{label}]({url})" for label, url in sections]
            lines += [""]
        lines += ["| Query | Asks |", "|---|---|"]
        for item in sorted(items, key=lambda i: i.sort_key):
            item.path.write_text(item.text(), encoding="utf-8")
            lines.append(f"| [{item.qid} {item.title}]({item.filename}) | {item.asks} |")
        (folder / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  {module:28} {len(items):3} queries")

    print(f"\n  {len(CATALOGUE)} queries in {len(by_module)} modules")


if __name__ == "__main__":
    main()
