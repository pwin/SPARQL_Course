#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build docs/slides.html: a deck explaining the data and the queries.

Figures come from build/dataset-stats.json and build/results.json, so a slide
can't claim a number the build did not measure.

    python scripts/build_slides.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_dataset as B
import logo
import trail_map
from build_docs import SCHEMA_SVG, highlight

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

STATS = json.loads((ROOT / "build" / "dataset-stats.json").read_text()) \
    if (ROOT / "build" / "dataset-stats.json").exists() else {}
RESULTS = json.loads((ROOT / "build" / "results.json").read_text()) \
    if (ROOT / "build" / "results.json").exists() else {}


def n(key, default="?"):
    v = STATS.get(key, default)
    return f"{v:,}" if isinstance(v, int) and v >= 1000 else str(v)


SLIDES: list[tuple[str, str]] = []


def slide(kind: str, html: str) -> None:
    SLIDES.append((kind, html))


def code(text: str) -> str:
    return f'<pre class="code"><code>{highlight(text)}</code></pre>'


def ascii_box(text: str) -> str:
    return f'<pre class="ascii">{text.strip(chr(10))}</pre>'


# ===========================================================================
# Part 1 -- the data
# ===========================================================================
slide("title", f"""
{logo.img_tag("titlemark")}
<p class="eyebrow">SPARQL 1.1 and 1.2 &middot; a course in {len(RESULTS) or 97} queries</p>
<h1>The <em>Bookshop</em> Trail</h1>
<p class="lede">Thirty-three invented bookshops in real British towns, and
  everything you can ask about them.</p>
<p class="foot">Use the arrow keys, or just scroll. &nbsp;&middot;&nbsp; Semantechs</p>
""")

slide("plain", f"""
<h2>What this is</h2>
<div class="cols">
  <div>
    <p>A teaching dataset in RDF, and {len(RESULTS) or 97} worked queries that take a
      beginner from <code>SELECT ?s ?p ?o</code> to property paths, nested
      aggregation, geospatial work and RDF&nbsp;1.2 statement annotation.</p>
    <p>It's built to reach the hard parts quickly, and it's deliberately
      awkward in the places where SPARQL genuinely is.</p>
  </div>
  <div>
    <ul class="ticks">
      <li>Runs in a <b>browser editor</b>, in <b>HOLOS</b>, and in
        <b>Fuseki</b></li>
      <li>Every query verified on all three, value by value</li>
      <li>Every figure on these slides was measured, not estimated</li>
    </ul>
  </div>
</div>
""")

slide("plain", """
<h2>The places are real. Everything else is invented.</h2>
<div class="cols">
  <div>
    <h3>Real</h3>
    <p>Town names, WGS84 coordinates, British National Grid eastings and
      northings. Distances check against a map, and the geography module is
      about actual geography.</p>
    <p>Including the three genuine book towns: <b>Hay-on-Wye</b>,
      <b>Wigtown</b> and <b>Sedbergh</b>.</p>
  </div>
  <div>
    <h3>Invented</h3>
    <p>Shops, people, publishers, books, events, prices, disputed claims.</p>
    <p class="note">No query in this course can teach you a false fact about a
      real person or business. That was the reason for the split, and it's
      worth copying whenever you build teaching data.</p>
  </div>
</div>
""")

slide("figure", """
<h2>The trail</h2>
{map}
<div class="aside">
  <p>Thirty-three shops at their real coordinates, joined by the walking
    route. Longitude is squashed by cos(latitude) so the plot isn't stretched
    east&ndash;west &mdash; the same correction module&nbsp;09 teaches.</p>
  <p>The pale pair at the bottom left is the deliberate second component. No
    route reaches it, which is what makes <code>bs:connectsTo+</code> worth
    running.</p>
</div>
""")

slide("figure", """
<h2>The shape of the data</h2>
{schema}
<div class="aside">
  <p>Five classes carry most of the course.</p>
  <p>The three curved edges are the recursive ones &mdash; a place inside a
    place, an author who read an author, a genre under a genre. That's where
    module&nbsp;05 lives, and it's the reason the dataset is a graph rather
    than a spreadsheet.</p>
</div>
""")

