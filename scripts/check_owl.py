#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the vocabulary and the datasets against the OWL 2 profiles.

    python scripts/check_owl.py            # DL, the profile the course targets
    python scripts/check_owl.py --profile EL

Uses ROBOT, which wraps the OWL API's own profile checker, so the answer is
the reference implementation's rather than an opinion. ROBOT is a single jar:

    curl -L -o lib/owl/robot.jar \\
      https://github.com/ontodev/robot/releases/latest/download/robot.jar

Exits non-zero if a file that claims to be in profile is not.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROBOT = ROOT / "lib" / "owl" / "robot.jar"

# (file, must-be-in-profile, why)
TARGETS = [
    ("01-vocabulary.ttl", True,
     "the schema on its own: this is the specification, and it is OWL 2 DL"),
    ("bookshop-trail-owl-dl.ttl", True,
     "schema and data together, with gYear and date swapped out"),
    ("bookshop-trail-1.1.ttl", False,
     "the teaching dataset: OUT of profile on purpose, because xsd:gYear and "
     "xsd:date are not in the OWL 2 datatype map and the course wants the "
     "portability lesson they create"),
]


def run(path: Path, profile: str) -> tuple[bool, str]:
    p = subprocess.run(
        ["java", "-jar", str(ROBOT), "validate-profile",
         "--profile", profile, "--input", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    ok = "in profile]" in out and "NOT in profile" not in out
    first = ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Use of") or line.startswith("Illegal"):
            first = line
            break
    return ok, first


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="DL",
                    choices=["DL", "EL", "QL", "RL", "Full"])
    args = ap.parse_args()

    if not ROBOT.exists():
        print(f"  ROBOT not found at {ROBOT}")
        print("  Download it with:")
        print("    curl -L -o lib/owl/robot.jar \\")
        print("      https://github.com/ontodev/robot/releases/latest/download/robot.jar")
        return 1

    print(f"\n  OWL 2 {args.profile} profile\n")
    failures = []
    for name, expected, why in TARGETS:
        path = ROOT / "data" / name
        if not path.exists():
            print(f"  {name:32} missing -- run build_dataset.py / make_dl_variant.py")
            failures.append(name)
            continue
        ok, detail = run(path, args.profile)
        want = "in profile" if expected else "out of profile, deliberately"
        got = "in profile" if ok else "NOT in profile"
        mark = "ok  " if ok == expected else "FAIL"
        print(f"  {mark} {name:32} {got}")
        print(f"       expected: {want}")
        print(f"       {why}")
        if not ok and detail:
            print(f"       first violation: {detail[:110]}")
        print()
        if ok != expected:
            failures.append(name)

    if failures:
        print(f"  {len(failures)} file(s) did not match expectations: "
              + ", ".join(failures))
        return 1
    print("  every file is exactly as in-profile as it claims to be")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
