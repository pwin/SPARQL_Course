#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build docs/index.html: the course document, generated from the catalogue.

The queries, their explanations and their diagrams all come from the same
objects that produce the .rq files, so the document can't drift from the
queries it describes.  Row counts come from build/results.json, written by
check_queries.py, so every "returns N rows" in the document was measured.

    python scripts/build_docs.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from collections import Counter
from urllib.parse import quote

from querycat import (CATALOGUE, MODULE_INFO, PROLOGUE, EDITOR_BASE,
                      RAW_BASE, REPO)
from lab_section import LAB_SECTION
from plans_section import PLANS_PREAMBLE

import queries_core          # noqa: F401
import queries_paths         # noqa: F401
import queries_geo           # noqa: F401
import queries_rdf12         # noqa: F401
import queries_forms         # noqa: F401
try:
    import queries_debug     # noqa: F401
except ModuleNotFoundError:
    pass

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

RESULTS_PATH = ROOT / "build" / "results.json"
RESULTS = json.loads(RESULTS_PATH.read_text()) if RESULTS_PATH.exists() else {}

# Measured when the data was built, so the figures on the page can't go stale
# the way the hard-coded ones did.
STATS_PATH = ROOT / "build" / "dataset-stats.json"
STATS = json.loads(STATS_PATH.read_text()) if STATS_PATH.exists() else {}


def stat(key, default="?"):
    v = STATS.get(key, default)
    return f"{v:,}" if isinstance(v, int) and v >= 1000 else str(v)

PREAMBLE = {"13-planning-and-debugging": PLANS_PREAMBLE}

ENGINE_LABEL = {"editor": "Editor", "holos": "HOLOS", "fuseki": "Fuseki"}


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# ---------------------------------------------------------------------------
# SPARQL syntax highlighting: small, dependency-free, and good enough.
# ---------------------------------------------------------------------------
KEYWORDS = {
    "SELECT", "WHERE", "PREFIX", "CONSTRUCT", "ASK", "DESCRIBE", "FROM", "NAMED",
    "GRAPH", "OPTIONAL", "UNION", "MINUS", "FILTER", "BIND", "VALUES", "SERVICE",
    "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "DISTINCT", "REDUCED",
    "AS", "ASC", "DESC", "NOT", "EXISTS", "IN", "SEPARATOR", "BASE", "a",
}
FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "SAMPLE", "GROUP_CONCAT", "STR", "LANG",
    "LANGDIR", "hasLANG", "hasLANGDIR", "STRLANGDIR", "DATATYPE", "BOUND", "IF",
    "COALESCE", "sameTerm", "isIRI", "isBLANK", "isLITERAL", "isNUMERIC",
    "isTRIPLE", "TRIPLE", "SUBJECT", "PREDICATE", "OBJECT", "REGEX", "REPLACE",
    "SUBSTR", "STRLEN", "UCASE", "LCASE", "CONCAT", "CONTAINS", "STRSTARTS",
    "STRENDS", "STRBEFORE", "STRAFTER", "ROUND", "FLOOR", "CEIL", "ABS", "RAND",
    "NOW", "YEAR", "MONTH", "DAY", "HOURS", "MINUTES", "SECONDS", "VERSION",
}


def highlight(code: str) -> str:
    """Tokenise just enough SPARQL to colour it. Comments, strings, IRIs,
    variables, prefixed names, keywords, functions, numbers."""
    import re

    token = re.compile(
        r"(?P<comment>#[^\n]*)"
        r"|(?P<string>\"\"\".*?\"\"\"|\"(?:[^\"\\]|\\.)*\")"
        r"|(?P<iri><[^>\s]*>)"
        r"|(?P<var>\?[A-Za-z_][A-Za-z0-9_]*)"
        r"|(?P<annot>\{\||\|\}|<<\(|\)>>)"
        r"|(?P<pname>[A-Za-z][A-Za-z0-9]*:[A-Za-z0-9_\-]*)"
        r"|(?P<word>[A-Za-z_][A-Za-z0-9_]*)"
        r"|(?P<num>\b\d+\.?\d*\b)",
        re.DOTALL,
    )

    out, last = [], 0
    for m in token.finditer(code):
        out.append(esc(code[last:m.start()]))
        kind = m.lastgroup
        text = esc(m.group())
        if kind == "word":
            upper = m.group().upper()
            if upper in {k.upper() for k in KEYWORDS}:
                kind = "kw"
            elif upper in {f.upper() for f in FUNCTIONS}:
                kind = "fn"
            else:
                kind = "plain"
        out.append(text if kind == "plain" else f'<span class="t-{kind}">{text}</span>')
        last = m.end()
    out.append(esc(code[last:]))
    return "".join(out)