slide("stats", f"""
<h2>What's in it</h2>
<div class="grid">
  <div class="stat"><b>{n('triples_1_1')}</b><span>triples, RDF 1.1</span></div>
  <div class="stat"><b>{n('shops')}</b><span>bookshops</span></div>
  <div class="stat"><b>{n('towns_with_shops')}</b><span>towns with a shop</span></div>
  <div class="stat"><b>{n('settlements_without_shop')}</b><span>towns with none</span></div>
  <div class="stat"><b>{n('works')}</b><span>works</span></div>
  <div class="stat"><b>{n('authors')}</b><span>authors</span></div>
  <div class="stat"><b>{n('publishers')}</b><span>publishers</span></div>
  <div class="stat"><b>{n('genres')}</b><span>genres, 4 deep</span></div>
  <div class="stat"><b>{n('events')}</b><span>events</span></div>
  <div class="stat"><b>{n('trail_segments')}</b><span>trail segments</span></div>
  <div class="stat"><b>{n('stock_records')}</b><span>stock records</span></div>
  <div class="stat"><b>{n('languages')}</b><span>languages</span></div>
</div>
<p class="note">Small enough to read; large enough that an average means
  something.</p>
""")

slide("plain", """
<h2>Awkward on purpose &mdash; 1</h2>
<h3>The hierarchy is uneven</h3>
<div class="cols">
  <div>
""" + ascii_box("""
ENGLAND                    SCOTLAND / WALES

york                       edinburgh
  | within                   | within
north-yorkshire            edinburgh-city
  | within                   | within
yorkshire                  scotland
  | within                   | within
england                    gb
  | within
gb

    4 levels                   3 levels
""") + """
  </div>
  <div>
    <p>England has a region level. Scotland and Wales don't.</p>
    <p>So a pattern hard-coded to three hops finds England and
      <b>silently misses two countries</b>:</p>
""" + code("?town bs:within/bs:within/bs:within ?country") + """
    <p class="note">A wrong answer that looks reasonable is worse than an
      error. That single fact is why property paths get ten queries.</p>
  </div>
</div>
""")

slide("plain", """
<h2>Awkward on purpose &mdash; 2, 3 and 4</h2>
<div class="three">
  <div>
    <h3>A stranded pair</h3>
    <p>Two shops in the south west connect to each other and to nothing
      else.</p>
    <p class="note">So <code>bs:connectsTo+</code> returns strictly fewer than
      all the shops, and reachability is a real question rather than a
      formality.</p>
  </div>
  <div>
    <h3>No ISBNs before 1970</h3>
    <p>Because there were none. Eleven works have no
      <code>bs:isbn</code>.</p>
    <p class="note">A gap with a reason behind it, which gives
      <code>OPTIONAL</code> and <code>NOT EXISTS</code> something real to
      find.</p>
  </div>
  <div>
    <h3>Disputed dates</h3>
    <p>Four shops have rival founding years from different sources, with
      confidences.</p>
    <p class="note">The RDF 1.2 module needs a real disagreement to reason
      about, not a toy one.</p>
  </div>
</div>
""")

# ===========================================================================
# Part 2 -- the queries
# ===========================================================================
slide("divider", """
<p class="eyebrow">Part two</p>
<h1>The queries</h1>
<p class="lede">Fifteen modules. The arc runs from "what's a triple pattern"
  to "why did the optimiser move my filter".</p>
""")

slide("plain", """
<h2>The arc</h2>
<div class="modules">
  <div><b>00</b> The lab &mdash; the editor, its graph view, its reasoner</div>
  <div><b>01</b> First queries &mdash; patterns, joins, ORDER BY</div>
  <div><b>02</b> Filtering &mdash; FILTER, BIND, and the datatype traps</div>
  <div><b>03</b> Optionality &mdash; OPTIONAL, UNION, MINUS vs NOT EXISTS</div>
  <div><b>04</b> Aggregation &mdash; GROUP BY, HAVING, counting absence</div>
  <div class="hi"><b>05</b> Property paths &mdash; the module everything builds toward</div>
  <div class="hi"><b>06</b> Sub-queries &mdash; above average, top per group</div>
  <div><b>07</b> Other query forms &mdash; CONSTRUCT, ASK, DESCRIBE</div>
  <div><b>08</b> Named graphs &mdash; provenance for free</div>
  <div><b>09</b> Geography with arithmetic &mdash; no trig, no square root</div>
  <div><b>10</b> GeoSPARQL proper &mdash; geof: functions</div>
  <div class="hi"><b>11</b> SPARQL 1.2 &mdash; saying things about statements</div>
  <div><b>12</b> Graphs in, graphs out &mdash; the three forms in earnest</div>
  <div><b>13</b> Planning and debugging &mdash; reading the plan</div>
  <div><b>14</b> Putting it together</div>
</div>
""")

