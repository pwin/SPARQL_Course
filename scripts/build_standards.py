# -*- coding: utf-8 -*-
"""Write the standards reading list into README.md.

README.md is hand-written apart from one block, marked with HTML comments,
which this script rewrites from specs.py so the reading list and the links
the course actually uses cannot drift apart.

    python scripts/build_standards.py
"""

from pathlib import Path

import specs

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

START = "<!-- standards:start -->"
END = "<!-- standards:end -->"


def block() -> str:
    lines = [START, ""]
    for group, entries in specs.STANDARDS:
        lines += [f"**{group}**", ""]
        for title, url, note in entries:
            lines.append(f"- [{title}]({url}) — {note}")
        lines.append("")
    lines += [
        "Each module also links to the particular sections it is defined by; "
        "those are in the module READMEs and at the head of every module in "
        "the course document. `python scripts/check_links.py` fetches every "
        "document and checks that each anchor still lands on its heading.",
        "",
        END,
    ]
    return "\n".join(lines)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"README.md has no {START} ... {END} block")
    head, _, rest = text.partition(START)
    _, _, tail = rest.partition(END)
    README.write_text(head + block() + tail, encoding="utf-8")
    n = sum(len(e) for _g, e in specs.STANDARDS)
    print(f"  README.md standards block rewritten: {n} documents")


if __name__ == "__main__":
    main()
