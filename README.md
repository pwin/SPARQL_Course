<img src="assets/semantechs-logo.png" alt="Semantechs" width="72" align="left" hspace="12">

# The Bookshop Trail — a SPARQL course

*A Semantechs teaching resource.*

<br clear="left">

A teaching dataset in RDF, and 139 worked queries that take a beginner from
`SELECT ?s ?p ?o` to property paths, nested aggregation, geospatial work and
RDF 1.2 statement annotation — quickly, and without toy data.

Everything here runs in three environments:

| Environment | What it is | Where it comes from | Script |
|---|---|---|---|
| **Turtle Editor Viewer** | Browser editor, graph visualiser and SPARQL panel (Comunica). The course is built around this one — you can *see* the graph you are querying. | **[semantechs.co.uk/turtle-editor-viewer](https://semantechs.co.uk/turtle-editor-viewer/)** — used online. Nothing to install, and no local copy needed. | [`open-editor.ps1`](scripts/open-editor.ps1) opens it with a chosen file already loaded |
| **Apache Jena Fuseki** | The reference server, for when you want a real endpoint over HTTP. Needs [Java 17+](https://adoptium.net). | [jena.apache.org/download](https://jena.apache.org/download/index.cgi) — or the script fetches [Jena](https://dlcdn.apache.org/jena/binaries/apache-jena-6.2.0.zip) and [Fuseki](https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-6.2.0.zip) and checks their published SHA-512 | [`setup-fuseki.ps1 -Install`](scripts/setup-fuseki.ps1) |
| **HOLOS** | RDF 1.2 triplestore with SPARQL 1.2 and 45 GeoSPARQL functions. The only one of the three that answers module 10 in full. | [github.com/pwin/triplestore](https://github.com/pwin/triplestore) — no binary release, so it is built from source; needs [Rust](https://rustup.rs) 1.87+ | [`setup-holos.ps1 -Install`](scripts/setup-holos.ps1) clones and builds it |
| *GeoSPARQL for Jena* | Not an environment — the add-on that gives Fuseki its coordinate reference systems. Needed only for module 10. | Apache Derby, and the [EPSG dataset](https://epsg.org/terms-of-use.html) from Maven Central under its own terms | [`setup-geosparql.ps1 -AcceptEpsgTerms`](scripts/setup-geosparql.ps1) |

Only the first is needed to do the course. Modules 01–09 and 11–14 all run in
the browser; module 10 wants a triplestore, and module 15 is about what each
one adds beyond the specification.

Every query in the course has been **run against all three** and its answers
compared value by value. Where they disagree, the query says so and explains
why — those disagreements turned out to be some of the most useful lessons in
the course.

---

## Start here

The fastest route in needs nothing but a browser. The Turtle Editor Viewer is
**used online** — there is nothing to install and nothing to run locally:

**<https://semantechs.co.uk/turtle-editor-viewer/>**

Open it, then:

1. **Choose File** → `data/04-bookshops.ttl`. It is small enough to see whole.
2. Look at the graph pane. That is your data.
3. Paste this into the SPARQL panel and press **Execute**:

```sparql
PREFIX bs:   <https://example.org/bookshop-trail/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?shop ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
}
ORDER BY ?name
```

Or skip the file-picking: this link opens the editor with the shops already
loaded.

<https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2F04-bookshops.ttl>

`./scripts/open-editor.ps1` builds those links for you; `-List` shows every
file it can open.

There are [slides](docs/slides.html) too — twenty-four of them, explaining the
data and the queries — if you would rather see the shape of the thing first.

Then read [`queries/00-the-lab/`](queries/00-the-lab/) -- twenty minutes on the
editor itself, the reasoner included -- and start on
[`queries/01-first-queries/`](queries/01-first-queries/).

### The other two, if you want them

Neither is needed for modules 01–09 and 11–14, which all run in the browser.
Both scripts install what they need:

```powershell
./scripts/setup-fuseki.ps1 -Install    # downloads Jena and Fuseki 6.2.0, checks
                                       # the published SHA-512, unpacks, loads,
                                       # and starts the server on :3030
./scripts/setup-holos.ps1  -Install    # clones and builds HOLOS; needs a Rust
                                       # toolchain from https://rustup.rs
```

Fuseki needs Java 17 or newer — [Adoptium](https://adoptium.net) has builds.
HOLOS is a Rust project with no binary release, so the first build takes a few
minutes and needs a C toolchain for RocksDB; on Windows that means the Visual
Studio Build Tools with the C++ workload.

HOLOS will answer a query straight from a Turtle file with no server at all,
which is the quickest way to try one:

```powershell
./scripts/setup-holos.ps1 -Query q31-*.rq
```

Reach for HOLOS when you get to **module 10**: it is the only one of the three
that answers `geof:distance` in metres.

---

## One click into the editor

The Turtle Editor Viewer accepts `?dot=<url>` and loads that URL straight into
the editor pane, so a link can carry a dataset with it. Every query in the
course document has an **Open the data in the editor** button that does exactly
that, and every module has one for its own file.

The pattern, if you want to build your own:

```
https://semantechs.co.uk/turtle-editor-viewer/?dot=<url-encoded raw URL>
```

For example, the shops on their own:

<https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSPARQL_Course%2Fmain%2Fdata%2F04-bookshops.ttl>

`raw.githubusercontent.com` sends `Access-Control-Allow-Origin: *`, so the
editor can fetch it. Any URL that does the same will work — the editor is the
hosted one either way.

Each query also has a **Copy query** button. What lands on your clipboard is
the query with a four-line comment at the top saying which query it is, what it
asks, and which file it needs:

```sparql
# Q31  Walking the trail in either direction
# Which shops can be reached on foot from The Inkwell?
# Data: bookshop-trail-1.1.ttl
# The Bookshop Trail -- https://github.com/pwin/SPARQL_Course

PREFIX bt:    <https://example.org/bookshop-trail/>
...
```

You end up with several tabs of SPARQL open soon enough; four lines at the top
saves working out which is which. The same link appears in each `.rq` file on a
`LOAD IT` line.

---

## The data

**The Bookshop Trail** is a fictional network of independent bookshops in real
British towns — including the three real book towns of Hay-on-Wye, Wigtown and
Sedbergh.

The split matters and is deliberate:

- **The places are real.** Real names, real WGS84 coordinates, real British
  National Grid eastings and northings. Distances are checkable against a map,
  and the geography module is about real geography.
- **Everything else is invented.** Shops, people, publishers, books, events,
  prices, claims. No query in this course can teach you a false fact about a
  real person or business.

> **Everything except the geography is fiction.** Any resemblance between a
> bookshop, publisher, author or book here and a real one is coincidental.
> Names were chosen to sound plausible for their setting, and with a plausible
> name in a real town some collision is statistically inevitable; none is
> intended. See [NOTICE.md](NOTICE.md), and open an issue if you find one that
> bothers you.

The area polygons are simplified coverage envelopes computed from the
settlements inside them, not official administrative boundaries. They are
labelled as such in the data, and q58 proves that every settlement really does
fall inside the polygon it claims.

### What is in it

| | |
|---|---|
| 4,698 triples | in the RDF 1.1 dataset (4,909 with the RDF 1.2 layer) |
| 33 bookshops | in 26 towns; 4 more towns have none, so negation has something to find |
| 74 works | 68 books and 6 translations, in English, Welsh, Gaelic, Arabic and Hebrew |
| 32 authors | joined by an influence graph with long chains, a diamond and one deliberate cycle |
| 13 publishers | imprints nested three deep |
| 31 genres | a SKOS tree 2 to 4 levels deep |
| 59 events | with attendance and ticket prices, for the aggregation work |
| 33 trail segments | mostly linear, two branches, one loop, and one deliberately unreachable pair |
| 95 stock records | the same facts modelled twice: RDF 1.1 n-ary nodes, and RDF 1.2 annotations |

Several features of the data exist purely to make a lesson land:

- The place hierarchy is **uneven** — England has a region level, Scotland and
  Wales do not — so a fixed-length chain of hops silently misses two countries
  and a property path does not (q28).
- Two shops in the south west connect to nothing else, so `bs:connectsTo+`
  returns strictly fewer than all the shops (q32).
- Books published before 1970 have **no ISBN**, because ISBNs did not exist
  yet — a natural gap for `OPTIONAL` and `NOT EXISTS` (q15).
- Four founding dates are **disputed**, with rival sources and confidences, so
  the RDF 1.2 module has something real to reason about (q61–q63).

### Files

```
data/
  01-vocabulary.ttl          the schema, described in RDF, so the data explains itself
  02-genres.ttl              SKOS genre tree
  03-places.ttl              places, containment, WGS84 geometry
  04-bookshops.ttl           the shops            <- start here in the editor
  05-people.ttl              authors and publishers
  06-books.ttl               works and translations
  07-events.ttl              events
  08-trail.ttl               trail segments and LineStrings
  09-stock.ttl               stock, the RDF 1.1 way
  10-annotations-1.2.ttl     claims about claims  (RDF 1.2 only)
  11-bng-geometry.ttl        the same places on the British National Grid

  bookshop-trail-1.1.ttl     files 01-09   -- any SPARQL 1.1 engine
  bookshop-trail-1.2.ttl     files 01-10   -- needs an RDF 1.2 parser
  bookshop-trail-full.ttl    files 01-11   -- adds the second coordinate system
  bookshop-trail.trig        the same triples in named graphs, for module 08

  bookshop-trail-owl-dl.ttl  the same data inside OWL 2 DL (see below)

  shapes.ttl                 SHACL constraints; the dataset conforms
  shapes-advanced.ttl        the constraints that need sh:sparql
```

The module files are small on purpose. The editor's graph view draws ten
subjects at a time, so a focused file is worth far more there than the
combined one.

---

## The course

Each query is a `.rq` file whose header carries the whole lesson: what it
asks, how it works, an ASCII diagram of the mechanism, what to take away, and
which engines run it. Read the file; do not just run it.

| Module | | |
|---|---|---|
| [00](queries/00-the-lab/) | **The lab** | the editor itself: graph view, layout engines, the HyLAR reasoner, SHACL, format conversion |
| [01](queries/01-first-queries/) | First queries | patterns, joins, `ORDER BY`, exploring an unknown dataset |
| [02](queries/02-filtering/) | Filtering and expressions | `FILTER`, `BIND`, strings, dates, language tags, datatype traps |
| [03](queries/03-optional-and-negation/) | Optional data and negation | `OPTIONAL`, `UNION`, `VALUES`, `MINUS` vs `NOT EXISTS` |
| [04](queries/04-aggregation/) | Counting and grouping | `GROUP BY`, `HAVING`, `GROUP_CONCAT`, counting things that are not there |
| [05](queries/05-property-paths/) | **Property paths** | `+ * ? ^ / \| !`, reachability, cycles, and why a fixed chain is wrong |
| [06](queries/06-subqueries/) | **Sub-queries** | above-average, top-per-group, aggregate-of-aggregate, `LIMIT` inside, `VALUES` as a join table |
| [07](queries/07-construct-ask-describe/) | Other query forms | `CONSTRUCT` as inference, `ASK`, and why not to trust `DESCRIBE` |
| [08](queries/08-named-graphs/) | Named graphs and federation | `GRAPH`, provenance for free, the default-graph surprise — then `SERVICE`, and four queries that join this dataset to **DBpedia** |
| [09](queries/09-geo-without-geosparql/) | Geography with arithmetic | bounding boxes and distance with no trig and no square root — runs in the browser |
| [10](queries/10-geosparql/) | GeoSPARQL proper | `geof:` functions, topology, and two coordinate systems in one query |
| [11](queries/11-sparql-1-2/) | **SPARQL 1.2 and RDF 1.2** | annotation syntax, triple terms, `rdf:reifies`, language direction |
| [12](queries/12-graphs-in-graphs-out/) | **Graphs in, graphs out** | ASK, DESCRIBE and CONSTRUCT in earnest: tests, subgraph extraction, vocabulary translation, an RDF 1.1 → 1.2 migration |
| [13](queries/13-planning-and-debugging/) | **Planning and debugging** | reading the plan on all three engines, and the diagnostics for empty results, cross products and inflated aggregates |
| [14](queries/14-challenges/) | **Putting it together** | questions that need three techniques at once |
| [15](queries/15-beyond-the-standard/) | Beyond the standard *(reference)* | `afn:`, `spif:`, `fn:`, `math:` — which engine has what, how each fails without it, and the portable rewrite |
| [16](queries/16-blank-nodes/) | **Blank nodes** | `isBLANK`, why a `_:b0` in your results is not a name, walking an RDF collection, and skolemising |
| [17](queries/17-updating-the-data/) | **Updating the data** | `INSERT`, `DELETE`, a migration applied in place, whole-graph operations, and the one that empties the store |

Modules 01–07, 12–14 and 16 run in **all three** environments. Module 09 does
too — that is its point. Module 11 needs an RDF 1.2 engine, and all three
qualify. Three do not run everywhere, each for its own reason: module 15 is
about what each engine adds beyond the specification; the four federated
queries at the end of module 08 are refused by HOLOS on purpose, and q108 is
about why; and module 17 needs a write endpoint, which the browser editor does
not have — Comunica the library runs updates perfectly well, but the editor's
SPARQL panel has no way to display a result that is empty by definition. Start
Fuseki with `-Writable` to follow module 17 against a server.

Module 10 is the partial exception, and the situation is more interesting than
"Jena cannot do it".

```powershell
./scripts/setup-geosparql.ps1 -AcceptEpsgTerms
```

Fuseki's self-contained jar **already carries Jena's whole GeoSPARQL
implementation** — the ARQ command line simply never puts it on the classpath.
Add it, plus Apache Derby and the EPSG dataset that Apache SIS needs for
coordinate reference systems, and the library appears. The script does that and
then verifies it by running a real query rather than assuming.

What then works on Jena, measured:

| | |
|---|---|
| topological — `sfWithin`, `sfIntersects`, Egenhofer, RCC8 | **works** |
| constructors — `envelope`, `boundary`, `convexHull`, `buffer` | **works** |
| `getSRID`, and EPSG:27700 once the EPSG dataset is installed | **works** |
| `geof:distance` in degrees or radians | **works** |
| `geof:distance` in metres, `geof:area`, `geof:length` | **unbound** |

The last row is a limitation of this Jena build, not of the setup: the call
succeeds, returns HTTP 200, and leaves the variable unbound. So **q58 runs on
Fuseki and HOLOS**; q57, q59 and q60 stay HOLOS-only. Comunica has no `geof:`
functions at all, which is why module 09 exists.

### Finding a feature

At 139 queries, reading front to back is not the only way in.
**[FEATURES.md](FEATURES.md)** lists every SPARQL keyword and function the
course demonstrates and which queries demonstrate it — 111 of them, each
linked to the section of the specification that defines it. It is generated by
scanning the query bodies, so it cannot disagree with them, and it doubles as
the coverage report: `python scripts/features.py` prints anything in the
catalogue with no query against it.

`docs/index.html` carries the same index, alongside two other reference
sections: **Talking to an endpoint** for the HTTP layer — the `query`
parameter, `Accept` headers, the Graph Store Protocol — and **The standards**,
the reading list with a link to every section this course is defined by.

### Suggested order

Beginners rarely need the whole of 02 and 03 before they can do something
interesting. A faster route that still lands the fundamentals:

> 00 → 01 → 02 (q07, q09, q11) → 03 (q14, q16) → 04 (q20, q22, q23) → **05 in
> full** → **06 in full** → 12 → 09 → 11 → 13 → 14

Module 12 pays off early: once you can write a `CONSTRUCT`, you can shrink any
part of the dataset into something the editor's graph view will draw, which
makes everything after it easier to see. Module 13 is worth reading the moment
a query first surprises you, whenever that happens.

Modules 05 and 06 are where SPARQL stops being a table language, and the whole
course is arranged to reach them quickly.

---

## The standards

Everything this course teaches is defined somewhere, usually in one short
section of one document, and reading that section is the fastest way to settle
an argument with an engine. Start with
[SPARQL 1.2 Query Language](https://www.w3.org/TR/sparql12-query/) — section
17.4 is the function reference you will open most often.

<!-- standards:start -->

**The query language**

- [SPARQL 1.2 Query Language](https://www.w3.org/TR/sparql12-query/) — The one to bookmark. Everything in modules 01 to 09 and 11 to 16 is defined here, and section 17.4 is the function reference you will open most often.
- [SPARQL 1.2 Update](https://www.w3.org/TR/sparql12-update/) — INSERT, DELETE and LOAD. The course reads rather than writes, so this appears only in module 12.
- [SPARQL 1.2 Federated Query](https://www.w3.org/TR/sparql12-federated-query/) — SERVICE, in its own short document. Module 08.
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) — The previous edition, still what most engines implement in full. Worth having open beside the 1.2 document when an engine disagrees with you.

**The data model and its syntaxes**

- [RDF 1.2 Concepts and Abstract Syntax](https://www.w3.org/TR/rdf12-concepts/) — What a triple, a literal, a blank node and a triple term actually are. Appendix B is the one on replacing blank nodes with IRIs.
- [RDF 1.2 Turtle](https://www.w3.org/TR/rdf12-turtle/) — The syntax every data file in this course is written in.
- [RDF 1.2 TriG](https://www.w3.org/TR/rdf12-trig/) — Turtle plus named graphs, which is what bookshop-trail.trig uses.
- [RDF 1.2 N-Triples](https://www.w3.org/TR/rdf12-n-triples/) — One triple per line, no abbreviations. The format to fall back on when a parser disagrees with you about Turtle.
- [RDF 1.2 Schema](https://www.w3.org/TR/rdf12-schema/) — rdfs:label, rdfs:subClassOf, rdfs:domain and rdfs:range.
- [RDF 1.2 Semantics](https://www.w3.org/TR/rdf12-semantics/) — What entailment means. Only needed if you start asking what a reasoner is allowed to conclude.

**Vocabularies the dataset uses**

- [OWL 2 Structural Specification](https://www.w3.org/TR/owl2-syntax/) — The normative one. The vocabulary file is OWL 2 DL, and this is the document that says what that requires.
- [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) — The readable one. Start here.
- [OWL 2 Profiles](https://www.w3.org/TR/owl2-profiles/) — What DL, EL, QL and RL are, and why the datatype map matters.
- [SKOS Reference](https://www.w3.org/TR/skos-reference/) — The genre scheme is a SKOS concept scheme: broader, narrower, prefLabel, altLabel.
- [PROV-O](https://www.w3.org/TR/prov-o/) — Where the provenance terms in the annotations come from.
- [SHACL](https://www.w3.org/TR/shacl/) — Validating the shape of the data, used in module 12. SHACL 1.2 Core is at https://www.w3.org/TR/shacl12-core/.
- [OGC GeoSPARQL 1.1](https://docs.ogc.org/is/22-047r1/22-047r1.html) — geo:asWKT, geof:sfWithin, geof:distance and the rest of module 10. An OGC standard, not a W3C one.

**Results, protocol and functions**

- [SPARQL 1.2 Query Results JSON Format](https://www.w3.org/TR/sparql12-results-json/) — What comes back over HTTP, and what the checking harness in this repository compares.
- [SPARQL 1.2 Query Results CSV and TSV Formats](https://www.w3.org/TR/sparql12-results-csv-tsv/) — The formats to ask for when the answer is going into a spreadsheet.
- [SPARQL 1.2 Query Results XML Format](https://www.w3.org/TR/sparql12-results-xml/) — The oldest of the three, still widely produced.
- [SPARQL 1.2 Protocol](https://www.w3.org/TR/sparql12-protocol/) — How a query gets to an endpoint over HTTP: the query parameter, default-graph-uri, and which verbs are allowed.
- [SPARQL 1.2 Graph Store HTTP Protocol](https://www.w3.org/TR/sparql12-graph-store-protocol/) — Managing whole graphs with PUT and DELETE rather than with SPARQL Update.
- [SPARQL 1.2 Service Description](https://www.w3.org/TR/sparql12-service-description/) — How an endpoint advertises what it supports -- including which extension functions, which module 15 is about.
- [SPARQL 1.2 Entailment Regimes](https://www.w3.org/TR/sparql12-entailment/) — What it means to query with a reasoner switched on.
- [XPath and XQuery Functions and Operators 3.1](https://www.w3.org/TR/xpath-functions-31/) — SPARQL borrows its function semantics from here, and module 15 meets the fn: library directly.

Each module also links to the particular sections it is defined by; those are in the module READMEs and at the head of every module in the course document. `python scripts/check_links.py` fetches every document and checks that each anchor still lands on its heading.

<!-- standards:end -->

---

## Seeing what the engine does

All three engines will show you the plan they built, and the three answers sit
at different levels — which is why it is worth looking at more than one.

```powershell
# Jena: the SPARQL algebra, without running anything
$env:JENA_HOME = "C:\apache-jena-6.2.0"
& "$env:JENA_HOME\bat\qparse.bat" --print=op  --query=build\plan.rq   # as written
& "$env:JENA_HOME\bat\qparse.bat" --print=opt --query=build\plan.rq   # as optimised

# HOLOS: the physical plan, with join algorithms and join keys
& holos.exe query --data data\bookshop-trail-1.1.ttl --query-file build\plan.rq --explain
& holos.exe query --data data\bookshop-trail-1.1.ttl --query-file build\plan.rq --reorder --explain
```

Jena shows *what* — `bgp`, `leftjoin`, `filter`, `path` — and `--print=opt`
shows the optimiser moving the `FILTER` inwards onto the pattern that binds
the variable it tests. HOLOS shows *how*: `HashBuildLeftProbeRight`,
`keys = ?shop`, and the same filter pushdown arrived at independently. Comunica
exposes `engine.explain(query, ctx, 'physical')`, which names the actor that
handled each operator.

[queries/13-planning-and-debugging/PLANS.md](queries/13-planning-and-debugging/PLANS.md)
walks through all three on the same query, explains the operator vocabulary,
and carries the debugging playbook — the ordered checklists for *empty
result*, *far too many rows*, *the numbers are wrong*, and *it is slow*. The
eight queries in that module are the diagnostics those checklists refer to.

---

## The specification is OWL 2 DL

`data/01-vocabulary.ttl` is not merely RDFS with some OWL sprinkled on: it is a
valid **OWL 2 DL** ontology, checked with the OWL API's own profile checker
rather than asserted.

```powershell
python scripts/check_owl.py          # DL by default; --profile EL, QL, RL
```

```
ok   01-vocabulary.ttl                in profile
ok   bookshop-trail-owl-dl.ttl        in profile
ok   bookshop-trail-1.1.ttl           NOT in profile   (deliberately)
```

Getting there was more instructive than expected, and the rules that bite are
the ones RDFS never mentions:

- **Everything must be declared** — every class, property and datatype,
  including the ones borrowed from SKOS, GeoSPARQL and PROV.
- **A property is object, datatype or annotation. Exactly one.** `rdf:Property`
  is not a declaration.
- **A transitive property is non-simple**, so `bs:within` may not also be
  declared functional.
- `bs:disputes` points at an RDF 1.2 triple term, which no OWL class or
  datatype can be the range of. It is declared an **annotation property** —
  the accurate declaration, and the exact point where the OWL specification stops and
  RDF 1.2 begins.

### The trap worth knowing

`xsd:gYear` and `xsd:date` are **not in the OWL 2 datatype map**. No amount of
careful declaration fixes that, and declaring them explicitly makes it *worse*:

```turtle
xsd:gYear a rdfs:Datatype .     # now it is a USER-DEFINED datatype,
                                # and using one in an assertion is a
                                # second, different violation
```

So the vocabulary declines to state a range for the four year properties and
the two date properties, and says why in their `rdfs:comment`. Declaring
`xsd:integer` instead would be worse still — it would be false of the data.

The teaching dataset keeps `xsd:gYear` on purpose, because the portability trap
it creates is one of the most useful lessons here (q07, q13, q62). A conformant
copy ships alongside it:

```powershell
python scripts/make_dl_variant.py    # data/bookshop-trail-owl-dl.ttl
```

160 years and 59 dates change type; nothing else does.

---

## Verification

The course does not take its own word for anything.

```powershell
python scripts/check_queries.py            # every query, every engine
python scripts/check_queries.py q27 q28    # just these
python scripts/check_queries.py --show q22 # print the result table
python scripts/check_queries.py --engine holos   # one engine only
```

Each query runs on every engine it claims to support, and the answers are
compared **value by value** — not merely by row count, which hides real
disagreements. The run fails if a query errors, or if two engines return
different answers without the query having declared that they would.

Seven queries do declare it, and each declaration is itself a lesson:

- **q24, q70, q74** — the order of items inside `GROUP_CONCAT` is unspecified,
  and the three engines really do differ. The membership is identical; only
  the sequence varies. `SAMPLE` is likewise free to pick any value.
- **q44, q82** — a `CONSTRUCT` template that fires more often than it produces
  distinct triples. HOLOS and Fuseki return the set; Comunica returns the
  stream, duplicates included. Both are defensible — a graph is a set, but a
  result stream need not be — and it matters the moment you count rows instead
  of loading them.
- **q46** — `DESCRIBE` returns whatever the engine thinks best. The
  specification says so.
- **q93** — deliberately. It is the diagnostic ladder for an empty result, and
  its third rung is the `xsd:gYear` cast: true on Fuseki, false on the other
  two, an error on none of them. Run it on the engine you actually use.

Three more disagreements were found and *fixed* rather than declared, because
they were bugs in the queries rather than facts about the engines: q41 needed
a tie-break (six authors have three books, so `LIMIT 3` was arbitrary), q64
was sorting on blank nodes, which no two engines order alike, and q83 nested
two independent patterns in one group, which built 102 triples to deliver the
20 that were wanted.

Row counts alone missed every one of them, and hid four silent datatype bugs
besides — q07, q13, q62 and q60 each returned a confident, plausible, wrong
answer until the values were compared rather than counted. Module 13 is the
generalisation of that experience.

### Things the checking found

Worth knowing before you write your own queries against a mixed estate:

| | editor | HOLOS | Fuseki |
|---|---|---|---|
| `xsd:integer(?gYear)` directly | 0 rows | 0 rows | works |
| `xsd:integer(STR(?gYear))` | works | works | works |
| `<< s p o ~ ?r >>` in a query | parse error | parse error | parse error |
| `{\| ... \|}` annotation in a query | works | works | works |
| `<<( ?s ?p ?o )>>` triple-term pattern | works | works | works |
| `isTRIPLE`, `SUBJECT`, `PREDICATE`, `OBJECT` | works | works | works |
| `LANGDIR`, `hasLANGDIR`, `STRLANGDIR` | works | works | works |
| `VERSION()` | parse error | parse error | works |
| `geof:` functions | none at all | 45 of them | warns, returns the row, leaves the value **unbound** |
| `afn:` (ARQ) and `fn:` (XPath) | error | works | works |
| `spif:` (SPIN) | error | works | returns the row, value **unbound** |
| `math:` (XPath) | error | error | works |

The first row is the dangerous one: casting a `gYear` straight to an integer
returns **zero rows** on two of the three engines and no error anywhere. Go via
`STR()`. q07 is built around this.

### SHACL

```powershell
holos validate --data data/bookshop-trail-1.1.ttl --shapes data/shapes.ttl
```

Reports `conforms true`. Break something in the data and run it again — that is
the fastest way to learn what a shape means.

---

## Rebuilding

The data is generated, so that it is consistent by construction: the coverage
polygons really do contain their settlements, the trail distances really are
the distance between their endpoints, and the National Grid coordinates really
are the projection of the WGS84 ones.

```powershell
python scripts/build_dataset.py     # data/*.ttl        (needs pyproj)
python scripts/make_dl_variant.py   # data/bookshop-trail-owl-dl.ttl
python scripts/build_queries.py     # queries/**/*.rq
python scripts/build_docs.py        # docs/index.html
python scripts/build_slides.py      # docs/slides.html
python scripts/build_standards.py   # the reading list block in this file
python scripts/features.py          # FEATURES.md, and the coverage report
```

Two checks are worth running after any of those:

```powershell
python scripts/check_queries.py     # every query, on all three engines
python scripts/check_queries.py --network   # the federated ones as well
python scripts/check_links.py       # every standards link, anchors included
```

| Script | |
|---|---|
| `content.py`, `content_works.py` | the source tables — places, shops, people, books, events |
| `build_dataset.py` | turns them into Turtle, TriG and geometry |
| `querycat.py` | the query catalogue: one object per lesson, and the `.rq` writer |
| `queries_core.py`, `queries_paths.py`, `queries_geo.py`, `queries_rdf12.py`, `queries_forms.py`, `queries_debug.py`, `queries_extensions.py`, `queries_federation.py`, `queries_blanknodes.py`, `queries_update.py`, `queries_toolkit.py` | the 139 queries and their explanations |
| `specs.py`, `check_links.py`, `build_standards.py` | the links into the standards, the check that every one still lands on its section, and the reading list in this file |
| `features.py` | [FEATURES.md](FEATURES.md): which query shows which keyword or function, by scanning the query bodies. It is also the coverage report — it is what found the thirty-six features this course used to describe and never demonstrate |
| `protocol_section.py` | talking to an endpoint over HTTP: the query parameter, `Accept`, the Graph Store Protocol |
| `engines.py` | runs a query on any of the three engines and normalises the answer |
| `check_queries.py` | the cross-engine comparison |
| `vocabulary.py` | the OWL 2 DL specification of the schema |
| `build_docs.py`, `lab_section.py`, `plans_section.py` | the course document |
| `build_slides.py`, `trail_map.py` | the slide deck, and the map generated from the coordinates |
| `check_owl.py`, `make_dl_variant.py` | OWL 2 profile checking, and the conformant dataset |
| `setup-fuseki.ps1`, `setup-holos.ps1` | install, load and run the two servers |
| `setup-geosparql.ps1` | GeoSPARQL for Jena: classpath, Derby, EPSG dataset |
| `open-editor.ps1` | builds a `?dot=` link and opens the hosted editor |

The `.rq` files are generated from the catalogue so that a query and its
explanation cannot drift apart. Edit the catalogue, not the `.rq`.

---

## Licence

MIT — see [LICENSE](LICENSE). Copyright © 2026 Peter Winstanley.

The **Semantechs name and mark** in `assets/` are excluded from that grant, as
trademarks normally are: the MIT licence covers the course, not the branding.
Fork and reuse the material freely; replace the mark with your own.

[NOTICE.md](NOTICE.md) covers what is and isn't in this repository: the
fiction disclaimer, the vocabularies referenced by IRI, and the third-party
tools the setup scripts fetch rather than redistribute. The EPSG geodetic
dataset in particular carries the IOGP's own terms and is deliberately not
committed here — `scripts/setup-geosparql.ps1` downloads it only when you pass
`-AcceptEpsgTerms`.
