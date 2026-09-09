# -*- coding: utf-8 -*-
"""Check every standards link, including the fragment.

A link into a specification is only useful if it lands on the right heading,
and W3C documents renumber their sections between drafts. This fetches each
document once and checks that every anchor this course points at is really
in it.

    python scripts/check_links.py
"""

import ssl
import sys
import urllib.request
from collections import defaultdict
from urllib.parse import urldefrag

import features
import specs

UA = {"User-Agent": "SPARQL-Course-link-check/1.0"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    wanted = defaultdict(set)          # document -> anchors used
    labels = {}                        # (doc, anchor) -> label

    def add(label, url):
        doc, frag = urldefrag(url)
        wanted[doc].add(frag)
        labels[(doc, frag)] = label

    for _group, entries in specs.STANDARDS:
        for title, url, _note in entries:
            add(title, url)
    for module, entries in specs.MODULE_SPECS.items():
        for label, url in entries:
            add(f"{module}: {label}", url)
    for qid, entries in specs.QUERY_SPECS.items():
        for label, url in entries:
            add(f"{qid}: {label}", url)
    # FEATURES.md links every keyword and function to the section that
    # defines it, which is another eighty-odd anchors to get wrong.
    for group, entries in features.FEATURES:
        for label, _pattern, url in entries:
            add(f"feature {label}", url)

    bad = []
    for doc in sorted(wanted):
        try:
            html = fetch(doc)
        except Exception as exc:                      # noqa: BLE001
            print(f"  UNREACHABLE  {doc}  ({exc})")
            bad.append(doc)
            continue
        anchors = [a for a in sorted(wanted[doc]) if a]
        missing = [a for a in anchors
                   if f'id="{a}"' not in html and f"id='{a}'" not in html
                   and f'name="{a}"' not in html]
        state = "ok" if not missing else f"{len(missing)} MISSING"
        print(f"  {len(html) // 1024:5} KB  {len(anchors):3} anchors  "
              f"{state:12}  {doc}")
        for a in missing:
            print(f"        no #{a}   ({labels[(doc, a)]})")
            bad.append(f"{doc}#{a}")

    print()
    if bad:
        print(f"  {len(bad)} link(s) need attention")
        return 1
    total = sum(len(v) for v in wanted.values())
    print(f"  {len(wanted)} documents, {total} links, all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