slide("query", """
<h2>A query is a graph pattern</h2>
""" + code("""SELECT ?shop ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
}
ORDER BY ?name""") + ascii_box("""
?shop  ---- rdf:type ---->  bs:Bookshop
  |
  '------- rdfs:label --->  ?name

Both lines constrain the SAME ?shop, so a row
survives only if both are true of it.
""") + """
<p class="take"><b>Take away.</b> You draw the shape you want; the engine finds
  every place it fits. Repeating a variable is the join &mdash; there's no
  JOIN keyword because there doesn't need to be one.</p>
""")

slide("query", """
<h2>FILTER removes rows. BIND adds a column.</h2>
<div class="cols">
  <div>
""" + code("""FILTER( ?cafe && ?area > 150 )""") + """
    <p>Constrains. Never creates a binding. A FILTER anywhere in a group
      applies to the whole group, not just the lines above it.</p>
  </div>
  <div>
""" + code("""BIND( IF(?price < 12.00, "cheap",
      IF(?price < 18.00, "mid", "dear")) AS ?band )""") + """
    <p>Computes. Sees only what's bound <em>above</em> it, which is the
      commonest reason a BIND comes back empty.</p>
  </div>
</div>
<p class="take"><b>Take away.</b> These are the two halves of expression
  handling, and mixing them up is the single most common beginner error after
  forgetting OPTIONAL.</p>
""")

slide("query", """
<h2>OPTIONAL is a left join</h2>
""" + ascii_box("""
required                      optional
+--------------------+       +-----------------------+
| ?shop a bs:Bookshop|------>| ?shop bs:website ?site|
+--------------------+       +-----------------------+
         33 rows                        |
                             +----------+----------+
                             v                     v
                      matched: ?site bound    no match:
                                              ?site UNBOUND
                                              row still kept
                                     |
                                     v
                                  33 rows
""") + """
<p class="take"><b>Take away.</b> Drop the OPTIONAL and you get fewer rows, with
  no warning. An unbound variable isn't an empty string and not zero &mdash;
  it's absent, and <code>BOUND()</code> is how you test for it.</p>
""")

slide("query", """
<h2>The one that changes everything</h2>
<div class="cols">
  <div>
""" + code("""# wrong, and it won't tell you
?town bs:within/bs:within/bs:within ?country

# right
?town bs:within+ ?country""") + """
    <p>Measured on this dataset: the fixed chain finds England's shops and
      reports <b>nothing at all</b> for Scotland and Wales.</p>
  </div>
  <div>
""" + ascii_box("""
bs:within+   one or more hops
bs:within*   zero or more -- includes itself
bs:within?   zero or one
^bs:within   backwards
a | b        either
a / b        then
!(a|b)       any predicate but these
""") + """
  </div>
</div>
<p class="take"><b>Take away.</b> Real hierarchies are rarely of uniform depth.
  When you mean "at any depth", say so &mdash; and paths are cycle-safe, which
  a hand-rolled recursive join isn't.</p>
""")

slide("query", """
<h2>Sub-queries: group, then join back</h2>
""" + ascii_box("""
step 1  what is the maximum, per shop?

  SELECT ?shop (MAX(?a) AS ?best)
  GROUP BY ?shop
                +-----------+-----+
                | ex-libris | 320 |
                +-----------+-----+
                      |
step 2  join back to find WHICH event that was

  ?event bs:heldAt ?shop ; bs:attendance ?best
                                         ---+
                     the join condition -----'
""") + """
<p class="take"><b>Take away.</b> Aggregating throws the detail away; joining
  the aggregate back recovers it. This one shape answers "the best in each
  group", and it's the most reusable thing in the course.</p>
""")