# ---------------------------------------------------------------------------
# The data-model diagram.  Hand-drawn, because a generated box-and-line layout
# never shows which relationships actually matter.
# ---------------------------------------------------------------------------
SCHEMA_SVG = """
<svg viewBox="0 0 900 560" role="img" aria-labelledby="schema-title schema-desc"
     class="schema">
  <title id="schema-title">The Bookshop Trail data model</title>
  <desc id="schema-desc">Bookshops sit in settlements, which nest inside council
  areas, regions and countries. Shops stock works, which have authors and
  genres. Events are held at shops. Trail segments join shops to each
  other.</desc>

  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" class="arrowhead"/>
    </marker>
  </defs>

  <!-- the place spine -->
  <g class="node place">
    <rect x="30" y="40" width="150" height="42" rx="3"/>
    <text x="105" y="60">bs:Country</text><text x="105" y="74" class="sub">%(countries)s</text>
  </g>
  <g class="node place">
    <rect x="30" y="130" width="150" height="42" rx="3"/>
    <text x="105" y="150">bs:Region</text><text x="105" y="164" class="sub">%(regions)s — England only</text>
  </g>
  <g class="node place">
    <rect x="30" y="220" width="150" height="42" rx="3"/>
    <text x="105" y="240">bs:CouncilArea</text><text x="105" y="254" class="sub">%(councils)s</text>
  </g>
  <g class="node place">
    <rect x="30" y="310" width="150" height="42" rx="3"/>
    <text x="105" y="330">bs:Settlement</text><text x="105" y="344" class="sub">%(settlements)s — %(settlements_without_shop)s with no shop</text>
  </g>

  <path d="M 105 130 L 105 92"   class="edge" marker-end="url(#arrow)"/>
  <path d="M 105 220 L 105 182"  class="edge" marker-end="url(#arrow)"/>
  <path d="M 105 310 L 105 272"  class="edge" marker-end="url(#arrow)"/>
  <path d="M 22 240 C -6 200, -6 110, 22 62" class="edge dashed" marker-end="url(#arrow)"/>
  <text x="16" y="152" class="elabel vert">bs:within</text>
  <text x="118" y="200" class="elabel">bs:within</text>
  <text x="118" y="290" class="elabel">bs:within</text>

  <!-- the shop -->
  <g class="node accent">
    <rect x="300" y="300" width="160" height="60" rx="3"/>
    <text x="380" y="325">bs:Bookshop</text><text x="380" y="343" class="sub">%(shops)s</text>
  </g>
  <path d="M 300 330 L 190 330" class="edge" marker-end="url(#arrow)"/>
  <text x="245" y="322" class="elabel mid">bs:locatedIn</text>

  <!-- trail loop -->
  <path d="M 340 300 C 320 250, 440 250, 420 300" class="edge accent-edge"
        marker-end="url(#arrow)"/>
  <text x="380" y="258" class="elabel mid accent-text">bs:connectsTo</text>

  <!-- events -->
  <g class="node">
    <rect x="300" y="430" width="160" height="60" rx="3"/>
    <text x="380" y="455">bs:Event</text><text x="380" y="473" class="sub">%(events)s</text>
  </g>
  <path d="M 380 430 L 380 372" class="edge" marker-end="url(#arrow)"/>
  <text x="390" y="405" class="elabel">bs:heldAt</text>

  <!-- works -->
  <g class="node">
    <rect x="580" y="300" width="160" height="60" rx="3"/>
    <text x="660" y="325">bs:Work</text><text x="660" y="343" class="sub">%(works)s</text>
  </g>
  <path d="M 470 330 L 570 330" class="edge" marker-end="url(#arrow)"/>
  <text x="520" y="322" class="elabel mid">bs:stocks</text>

  <!-- authors -->
  <g class="node">
    <rect x="580" y="180" width="160" height="60" rx="3"/>
    <text x="660" y="205">bs:Author</text><text x="660" y="223" class="sub">%(authors)s</text>
  </g>
  <path d="M 660 300 L 660 252" class="edge" marker-end="url(#arrow)"/>
  <text x="670" y="280" class="elabel">bs:author</text>
  <path d="M 620 180 C 600 130, 720 130, 700 180" class="edge accent-edge"
        marker-end="url(#arrow)"/>
  <text x="660" y="138" class="elabel mid accent-text">bs:influencedBy</text>
  <path d="M 580 210 L 480 210" class="edge" marker-end="url(#arrow)"/>
  <text x="530" y="202" class="elabel mid">bs:featuring</text>
  <path d="M 470 210 C 400 215, 400 420, 380 428" class="edge"/>

  <!-- genres -->
  <g class="node">
    <rect x="580" y="430" width="160" height="60" rx="3"/>
    <text x="660" y="455">skos:Concept</text><text x="660" y="473" class="sub">%(genres)s genres</text>
  </g>
  <path d="M 660 430 L 660 372" class="edge" marker-end="url(#arrow)"/>
  <text x="670" y="405" class="elabel">bs:genre</text>
  <path d="M 740 460 C 800 440, 800 480, 745 478" class="edge accent-edge"
        marker-end="url(#arrow)"/>
  <text x="800" y="462" class="elabel accent-text">skos:broader</text>

  <!-- publishers -->
  <g class="node">
    <rect x="790" y="300" width="90" height="60" rx="3"/>
    <text x="835" y="325">Publisher</text><text x="835" y="343" class="sub">%(publishers)s</text>
  </g>
  <path d="M 750 330 L 780 330" class="edge" marker-end="url(#arrow)"/>
  <path d="M 835 300 C 855 265, 880 300, 862 305" class="edge accent-edge"
        marker-end="url(#arrow)"/>
  <text x="838" y="258" class="elabel mid accent-text">bs:imprintOf</text>

  <text x="450" y="530" class="caption">
    Curved edges point back to the same class — the recursive links. They are
    where the property-path module lives.
  </text>
</svg>
"""


