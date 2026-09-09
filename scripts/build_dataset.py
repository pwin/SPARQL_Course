#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Bookshop Trail teaching dataset.

Everything a learner reads is generated from the tables in content.py and
content_works.py, so the data is consistent by construction: coverage
polygons really do contain their settlements, trail lengths really are the
distance between their endpoints, and the British National Grid coordinates
really are the projection of the WGS84 ones.

    python scripts/build_dataset.py

Deterministic: same input, same bytes out.
"""
from __future__ import annotations

import math
import random
import re
import sys
import textwrap
from pathlib import Path

from urllib.parse import quote

from pyproj import Transformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content as C
import content_works as W
import vocabulary as V

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

RNG = random.Random(20260909)

TO_BNG = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
FROM_BNG = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

NS = "https://example.org/bookshop-trail/"
VOCAB = NS + "schema#"

PREFIXES = [
    ("bt",    NS),
    ("bs",    VOCAB),
    ("rdf",   "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",  "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl",   "http://www.w3.org/2002/07/owl#"),
    ("xsd",   "http://www.w3.org/2001/XMLSchema#"),
    ("skos",  "http://www.w3.org/2004/02/skos/core#"),
    ("dct",   "http://purl.org/dc/terms/"),
    ("geo",   "http://www.opengis.net/ont/geosparql#"),
    ("sf",    "http://www.opengis.net/ont/sf#"),
    ("wgs84", "http://www.w3.org/2003/01/geo/wgs84_pos#"),
    ("prov",  "http://www.w3.org/ns/prov#"),
]

CRS84_URI = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
BNG_URI = "http://www.opengis.net/def/crs/EPSG/0/27700"


# ---------------------------------------------------------------------------
# Turtle emission
# ---------------------------------------------------------------------------
def prefix_block() -> str:
    return "\n".join(f"@prefix {p}: <{u}> ." for p, u in PREFIXES)


def banner(title: str, blurb: str) -> str:
    rule = "#" * 76
    body = "\n".join("#  " + line for line in textwrap.wrap(blurb, 70))
    return f"{rule}\n#  {title}\n{rule}\n{body}\n#\n"


def section(title: str) -> str:
    return f"\n# {'-' * 72}\n# {title}\n# {'-' * 72}\n"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def lit(s: str, lang: str | None = None, direction: str | None = None) -> str:
    out = f'"{esc(s)}"'
    if lang and direction:
        return f"{out}@{lang}--{direction}"
    if lang:
        return f"{out}@{lang}"
    return out


def typed(value, datatype: str) -> str:
    return f'"{value}"^^{datatype}'


def emit(subject: str, pairs: list[tuple[str, object]]) -> str:
    """One subject block in idiomatic Turtle, predicates aligned."""
    live = [(p, v) for p, v in pairs if v is not None and v != []]
    if not live:
        return ""
    lines = [subject]
    width = max(len(p) for p, _ in live)
    for i, (pred, val) in enumerate(live):
        if isinstance(val, (list, tuple)):
            val = ", ".join(str(v) for v in val)
        end = " ;" if i < len(live) - 1 else " ."
        lines.append(f"    {pred.ljust(width)}  {val}{end}")
    return "\n".join(lines) + "\n\n"


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def to_bng(lon, lat):
    return TO_BNG.transform(lon, lat)


def from_bng(e, n):
    return FROM_BNG.transform(e, n)


def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def coverage_polygon(points_lonlat, margin_m=12000.0):
    """An envelope that provably contains every input point.

    Hull in BNG metres, then each vertex pushed `margin_m` outward from the
    centroid.  For a convex polygon that can only grow the area, so
    containment is guaranteed; 1- and 2-point cases become boxes.
    """
    bng = [to_bng(lon, lat) for lon, lat in points_lonlat]
    hull = convex_hull(bng)
    if len(hull) < 3:
        xs = [p[0] for p in bng]
        ys = [p[1] for p in bng]
        x0, x1 = min(xs) - margin_m, max(xs) + margin_m
        y0, y1 = min(ys) - margin_m, max(ys) + margin_m
        hull = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    else:
        cx = sum(p[0] for p in hull) / len(hull)
        cy = sum(p[1] for p in hull) / len(hull)
        grown = []
        for x, y in hull:
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy) or 1.0
            grown.append((x + dx / d * margin_m, y + dy / d * margin_m))
        hull = grown
    ring = [from_bng(x, y) for x, y in hull]
    ring.append(ring[0])
    return ring


def haversine_km(a, b):
    (lon1, lat1), (lon2, lat2) = a, b
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def wkt_lit(wkt: str, crs: str = CRS84_URI) -> str:
    """A GeoSPARQL WKT literal.  The CRS URI is part of the lexical form."""
    return f'"<{crs}> {wkt}"^^geo:wktLiteral'


def pt(lon, lat):
    return f"POINT({lon:.5f} {lat:.5f})"


def poly(ring):
    return "POLYGON((" + ", ".join(f"{lo:.5f} {la:.5f}" for lo, la in ring) + "))"


def line(points):
    return "LINESTRING(" + ", ".join(f"{lo:.5f} {la:.5f}" for lo, la in points) + ")"


# ---------------------------------------------------------------------------
# Derived data
# ---------------------------------------------------------------------------
SETTLEMENT = {s[0]: s for s in C.SETTLEMENTS}
COUNCIL = {c[0]: c for c in C.COUNCILS}
REGION = {r[0]: r for r in C.REGIONS}
COUNTRY = {c[0]: c for c in C.COUNTRIES}
SHOP = {s[0]: s for s in C.SHOPS}
AUTHOR = {a[0]: a for a in C.AUTHORS}
BOOK = {b[0]: b for b in W.BOOKS}
TRANSLATION = {t[0]: t for t in W.TRANSLATIONS}

# Shop coordinates: a deterministic offset from the town centre, so two shops
# in the same town are a few hundred metres apart rather than co-located.
SHOP_XY: dict[str, tuple[float, float]] = {}
for _sid, _lbl, _town, *_rest in C.SHOPS:
    _lat, _lon = SETTLEMENT[_town][2], SETTLEMENT[_town][3]
    _bearing = RNG.uniform(0, 2 * math.pi)
    _dist_m = RNG.uniform(120, 700)
    _dlat = (_dist_m * math.cos(_bearing)) / 111_320.0
    _dlon = (_dist_m * math.sin(_bearing)) / (111_320.0 * math.cos(math.radians(_lat)))
    SHOP_XY[_sid] = (round(_lon + _dlon, 5), round(_lat + _dlat, 5))

PLACE_XY = {s[0]: (s[3], s[2]) for s in C.SETTLEMENTS}

# Settlements, councils, regions and countries all share the bt:place- prefix,
# so their ids must be disjoint.  They were not, once: `cardiff` named both the
# city and its council area, which quietly merged the two into one resource
# with a bs:within self-loop.  Fail the build rather than ship that again.
_place_ids = [
    ("settlement", [s[0] for s in C.SETTLEMENTS]),
    ("council", [c[0] for c in C.COUNCILS]),
    ("region", [r[0] for r in C.REGIONS]),
    ("country", [c[0] for c in C.COUNTRIES]),
]
_seen: dict[str, str] = {}
for _kind, _ids in _place_ids:
    for _i in _ids:
        if _i in _seen:
            raise SystemExit(f"place id collision: {_i!r} is both a {_seen[_i]} and a {_kind}")
        _seen[_i] = _kind


def isbn13(seed_text: str) -> str:
    """A structurally valid ISBN-13 with a correct check digit."""
    r = random.Random(seed_text)
    core = "978" + "".join(str(r.randint(0, 9)) for _ in range(9))
    total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(core))
    return core + str((10 - total % 10) % 10)


BOOK_FACTS: dict[str, dict] = {}
for _b in W.BOOKS:
    _bid, _title, _auth, _imp, _year, _genre, _lang = _b
    _r = random.Random("book:" + _bid)
    BOOK_FACTS[_bid] = {
        "pages": _r.randrange(128, 656, 8),
        "rrp": round(_r.uniform(8.99, 24.0), 2),
        # ISBNs only exist from 1970 onward: a natural gap for OPTIONAL.
        "isbn": isbn13(_bid) if _year >= 1970 else None,
    }
for _t in W.TRANSLATIONS:
    _r = random.Random("book:" + _t[0])
    BOOK_FACTS[_t[0]] = {
        "pages": _r.randrange(128, 656, 8),
        "rrp": round(_r.uniform(11.0, 27.0), 2),
        "isbn": isbn13(_t[0]) if _t[6] >= 1970 else None,
    }

# Which shops publish a website: a deliberate gap for OPTIONAL to find.
HAS_WEBSITE = {s[0] for s in C.SHOPS if random.Random("web:" + s[0]).random() < 0.7}


def place(pid: str) -> str:
    return f"bt:place-{pid}"


def shop(sid: str) -> str:
    return f"bt:shop-{sid}"


def author(aid: str) -> str:
    return f"bt:author-{aid}"


def pub(pid: str) -> str:
    return f"bt:pub-{pid}"


def book(bid: str) -> str:
    return f"bt:book-{bid}"


def genre(gid: str) -> str:
    return f"bt:genre-{gid}"


def event_id(shop_id: str, date: str) -> str:
    return f"bt:event-{shop_id}-{date}"


def source(sid: str) -> str:
    return f"bt:source-{sid}"


# ===========================================================================
# 01  Vocabulary
# ===========================================================================
CLASSES = [
    ("Place", None, "Anywhere on the map: a settlement, a council area, a region or a country."),
    ("Settlement", "Place", "A town or city. The only kind of Place a bookshop sits in."),
    ("CouncilArea", "Place", "A local authority area."),
    ("Region", "Place", "A grouping of council areas. England has them; Scotland and Wales, in this dataset, do not."),
    ("Country", "Place", "Scotland, England or Wales."),
    ("Bookshop", None, "An independent bookshop on the trail."),
    ("Person", None, "A human being."),
    ("Author", "Person", "Someone who wrote at least one work in this dataset."),
    ("Publisher", None, "A publishing house or one of its imprints."),
    ("Work", None, "A book. Translations are Works in their own right."),
    ("Translation", "Work", "A work that is a translation of another work."),
    ("Series", None, "An ordered set of works."),
    ("Event", None, "Something that happened at a bookshop on a given day."),
    ("TrailSegment", None, "A walkable link between two bookshops."),
    ("StockRecord", None, "How many copies of a work a shop holds, and at what price. "
                          "The RDF 1.1 way of saying something about a relationship."),
    ("Source", None, "Something that makes claims: a guidebook, a survey, a newspaper."),
]

PROPERTIES = [
    ("within", "Place", "Place", "Directly inside another place. Chain it with + or * to reach any ancestor.", "transitive"),
    ("locatedIn", "Bookshop", "Settlement", "The settlement a shop trades in.", None),
    ("founded", "Bookshop", "xsd:gYear", "The year the shop opened.", None),
    ("floorArea", "Bookshop", "xsd:decimal", "Selling floor in square metres.", None),
    ("staffCount", "Bookshop", "xsd:integer", "People on the payroll.", None),
    ("specialises", "Bookshop", "skos:Concept", "The genre the shop is known for.", None),
    ("sellsSecondHand", "Bookshop", "xsd:boolean", "Whether the shop deals in second-hand books.", None),
    ("hasCafe", "Bookshop", "xsd:boolean", "Whether there is a cafe on the premises.", None),
    ("website", "Bookshop", "xsd:anyURI", "The shop's own site. Not every shop has one.", None),
    ("connectsTo", "Bookshop", "Bookshop", "A trail segment runs between these two shops. Walkable in either direction, "
                                           "but asserted once, so queries need connectsTo|^connectsTo.", "symmetric"),
    ("segmentFrom", "TrailSegment", "Bookshop", "One end of a trail segment.", None),
    ("segmentTo", "TrailSegment", "Bookshop", "The other end of a trail segment.", None),
    ("distanceKm", "TrailSegment", "xsd:decimal", "Straight-line distance between the two ends, in kilometres.", None),
    ("waymarked", "TrailSegment", "xsd:boolean", "Whether the segment has signposts.", None),
    ("born", "Person", "xsd:gYear", "Year of birth.", None),
    ("died", "Person", "xsd:gYear", "Year of death. Absent for the living.", None),
    ("basedIn", "Person", "Settlement", "Where the person lives or lived.", None),
    ("writesIn", "Author", "xsd:string", "BCP 47 code of the language the author writes in.", None),
    ("influencedBy", "Author", "Author", "Whom this author read first. Not transitive: influence fades.", None),
    ("wrote", "Author", "Work", "Inverse of bs:author.", None),
    ("author", "Work", "Author", "Who wrote it.", None),
    ("publishedBy", "Work", "Publisher", "The imprint that published it.", None),
    ("imprintOf", "Publisher", "Publisher", "This publisher is an imprint of that one. Chains run three deep.", None),
    ("publicationYear", "Work", "xsd:gYear", "Year of first publication of this edition.", None),
    ("genre", "Work", "skos:Concept", "A concept from the genre scheme.", None),
    ("pages", "Work", "xsd:integer", "Extent in pages.", None),
    ("rrp", "Work", "xsd:decimal", "Recommended retail price in pounds.", None),
    ("isbn", "Work", "xsd:string", "ISBN-13. Books published before 1970 do not have one.", None),
    ("originalLanguage", "Work", "xsd:string", "The language the work was written in.", None),
    ("translationOf", "Translation", "Work", "The work this is a translation of.", None),
    ("translatedBy", "Translation", "Author", "Who translated it. Not always recorded.", None),
    ("inSeries", "Work", "Series", "The series this work belongs to.", None),
    ("seriesPosition", "Work", "xsd:integer", "Position within the series, counting from 1.", None),
    ("heldAt", "Event", "Bookshop", "Where the event happened.", None),
    ("eventKind", "Event", "xsd:string", "Reading, Signing, Launch, Workshop, Panel, Book Club or Lecture.", None),
    ("eventDate", "Event", "xsd:date", "The day it happened.", None),
    ("featuring", "Event", "Author", "The author who appeared.", None),
    ("attendance", "Event", "xsd:integer", "How many people came.", None),
    ("ticketPrice", "Event", "xsd:decimal", "Price in pounds. Zero means free.", None),
    ("stocks", "Bookshop", "Work", "The shop has this work on the shelves.", None),
    ("atShop", "StockRecord", "Bookshop", "The shop this stock record is about.", None),
    ("ofWork", "StockRecord", "Work", "The work this stock record is about.", None),
    ("copies", "StockRecord", "xsd:integer", "Copies held.", None),
    ("shelfPrice", "StockRecord", "xsd:decimal", "What this shop charges, which may differ from the RRP.", None),
    ("easting", "Place", "xsd:decimal", "British National Grid easting in metres (EPSG:27700). "
                "Plane coordinates, so ordinary arithmetic on them is correct.", None),
    ("northing", "Place", "xsd:decimal", "British National Grid northing in metres (EPSG:27700).", None),
    ("population", "Settlement", "xsd:integer", "Resident population.", None),
    ("isBookTown", "Settlement", "xsd:boolean", "Whether the town is a recognised book town.", None),
    ("claimedBy", None, "Source", "Which source asserted the annotated statement.", None),
    ("confidence", None, "xsd:decimal", "How much the source is trusted, from 0 to 1.", None),
    ("statedOn", None, "xsd:date", "The date the claim was made.", None),
    ("critic", None, "xsd:string", "The reviewer's name.", None),
    ("publication", None, "xsd:string", "Where the review appeared.", None),
    ("rating", "Work", "xsd:integer", "A score out of ten. Always annotated with who gave it.", None),
    ("disputes", "Source", None, "A triple term this source says is wrong.", None),
    ("sourceKind", "Source", "xsd:string", "guidebook, survey, register, newspaper or self-reported.", None),
]


def build_vocabulary() -> str:
    """Emit the schema as an OWL 2 DL ontology.

    The specification lives in vocabulary.py; this only renders it.  Checked
    with ROBOT: see scripts/check_owl.py.
    """
    out = [prefix_block(), "\n\n", banner(
        "01  VOCABULARY  (OWL 2 DL)",
        "The schema, described in RDF so the dataset can explain itself. "
        "Query this file to find out what the data holds: it is the first "
        "thing worth asking a strange endpoint. It is also a valid OWL 2 DL "
        "ontology, which is stricter than it looks -- every class, property "
        "and datatype is declared, every property is exactly one of object, "
        "datatype or annotation, and nothing transitive is declared "
        "functional. Run scripts/check_owl.py to have that checked rather "
        "than believed.")]

    out.append(emit("<https://example.org/bookshop-trail/schema>", [
        ("a", "owl:Ontology"),
        ("rdfs:label", lit("The Bookshop Trail schema", "en")),
        ("rdfs:comment", lit("A teaching vocabulary for a fictional network of "
                             "independent bookshops at real British locations. "
                             "Conforms to OWL 2 DL.", "en")),
        ("owl:versionInfo", lit("2.0.0")),
    ]))

    # ---------------------------------------------------------------- datatypes
    out.append(section("Datatypes. OWL 2 DL requires even the XSD ones to be "
                       "declared; an undeclared datatype is the commonest way "
                       "a hand-written vocabulary falls out of the profile"))
    for dt in V.DATATYPES:
        out.append(emit(dt, [("a", "rdfs:Datatype")]))

    # ---------------------------------------------------------------- classes
    out.append(section("Classes"))
    for name, parent, comment, _group in V.CLASSES:
        out.append(emit(f"bs:{name}", [
            ("a", "owl:Class"),
            ("rdfs:subClassOf", f"bs:{parent}" if parent else None),
            ("rdfs:label", lit(name, "en")),
            ("rdfs:comment", lit(comment, "en")),
        ]))

    out.append(section("Classes borrowed from other vocabularies. Declared "
                       "here because the profile is checked over the imports "
                       "closure, and nothing is imported"))
    for iri, comment in V.EXTERNAL_CLASSES:
        out.append(emit(iri, [
            ("a", "owl:Class"),
            ("rdfs:comment", lit(comment, "en")),
        ]))

    groups = {}
    for name, _parent, _comment, group in V.CLASSES:
        if group:
            groups.setdefault(group, []).append(f"bs:{name}")
    out.append(section("Disjointness. Nothing in this dataset is both a place "
                       "and a bookshop, and saying so is what lets a reasoner "
                       "detect it if something ever is"))
    for group, members in groups.items():
        members_list = " ".join(members)
        out.append("[] a owl:AllDisjointClasses ;" + chr(10) +
                   "   owl:members ( " + members_list + " ) ." + chr(10) * 2)

    # ---------------------------------------------------------------- properties
    def domain_term(domain):
        if domain is None:
            return None
        if isinstance(domain, tuple):
            members = " ".join(d if ":" in d else f"bs:{d}" for d in domain)
            return f"[ a owl:Class ; owl:unionOf ( {members} ) ]"
        return domain if ":" in domain else f"bs:{domain}"

    out.append(section("Object properties: the range of every one is a class"))
    for name, domain, rng, comment, chars in V.OBJECT_PROPERTIES:
        types = ["owl:ObjectProperty"] + list(chars)
        out.append(emit(f"bs:{name}", [
            ("a", ", ".join(types)),
            ("rdfs:domain", domain_term(domain)),
            ("rdfs:range", domain_term(rng)),
            ("rdfs:label", lit(name, "en")),
            ("rdfs:comment", lit(comment, "en")),
        ]))

    out.append(section("Datatype properties: the range of every one is a "
                       "datatype"))
    for name, domain, rng, comment, chars in V.DATA_PROPERTIES:
        types = ["owl:DatatypeProperty"] + list(chars)
        out.append(emit(f"bs:{name}", [
            ("a", ", ".join(types)),
            ("rdfs:domain", domain_term(domain)),
            ("rdfs:range", rng),
            ("rdfs:label", lit(name, "en")),
            ("rdfs:comment", lit(comment, "en")),
        ]))

    out.append(section("Annotation properties. This is where the OWL "
                       "specification stops and RDF 1.2 begins"))
    for name, comment in V.ANNOTATION_PROPERTIES:
        out.append(emit(f"bs:{name}", [
            ("a", "owl:AnnotationProperty"),
            ("rdfs:label", lit(name, "en")),
            ("rdfs:comment", lit(comment, "en")),
        ]))

    out.append(section("Properties borrowed from other vocabularies"))
    kinds = {"object": "owl:ObjectProperty", "data": "owl:DatatypeProperty",
             "annotation": "owl:AnnotationProperty"}
    for kind, iri, domain, rng in V.EXTERNAL_PROPERTIES:
        out.append(emit(iri, [
            ("a", kinds[kind]),
            ("rdfs:domain", domain_term(domain) if kind != "annotation" else None),
            ("rdfs:range", (domain_term(rng) if kind == "object" else rng)
                            if kind != "annotation" else None),
        ]))

    out.append(section("Inverses. bs:hasImprint is asserted nowhere in the "
                       "data, so a reasoner has something to do and q44 has "
                       "something to CONSTRUCT"))
    out.append(emit("bs:wrote", [("owl:inverseOf", "bs:author")]))
    out.append(emit("bs:hasImprint", [("owl:inverseOf", "bs:imprintOf")]))
    return "".join(out)


def build_genres() -> str:
    out = [prefix_block(), "\n\n", banner(
        "02  GENRE SCHEME",
        "A SKOS taxonomy. Depth varies from two to four levels, on purpose: a "
        "fixed-length pattern such as ?g skos:broader/skos:broader bs:Fiction "
        "will silently miss whole branches, which is the lesson that makes "
        "property paths click.")]

    out.append(emit("bt:genre-scheme", [
        ("a", "skos:ConceptScheme"),
        ("rdfs:label", lit("Bookshop Trail genre scheme", "en")),
        ("skos:prefLabel", lit("Bookshop Trail genre scheme", "en")),
        ("skos:hasTopConcept", genre("literature")),
    ]))

    children: dict[str, list[str]] = {}
    for gid, _lbl, broader, _alt, _note in C.GENRES:
        if broader:
            children.setdefault(broader, []).append(gid)

    for gid, label, broader, alts, note in C.GENRES:
        pairs = [
            ("a", "skos:Concept"),
            ("skos:inScheme", "bt:genre-scheme"),
            ("skos:prefLabel", lit(label, "en")),
            ("rdfs:label", lit(label, "en")),
        ]
        for alt in alts:
            pairs.append(("skos:altLabel", lit(alt, "en")))
        for text, lang in C.GENRE_ALT_LANG.get(gid, []):
            pairs.append(("skos:prefLabel", lit(text, lang)))
        if broader:
            pairs.append(("skos:broader", genre(broader)))
        else:
            pairs.append(("skos:topConceptOf", "bt:genre-scheme"))
        kids = children.get(gid, [])
        if kids:
            pairs.append(("skos:narrower", ", ".join(genre(k) for k in kids)))
        if note:
            pairs.append(("skos:scopeNote", lit(note, "en")))
        out.append(emit(genre(gid), pairs))
    return "".join(out)


# ===========================================================================
# 03  Places
# ===========================================================================
def build_places() -> str:
    out = [prefix_block(), "\n\n", banner(
        "03  PLACES",
        "Real British places with real WGS84 coordinates, so distances and "
        "containment can be checked against a map. Settlements carry a point; "
        "council areas, regions and countries carry a simplified coverage "
        "polygon computed from the settlements inside them -- a stated "
        "envelope, not an official boundary.")]

    out.append(emit(place("gb"), [
        ("a", "bs:Place, geo:Feature"),
        ("rdfs:label", lit("Great Britain", "en")),
        ("skos:notation", lit("GB")),
    ]))

    out.append(section("Countries"))
    country_pts: dict[str, list] = {c[0]: [] for c in C.COUNTRIES}
    council_pts: dict[str, list] = {c[0]: [] for c in C.COUNCILS}
    region_pts: dict[str, list] = {r[0]: [] for r in C.REGIONS}
    for sid, _lbl, lat, lon, council, _pop, _bt in C.SETTLEMENTS:
        council_pts[council].append((lon, lat))
        parent = COUNCIL[council][2]
        if parent in region_pts:
            region_pts[parent].append((lon, lat))
            country_pts[REGION[parent][2]].append((lon, lat))
        else:
            country_pts[parent].append((lon, lat))

    for cid, label, alt_name, alt_lang in C.COUNTRIES:
        pairs = [
            ("a", "bs:Country, bs:Place, geo:Feature"),
            ("rdfs:label", lit(label, "en")),
        ]
        if alt_name:
            pairs.append(("rdfs:label", lit(alt_name, alt_lang)))
        pairs += [
            ("bs:within", place("gb")),
            ("geo:hasGeometry", f"bt:geom-{cid}"),
            ("geo:hasDefaultGeometry", f"bt:geom-{cid}"),
        ]
        out.append(emit(place(cid), pairs))
        out.append(emit(f"bt:geom-{cid}", [
            ("a", "sf:Polygon, geo:Geometry"),
            ("geo:asWKT", wkt_lit(poly(coverage_polygon(country_pts[cid], 25000)))),
        ]))

    out.append(section("Regions (England only)"))
    for rid, label, country in C.REGIONS:
        out.append(emit(place(rid), [
            ("a", "bs:Region, bs:Place, geo:Feature"),
            ("rdfs:label", lit(label, "en")),
            ("bs:within", place(country)),
            ("geo:hasGeometry", f"bt:geom-{rid}"),
            ("geo:hasDefaultGeometry", f"bt:geom-{rid}"),
        ]))
        out.append(emit(f"bt:geom-{rid}", [
            ("a", "sf:Polygon, geo:Geometry"),
            ("geo:asWKT", wkt_lit(poly(coverage_polygon(region_pts[rid], 18000)))),
        ]))

    out.append(section("Council areas"))
    for cid, label, parent in C.COUNCILS:
        out.append(emit(place(cid), [
            ("a", "bs:CouncilArea, bs:Place, geo:Feature"),
            ("rdfs:label", lit(label, "en")),
            ("bs:within", place(parent)),
            ("geo:hasGeometry", f"bt:geom-{cid}"),
            ("geo:hasDefaultGeometry", f"bt:geom-{cid}"),
        ]))
        out.append(emit(f"bt:geom-{cid}", [
            ("a", "sf:Polygon, geo:Geometry"),
            ("geo:asWKT", wkt_lit(poly(coverage_polygon(council_pts[cid], 12000)))),
        ]))

    out.append(section("Settlements"))
    for sid, label, lat, lon, council, pop, is_book_town in C.SETTLEMENTS:
        pairs = [
            ("a", "bs:Settlement, bs:Place, geo:Feature"),
            ("rdfs:label", lit(label, "en")),
        ]
        for text, lang in C.PLACE_ALT_NAMES.get(sid, []):
            pairs.append(("rdfs:label", lit(text, lang)))
        dbp = C.DBPEDIA.get(sid)
        if dbp:
            pairs.append(("owl:sameAs",
                          "<http://dbpedia.org/resource/"
                          + quote(dbp, safe="_,-") + ">"))
        pairs += [
            ("bs:within", place(council)),
            ("bs:population", typed(pop, "xsd:integer")),
            ("bs:isBookTown", "true" if is_book_town else "false"),
            ("wgs84:lat", typed(f"{lat}", "xsd:decimal")),
            ("wgs84:long", typed(f"{lon}", "xsd:decimal")),
            ("geo:hasGeometry", f"bt:geom-{sid}"),
            ("geo:hasDefaultGeometry", f"bt:geom-{sid}"),
        ]
        out.append(emit(place(sid), pairs))
        out.append(emit(f"bt:geom-{sid}", [
            ("a", "sf:Point, geo:Geometry"),
            ("geo:asWKT", wkt_lit(pt(lon, lat))),
        ]))
    return "".join(out)


# ===========================================================================
# 04  Bookshops
# ===========================================================================
def build_bookshops() -> str:
    out = [prefix_block(), "\n\n", banner(
        "04  BOOKSHOPS",
        "Thirty-three invented shops in real towns. Every shop has a point "
        "geometry a few hundred metres from the town centre, so two shops in "
        "the same town are genuinely a short walk apart. Not every shop has a "
        "website: that gap is what OPTIONAL is for.")]

    for sid, label, town, founded, area, staff, spec, second_hand, cafe in C.SHOPS:
        lon, lat = SHOP_XY[sid]
        pairs = [
            ("a", "bs:Bookshop, geo:Feature"),
            ("rdfs:label", lit(label, "en")),
            ("bs:locatedIn", place(town)),
            ("bs:founded", typed(founded, "xsd:gYear")),
            ("bs:floorArea", typed(f"{area}.0", "xsd:decimal")),
            ("bs:staffCount", typed(staff, "xsd:integer")),
            ("bs:specialises", genre(spec)),
            ("bs:sellsSecondHand", "true" if second_hand else "false"),
            ("bs:hasCafe", "true" if cafe else "false"),
        ]
        if sid in HAS_WEBSITE:
            pairs.append(("bs:website", typed(f"https://example.org/shops/{sid}", "xsd:anyURI")))
        pairs += [
            ("wgs84:lat", typed(f"{lat}", "xsd:decimal")),
            ("wgs84:long", typed(f"{lon}", "xsd:decimal")),
            ("geo:hasGeometry", f"bt:geom-shop-{sid}"),
            ("geo:hasDefaultGeometry", f"bt:geom-shop-{sid}"),
        ]
        out.append(emit(shop(sid), pairs))
        out.append(emit(f"bt:geom-shop-{sid}", [
            ("a", "sf:Point, geo:Geometry"),
            ("geo:asWKT", wkt_lit(pt(lon, lat))),
        ]))
    return "".join(out)


# ===========================================================================
# 05  People and publishers
# ===========================================================================
def build_people() -> str:
    out = [prefix_block(), "\n\n", banner(
        "05  AUTHORS AND PUBLISHERS",
        "The influence graph is a directed graph with long chains, a diamond, "
        "and one mutual pair -- because a learner has to discover that "
        "bs:influencedBy+ copes with a cycle and a hand-rolled recursive join "
        "does not. Publisher imprints nest three deep.")]

    out.append(section("Publishers"))
    for pid, label, parent, founded, town in C.PUBLISHERS:
        out.append(emit(pub(pid), [
            ("a", "bs:Publisher"),
            ("rdfs:label", lit(label, "en")),
            ("bs:imprintOf", pub(parent) if parent else None),
            ("bs:founded", typed(founded, "xsd:gYear")),
            ("bs:locatedIn", place(town)),
        ]))

    out.append(section("Authors"))
    influences = {a[0]: list(a[6]) for a in C.AUTHORS}
    for a, b in C.MUTUAL_INFLUENCE:
        if b not in influences[a]:
            influences[a].append(b)
        if a not in influences[b]:
            influences[b].append(a)

    for aid, name, born, died, based, lang, _infl in C.AUTHORS:
        pairs = [
            ("a", "bs:Author, bs:Person"),
            ("rdfs:label", lit(name, "en")),
            ("bs:born", typed(born, "xsd:gYear")),
            ("bs:died", typed(died, "xsd:gYear") if died else None),
            ("bs:basedIn", place(based)),
            ("bs:writesIn", lit(lang)),
        ]
        infl = influences[aid]
        if infl:
            pairs.append(("bs:influencedBy", ", ".join(author(i) for i in infl)))
        out.append(emit(author(aid), pairs))
    return "".join(out)


# ===========================================================================
# 06  Books
# ===========================================================================
def build_books() -> str:
    out = [prefix_block(), "\n\n", banner(
        "06  WORKS",
        "Sixty-eight books and six translations. Books published before 1970 "
        "have no ISBN, which is both true of the world and useful: it gives "
        "OPTIONAL and NOT EXISTS something real to find.")]

    for bid, title, aid, imprint, year, gid, lang in W.BOOKS:
        f = BOOK_FACTS[bid]
        out.append(emit(book(bid), [
            ("a", "bs:Work"),
            ("rdfs:label", lit(title, "en" if lang == "en" else lang)),
            ("dct:title", lit(title, "en" if lang == "en" else lang)),
            ("bs:author", author(aid)),
            ("bs:publishedBy", pub(imprint)),
            ("bs:publicationYear", typed(year, "xsd:gYear")),
            ("bs:genre", genre(gid)),
            ("bs:pages", typed(f["pages"], "xsd:integer")),
            ("bs:rrp", typed(f'{f["rrp"]:.2f}', "xsd:decimal")),
            ("bs:isbn", lit(f["isbn"]) if f["isbn"] else None),
            ("bs:originalLanguage", lit(lang)),
        ]))

    out.append(section("Translations -- the base direction on these is what "
                       "LANGDIR and hasLANGDIR are for"))
    for tid, title, of_book, lang, direction, translator, year, imprint in W.TRANSLATIONS:
        f = BOOK_FACTS[tid]
        label = lit(title, lang, direction if direction == "rtl" else None)
        out.append(emit(book(tid), [
            ("a", "bs:Translation, bs:Work"),
            ("rdfs:label", label),
            ("dct:title", label),
            ("bs:translationOf", book(of_book)),
            ("bs:author", author(BOOK[of_book][2])),
            ("bs:translatedBy", author(translator) if translator else None),
            ("bs:publishedBy", pub(imprint)),
            ("bs:publicationYear", typed(year, "xsd:gYear")),
            ("bs:genre", genre("translated-fiction")),
            ("bs:pages", typed(f["pages"], "xsd:integer")),
            ("bs:rrp", typed(f'{f["rrp"]:.2f}', "xsd:decimal")),
            ("bs:isbn", lit(f["isbn"]) if f["isbn"] else None),
            ("bs:originalLanguage", lit(BOOK[of_book][6])),
        ]))

    out.append(section("Series"))
    for sid, label, members in W.SERIES:
        out.append(emit(f"bt:series-{sid}", [
            ("a", "bs:Series"),
            ("rdfs:label", lit(label, "en")),
        ]))
        for i, bid in enumerate(members, start=1):
            out.append(emit(book(bid), [
                ("bs:inSeries", f"bt:series-{sid}"),
                ("bs:seriesPosition", typed(i, "xsd:integer")),
            ]))

    out.append(section("bs:wrote -- asserted so that beginners have an easy "
                       "forward path before they meet ^bs:author"))
    by_author: dict[str, list[str]] = {}
    for bid, _t, aid, *_ in W.BOOKS:
        by_author.setdefault(aid, []).append(bid)
    for aid, bids in by_author.items():
        out.append(emit(author(aid), [("bs:wrote", ", ".join(book(b) for b in bids))]))
    return "".join(out)


# ===========================================================================
# 07  Events
# ===========================================================================
def build_events() -> str:
    out = [prefix_block(), "\n\n", banner(
        "07  EVENTS",
        "Fifty-nine events across 2025. Attendance and ticket price are what "
        "the aggregation and sub-query modules work on: totals per shop, "
        "averages per region, the best-attended event in each country.")]

    for shop_id, kind, date, aid, attendance, price in W.EVENTS:
        eid = event_id(shop_id, date)
        out.append(emit(eid, [
            ("a", "bs:Event"),
            ("rdfs:label", lit(f"{kind} with {AUTHOR[aid][1]}", "en")),
            ("bs:heldAt", shop(shop_id)),
            ("bs:eventKind", lit(kind)),
            ("bs:eventDate", typed(date, "xsd:date")),
            ("bs:featuring", author(aid)),
            ("bs:attendance", typed(attendance, "xsd:integer")),
            ("bs:ticketPrice", typed(f"{price:.2f}", "xsd:decimal")),
        ]))
    return "".join(out)


# ===========================================================================
# 08  Trail
# ===========================================================================
def build_trail() -> str:
    out = [prefix_block(), "\n\n", banner(
        "08  THE TRAIL",
        "Thirty-three segments joining the shops. Mostly linear, with two "
        "branches and one loop -- and one pair of shops in the south west that "
        "connects to nothing else. bs:connectsTo+ therefore returns a strictly "
        "smaller set than 'every shop', which is the point.")]

    for a, b, waymarked in W.TRAIL:
        seg = f"bt:seg-{a}-{b}"
        pa, pb = SHOP_XY[a], SHOP_XY[b]
        dist = haversine_km(pa, pb)
        # A midpoint nudged sideways, so the segment is a real line rather
        # than two points: geof:length then has something to measure.
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        n = math.hypot(dx, dy) or 1.0
        mx += -dy / n * 0.02
        my += dx / n * 0.02
        out.append(emit(seg, [
            ("a", "bs:TrailSegment, geo:Feature"),
            ("rdfs:label", lit(f"{SHOP[a][1]} to {SHOP[b][1]}", "en")),
            ("bs:segmentFrom", shop(a)),
            ("bs:segmentTo", shop(b)),
            ("bs:distanceKm", typed(f"{dist:.1f}", "xsd:decimal")),
            ("bs:waymarked", "true" if waymarked else "false"),
            ("geo:hasGeometry", f"bt:geom-{seg[3:]}"),
            ("geo:hasDefaultGeometry", f"bt:geom-{seg[3:]}"),
        ]))
        out.append(emit(f"bt:geom-{seg[3:]}", [
            ("a", "sf:LineString, geo:Geometry"),
            ("geo:asWKT", wkt_lit(line([pa, (round(mx, 5), round(my, 5)), pb]))),
        ]))
        out.append(emit(shop(a), [("bs:connectsTo", shop(b))]))
    return "".join(out)


# ===========================================================================
# 09  Stock (RDF 1.1 style)
# ===========================================================================
def build_stock() -> str:
    out = [prefix_block(), "\n\n", banner(
        "09  STOCK, THE RDF 1.1 WAY",
        "Ninety-five stock records. Each says how many copies a shop holds "
        "and at what price -- facts about a relationship, not about a thing. "
        "RDF 1.1 has to invent a node to hang them on. File 10 says the same "
        "thing in RDF 1.2 with no invented node at all; comparing the two is "
        "the whole point of the SPARQL 1.2 module.")]

    for shop_id, work, copies, price in W.STOCK:
        out.append(emit(f"bt:stock-{shop_id}--{work}", [
            ("a", "bs:StockRecord"),
            ("bs:atShop", shop(shop_id)),
            ("bs:ofWork", book(work)),
            ("bs:copies", typed(copies, "xsd:integer")),
            ("bs:shelfPrice", typed(f"{price:.2f}", "xsd:decimal")),
        ]))

    out.append(section("The plain link, so simple queries stay simple"))
    by_shop: dict[str, list[str]] = {}
    for shop_id, work, _c, _p in W.STOCK:
        by_shop.setdefault(shop_id, []).append(work)
    for shop_id, works in by_shop.items():
        out.append(emit(shop(shop_id), [("bs:stocks", ", ".join(book(w) for w in works))]))

    out.append(section("Sources that make claims about this dataset"))
    for sid, label, kind, confidence in W.SOURCES:
        out.append(emit(source(sid), [
            ("a", "bs:Source, prov:Entity"),
            ("rdfs:label", lit(label, "en")),
            ("bs:sourceKind", lit(kind)),
            ("bs:confidence", typed(f"{confidence:.2f}", "xsd:decimal")),
        ]))
    return "".join(out)


# ===========================================================================
# 10  RDF 1.2 annotations
# ===========================================================================
def build_annotations() -> str:
    out = [prefix_block(), "\n\n", banner(
        "10  CLAIMS ABOUT CLAIMS  (RDF 1.2 ONLY)",
        "This file will not parse in an RDF 1.1 tool, and that is deliberate: "
        "it is the file that shows what RDF 1.2 buys you. Everything here is a "
        "statement about a statement -- who said it, when, how much they are "
        "trusted -- written with the annotation syntax {| ... |} and with "
        "triple terms <<( s p o )>>.")]

    out.append(section("Stock, said in RDF 1.2 -- compare with file 09"))
    out.append("# The base triple is asserted by the annotation syntax itself, so\n"
               "# this file re-states nothing that file 09 already holds.\n\n")
    for shop_id, work, copies, price in W.STOCK[:24]:
        out.append(f"{shop(shop_id)} bs:stocks {book(work)}\n"
                   f"    {{| bs:copies {typed(copies, 'xsd:integer')} ;\n"
                   f"       bs:shelfPrice {typed(f'{price:.2f}', 'xsd:decimal')} |}} .\n\n")

    out.append(section("Disputed founding dates -- two sources, one shop, "
                       "different answers"))
    for shop_id, year, src, confidence in W.DISPUTED_FOUNDING:
        out.append(f"{shop(shop_id)} bs:founded {typed(year, 'xsd:gYear')}\n"
                   f"    {{| bs:claimedBy {source(src)} ;\n"
                   f"       bs:confidence {typed(f'{confidence:.2f}', 'xsd:decimal')} |}} .\n\n")

    out.append(section("Attendance as reported by different sources"))
    for shop_id, _kind, date, figure, src in W.DISPUTED_ATTENDANCE:
        out.append(f"{event_id(shop_id, date)} bs:attendance {typed(figure, 'xsd:integer')}\n"
                   f"    {{| bs:claimedBy {source(src)} |}} .\n\n")

    out.append(section("Reviews -- the score is the fact, the reviewer is the "
                       "annotation"))
    for work, score, critic, date, publication in W.RATINGS:
        out.append(f"{book(work)} bs:rating {typed(score, 'xsd:integer')}\n"
                   f"    {{| bs:critic {lit(critic)} ;\n"
                   f"       bs:statedOn {typed(date, 'xsd:date')} ;\n"
                   f"       bs:publication {lit(publication)} |}} .\n\n")

    out.append(section("Triple terms in object position -- a source pointing "
                       "at a statement it rejects"))
    out.append(emit(source("national-register"), [
        ("bs:disputes", f"<<( {shop('ex-libris')} bs:founded {typed(1921, 'xsd:gYear')} )>>"),
    ]))
    out.append(emit(source("county-survey"), [
        ("bs:disputes", f"<<( {shop('candlemas')} bs:founded {typed(1928, 'xsd:gYear')} )>>"),
    ]))
    out.append(emit(source("trail-guide-2024"), [
        ("bs:disputes", f"<<( {shop('castle-steps')} bs:founded {typed(1965, 'xsd:gYear')} )>>"),
    ]))

    out.append(section("Language with a base direction"))
    out.append("# Every translation label in file 06 already carries a direction where\n"
               "# the script needs one.  These are the shop notices in the same\n"
               "# languages, so hasLANGDIR has more than six rows to work with.\n\n")
    notices = [
        ("verso", "Translated fiction from twenty languages", "en", None),
        ("verso", "خيال مترجم من عشرين لغة", "ar", "rtl"),
        ("turn-the-page", "New translations every month", "en", None),
        ("turn-the-page", "תרגומים חדשים מדי חודש", "he", "rtl"),
        ("cliff-road", "Barddoniaeth Gymraeg", "cy", None),
        ("castle-steps", "Llyfrau hanes lleol", "cy", None),
        ("northern-light", "Leabhraichean Gaidhlig", "gd", None),
        ("sea-margin", "Sgeulachdan an eilein", "gd", None),
    ]
    for shop_id, text, lang, direction in notices:
        out.append(emit(shop(shop_id), [
            ("skos:note", lit(text, lang, direction)),
        ]))
    return "".join(out)


# ===========================================================================
# 11  British National Grid geometry
# ===========================================================================
def build_bng() -> str:
    out = [prefix_block(), "\n\n", banner(
        "11  THE SAME PLACES ON THE BRITISH NATIONAL GRID  (ADVANCED)",
        "Every settlement and shop again, in EPSG:27700 metres instead of "
        "degrees, both as a WKT geometry and as two plain decimals. The "
        "decimals matter: a projected grid is flat, so Pythagoras on eastings "
        "and northings is correct, while the same sum on degrees is not. An "
        "engine that reads the CRS URI in a WKT literal will answer distance "
        "and containment questions across both files; one that assumes CRS84 "
        "will produce nonsense. That is the lesson. HOLOS reads all four "
        "systems; check your own engine before trusting the answers.")]

    out.append(section("Settlements"))
    for sid, label, lat, lon, *_ in C.SETTLEMENTS:
        e, n = to_bng(lon, lat)
        out.append(emit(place(sid), [
            ("geo:hasGeometry", f"bt:geom-{sid}-bng"),
            ("bs:easting", typed(f"{e:.1f}", "xsd:decimal")),
            ("bs:northing", typed(f"{n:.1f}", "xsd:decimal")),
        ]))
        out.append(emit(f"bt:geom-{sid}-bng", [
            ("a", "sf:Point, geo:Geometry"),
            ("rdfs:label", lit(f"{label} on the National Grid", "en")),
            ("geo:asWKT", wkt_lit(f"POINT({e:.1f} {n:.1f})", BNG_URI)),
        ]))

    out.append(section("Bookshops"))
    for sid, label, *_ in C.SHOPS:
        lon, lat = SHOP_XY[sid]
        e, n = to_bng(lon, lat)
        out.append(emit(shop(sid), [
            ("geo:hasGeometry", f"bt:geom-shop-{sid}-bng"),
            ("bs:easting", typed(f"{e:.1f}", "xsd:decimal")),
            ("bs:northing", typed(f"{n:.1f}", "xsd:decimal")),
        ]))
        out.append(emit(f"bt:geom-shop-{sid}-bng", [
            ("a", "sf:Point, geo:Geometry"),
            ("rdfs:label", lit(f"{label} on the National Grid", "en")),
            ("geo:asWKT", wkt_lit(f"POINT({e:.1f} {n:.1f})", BNG_URI)),
        ]))
    return "".join(out)


# ===========================================================================
# Assembly
# ===========================================================================
MODULES = [
    ("01-vocabulary.ttl", build_vocabulary),
    ("02-genres.ttl", build_genres),
    ("03-places.ttl", build_places),
    ("04-bookshops.ttl", build_bookshops),
    ("05-people.ttl", build_people),
    ("06-books.ttl", build_books),
    ("07-events.ttl", build_events),
    ("08-trail.ttl", build_trail),
    ("09-stock.ttl", build_stock),
    ("10-annotations-1.2.ttl", build_annotations),
    ("11-bng-geometry.ttl", build_bng),
]

GRAPH_OF = {
    "01-vocabulary.ttl": "bt:graph-vocabulary",
    "02-genres.ttl": "bt:graph-genres",
    "03-places.ttl": "bt:graph-places",
    "04-bookshops.ttl": "bt:graph-shops",
    "05-people.ttl": "bt:graph-people",
    "06-books.ttl": "bt:graph-books",
    "07-events.ttl": "bt:graph-events",
    "08-trail.ttl": "bt:graph-trail",
    "09-stock.ttl": "bt:graph-stock",
    "10-annotations-1.2.ttl": "bt:graph-claims",
    "11-bng-geometry.ttl": "bt:graph-bng",
}


def strip_prologue(text: str) -> str:
    """Drop the @prefix block so files can be concatenated."""
    lines = text.splitlines(keepends=True)
    out, seen = [], False
    for line in lines:
        if line.startswith("@prefix"):
            seen = True
            continue
        if seen or line.strip():
            out.append(line)
    return "".join(out)


def count_triples(path: Path) -> int | None:
    """Ask whichever engine is installed how many distinct triples a file
    holds.  Hard-coding the figure in the README and the course document went
    stale the first time a property was added to the vocabulary, so the
    figures are now measured at build time and written to
    build/dataset-stats.json."""
    import json as _json
    import os
    import shutil as _shutil
    import subprocess

    holos = Path(os.environ.get(
        "HOLOS_EXE", r"C:/repos/new_triplestore_sparql_engine/target/release/holos.exe"))
    if holos.exists():
        p = subprocess.run(
            [str(holos), "query", "--data", str(path),
             "--query", "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in reversed(p.stdout.splitlines()):
            if line.startswith("{"):
                try:
                    b = _json.loads(line)["results"]["bindings"]
                    return int(b[0]["n"]["value"])
                except (KeyError, IndexError, ValueError):
                    return None
    riot = Path(os.environ.get("JENA_HOME", r"C:/apache-jena-6.2.0")) / "bat" / "riot.bat"
    if riot.exists():
        p = subprocess.run([str(riot), "--count", str(path)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env={**os.environ,
                           "JENA_HOME": str(riot.parent.parent)})
        for line in p.stdout.splitlines():
            if "Triples =" in line:
                return int(line.split("=")[-1].strip().replace(",", ""))
    return None


def write_stats() -> None:
    import json as _json
    stats = {
        "settlements": len(C.SETTLEMENTS),
        "settlements_without_shop": len(
            {s[0] for s in C.SETTLEMENTS} - {s[2] for s in C.SHOPS}),
        "councils": len(C.COUNCILS),
        "regions": len(C.REGIONS),
        "countries": len(C.COUNTRIES),
        "shops": len(C.SHOPS),
        "towns_with_shops": len({s[2] for s in C.SHOPS}),
        "authors": len(C.AUTHORS),
        "publishers": len(C.PUBLISHERS),
        "genres": len(C.GENRES),
        "books": len(W.BOOKS),
        "translations": len(W.TRANSLATIONS),
        "works": len(W.BOOKS) + len(W.TRANSLATIONS),
        "events": len(W.EVENTS),
        "stock_records": len(W.STOCK),
        "trail_segments": len(W.TRAIL),
        "languages": len({b[6] for b in W.BOOKS} | {t[3] for t in W.TRANSLATIONS}),
    }
    for name in ("bookshop-trail-1.1.ttl", "bookshop-trail-1.2.ttl",
                 "bookshop-trail-full.ttl"):
        n = count_triples(DATA / name)
        if n is not None:
            stats["triples_" + name.replace("bookshop-trail-", "").replace(".ttl", "")
                  .replace(".", "_").replace("-", "_")] = n
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    (out / "dataset-stats.json").write_text(_json.dumps(stats, indent=2), encoding="utf-8")
    print(f"  wrote build/dataset-stats.json  "
          f"({stats.get('triples_1_1', '?')} triples in the 1.1 dataset)")


def main() -> None:
    written = {}
    for filename, builder in MODULES:
        text = builder()
        (DATA / filename).write_text(text, encoding="utf-8")
        written[filename] = text
        print(f"  wrote data/{filename:26} {len(text.splitlines()):5} lines")

    combos = {
        "bookshop-trail-1.1.ttl": [m for m, _ in MODULES if "1.2" not in m and "bng" not in m],
        "bookshop-trail-1.2.ttl": [m for m, _ in MODULES if "bng" not in m],
        "bookshop-trail-full.ttl": [m for m, _ in MODULES],
    }
    headers = {
        "bookshop-trail-1.1.ttl":
            ("THE BOOKSHOP TRAIL -- COMPLETE DATASET, RDF 1.1",
             "Files 01 to 09 in one document. Loads in any SPARQL 1.1 engine, "
             "including the SPARQL panel of the Turtle Editor Viewer. Start here."),
        "bookshop-trail-1.2.ttl":
            ("THE BOOKSHOP TRAIL -- COMPLETE DATASET, RDF 1.2",
             "Files 01 to 10. Needs an RDF 1.2 parser: it contains annotation "
             "syntax and triple terms. Works in the Turtle Editor Viewer, in "
             "HOLOS and in Jena 6."),
        "bookshop-trail-full.ttl":
            ("THE BOOKSHOP TRAIL -- EVERYTHING, INCLUDING THE NATIONAL GRID",
             "Files 01 to 11. Adds a second geometry per settlement in "
             "EPSG:27700, for the coordinate-reference-system module."),
    }
    written_combined = {}
    for name, parts in combos.items():
        title, blurb = headers[name]
        body = [prefix_block(), "\n\n", banner(title, blurb)]
        for part in parts:
            body.append(f"\n#\n#  ==== {part} " + "=" * (60 - len(part)) + "\n#\n\n")
            body.append(strip_prologue(written[part]))
        text = "".join(body)
        (DATA / name).write_text(text, encoding="utf-8")
        written_combined[name] = text
        print(f"  wrote data/{name:26} {len(text.splitlines()):5} lines")

    # TriG: one named graph per module, for the GRAPH / FROM NAMED module.
    trig = [prefix_block(), "\n\n", banner(
        "THE BOOKSHOP TRAIL AS A DATASET OF NAMED GRAPHS",
        "The same triples, filed by subject matter. Load this instead of the "
        "Turtle when you want to practise GRAPH, FROM and FROM NAMED. The "
        "default graph holds only the description of the graphs themselves.")]
    trig.append(emit("bt:dataset", [
        ("a", "prov:Entity"),
        ("rdfs:label", lit("The Bookshop Trail", "en")),
        ("dct:description", lit("A teaching dataset for SPARQL 1.1 and 1.2.", "en")),
    ]))
    for filename, _ in MODULES:
        if "bng" in filename:
            continue
        g = GRAPH_OF[filename]
        trig.append(emit(g, [
            ("a", "prov:Entity"),
            ("rdfs:label", lit(filename.replace(".ttl", ""), "en")),
            ("dct:isPartOf", "bt:dataset"),
        ]))
    for filename, _ in MODULES:
        if "bng" in filename:
            continue
        g = GRAPH_OF[filename]
        body = strip_prologue(written[filename])
        indented = "\n".join(("    " + l) if l.strip() else l for l in body.splitlines())
        trig.append(f"\n{g} {{\n{indented}\n}}\n")
    (DATA / "bookshop-trail.trig").write_text("".join(trig), encoding="utf-8")
    print("  wrote data/bookshop-trail.trig")
    write_stats()


if __name__ == "__main__":
    main()