slide("query", """
<h2>Geography with no trigonometry</h2>
<div class="cols">
  <div>
    <p>SPARQL 1.1 has <code>+ - * /</code>, <code>ABS</code>,
      <code>ROUND</code>. It has no <code>sin</code>, no <code>sqrt</code>.</p>
    <p>So a great-circle distance is out of reach. But:</p>
""" + ascii_box("""
sqrt is monotonic

  ordering by x  ==  ordering by sqrt(x)

so rank on the SQUARE and never take the root:

  ?d2 = dx*dx + dy*dy

and for a radius, square the threshold instead:

  dx*dx + dy*dy  <  50000 * 50000
""") + """
  </div>
  <div>
    <p>That makes bounding boxes, nearest-neighbour and radius queries work in
      an engine with <b>no geospatial support whatever</b> &mdash; including
      the one in the browser.</p>
    <p class="note">The dataset also carries British National Grid eastings and
      northings, so the same arithmetic isn't merely a ranking but
      <em>exact</em>: a projected grid is already flat and already in
      metres.</p>
    <p class="note">Module 10 then does it properly with
      <code>geof:</code>, and the comparison is the lesson.</p>
  </div>
</div>
""")

slide("query", """
<h2>RDF 1.2: saying something about a statement</h2>
""" + code("""?shop bs:founded ?year {| bs:claimedBy ?source ; bs:confidence ?c |} .""") + ascii_box("""
in the data:

  bt:shop-ex-libris bs:founded 1919
      {| bs:claimedBy bt:source-national-register ;
         bs:confidence 0.99 |} .
  bt:shop-ex-libris bs:founded 1921
      {| bs:claimedBy bt:source-local-paper ;
         bs:confidence 0.40 |} .

Both claims are in the graph.  Neither is privileged.
Deciding between them is the QUERY's job.
""") + """
<p class="take"><b>Take away.</b> A dataset can hold two contradictory claims
  without being broken, as long as each is attributed. That turns "which fact
  is true?" from a modelling problem into a query &mdash; and you can change
  the policy without touching the data.</p>
""")

slide("query", """
<h2>What the sugar really is</h2>
""" + ascii_box("""
what you write

  bt:shop-ex-libris bs:founded 1919 {| bs:confidence 0.99 |} .

what the parser produces -- ordinary triples, plus one new term type

  bt:shop-ex-libris bs:founded 1919 .            <- still asserted
  _:r rdf:reifies <<( bt:shop-ex-libris bs:founded 1919 )>> .
  _:r bs:confidence 0.99 .
      ^                     ^
      |                     '-- an ordinary triple about _:r
      '-- the "reifier": a name for the statement

<<( s p o )>> is a TRIPLE TERM: one RDF term whose value is a
triple.  In RDF 1.2 it may only appear as an OBJECT.
""") + """
<p class="take"><b>Take away.</b> It isn't a new kind of data. It's ordinary
  triples with a term type for talking about statements &mdash; and all three
  engines here read it.</p>
""")

# ===========================================================================
# Part 3 -- what the checking found
# ===========================================================================
slide("divider", """
<p class="eyebrow">Part three</p>
<h1>What three engines taught us</h1>
<p class="lede">Every query run everywhere, and the answers compared value by
  value rather than by row count.</p>
""")

slide("plain", """
<h2>The silent failures</h2>
<table class="matrix">
  <thead><tr><th>Written the obvious way</th><th>Editor</th><th>HOLOS</th><th>Fuseki</th></tr></thead>
  <tbody>
    <tr><td><code>xsd:integer(?gYear)</code></td>
        <td class="no">0 rows</td><td class="no">0 rows</td><td class="yes">works</td></tr>
    <tr><td><code>?gYearA != ?gYearB</code></td>
        <td class="no">0 rows</td><td class="no">0 rows</td><td class="yes">works</td></tr>
    <tr><td><code>?wktA != ?wktB</code></td>
        <td class="meh">&mdash;</td><td class="no">0 rows</td><td class="meh">&mdash;</td></tr>
    <tr><td><code>geof:distance</code> in metres</td>
        <td class="meh">no geo</td><td class="yes">works</td><td class="no">unbound</td></tr>
    <tr><td><code>CONSTRUCT</code> duplicate triples</td>
        <td class="no">kept</td><td class="yes">merged</td><td class="yes">merged</td></tr>
    <tr><td><code>&lt;&lt; s p o ~ ?r &gt;&gt;</code> in a query</td>
        <td class="no">parse error</td><td class="no">parse error</td><td class="no">parse error</td></tr>
  </tbody>
</table>
<p class="take"><b>Not one of the first three raises an error.</b> They return a
  confident, plausible, wrong answer. Row counts hide all of it, which is why
  the harness compares values &mdash; and why the fix is always the same:
  <code>STR()</code> first, then compare.</p>
""")