def engine_strip(item) -> str:
    got = RESULTS.get(item.qid, {})
    cells = []
    for eng in ("editor", "holos", "fuseki"):
        label = ENGINE_LABEL[eng]
        if eng not in item.engines:
            cells.append(f'<span class="eng eng-na" title="not claimed for this engine">'
                         f'{label}</span>')
            continue
        r = got.get(eng)
        if r and r.get("ok"):
            cells.append(f'<span class="eng eng-ok">{label}'
                         f'<b>{r["rows"]}</b></span>')
        elif r:
            cells.append(f'<span class="eng eng-bad">{label}<b>error</b></span>')
        else:
            cells.append(f'<span class="eng eng-ok">{label}</span>')
    return '<div class="engines">' + "".join(cells) + \
           f'<span class="datafile">{esc(item.data)}</span></div>'


def extra_prefixes(item) -> str:
    """Show any PREFIX line this query needs beyond the shared prologue.

    The prologue itself isn't repeated 97 times; a query that needs more than
    it must say so, or the code block on the page won't run as printed.
    """
    if item.prefixes == PROLOGUE:
        return ""
    base = set(PROLOGUE.splitlines())
    added = [l for l in item.prefixes.splitlines() if l.strip() and l not in base]
    if not added:
        return ""
    return highlight(chr(10).join(added)) + chr(10) * 2


def query_section(item) -> str:
    learn = "".join(f"<li>{esc(x)}</li>" for x in item.learn)
    note = ""
    if item.notes:
        text = item.notes
        kind = "declared" if text.startswith("engines-differ") else "note"
        if kind == "declared":
            text = text[len("engines-differ:"):].strip()
            head = "Engines differ, and that's expected"
        else:
            head = "Note"
        note = (f'<div class="callout callout-{kind}">'
                f'<b>{head}.</b> {esc(text)}</div>')

    return f"""
<article class="query" id="{item.qid}">
  <header class="qhead">
    <span class="qid">{item.qid.upper()}</span>
    <h3>{esc(item.title)}</h3>
  </header>
  <p class="asks">{esc(item.asks)}</p>

  <div class="actions">
    <a class="btn btn-open" href="{item.editor_url}" target="_blank"
       rel="noopener">Open the data in the editor</a>
    <button class="btn btn-copy" type="button">Copy query</button>
    <span class="hint">{esc(item.data)}</span>
  </div>
  <pre class="copysrc" hidden>{esc(item.copy_text)}</pre>

  <div class="code-wrap"><pre class="code"><code>{extra_prefixes(item)}{highlight(item.body)}</code></pre></div>

  <div class="mech">
    <div class="mech-prose">
      <h4>How it works</h4>
      <p>{esc(item.how)}</p>
      <h4>What to take away</h4>
      <ul class="learn">{learn}</ul>
    </div>
    <figure class="diagram">
      <pre>{esc(item.diagram.strip(chr(10)))}</pre>
    </figure>
  </div>
  {note}
  {engine_strip(item)}
</article>
"""


