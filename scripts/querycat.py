# -*- coding: utf-8 -*-
"""The query catalogue: one place where every lesson is defined.

Each Query below becomes a .rq file with a structured header, and the same
metadata drives the course document.  Keeping them in one object is what stops
the explanation and the query drifting apart.

    python scripts/build_queries.py     # write queries/**/*.rq
    python scripts/check_queries.py     # run every one on every engine
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "queries"

# Where the course lives, and where a learner's browser can reach the data.
# The Turtle Editor Viewer takes ?dot=<url> and loads that URL into the editor
# pane, so a link can carry a dataset with it.
REPO = "https://github.com/pwin/SPARQL_Course"
RAW_BASE = "https://raw.githubusercontent.com/pwin/SPARQL_Course/main/data/"
EDITOR_BASE = "https://semantechs.co.uk/turtle-editor-viewer/"

# Which dataset file a query needs.
D11 = "bookshop-trail-1.1.ttl"
D12 = "bookshop-trail-1.2.ttl"
DFULL = "bookshop-trail-full.ttl"
DTRIG = "bookshop-trail.trig"

# Engine keys used in the compatibility line.
EDITOR = "editor"    # Turtle Editor Viewer (Comunica)
HOLOS = "holos"      # HOLOS / new_triplestore_sparql_engine
FUSEKI = "fuseki"    # Apache Jena Fuseki 6.2.0 / ARQ
ALL = (EDITOR, HOLOS, FUSEKI)

PROLOGUE = """PREFIX bt:    <https://example.org/bookshop-trail/>
PREFIX bs:    <https://example.org/bookshop-trail/schema#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX geo:   <http://www.opengis.net/ont/geosparql#>
PREFIX geof:  <http://www.opengis.net/def/function/geosparql/>
PREFIX wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dct:   <http://purl.org/dc/terms/>
"""


@dataclass
class Query:
    qid: str                    # "q07"
    module: str                 # folder name, e.g. "05-property-paths"
    title: str
    asks: str                   # what question it answers, in one sentence
    how: str                    # the mechanism, a short paragraph
    diagram: str                # an ASCII diagram of the mechanism
    learn: list[str]            # takeaways
    body: str                   # the query itself, without the prologue
    data: str = D11
    engines: tuple = ALL
    notes: str = ""             # engine caveats, gotchas
    prefixes: str = PROLOGUE
    expect: str = ""            # filled in by check_queries.py
    order: int = 0

    @property
    def filename(self) -> str:
        slug = self.title.lower()
        for ch in " ,'()/":
            slug = slug.replace(ch, "-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return f"{self.qid}-{slug.strip('-')}.rq"

    @property
    def path(self) -> Path:
        return QUERIES / self.module / self.filename

    @property
    def data_url(self) -> str:
        """The raw URL of the file this query needs."""
        return RAW_BASE + self.data

    @property
    def editor_url(self) -> str:
        """A link that opens the Turtle Editor Viewer with the data loaded."""
        return EDITOR_BASE + "?dot=" + quote(self.data_url, safe="")

    @property
    def copy_text(self) -> str:
        """The query as a learner should paste it: a comment saying which
        query this is and what it asks, then the prologue, then the body.

        The comment matters. A student ends up with a dozen tabs of SPARQL
        open and no idea which is which; four lines at the top fixes that,
        and costs nothing at execution.
        """
        nl = chr(10)
        head = [
            "# " + self.qid.upper() + "  " + self.title,
            "# " + self.asks,
            "# Data: " + self.data,
            "# The Bookshop Trail -- " + REPO,
        ]
        return (nl.join(head) + nl * 2
                + self.prefixes.rstrip() + nl * 2
                + self.body.strip() + nl)


    def text(self) -> str:
        """The .rq file: a header a learner can read, then the query."""
        rule = "# " + "=" * 74
        out = [rule, f"#  {self.qid.upper()}  {self.title}", rule, "#"]

        def block(label, content, bullet=False):
            out.append(f"#  {label}")
            if bullet:
                for item in content:
                    wrapped = textwrap.wrap(item, 66)
                    out.append(f"#    - {wrapped[0]}")
                    for cont in wrapped[1:]:
                        out.append(f"#      {cont}")
            else:
                for line in textwrap.wrap(content, 70):
                    out.append(f"#    {line}")
            out.append("#")

        block("ASKS", self.asks)
        block("HOW IT WORKS", self.how)
        out.append("#  DIAGRAM")
        for line in self.diagram.strip(chr(10)).splitlines():
            # rstrip so a blank diagram line becomes "#" rather than "#" plus
            # four spaces -- trailing whitespace in a file people read.
            out.append(f"#    {line}".rstrip())
        out.append("#")
        block("WHAT TO TAKE AWAY", self.learn, bullet=True)
        if self.notes:
            block("NOTE", self.notes)
        out.append(f"#  DATA     {self.data}")
        out.append(f"#  LOAD IT  {self.editor_url}")
        out.append(f"#  RUNS ON  {', '.join(self.engines)}")
        if self.expect:
            out.append(f"#  RETURNS  {self.expect}")
        out.append(rule)
        out.append("")
        out.append(self.prefixes.rstrip())
        out.append("")
        out.append(self.body.strip())
        out.append("")
        return chr(10).join(out)


CATALOGUE: list[Query] = []


def q(**kwargs) -> Query:
    item = Query(**kwargs)
    item.order = len(CATALOGUE)
    CATALOGUE.append(item)
    return item


MODULE_INFO = {
    "01-first-queries": (
        "First queries",
        "Everything here runs in the browser. Paste the data into the Turtle "
        "Editor Viewer, paste the query into the SPARQL panel, press Execute. "
        "The aim of this module is to make the shape of a query familiar: a "
        "graph pattern goes in, a table comes out.",
    ),
    "02-filtering": (
        "Filtering and expressions",
        "A pattern says which shape to match; a FILTER says which of the "
        "matches to keep. This module is also where the built-in functions "
        "live, and where the difference between a value and its lexical form "
        "starts to matter.",
    ),
    "03-optional-and-negation": (
        "Optional data, alternatives and negation",
        "Real data has holes. OPTIONAL keeps a row when the extra fact is "
        "missing, UNION merges two shapes, and MINUS and NOT EXISTS remove "
        "rows -- in ways that aren't quite interchangeable.",
    ),
    "04-aggregation": (
        "Counting, grouping and summarising",
        "GROUP BY collapses many rows into one per group. HAVING filters the "
        "groups. The trap that catches everyone is putting an aggregate in "
        "the wrong place, and this module walks straight into it on purpose.",
    ),
    "05-property-paths": (
        "Property paths",
        "The feature that turns SPARQL from a table language into a graph "
        "language. A path expression walks an arbitrary number of hops, in "
        "either direction, and it terminates even when the data has cycles.",
    ),
    "06-subqueries": (
        "Sub-queries",
        "A SELECT inside a WHERE clause. It runs first, produces a small "
        "table, and the outer query joins against it. This is how you say "
        "'above average', 'the top three in each group', and 'the one with "
        "the most'.",
    ),
    "07-construct-ask-describe": (
        "Other query forms",
        "SELECT isn't the only answer shape. CONSTRUCT builds a new graph, "
        "ASK returns a boolean, DESCRIBE hands back whatever the engine "
        "thinks describes a resource. This module introduces the three; "
        "module 12 uses them in earnest, and is worth reaching for as soon as "
        "these five make sense.",
    ),
    "08-named-graphs": (
        "Named graphs",
        "The dataset also ships as TriG, with each subject area in its own "
        "named graph. GRAPH lets you ask where a fact came from, which is the "
        "cheapest form of provenance there's.",
    ),
    "09-geo-without-geosparql": (
        "Geospatial with nothing but arithmetic",
        "Every engine can do geography if the coordinates are plain numbers. "
        "This module builds bounding boxes and a great-circle distance out of "
        "FILTER and BIND alone -- so it runs in the browser, with no "
        "GeoSPARQL support of any kind.",
    ),
    "10-geosparql": (
        "GeoSPARQL proper",
        "The same questions, asked with geof: functions against WKT "
        "geometries. Shorter, exact, and dependent on an engine that "
        "implements them. HOLOS and a GeoSPARQL-enabled Fuseki do; the "
        "browser editor doesn't.",
    ),
    "11-sparql-1-2": (
        "SPARQL 1.2 and RDF 1.2",
        "How to say something about a statement, and how to ask about it "
        "afterwards. Triple terms, the annotation syntax, and language "
        "strings that know which way they are written.",
    ),
    "12-graphs-in-graphs-out": (
        "Graphs in, graphs out",
        "Module 07 introduced ASK, CONSTRUCT and DESCRIBE. This one uses them "
        "in earnest. The shift is in what SPARQL is for: not answering a "
        "question and printing a table, but testing a condition, or taking a "
        "graph in and handing a different graph back. Every query here "
        "returns a boolean or RDF -- not one of them returns a table.",
    ),
    "13-planning-and-debugging": (
        "Planning and debugging",
        "Why a query is slow, why it returns nothing, and why it returns far "
        "too much. All three engines will show you the plan they built; this "
        "module reads those plans, and collects the diagnostic queries worth "
        "reaching for before you start rewriting anything.",
    ),
    "14-challenges": (
        "Putting it together",
        "Questions with no single obvious shape, each needing two or three "
        "of the techniques above at once. Try them before reading the answer.",
    ),
}