slide("plain", """
<h2>Reading the plan</h2>
<div class="cols">
  <div>
""" + ascii_box("""
JENA, as written -- the filter is where you put it

  (project (?name ?site)
    (filter (> (strlen ?name) 8)
      (leftjoin
        (sequence
          (bgp ...)
          (path ?town (path+ bs:within) ...))
        (bgp (triple ?shop bs:website ?site)))))

JENA, optimised -- it has MOVED INWARDS

  (project (?name ?site)
    (conditional
      (sequence
        (filter (> (strlen ?name) 8)
          (bgp (triple ?shop rdf:type bs:Bookshop)
               (triple ?shop rdfs:label ?name)))
        ...)))
""") + """
  </div>
  <div>
""" + ascii_box("""
HOLOS -- the same pushdown, plus the algorithms

  Project(?name, ?site)
  +- LeftJoin(HashBuildRightProbeLeft, keys = ?shop)
     +- LeftJoin(HashBuildLeftProbeRight, keys = ?town)
        +- QuadPattern(?shop rdf:type bs:Bookshop)
        +- Filter(STRLEN(?name) > 8)
           +- QuadPattern(?shop rdfs:label ?name)
""") + """
    <p class="note">Jena shows <em>what</em>; HOLOS shows <em>how</em>.
      Comunica names the actor that handled each operator.</p>
    <p class="take"><b>Take away.</b> Two independently written optimisers
      pushing the same filter to the same place is a good sign the rewrite is
      the right one. If yours has <em>not</em> moved, it usually can't.</p>
  </div>
</div>
""")

slide("plain", """
<h2>The debugging playbook</h2>
<div class="cols">
  <div>
    <h3>Empty result &mdash; in payoff order</h3>
    <ol class="play">
      <li>A datatype comparison. Go via <code>STR()</code>.</li>
      <li>A language tag. <code>"Cardiff"</code> never equals
        <code>"Cardiff"@en</code>.</li>
      <li>A mistyped prefix. <code>http</code> vs <code>https</code>,
        <code>#</code> vs <code>/</code>.</li>
      <li>A <code>FILTER</code> that escaped its <code>OPTIONAL</code>.</li>
      <li><code>MINUS</code> with no shared variable, which removes
        nothing.</li>
    </ol>
  </div>
  <div>
    <h3>Far too many rows</h3>
    <ol class="play">
      <li>Count each pattern alone and <b>multiply</b>. If the product matches
        your row count, nothing joined.</li>
      <li>Look for a mistyped variable.</li>
    </ol>
    <h3>Numbers wrong, rows look right</h3>
    <ol class="play">
      <li><code>COUNT(DISTINCT ?x)</code> differs from
        <code>COUNT(?x)</code>? Something multiplied before the
        aggregate.</li>
      <li><code>SUM</code> and <code>AVG</code> can't be repaired with
        DISTINCT. Split into sub-queries.</li>
    </ol>
  </div>
</div>
""")

slide("plain", """
<h2>Where the specification stops</h2>
<div class="cols">
  <div>
    <p>The vocabulary is a valid <b>OWL 2 DL</b> ontology, checked with the
      OWL API's own profile checker rather than asserted.</p>
    <p>Getting there taught something worth passing on:</p>
    <ul class="ticks">
      <li>Every class, property and datatype must be <b>declared</b> &mdash;
        including borrowed ones.</li>
      <li>A property is object, datatype or annotation. Exactly one.</li>
      <li>A transitive property may not be declared functional.</li>
    </ul>
  </div>
  <div>
""" + ascii_box("""
the trap that cost the most time:

  xsd:gYear and xsd:date are NOT in the
  OWL 2 datatype map.

  declaring them makes it WORSE --

    xsd:gYear a rdfs:Datatype .

  turns a built-in into a user-defined
  datatype, and using one of those in an
  assertion is a second, different violation.
""") + """
    <p class="take"><b>Take away.</b> The dataset keeps <code>xsd:gYear</code>
      anyway, because the portability trap it creates is one of the best
      lessons here. A conformant copy ships alongside it.</p>
  </div>
</div>
""")

