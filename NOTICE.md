# Notices, attribution and provenance

## What is in this repository, and who owns it

Everything committed here — the dataset, the queries, the explanations, the
diagrams, the build scripts, the course document and the slides — was written
for this project and is copyright © 2026 Peter Winstanley, released under the
MIT License in [LICENSE](LICENSE).

No third-party text, data or code is copied into this repository.

## The dataset is fiction

**The places are real. Everything else is invented.**

- **Real:** town and city names, their WGS84 coordinates, and the British
  National Grid eastings and northings computed from them. These are matters
  of fact, not authorship. The three book towns — Hay-on-Wye, Wigtown and
  Sedbergh — really are Britain's book towns; the book-town idea is Richard
  Booth's, from Hay in the 1960s, and is described here as fact rather than
  reproduced from any source.
- **Invented:** every bookshop, person, publisher, book, series, event, price,
  trail segment, stock record, review and disputed claim.

> Any resemblance between a bookshop, publisher, author or book in this dataset
> and a real one is coincidental. Names were chosen to sound plausible for
> their setting, and with a plausible name in a real town some collision is
> statistically inevitable; none is intended, and nothing here is a statement
> about any real business or person. If you find a collision that troubles
> you, open an issue and it will be renamed.

The county and council polygons are **simplified coverage envelopes** computed
from the settlements inside them. They are not administrative boundaries, are
not derived from any boundary dataset, and are labelled as envelopes in the
data.

The coordinates were written from general knowledge and are given to five
decimal places — roughly a metre — which is far coarser than any surveyed
source and is not an extract from one. The National Grid values are computed
from them with `pyproj` using the published EPSG:27700 transformation.

## Vocabularies referenced

The dataset uses terms from published vocabularies by IRI. It does **not**
copy their definitions; where a borrowed class or property is declared in
`data/01-vocabulary.ttl` (as OWL 2 DL requires), the accompanying comment was
written here.

| Vocabulary | Publisher |
|---|---|
| RDF, RDFS, OWL, SKOS, PROV-O | W3C |
| GeoSPARQL (`geo:`, `geof:`, `sf:`) | Open Geospatial Consortium |
| Dublin Core Terms (`dct:`) | DCMI |
| WGS84 Geo Positioning (`wgs84:`) | W3C |
| schema.org (`schema:`, used only in q85's CONSTRUCT template) | W3C Schema.org Community Group |

Instance IRIs use `https://example.org/`, which RFC 6761 reserves for
documentation and examples.

## Tools used, and not redistributed

None of these are committed. The setup scripts fetch them, and `.gitignore`
keeps them out.

| Tool | Licence | How it is obtained |
|---|---|---|
| **Apache Jena** and **Fuseki** | Apache-2.0 | installed separately by the user |
| **Apache Derby** | Apache-2.0 | copied from a local Apache SIS install, or downloaded from Maven Central, by `scripts/setup-geosparql.ps1` |
| **ROBOT** (OWL 2 profile checking) | BSD-3-Clause | downloaded by the user; the command is in `scripts/check_owl.py` |
| **Comunica** | MIT | a dependency of the Turtle Editor Viewer |
| **Turtle Editor Viewer** | MIT | a separate project by the same author |
| **HOLOS** | see its own repository | a separate project |
| **pyproj** | MIT | `pip install pyproj` |

### The EPSG geodetic dataset — read this one

`scripts/setup-geosparql.ps1` can download
`org.apache.sis.non-free:sis-epsg`, which packages the **EPSG Geodetic
Parameter Dataset**. Apache publishes it under the groupId `non-free`
precisely because the dataset carries the IOGP's own terms of use rather than
an open-source licence.

For that reason:

- the download happens only when you pass `-AcceptEpsgTerms`, which is your
  confirmation that you accept those terms;
- neither the jar nor the database Apache SIS builds from it
  (`build/sis-data/`) is committed to this repository;
- both are listed in `.gitignore`.

The terms are at <https://epsg.org/terms-of-use.html>. The EPSG Dataset is
owned by the International Association of Oil & Gas Producers (IOGP).

Nothing in this course *needs* it: it is required only for projected
coordinate reference systems such as EPSG:27700 in module 10. Module 09
answers the same geographic questions with arithmetic alone, on every engine,
and needs nothing beyond the data in this repository.

## The Semantechs mark

`assets/semantechs-logo.png` is the Semantechs mark. It appears at the head of
the course document, on the first slide, and as the favicon of both pages.

Trademarks sit outside a copyright licence, so the MIT grant in
[LICENSE](LICENSE) does not extend to it. Everything else here is covered.
If you fork this course, swap the mark for your own.

## Fonts

The course document and slides load Newsreader, Atkinson Hyperlegible and
JetBrains Mono from Google Fonts by URL. No font files are redistributed. All
three are under the SIL Open Font License.

## Prior art

The course claims no novelty in SPARQL technique. The curriculum shape
(patterns → filters → optionality → aggregation → paths → sub-queries) is the
standard one; the query idioms — group-then-rejoin for top-N-per-group, the
`OPTIONAL`+`!BOUND` anti-join, ranking on squared distance — are long-standing
and widely taught. The genre of a small fictional world built for teaching is
well established.

What is offered here is the synthesis, the explanations, and the
verification: 97 queries run against three engines with the answers compared
value by value, and the disagreements chased down rather than smoothed over.
Those engine findings are measurements taken during the build, and are
reproducible with `python scripts/check_queries.py`.