def build() -> str:
    grouped: dict[str, list] = {}
    for item in CATALOGUE:
        grouped.setdefault(item.module, []).append(item)
    # By module number, not by the order the query files happened to import.
    by_module = dict(sorted(grouped.items(), key=lambda kv: kv[0]))

    nav = ['<li><a href="#m00"><span class="n">00</span>The lab'
           '<span class="c">3</span></a></li>']
    body = [LAB_SECTION]
    for i, (module, items) in enumerate(by_module.items(), start=1):
        title, blurb = MODULE_INFO[module]
        num = module.split("-")[0]
        items = sorted(items, key=lambda x: x.qid)
        nav.append(
            f'<li><a href="#m{num}"><span class="n">{num}</span>{esc(title)}'
            f'<span class="c">{len(items)}</span></a></li>')
        preamble = PREAMBLE.get(module, "")
        sections = preamble + "".join(query_section(x) for x in items)
        # the file most of this module's queries need
        common = Counter(x.data for x in items).most_common(1)[0][0]
        module_link = (
            f'<p class="module-open"><a class="btn btn-open" target="_blank" '
            f'rel="noopener" href="{EDITOR_BASE}?dot={quote(RAW_BASE + common, safe="")}">'
            f'Open {esc(common)} in the editor</a></p>')
        body.append(f"""
<section class="module" id="m{num}">
  <div class="module-head">
    <span class="module-num">Module {num}</span>
    <h2>{esc(title)}</h2>
    <p class="module-blurb">{esc(blurb)}</p>
    {module_link}
  </div>
  {sections}
</section>""")

    total = len(CATALOGUE)
    checked = sum(1 for q in CATALOGUE if q.qid in RESULTS)

    schema = SCHEMA_SVG % {k: STATS.get(k, "?") for k in (
        "countries", "regions", "councils", "settlements",
        "settlements_without_shop", "shops", "events", "works", "authors",
        "genres", "publishers")}
    return TEMPLATE.format(
        nav="".join(nav),
        body="".join(body),
        schema=schema,
        total=total,
        checked=checked,
        modules=len(by_module),
        triples=stat("triples_1_1"),
        shops=stat("shops"),
        towns=stat("towns_with_shops"),
        works=stat("works"),
        languages=stat("languages"),
    )


