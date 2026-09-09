#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run every query against every engine it claims to support, and compare the
answers -- not just the row counts.

    python scripts/check_queries.py              # all of them
    python scripts/check_queries.py q14 q15      # just these
    python scripts/check_queries.py --engine holos
    python scripts/check_queries.py --show q22   # print the result table

Exits non-zero if a query fails on an engine it claims to run on, or if two
engines return different answers without the query having said they would.
Writes build/results.json, which is what the course document quotes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from querycat import CATALOGUE
from engines import run_all

import queries_core          # noqa: F401  (importing registers the queries)
for _mod in ("queries_paths", "queries_geo", "queries_rdf12",
             "queries_forms", "queries_debug"):
    try:
        __import__(_mod)
    except ModuleNotFoundError:
        pass

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUILD = ROOT / "build"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="*", help="query ids (default: all)")
    ap.add_argument("--engine", action="append", help="restrict to one engine")
    ap.add_argument("--show", help="print the result table for this query id")
    args = ap.parse_args()

    items = CATALOGUE
    if args.only:
        wanted = {o.lower() for o in args.only}
        items = [i for i in items if i.qid in wanted]
    if args.show:
        items = [i for i in CATALOGUE if i.qid == args.show.lower()]

    BUILD.mkdir(exist_ok=True)
    results: dict[str, dict] = {}
    failures: list[str] = []
    disagreements: list[str] = []

    width = max((len(i.qid) + len(i.title) for i in items), default=40) + 4
    for item in items:
        engines = [e for e in item.engines if not args.engine or e in args.engine]
        if not engines:
            continue
        qfile = BUILD / f"{item.qid}.rq"
        qfile.write_text(item.prefixes + "\n" + item.body + "\n", encoding="utf-8")
        got = run_all([DATA / item.data], qfile, engines=tuple(engines))

        row, cells, sigs = {}, [], {}
        for name in ("editor", "holos", "fuseki"):
            if name not in engines:
                cells.append(f"{name}:  -   ")
                continue
            r = got[name]
            row[name] = {"ok": r.ok, "rows": r.rows, "error": r.error}
            if r.ok:
                cells.append(f"{name}:{r.rows:>4}  ")
                sigs[name] = r.signature()
            else:
                cells.append(f"{name}:FAIL ")
                failures.append(f"{item.qid} on {name}: {r.error}")

        note = ""
        if len(set(sigs.values())) > 1:
            note = "   <-- ENGINES DISAGREE"
            if "engines-differ" not in item.notes:
                disagreements.append(
                    f"{item.qid}: " + ", ".join(f"{k}={len(v.splitlines())} rows" for k, v in sigs.items()))
        results[item.qid] = row
        print(f"  {item.qid} {item.title:<{width}} " + "".join(cells) + note)

        if args.show:
            first = next(iter(got.values()))
            for b in first.bindings[:25]:
                print("     ", {k: v["value"] for k, v in b.items()})
            print(f"      ({first.rows} rows)")

    # Merge rather than overwrite: a targeted run must not wipe the counts for
    # the queries it did not touch, because build_queries.py and build_docs.py
    # quote this file.
    out = BUILD / "results.json"
    merged = {}
    if out.exists():
        try:
            merged = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            merged = {}
    merged.update(results)
    out.write_text(json.dumps(dict(sorted(merged.items())), indent=2), encoding="utf-8")

    ok = True
    if failures:
        ok = False
        print(f"\n  {len(failures)} failure(s):")
        for f in failures:
            print(f"    {f}")
    if disagreements:
        ok = False
        print(f"\n  {len(disagreements)} undeclared disagreement(s):")
        for d in disagreements:
            print(f"    {d}")
    if ok:
        print(f"\n  all {len(results)} queries ran, and every engine agreed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
