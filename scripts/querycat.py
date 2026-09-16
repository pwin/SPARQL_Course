# -*- coding: utf-8 -*-
"""The query catalogue: one place where every lesson is defined.

Each Query below becomes a .rq file with a structured header, and the same
metadata drives the course document.  Keeping them in one object is what stops
the explanation and the query drifting apart.

    python scripts/build_queries.py     # write queries/**/*.rq
    python scripts/check_queries.py     # run every one on every engine
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from urllib.parse import quote
from pathlib import Path

import specs

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
# Comunica the library, as distinct from the editor built on it. Module 17
# needs the distinction: the library runs SPARQL Update perfectly well, and
# the editor's SPARQL panel has no way to show the result of one.
COMUNICA = "comunica"
ALL = (EDITOR, HOLOS, FUSEKI)
ALL_UPDATE = (COMUNICA, HOLOS, FUSEKI)

# Every prefix the course knows about.  A query declares only the ones it
# actually uses: ten PREFIX lines above a two-line query is noise, and the
# reader has to check each one before trusting that it matters.
KNOWN_PREFIXES = [
    ("bt",     "https://example.org/bookshop-trail/"),
    ("bs",     "https://example.org/bookshop-trail/schema#"),
    ("rdf",    "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",   "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl",    "http://www.w3.org/2002/07/owl#"),
    ("xsd",    "http://www.w3.org/2001/XMLSchema#"),
    ("skos",   "http://www.w3.org/2004/02/skos/core#"),
    ("dct",    "http://purl.org/dc/terms/"),
    ("geo",    "http://www.opengis.net/ont/geosparql#"),
    ("geof",   "http://www.opengis.net/def/function/geosparql/"),
    ("sf",     "http://www.opengis.net/ont/sf#"),
    ("wgs84",  "http://www.w3.org/2003/01/geo/wgs84_pos#"),
    ("prov",   "http://www.w3.org/ns/prov#"),
    ("schema", "https://schema.org/"),
    # Extension-function libraries. None of these are in the SPARQL
    # specification; module 15 measures which engines provide them.
    ("afn",    "http://jena.apache.org/ARQ/function#"),
    ("spif",   "http://spinrdf.org/spif#"),
    ("fn",     "http://www.w3.org/2005/xpath-functions#"),
    ("math",   "http://www.w3.org/2005/xpath-functions/math#"),
    # Only used by the federated queries in module 08, where the remote
    # endpoint is DBpedia.
    ("dbo",    "http://dbpedia.org/ontology/"),
]
PREFIX_URI = dict(KNOWN_PREFIXES)

# Angle-bracket IRIs and quoted strings can both contain a colon, so they are
# removed before looking for prefixed names -- otherwise every
# <http://...> in a query declares a prefix called "http".
_IRI = re.compile(r"<[^>\s]*>")
_STR = re.compile(r"\"\"\".*?\"\"\"|\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'", re.S)
_COMMENT = re.compile("#[^" + chr(10) + "]*")
_PNAME = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z][A-Za-z0-9._-]*):")


def prefixes_used(text: str) -> set:
    """Which known prefixes a query actually mentions."""
    stripped = _COMMENT.sub(" ", _STR.sub(" ", _IRI.sub(" ", text)))
    return {m.group(1) for m in _PNAME.finditer(stripped)} & set(PREFIX_URI)


def prologue_for(names) -> str:
    """A PREFIX block in the canonical order, aligned."""
    names = set(names)
    rows = [(p, u) for p, u in KNOWN_PREFIXES if p in names]
    if not rows:
        return ""
    width = max(len(p) for p, _ in rows) + 1
    return chr(10).join(f"PREFIX {(p + ':').ljust(width)} <{u}>" for p, u in rows)



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
    # Prefixes a query needs but does not mention, if any. Nothing needs this
    # except a CONSTRUCT whose output vocabulary is wider than its template.
    extra_prefixes: tuple = ()
    # A query that calls out to a remote endpoint. Skipped by the checker
    # unless --network is given, so the default run stays deterministic and
    # works with no internet: a course should not fail because DBpedia is busy.
    network: bool = False
    # An update request rather than a query. `body` holds the update; `verify`
    # holds a SELECT that shows what it did, run against the result. Without
    # the second half an update is unverifiable, and every claim in this
    # course is meant to be checkable.
    verify: str = ""
    # Where this query sits inside its module. Query ids are permanent -- a
    # link to q51 has to keep working -- so a lesson added later cannot take
    # the number its position deserves. This overrides the reading order
    # without touching the id: 51.5 sits between q51 and q52.
    place: float = 0.0
    # A SHACL shapes file to open alongside the data. The editor accepts
    # &shapes=<url> and puts it in its own tab, already selected for
    # validation, so a query about validation can hand the reader both files.
    shapes: str = ""
    expect: str = ""            # filled in by check_queries.py
    order: int = 0

    @property
    def sort_key(self) -> float:
        return self.place or float(self.qid[1:])

    @property
    def is_update(self) -> bool:
        return bool(self.verify)

    @property
    def filename(self) -> str:
        slug = self.title.lower()
        # Anything a filesystem would object to, plus the punctuation that
        # makes a name awkward to type.  Windows rejects ? * : " < > | outright.
        for ch in " ,'()/?*:\"<>|!":
            slug = slug.replace(ch, "-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        ext = "ru" if self.is_update else "rq"
        return f"{self.qid}-{slug.strip('-')}.{ext}"

    @property
    def path(self) -> Path:
        return QUERIES / self.module / self.filename

    @property
    def prologue(self) -> str:
        """Only the prefixes this query actually needs.

        A SELECT needs whatever its text mentions: prefixes play no part in
        how results come back. A CONSTRUCT or DESCRIBE returns RDF, and the
        engine serialises that graph using the query's prefixes, so those two
        also need whatever the *output* will mention. For a CONSTRUCT that is
        the template plus bt:, because the subjects are nearly always
        instances. For a DESCRIBE the output cannot be known in advance, so it
        keeps the full set and is the one query form that still carries
        prefixes it may not use.
        """
        names = prefixes_used(self.body) | set(self.extra_prefixes)
        if self.verify:
            names |= prefixes_used(self.verify)
        head = self.body.lstrip().upper()
        if head.startswith("DESCRIBE"):
            names |= {"bt", "bs", "rdfs", "skos", "geo", "sf", "dct", "wgs84",
                      "xsd", "rdf"}
        elif head.startswith("CONSTRUCT"):
            names |= {"bt"}
        return prologue_for(names)

    @property
    def data_url(self) -> str:
        """The raw URL of the file this query needs."""
        return RAW_BASE + self.data

    @property
    def editor_url(self) -> str:
        """A link that opens the Turtle Editor Viewer with the data loaded,
        and the shapes too when the query has some."""
        url = EDITOR_BASE + "?dot=" + quote(self.data_url, safe="")
        if self.shapes:
            url += "&shapes=" + quote(RAW_BASE + self.shapes, safe="")
        return url

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
        text = (nl.join(head) + nl * 2
                + self.prologue + nl * 2
                + self.body.strip() + nl)
        if self.verify:
            text += (nl + "# Then run this to see what it did:" + nl
                     + nl.join("# " + l for l in self.verify.strip().splitlines())
                     + nl)
        return text


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
        if self.network:
            out.append("#  NETWORK  calls a remote endpoint; needs the internet")
        out.append(f"#  DATA     {self.data}")
        out.append(f"#  LOAD IT  {self.editor_url}")
        out.append(f"#  RUNS ON  {', '.join(self.engines)}")
        for i, (label, url) in enumerate(specs.for_query(self.qid, self.module,
                                                         limit=2)):
            out.append(f"#  {'SPEC    ' if i == 0 else '        '} {label}")
            out.append(f"#           {url}")
        if self.expect:
            out.append(f"#  RETURNS  {self.expect}")
        out.append(rule)
        out.append("")
        out.append(self.prologue)
        out.append("")
        out.append(self.body.strip())
        out.append("")
        if self.verify:
            out.append("")
            out.append("# " + "-" * 72)
            out.append("#  CHECK IT WORKED.  Run this afterwards, against the")
            out.append("#  updated store.  An update returns nothing, so this")
            out.append("#  is the only way to see what it did.")
            out.append("# " + "-" * 72)
            out.append("#")
            for line in self.verify.strip().splitlines():
                out.append(("#  " + line).rstrip())
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
        "rows -- in ways that aren't quite interchangeable. VALUES is the "
        "other half of the same idea: rather than filtering rows out, it "
        "supplies the ones you want.",
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
        "the most'. A VALUES block is the same shape with the table written "
        "by hand instead of computed.",
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
        "Named graphs and federation",
        "The dataset also ships as TriG, with each subject area in its own "
        "named graph. GRAPH lets you ask where a fact came from, which is the "
        "cheapest form of provenance there's. The second half of the module "
        "takes the same idea across the network: SERVICE puts the other graph "
        "on somebody else's machine, and the last four queries join this "
        "dataset to DBpedia.",
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
    "15-beyond-the-standard": (
        "Beyond the standard",
        "Reference rather than lesson. Every engine adds functions the "
        "specification doesn't define -- ARQ's afn:, SPIN's spif:, the XPath "
        "fn: library, GeoSPARQL's geof: -- and they're genuinely useful right "
        "up until you move the query. This module measures which of them your "
        "three engines actually have, shows what each does when a function is "
        "missing, and ends with the portable rewrite.",
    ),
    "17-updating-the-data": (
        "Updating the data",
        "Everything before this reads. SPARQL Update writes: INSERT, DELETE, "
        "the two together, whole-graph operations, and a migration applied in "
        "place rather than handed back. An update returns nothing, so every "
        "query here comes with a second one that shows what it did. The "
        "editor's SPARQL panel cannot run these -- use Fuseki or HOLOS.",
    ),
    "16-blank-nodes": (
        "Blank nodes",
        "The nodes with no name. They are how RDF writes lists, restrictions "
        "and anything else that is structure rather than a thing, and they "
        "behave differently from everything else in the language: they have "
        "identity inside a query and none outside it. This module is late in "
        "the sequence because it needs property paths and sub-queries, but the "
        "hazards in it turn up from module 01 onwards.",
    ),
    "18-inference": (
        "Inference",
        "A reasoner derives new triples from the ones you have plus the rules "
        "in the vocabulary. For the commonest cases -- transitivity, inverse "
        "properties, class hierarchies -- SPARQL does the same job at query "
        "time, on every engine, with nothing stored and nothing to keep up to "
        "date. This module writes those inferences as queries; the reference "
        "section on reasoning measures what happens when you switch a real "
        "reasoner on instead, and no two of the three engines agree.",
    ),
    "14-challenges": (
        "Putting it together",
        "Questions with no single obvious shape, each needing two or three "
        "of the techniques above at once. Try them before reading the answer.",
    ),
}