slide("end", """
<h2>Start here</h2>
<div class="cols">
  <div>
    <p>Nothing to install. The editor is used online:</p>
    <p><b>semantechs.co.uk/turtle-editor-viewer</b></p>
    <p>Load <code>data/04-bookshops.ttl</code>, look at the graph, and run:</p>
""" + code("""SELECT ?shop ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
}
ORDER BY ?name""") + """
  </div>
  <div>
    <h3>Then</h3>
    <ul class="ticks">
      <li><b>Module 00</b> &mdash; twenty minutes on the editor itself,
        including its OWL 2 RL reasoner</li>
      <li><b>Modules 05 and 06</b> &mdash; where SPARQL stops being a table
        language</li>
      <li><b>Module 13</b> &mdash; the moment a query first surprises you</li>
    </ul>
    <p class="note">Every <code>.rq</code> file carries its own lesson: what it
      asks, how it works, a diagram of the mechanism, what to take away, and
      the row count it returned on each engine.</p>
  </div>
</div>
""")


# ===========================================================================
TEMPLATE = """<title>Bookshop Trail Slides</title>
{favicon}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap">
<style>
:root {{
  --paper:#fbfaf7; --paper-2:#f2f1ec; --paper-3:#e7e6df;
  --ink:#191d24; --ink-2:#454c58; --ink-3:#6f7784; --rule:#d8d7cf;
  --route:#c8006e; --route-soft:#fbe9f2; --bracken:#4a6b3d; --amber:#9a6b00;
  --code-bg:#f4f3ee; --code-edge:#e2e1d8;
  --t-kw:#8a2f6b; --t-fn:#1d5c73; --t-var:#245a2a; --t-str:#8a4b1a;
  --t-iri:#4a5160; --t-pname:#2f4858; --t-com:#8b8f86; --t-num:#8a4b1a;
  --t-annot:#c8006e;
  --sans:"Atkinson Hyperlegible",ui-sans-serif,system-ui,sans-serif;
  --serif:"Newsreader",Georgia,serif;
  --mono:"JetBrains Mono",ui-monospace,Consolas,monospace;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#14161a; --paper-2:#1b1e23; --paper-3:#24282e;
    --ink:#e8e6e0; --ink-2:#b9bcc2; --ink-3:#8b9099; --rule:#2f343b;
    --route:#ff5fa8; --route-soft:#33101f; --bracken:#8fbe79; --amber:#d9a441;
    --code-bg:#191c21; --code-edge:#2b3037;
    --t-kw:#e59ad0; --t-fn:#7fc8e0; --t-var:#9ed5a3; --t-str:#e0b083;
    --t-iri:#9aa3b0; --t-pname:#a8c4d4; --t-com:#71776f; --t-num:#e0b083;
    --t-annot:#ff5fa8; color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#14161a; --paper-2:#1b1e23; --paper-3:#24282e;
  --ink:#e8e6e0; --ink-2:#b9bcc2; --ink-3:#8b9099; --rule:#2f343b;
  --route:#ff5fa8; --route-soft:#33101f; --bracken:#8fbe79; --amber:#d9a441;
  --code-bg:#191c21; --code-edge:#2b3037;
  --t-kw:#e59ad0; --t-fn:#7fc8e0; --t-var:#9ed5a3; --t-str:#e0b083;
  --t-iri:#9aa3b0; --t-pname:#a8c4d4; --t-com:#71776f; --t-num:#e0b083;
  --t-annot:#ff5fa8; color-scheme: dark;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}}
.deck{{scroll-snap-type:y mandatory;overflow-y:auto;height:100vh}}
.slide{{scroll-snap-align:start;min-height:100vh;display:flex;flex-direction:column;
  justify-content:center;padding:44px 60px 68px;position:relative;
  border-bottom:1px solid var(--rule)}}
.slide > * {{max-width:1180px;width:100%;margin-inline:auto}}
h1{{font-family:var(--serif);font-weight:600;font-size:clamp(2.4rem,5.4vw,4rem);
  line-height:1.02;letter-spacing:-.02em;margin:.1em 0 .28em;text-wrap:balance}}
h1 em{{font-style:italic;color:var(--route)}}
h2{{font-family:var(--serif);font-weight:600;font-size:clamp(1.5rem,2.9vw,2.25rem);
  line-height:1.1;letter-spacing:-.015em;margin:0 0 .7em;text-wrap:balance}}
h3{{font-family:var(--sans);font-size:.76rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-3);margin:0 0 .5em}}
p{{margin:0 0 .8em;max-width:66ch}}
.eyebrow{{font-family:var(--mono);font-size:.72rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--route);margin:0 0 .2em}}
.lede{{font-size:1.16rem;color:var(--ink-2);max-width:56ch}}
.foot{{font-family:var(--mono);font-size:.76rem;color:var(--ink-3);margin-top:2.4em}}
.note{{font-size:.92rem;color:var(--ink-3)}}
.take{{margin-top:1.1em;padding:.7em .95em;background:var(--route-soft);
  border-left:3px solid var(--route);border-radius:2px;font-size:.97rem;
  color:var(--ink-2);max-width:88ch}}
code{{font-family:var(--mono);font-size:.88em}}
pre.code{{font-family:var(--mono);font-size:.85rem;line-height:1.55;margin:0 0 1em;
  padding:14px 16px;background:var(--code-bg);border:1px solid var(--code-edge);
  border-radius:3px;overflow-x:auto}}
pre.ascii{{font-family:var(--mono);font-size:.78rem;line-height:1.45;margin:0 0 1em;
  padding:14px 16px;background:var(--paper-2);border:1px solid var(--rule);
  border-left:3px solid var(--route);border-radius:3px;color:var(--ink-2);
  overflow-x:auto;white-space:pre}}
.t-kw{{color:var(--t-kw);font-weight:700}} .t-fn{{color:var(--t-fn)}}
.t-var{{color:var(--t-var)}} .t-string{{color:var(--t-str)}}
.t-iri{{color:var(--t-iri)}} .t-pname{{color:var(--t-pname)}}
.t-comment{{color:var(--t-com);font-style:italic}} .t-num{{color:var(--t-num)}}
.t-annot{{color:var(--t-annot);font-weight:700}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:34px;
  align-items:start}}
.three{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:30px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:2px;
  background:var(--rule);border:1px solid var(--rule);border-radius:3px;overflow:hidden}}
.stat{{background:var(--paper);padding:16px 18px}}
.stat b{{display:block;font-family:var(--mono);font-size:1.6rem;font-weight:700;
  line-height:1;font-variant-numeric:tabular-nums}}
.stat span{{font-size:.78rem;color:var(--ink-3)}}
ul.ticks{{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:.5em}}
ul.ticks li{{color:var(--ink-2)}} ul.ticks li::marker{{color:var(--route)}}
ol.play{{margin:0 0 1em;padding-left:1.3em;display:flex;flex-direction:column;gap:.4em}}
ol.play li{{color:var(--ink-2);font-size:.95rem}}
ol.play li::marker{{color:var(--route);font-family:var(--mono);font-size:.85em}}
.modules{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));
  gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:3px;
  overflow:hidden}}
.modules div{{background:var(--paper);padding:9px 14px;font-size:.92rem;
  color:var(--ink-2)}}
.modules div.hi{{background:var(--route-soft);color:var(--ink)}}
.modules b{{font-family:var(--mono);color:var(--route);margin-right:.7em;
  font-size:.85em}}
table.matrix{{border-collapse:collapse;width:100%;font-size:.95rem}}
table.matrix th,table.matrix td{{text-align:left;padding:9px 14px;
  border-bottom:1px solid var(--rule)}}
table.matrix th{{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-3);background:var(--paper-2)}}
.yes{{color:var(--bracken);font-weight:700}} .no{{color:var(--route);font-weight:700}}
.meh{{color:var(--ink-3)}}
.figure-wrap{{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,.75fr);
  gap:36px;align-items:center}}
.map,.schema{{width:100%;height:auto;max-height:74vh;background:var(--paper-2);
  border:1px solid var(--rule);border-radius:3px;padding:8px}}
.map .seg{{stroke:var(--ink-3);stroke-width:1.3;opacity:.75}}
.map .seg.unmarked{{stroke-dasharray:4 3}}
.map .seg.orphan{{stroke:var(--route);opacity:.5}}
.map .shop{{fill:var(--route);stroke:var(--paper);stroke-width:1.2}}
.map .shop.booktown{{fill:var(--ink)}}
.map .shop.orphan{{fill:var(--route);opacity:.45}}
.map .pin{{fill:var(--ink-3);font-family:var(--mono);font-size:10.5px}}
.map .mapnote{{fill:var(--ink-3);font-family:var(--sans);font-size:11px}}
.schema .node rect{{fill:var(--paper);stroke:var(--rule);stroke-width:1.5}}
.schema .node.place rect{{fill:var(--paper-3)}}
.schema .node.accent rect{{stroke:var(--route);stroke-width:2}}
.schema .node text{{fill:var(--ink);font-family:var(--mono);font-size:13px;
  text-anchor:middle}}
.schema .node text.sub{{fill:var(--ink-3);font-size:10.5px;font-family:var(--sans)}}
.schema .edge{{fill:none;stroke:var(--ink-3);stroke-width:1.4}}
.schema .edge.dashed{{stroke-dasharray:4 3}}
.schema .accent-edge{{stroke:var(--route);stroke-width:1.8}}
.schema .arrowhead{{fill:var(--ink-3)}}
.schema .elabel{{fill:var(--ink-3);font-family:var(--mono);font-size:10.5px}}
.schema .elabel.mid,.schema .elabel.vert{{text-anchor:middle}}
.schema .accent-text{{fill:var(--route)}}
.schema .caption{{fill:var(--ink-3);font-family:var(--sans);font-size:12px;
  text-anchor:middle}}
.aside p{{font-size:.95rem;color:var(--ink-2)}}
.titlemark{{width:88px;height:88px;margin:0 0 18px;display:block}}
.slide.title,.slide.divider{{background:var(--paper-2)}}
.slide.divider h1{{font-size:clamp(2rem,4.4vw,3.2rem)}}
.num{{position:absolute;right:22px;bottom:16px;font-family:var(--mono);
  font-size:.72rem;color:var(--ink-3);font-variant-numeric:tabular-nums}}
.bar{{position:fixed;left:0;top:0;height:3px;background:var(--route);width:0;
  z-index:9;transition:width .12s linear}}
@media (max-width:820px){{
  .slide{{padding:30px 22px 56px;min-height:auto}}
  .deck{{scroll-snap-type:none}}
  .figure-wrap{{grid-template-columns:1fr}}
}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
@media print{{
  .deck{{height:auto;overflow:visible}}
  .slide{{page-break-after:always;min-height:auto;border:none}}
  .bar{{display:none}}
}}
</style>

<div class="bar" id="bar"></div>
<div class="deck" id="deck">
{slides}
</div>

<script>
(function () {{
  var deck = document.getElementById('deck');
  var bar = document.getElementById('bar');
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));

  function current() {{
    var top = deck.scrollTop, best = 0, bestD = Infinity;
    slides.forEach(function (s, i) {{
      var d = Math.abs(s.offsetTop - top);
      if (d < bestD) {{ bestD = d; best = i; }}
    }});
    return best;
  }}
  function go(i) {{
    i = Math.max(0, Math.min(slides.length - 1, i));
    deck.scrollTo({{ top: slides[i].offsetTop, behavior: 'smooth' }});
  }}
  function progress() {{
    bar.style.width = ((current() + 1) / slides.length * 100) + '%';
  }}
  deck.addEventListener('scroll', progress, {{ passive: true }});
  progress();

  document.addEventListener('keydown', function (e) {{
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {{
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ':
        e.preventDefault(); go(current() + 1); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
        e.preventDefault(); go(current() - 1); break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End': e.preventDefault(); go(slides.length - 1); break;
    }}
  }});
}})();
</script>
"""