TEMPLATE = """<title>The Bookshop Trail</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap">
<style>
/* ---------------------------------------------------------------------------
   Palette: the margin of an Ordnance Survey walking map.  Landranger magenta
   for the route, a blue-black printer's ink for the type, and a paper ground
   with a faint green bias so it reads as stock rather than as screen white.
   --------------------------------------------------------------------------- */
:root {{
  --paper:      #fbfaf7;
  --paper-2:    #f2f1ec;
  --paper-3:    #e7e6df;
  --ink:        #191d24;
  --ink-2:      #454c58;
  --ink-3:      #6f7784;
  --rule:       #d8d7cf;
  --route:      #c8006e;   /* Landranger magenta */
  --route-soft: #fbe9f2;
  --bracken:    #4a6b3d;
  --bracken-soft:#eaf0e6;
  --amber:      #9a6b00;
  --amber-soft: #fbf1dc;
  --code-bg:    #f4f3ee;
  --code-edge:  #e2e1d8;

  --t-kw:    #8a2f6b;
  --t-fn:    #1d5c73;
  --t-var:   #245a2a;
  --t-str:   #8a4b1a;
  --t-iri:   #4a5160;
  --t-pname: #2f4858;
  --t-com:   #8b8f86;
  --t-num:   #8a4b1a;
  --t-annot: #c8006e;

  --sans: "Atkinson Hyperlegible", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --serif: "Newsreader", Georgia, "Times New Roman", serif;
  --mono: "JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;

  --maxw: 74ch;
  color-scheme: light;
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:      #14161a;
    --paper-2:    #1b1e23;
    --paper-3:    #24282e;
    --ink:        #e8e6e0;
    --ink-2:      #b9bcc2;
    --ink-3:      #8b9099;
    --rule:       #2f343b;
    --route:      #ff5fa8;
    --route-soft: #33101f;
    --bracken:    #8fbe79;
    --bracken-soft:#18241a;
    --amber:      #d9a441;
    --amber-soft: #2a2113;
    --code-bg:    #191c21;
    --code-edge:  #2b3037;

    --t-kw:    #e59ad0;
    --t-fn:    #7fc8e0;
    --t-var:   #9ed5a3;
    --t-str:   #e0b083;
    --t-iri:   #9aa3b0;
    --t-pname: #a8c4d4;
    --t-com:   #71776f;
    --t-num:   #e0b083;
    --t-annot: #ff5fa8;
    color-scheme: dark;
  }}
}}

:root[data-theme="dark"] {{
  --paper:      #14161a;
  --paper-2:    #1b1e23;
  --paper-3:    #24282e;
  --ink:        #e8e6e0;
  --ink-2:      #b9bcc2;
  --ink-3:      #8b9099;
  --rule:       #2f343b;
  --route:      #ff5fa8;
  --route-soft: #33101f;
  --bracken:    #8fbe79;
  --bracken-soft:#18241a;
  --amber:      #d9a441;
  --amber-soft: #2a2113;
  --code-bg:    #191c21;
  --code-edge:  #2b3037;

  --t-kw:    #e59ad0;
  --t-fn:    #7fc8e0;
  --t-var:   #9ed5a3;
  --t-str:   #e0b083;
  --t-iri:   #9aa3b0;
  --t-pname: #a8c4d4;
  --t-com:   #71776f;
  --t-num:   #e0b083;
  --t-annot: #ff5fa8;
  color-scheme: dark;
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

a {{ color: var(--route); text-decoration-thickness: 1px; text-underline-offset: 2px; }}
a:focus-visible, button:focus-visible {{ outline: 2px solid var(--route); outline-offset: 2px; }}

/* ------------------------------------------------------------------ shell */
.shell {{ display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 0; }}

.rail {{
  position: sticky; top: 0; align-self: start; height: 100vh;
  overflow-y: auto; padding: 28px 20px 40px;
  border-right: 1px solid var(--rule); background: var(--paper-2);
}}
.rail .brand {{ font-family: var(--serif); font-size: 1.15rem; line-height: 1.25;
  margin: 0 0 4px; }}
.rail .brand em {{ font-style: italic; color: var(--route); }}
.rail .tagline {{ font-size: .78rem; color: var(--ink-3); margin: 0 0 20px; }}
.rail ol {{ list-style: none; margin: 0; padding: 0; display: flex;
  flex-direction: column; gap: 1px; }}
.rail a {{
  display: grid; grid-template-columns: 26px 1fr auto; align-items: baseline;
  gap: 6px; padding: 6px 8px; border-radius: 2px;
  color: var(--ink-2); text-decoration: none; font-size: .82rem; line-height: 1.3;
}}
.rail a:hover {{ background: var(--paper-3); color: var(--ink); }}
.rail .n {{ font-family: var(--mono); font-size: .72rem; color: var(--route); }}
.rail .c {{ font-family: var(--mono); font-size: .68rem; color: var(--ink-3); }}
.rail .railnote {{ font-size: .74rem; color: var(--ink-3); margin-top: 22px;
  padding-top: 14px; border-top: 1px solid var(--rule); }}

main {{ padding: 0 0 100px; min-width: 0; }}
.wrap {{ padding: 0 40px; }}

/* ------------------------------------------------------------------ hero */
.hero {{ padding: 56px 40px 34px; border-bottom: 1px solid var(--rule); }}
.eyebrow {{
  font-family: var(--mono); font-size: .7rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--route); margin: 0 0 14px;
}}
h1 {{
  font-family: var(--serif); font-weight: 600; font-size: clamp(2.1rem, 4.4vw, 3.1rem);
  line-height: 1.05; margin: 0 0 16px; letter-spacing: -.015em; text-wrap: balance;
  max-width: 20ch;
}}
.standfirst {{ font-size: 1.06rem; color: var(--ink-2); max-width: var(--maxw); margin: 0 0 26px; }}
.standfirst strong {{ color: var(--ink); font-weight: 400;
  border-bottom: 2px solid var(--route-soft); }}

.facts {{ display: flex; flex-wrap: wrap; gap: 0; margin-top: 8px;
  border-top: 1px solid var(--rule); }}
.fact {{ padding: 14px 26px 12px 0; margin-right: 26px; }}
.fact b {{ display: block; font-family: var(--mono); font-size: 1.45rem;
  font-weight: 700; line-height: 1; color: var(--ink); font-variant-numeric: tabular-nums; }}
.fact span {{ font-size: .76rem; color: var(--ink-3); }}

/* ------------------------------------------------------------------ prose */
.intro {{ padding: 34px 40px 10px; }}
.intro h2, .schema-block h2 {{ font-family: var(--serif); font-weight: 600;
  font-size: 1.5rem; margin: 34px 0 10px; letter-spacing: -.01em; }}
.intro p, .schema-block p {{ max-width: var(--maxw); color: var(--ink-2); }}
.intro p strong {{ color: var(--ink); }}

.grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 22px; margin: 22px 0; }}
.panel {{ border: 1px solid var(--rule); border-radius: 3px; padding: 16px 18px;
  background: var(--paper-2); }}
.panel h3 {{ font-family: var(--sans); font-size: .8rem; letter-spacing: .06em;
  text-transform: uppercase; color: var(--ink-3); margin: 0 0 10px; }}
.panel p {{ margin: 0 0 8px; font-size: .92rem; }}
.panel :last-child {{ margin-bottom: 0; }}
.panel code {{ font-family: var(--mono); font-size: .82rem; }}

/* ------------------------------------------------------------------ table */
.tablewrap {{ overflow-x: auto; margin: 18px 0 26px; border: 1px solid var(--rule);
  border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; font-size: .88rem; }}
th, td {{ text-align: left; padding: 9px 14px; border-bottom: 1px solid var(--rule); }}
th {{ font-size: .72rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--ink-3); background: var(--paper-2); font-weight: 700; }}
tr:last-child td {{ border-bottom: none; }}
td code {{ font-family: var(--mono); font-size: .82rem; }}
.yes {{ color: var(--bracken); font-weight: 700; }}
.no  {{ color: var(--route); font-weight: 700; }}
.meh {{ color: var(--ink-3); }}

/* ------------------------------------------------------------------ schema */
.schema-block {{ padding: 10px 40px 20px; }}
.schema {{ width: 100%; height: auto; max-width: 940px;
  background: var(--paper-2); border: 1px solid var(--rule); border-radius: 3px;
  padding: 10px; }}
.schema .node rect {{ fill: var(--paper); stroke: var(--rule); stroke-width: 1.5; }}
.schema .node.place rect {{ fill: var(--paper-3); }}
.schema .node.accent rect {{ stroke: var(--route); stroke-width: 2; }}
.schema .node text {{ fill: var(--ink); font-family: var(--mono); font-size: 13px;
  text-anchor: middle; }}
.schema .node text.sub {{ fill: var(--ink-3); font-size: 10.5px;
  font-family: var(--sans); }}
.schema .edge {{ fill: none; stroke: var(--ink-3); stroke-width: 1.4; }}
.schema .edge.dashed {{ stroke-dasharray: 4 3; }}
.schema .accent-edge {{ stroke: var(--route); stroke-width: 1.8; }}
.schema .arrowhead {{ fill: var(--ink-3); }}
.schema .elabel {{ fill: var(--ink-3); font-family: var(--mono); font-size: 10.5px; }}
.schema .elabel.mid {{ text-anchor: middle; }}
.schema .elabel.vert {{ text-anchor: middle; }}
.schema .accent-text {{ fill: var(--route); }}
.schema .caption {{ fill: var(--ink-3); font-family: var(--sans); font-size: 12px;
  text-anchor: middle; }}

/* ------------------------------------------------------------------ modules */
.module {{ padding: 0 40px; scroll-margin-top: 12px; }}
.module-head {{ padding: 52px 0 8px; margin-top: 34px; border-top: 2px solid var(--ink); }}
.module-num {{ font-family: var(--mono); font-size: .72rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--route); }}
.module-head h2 {{ font-family: var(--serif); font-weight: 600;
  font-size: clamp(1.6rem, 3vw, 2.1rem); margin: 6px 0 10px; letter-spacing: -.015em;
  text-wrap: balance; }}
.module-blurb {{ max-width: var(--maxw); color: var(--ink-2); margin: 0 0 8px; }}

/* ------------------------------------------------------------------ query */
.query {{ padding: 30px 0 26px; border-bottom: 1px solid var(--rule);
  scroll-margin-top: 12px; }}
.qhead {{ display: flex; align-items: baseline; gap: 12px; }}
.qid {{ font-family: var(--mono); font-size: .78rem; font-weight: 700;
  color: var(--paper); background: var(--route); padding: 2px 7px; border-radius: 2px;
  letter-spacing: .04em; }}
.qhead h3 {{ font-family: var(--serif); font-weight: 600; font-size: 1.35rem;
  margin: 0; letter-spacing: -.01em; }}
.asks {{ max-width: var(--maxw); color: var(--ink-2); margin: 8px 0 16px;
  font-size: 1.02rem; }}

.code-wrap {{ overflow-x: auto; background: var(--code-bg);
  border: 1px solid var(--code-edge); border-radius: 3px; }}
pre.code {{ margin: 0; padding: 15px 18px; font-family: var(--mono);
  font-size: .84rem; line-height: 1.6; }}
pre.code code {{ font-family: inherit; }}
.t-kw    {{ color: var(--t-kw); font-weight: 700; }}
.t-fn    {{ color: var(--t-fn); }}
.t-var   {{ color: var(--t-var); }}
.t-string{{ color: var(--t-str); }}
.t-iri   {{ color: var(--t-iri); }}
.t-pname {{ color: var(--t-pname); }}
.t-comment {{ color: var(--t-com); font-style: italic; }}
.t-num   {{ color: var(--t-num); }}
.t-annot {{ color: var(--t-annot); font-weight: 700; }}

.mech {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
  gap: 26px; margin-top: 20px; align-items: start; }}
.mech-prose h4 {{ font-family: var(--sans); font-size: .74rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--ink-3); margin: 0 0 6px; }}
.mech-prose h4 + p {{ margin-top: 0; }}
.mech-prose p {{ margin: 0 0 18px; color: var(--ink-2); font-size: .95rem; }}
ul.learn {{ margin: 0; padding-left: 18px; display: flex; flex-direction: column;
  gap: 7px; }}
ul.learn li {{ font-size: .93rem; color: var(--ink-2); }}
ul.learn li::marker {{ color: var(--route); }}

.diagram {{ margin: 0; }}
.diagram pre {{
  margin: 0; padding: 14px 16px; overflow-x: auto;
  background: var(--paper-2); border: 1px solid var(--rule);
  border-left: 3px solid var(--route);
  border-radius: 3px; font-family: var(--mono); font-size: .74rem;
  line-height: 1.45; color: var(--ink-2); white-space: pre;
}}

.callout {{ margin: 18px 0 0; padding: 11px 14px; border-radius: 3px;
  font-size: .89rem; max-width: 90ch; }}
.callout b {{ font-weight: 700; }}
.callout-note {{ background: var(--bracken-soft); border-left: 3px solid var(--bracken);
  color: var(--ink-2); }}
.callout-declared {{ background: var(--amber-soft); border-left: 3px solid var(--amber);
  color: var(--ink-2); }}

.actions {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
  margin: 0 0 12px; }}
.btn {{
  font-family: var(--sans); font-size: .8rem; line-height: 1;
  padding: 7px 12px; border-radius: 3px; cursor: pointer;
  border: 1px solid var(--rule); background: var(--paper-2); color: var(--ink-2);
  text-decoration: none; display: inline-block;
}}
.btn:hover {{ border-color: var(--route); color: var(--ink); }}
.btn-open {{ border-color: var(--route); color: var(--route); }}
.btn-open:hover {{ background: var(--route-soft); }}
.btn-copy.done {{ border-color: var(--bracken); color: var(--bracken); }}
.actions .hint {{ font-family: var(--mono); font-size: .7rem; color: var(--ink-3); }}
.module-open {{ margin: 10px 0 0; }}
.engines {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin-top: 16px; }}
.eng {{ font-family: var(--mono); font-size: .72rem; padding: 2px 8px;
  border-radius: 999px; border: 1px solid var(--rule); color: var(--ink-3); }}
.eng b {{ margin-left: 6px; font-weight: 700; font-variant-numeric: tabular-nums; }}
.eng-ok {{ color: var(--bracken); border-color: var(--bracken); }}
.eng-ok b {{ color: var(--ink-2); }}
.eng-bad {{ color: var(--route); border-color: var(--route); }}
.eng-na {{ opacity: .45; text-decoration: line-through; }}
.datafile {{ font-family: var(--mono); font-size: .7rem; color: var(--ink-3);
  margin-left: auto; }}

footer {{ padding: 40px; border-top: 1px solid var(--rule); color: var(--ink-3);
  font-size: .85rem; }}
footer p {{ max-width: var(--maxw); }}

@media (max-width: 1080px) {{
  .mech {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 860px) {{
  .shell {{ grid-template-columns: 1fr; }}
  .rail {{ position: static; height: auto; border-right: none;
    border-bottom: 1px solid var(--rule); }}
  .rail ol {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); }}
  .hero, .intro, .module, .schema-block, .wrap {{ padding-left: 20px; padding-right: 20px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; transition: none !important; }}
}}
</style>

<div class="shell">
  <nav class="rail" aria-label="Modules">
    <p class="brand">The <em>Bookshop</em> Trail</p>
    <p class="tagline">A SPARQL course in {total} queries</p>
    <ol>{nav}</ol>
    <p class="railnote">Every query on this page has been run against the
      browser editor, HOLOS and Fuseki, and the answers compared value by
      value. The badges under each query are measured row counts.</p>
  </nav>

  <main>
    <div class="hero">
      <p class="eyebrow">SPARQL 1.1 &amp; 1.2 · {total} queries · {modules} modules</p>
      <h1>Learn SPARQL on a trail of imaginary bookshops</h1>
      <p class="standfirst">Thirty-three invented bookshops in <strong>real
        British towns</strong>, with real coordinates, a genre taxonomy, an
        author-influence graph and a walking route between the shops. It's
        built to get a beginner to property paths and nested aggregation
        quickly — and it's deliberately awkward in the places where SPARQL
        is genuinely hard.</p>
      <div class="facts">
        <div class="fact"><b>{triples}</b><span>triples, RDF 1.1</span></div>
        <div class="fact"><b>{total}</b><span>worked queries</span></div>
        <div class="fact"><b>3</b><span>engines, all verified</span></div>
        <div class="fact"><b>{shops}</b><span>bookshops in {towns} towns</span></div>
        <div class="fact"><b>{works}</b><span>works, {languages} languages</span></div>
      </div>
    </div>

    <div class="intro">
      <h2>What you're querying</h2>
      <p><strong>The places are real.</strong> Real names, real WGS84
        coordinates, real British National Grid eastings and northings — so
        distances are checkable against a map and the geography module is
        about actual geography. <strong>Everything else is invented.</strong>
        Shops, people, publishers, books, events, prices, disputed claims. No
        query here can teach you a false fact about a real person or
        business.</p>

      <div class="grid2">
        <div class="panel">
          <h3>Where to run it</h3>
          <p>The course is built around the <b>Turtle Editor Viewer</b>: a
            browser editor that parses your Turtle, draws the graph and runs
            SPARQL in the same window. Load <code>data/04-bookshops.ttl</code>,
            look at the graph, then query it.</p>
          <p>Modules 01–09, 11 and 12 also run unchanged in <b>HOLOS</b> and
            <b>Fuseki</b>. Module 10 needs GeoSPARQL functions, so in practice
            it needs HOLOS.</p>
        </div>
        <div class="panel">
          <h3>The awkward bits, on purpose</h3>
          <p>The place hierarchy is <b>uneven</b> — England has a region level,
            Scotland and Wales don't — so a three-hop chain silently misses
            two countries.</p>
          <p>Two shops connect to nothing else. Books before 1970 have no
            ISBN. Four founding dates are disputed by rival sources. Each gap
            exists so a lesson has something real to find.</p>
        </div>
      </div>

      <h2>What the cross-engine checking found</h2>
      <p>Every query was run on all three engines and the answers compared
        value by value, not by row count — which hides real disagreements.
        Some of what that turned up is worth knowing before you write
        anything of your own.</p>

      <div class="tablewrap">
        <table>
          <thead><tr><th>Written as</th><th>Editor (Comunica)</th><th>HOLOS</th><th>Fuseki (ARQ)</th></tr></thead>
          <tbody>
            <tr><td><code>xsd:integer(?gYear)</code></td>
                <td class="no">0 rows, no error</td><td class="no">0 rows, no error</td><td class="yes">works</td></tr>
            <tr><td><code>xsd:integer(STR(?gYear))</code></td>
                <td class="yes">works</td><td class="yes">works</td><td class="yes">works</td></tr>
            <tr><td><code>{{| ... |}}</code> annotation pattern</td>
                <td class="yes">works</td><td class="yes">works</td><td class="yes">works</td></tr>
            <tr><td><code>&lt;&lt;( ?s ?p ?o )&gt;&gt;</code> triple term</td>
                <td class="yes">works</td><td class="yes">works</td><td class="yes">works</td></tr>
            <tr><td><code>&lt;&lt; s p o ~ ?r &gt;&gt;</code> in a query</td>
                <td class="no">parse error</td><td class="no">parse error</td><td class="no">parse error</td></tr>
            <tr><td><code>isTRIPLE</code>, <code>SUBJECT</code>, <code>LANGDIR</code></td>
                <td class="yes">works</td><td class="yes">works</td><td class="yes">works</td></tr>
            <tr><td><code>VERSION()</code></td>
                <td class="no">parse error</td><td class="no">parse error</td><td class="yes">works</td></tr>
            <tr><td><code>geof:</code> functions</td>
                <td class="meh">none at all</td><td class="yes">45 of them</td>
                <td class="no">warns, returns the row, leaves the value unbound</td></tr>
          </tbody>
        </table>
      </div>
      <p>The first row is the dangerous one. Casting an <code>xsd:gYear</code>
        straight to an integer returns <b>zero rows</b> on two of the three
        engines, and raises no error anywhere — it looks exactly like a fact
        about your data. Go via <code>STR()</code>. Q07 is built around it.</p>
    </div>

    <div class="schema-block">
      <h2>The shape of the data</h2>
      <p>Five classes carry most of the course. The three curved edges are the
        recursive ones — a place inside a place, an author who read an author,
        a genre under a genre — and they are where module 05 lives.</p>
      {schema}
    </div>

    {body}

    <footer>
      <p>The Bookshop Trail — a teaching dataset for SPARQL 1.1 and 1.2.
        Places and coordinates are real; shops, people, publishers, books and
        events are invented. {checked} of {total} queries carry measured row
        counts from the cross-engine run.</p>
    </footer>
  </main>
</div>

<script>
(function () {{
  function flash(btn, text) {{
    var was = btn.textContent;
    btn.textContent = text;
    btn.classList.add('done');
    setTimeout(function () {{
      btn.textContent = was;
      btn.classList.remove('done');
    }}, 1600);
  }}
  document.addEventListener('click', function (e) {{
    var btn = e.target.closest && e.target.closest('.btn-copy');
    if (!btn) return;
    var src = btn.closest('.actions').parentNode.querySelector('.copysrc');
    if (!src) return;
    var text = src.textContent;
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(
        function () {{ flash(btn, 'Copied'); }},
        function () {{ fallback(src, btn); }});
    }} else {{
      fallback(src, btn);
    }}
  }});
  // Clipboard access can be refused; showing the text and selecting it lets
  // the reader press Ctrl+C, which is better than a button that does nothing.
  function fallback(src, btn) {{
    src.hidden = false;
    var r = document.createRange();
    r.selectNodeContents(src);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(r);
    flash(btn, 'Selected — press Ctrl+C');
  }}
}})();
</script>
"""


def main() -> None:
    out = DOCS / "index.html"
    out.write_text(build(), encoding="utf-8")
    size = out.stat().st_size
    print(f"  wrote docs/index.html  {size/1024:.0f} KB, {len(CATALOGUE)} queries")
    if not RESULTS:
        print("  (no build/results.json -- run check_queries.py for measured row counts)")


if __name__ == "__main__":
    main()