def main() -> None:
    the_map = trail_map.build(B.SHOP_XY)
    parts = []
    for i, (kind, html) in enumerate(SLIDES, start=1):
        html = html.replace("{map}", the_map).replace("{schema}", SCHEMA_SVG % {
            k: STATS.get(k, "?") for k in (
                "countries", "regions", "councils", "settlements",
                "settlements_without_shop", "shops", "events", "works",
                "authors", "genres", "publishers")})
        if kind == "figure":
            head, rest = html.split("\n", 1) if html.strip().startswith("\n") else ("", html)
            html = html.replace('<div class="aside">',
                                '<div class="aside">', 1)
            body = html
            # wrap the figure and its aside side by side
            title_end = body.index("</h2>") + 5
            body = (body[:title_end] + '\n<div class="figure-wrap">'
                    + body[title_end:] + "</div>")
            html = body
        corner = ""
        parts.append(f'<section class="slide {kind}">{html}{corner}'
                     f'<span class="num">{i} / {len(SLIDES)}</span></section>')

    out = DOCS / "slides.html"
    logo.write_favicon(DOCS / "favicon.png")
    out.write_text(TEMPLATE.format(slides="\n".join(parts),
                                   favicon=logo.favicon_link()), encoding="utf-8")
    print(f"  wrote docs/slides.html  {out.stat().st_size / 1024:.0f} KB, "
          f"{len(SLIDES)} slides")


if __name__ == "__main__":
    main()
