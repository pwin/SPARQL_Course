# -*- coding: utf-8 -*-
"""The Bookshop Trail vocabulary, specified as an OWL 2 DL ontology.

OWL 2 DL is stricter than the RDFS-with-a-bit-of-OWL that most published
vocabularies use, and the strictness is the point of specifying it that way:
a DL ontology can be handed to a reasoner with a decidability guarantee.  Four
rules do most of the work, and the first three are what an RDFS vocabulary
usually breaks:

  1. Every IRI used as a class, property or datatype must be DECLARED --
     including the ones borrowed from other vocabularies and including the
     built-in XSD datatypes.
  2. A property is an object property, a datatype property or an annotation
     property.  Exactly one.  `rdf:Property` is not a declaration.
  3. A datatype property's range must be a datatype; an object property's
     range must be a class.
  4. A transitive property is "non-simple" and may not be declared functional
     or used in a cardinality restriction.

Checked with:

    java -jar lib/owl/robot.jar validate-profile --profile DL \\
         --input data/01-vocabulary.ttl
"""

# ---------------------------------------------------------------------------
# Classes.  (name, parent-or-None, comment, disjoint-group-or-None)
# ---------------------------------------------------------------------------
CLASSES = [
    ("Place", None,
     "Anywhere on the map: a settlement, a council area, a region or a country.",
     "thing"),
    ("Settlement", "Place",
     "A town or city. The only kind of Place a bookshop sits in.", "place"),
    ("CouncilArea", "Place", "A local authority area.", "place"),
    ("Region", "Place",
     "A grouping of council areas. England has them; Scotland and Wales, in "
     "this dataset, do not.", "place"),
    ("Country", "Place", "Scotland, England or Wales.", "place"),

    ("Bookshop", None, "An independent bookshop on the trail.", "thing"),
    ("Person", None, "A human being.", "thing"),
    ("Author", "Person",
     "Someone who wrote at least one work in this dataset.", None),
    ("Publisher", None, "A publishing house or one of its imprints.", "thing"),
    ("Work", None, "A book. Translations are Works in their own right.", "thing"),
    ("Translation", "Work", "A work that is a translation of another work.", None),
    ("Series", None, "An ordered set of works.", "thing"),
    ("Event", None, "Something that happened at a bookshop on a given day.", "thing"),
    ("TrailSegment", None, "A walkable link between two bookshops.", "thing"),
    ("StockRecord", None,
     "How many copies of a work a shop holds, and at what price. The RDF 1.1 "
     "way of saying something about a relationship.", "thing"),
    ("Source", None,
     "Something that makes claims: a guidebook, a survey, a newspaper.", "thing"),
    ("DataIssue", None,
     "A finding produced by the validation report in q88. Nothing in the "
     "shipped data has this type; the CONSTRUCT mints them.", "thing"),
]

# Classes borrowed from other vocabularies.  OWL 2 DL needs them declared even
# though they are defined elsewhere, because the profile is checked over the
# imports closure and nothing is imported here.
EXTERNAL_CLASSES = [
    ("skos:Concept", "A concept in the genre scheme."),
    ("skos:ConceptScheme", "The genre scheme itself."),
    ("geo:Feature", "A GeoSPARQL feature: something with a geometry."),
    ("geo:Geometry", "A GeoSPARQL geometry."),
    ("sf:Point", "A Simple Features point."),
    ("sf:Polygon", "A Simple Features polygon."),
    ("sf:LineString", "A Simple Features line."),
    ("prov:Entity", "A PROV entity, used for the named graphs and the sources."),
]

# Datatypes.  Undeclared datatypes are the commonest OWL 2 DL violation in a
# hand-written vocabulary, because RDFS never asked for the declaration.
# Only datatypes that are IN the OWL 2 datatype map, and even these need no
# rdfs:Datatype declaration -- OWL 2 knows them.  Declaring a built-in turns it
# into a *defined* datatype, and using a defined datatype in an assertion is
# itself a DL violation.  So this list is empty, and the comment is the lesson.
DATATYPES = []

YEAR_NOTE = (
    "No range is declared, and that is deliberate: the shipped 1.1 data types this as xsd:gYear, which is not in the OWL 2 datatype map, so declaring the range would put the specification outside OWL 2 DL. Declaring xsd:integer instead would be worse -- it would be false of the data. See data/bookshop-trail-owl-dl.ttl."
)
DATE_NOTE = (
    "No range is declared, and that is deliberate: the shipped 1.1 data types this as xsd:date, which is not in the OWL 2 datatype map, so declaring the range would put the specification outside OWL 2 DL. Declaring xsd:integer instead would be worse -- it would be false of the data. See data/bookshop-trail-owl-dl.ttl."
)


# ---------------------------------------------------------------------------
# Object properties.  (name, domain, range, comment, characteristics)
# `domain` may be a tuple, which becomes an owl:unionOf.
# ---------------------------------------------------------------------------
OBJECT_PROPERTIES = [
    ("within", "Place", "Place",
     "Directly inside another place. Chain it with + or * to reach any "
     "ancestor. Transitive, and therefore non-simple: OWL 2 DL forbids "
     "declaring it functional or counting it in a cardinality restriction.",
     ["owl:TransitiveProperty"]),
    ("locatedIn", ("Bookshop", "Publisher"), "Settlement",
     "The settlement a shop or publisher trades in.",
     ["owl:FunctionalProperty"]),
    ("specialises", "Bookshop", "skos:Concept",
     "The genre the shop is known for.", ["owl:FunctionalProperty"]),
    ("connectsTo", "Bookshop", "Bookshop",
     "A trail segment runs between these two shops. Walkable in either "
     "direction, but asserted once, so queries need connectsTo|^connectsTo.",
     ["owl:SymmetricProperty"]),
    ("segmentFrom", "TrailSegment", "Bookshop",
     "One end of a trail segment.", ["owl:FunctionalProperty"]),
    ("segmentTo", "TrailSegment", "Bookshop",
     "The other end of a trail segment.", ["owl:FunctionalProperty"]),
    ("basedIn", "Person", "Settlement",
     "Where the person lives or lived.", ["owl:FunctionalProperty"]),
    ("influencedBy", "Author", "Author",
     "Whom this author read first. Deliberately NOT transitive: influence "
     "fades, and the course wants bs:influencedBy+ to be the learner's job "
     "rather than the reasoner's.", []),
    ("wrote", "Author", "Work", "Inverse of bs:author.", []),
    ("author", "Work", "Author", "Who wrote it.", []),
    ("publishedBy", "Work", "Publisher",
     "The imprint that published it.", ["owl:FunctionalProperty"]),
    ("imprintOf", "Publisher", "Publisher",
     "This publisher is an imprint of that one. Chains run three deep. Not "
     "declared transitive, so that q44 has something to CONSTRUCT.",
     ["owl:FunctionalProperty"]),
    ("hasImprint", "Publisher", "Publisher",
     "Asserted nowhere in the data: it exists so a reasoner can infer it, and "
     "so ^bs:imprintOf has something to be compared with.", []),
    ("genre", "Work", "skos:Concept",
     "A concept from the genre scheme.", []),
    ("translationOf", "Translation", "Work",
     "The work this is a translation of.", ["owl:FunctionalProperty"]),
    ("translatedBy", "Translation", "Author",
     "Who translated it. Not always recorded.", []),
    ("inSeries", "Work", "Series",
     "The series this work belongs to.", ["owl:FunctionalProperty"]),
    ("heldAt", "Event", "Bookshop",
     "Where the event happened.", ["owl:FunctionalProperty"]),
    ("featuring", "Event", "Author", "The author who appeared.", []),
    ("stocks", "Bookshop", "Work",
     "The shop has this work on the shelves.", []),
    ("atShop", "StockRecord", "Bookshop",
     "The shop this stock record is about.", ["owl:FunctionalProperty"]),
    ("ofWork", "StockRecord", "Work",
     "The work this stock record is about.", ["owl:FunctionalProperty"]),
    ("claimedBy", None, "Source",
     "Which source asserted the annotated statement. Its subject is an RDF "
     "1.2 reifier, so no domain is stated.", []),
    ("about", "DataIssue", None,
     "What a validation finding is about. Range unstated because a finding "
     "may be about a work or a shop.", []),
]

# ---------------------------------------------------------------------------
# Datatype properties.  (name, domain, range, comment, characteristics)
# ---------------------------------------------------------------------------
DATA_PROPERTIES = [
    ("founded", ("Bookshop", "Publisher"), None,
     "The year the shop or publisher opened. NOT functional: the RDF 1.2 "
     "layer records rival claims about four of them, and a functional "
     "declaration would make those a contradiction rather than a "
     "disagreement." + YEAR_NOTE, []),
    ("floorArea", "Bookshop", "xsd:decimal",
     "Selling floor in square metres.", ["owl:FunctionalProperty"]),
    ("staffCount", "Bookshop", "xsd:integer",
     "People on the payroll.", ["owl:FunctionalProperty"]),
    ("sellsSecondHand", "Bookshop", "xsd:boolean",
     "Whether the shop deals in second-hand books.", ["owl:FunctionalProperty"]),
    ("hasCafe", "Bookshop", "xsd:boolean",
     "Whether there is a cafe on the premises.", ["owl:FunctionalProperty"]),
    ("website", "Bookshop", "xsd:anyURI",
     "The shop's own site. Not every shop has one.", ["owl:FunctionalProperty"]),
    ("distanceKm", "TrailSegment", "xsd:decimal",
     "Straight-line distance between the two ends, in kilometres.",
     ["owl:FunctionalProperty"]),
    ("waymarked", "TrailSegment", "xsd:boolean",
     "Whether the segment has signposts.", ["owl:FunctionalProperty"]),
    ("born", "Person", None, "Year of birth." + YEAR_NOTE, ["owl:FunctionalProperty"]),
    ("died", "Person", None,
     "Year of death. Absent for the living." + YEAR_NOTE,
     ["owl:FunctionalProperty"]),
    ("writesIn", "Author", "xsd:string",
     "BCP 47 code of the language the author writes in.", []),
    ("publicationYear", "Work", None,
     "Year of first publication of this edition." + YEAR_NOTE,
     ["owl:FunctionalProperty"]),
    ("pages", "Work", "xsd:integer", "Extent in pages.", ["owl:FunctionalProperty"]),
    ("rrp", "Work", "xsd:decimal",
     "Recommended retail price in pounds.", ["owl:FunctionalProperty"]),
    ("isbn", "Work", "xsd:string",
     "ISBN-13. Books published before 1970 do not have one.",
     ["owl:FunctionalProperty"]),
    ("originalLanguage", "Work", "xsd:string",
     "The language the work was written in.", ["owl:FunctionalProperty"]),
    ("seriesPosition", "Work", "xsd:integer",
     "Position within the series, counting from 1.", ["owl:FunctionalProperty"]),
    ("eventKind", "Event", "xsd:string",
     "Reading, Signing, Launch, Workshop, Panel, Book Club or Lecture.",
     ["owl:FunctionalProperty"]),
    ("eventDate", "Event", None,
     "The day it happened." + DATE_NOTE, ["owl:FunctionalProperty"]),
    ("attendance", "Event", "xsd:integer",
     "How many people came. NOT functional, for the same reason as "
     "bs:founded: sources disagree.", []),
    ("ticketPrice", "Event", "xsd:decimal",
     "Price in pounds. Zero means free.", ["owl:FunctionalProperty"]),
    ("copies", "StockRecord", "xsd:integer",
     "Copies held.", ["owl:FunctionalProperty"]),
    ("shelfPrice", "StockRecord", "xsd:decimal",
     "What this shop charges, which may differ from the RRP.",
     ["owl:FunctionalProperty"]),
    ("population", "Settlement", "xsd:integer",
     "Resident population.", ["owl:FunctionalProperty"]),
    ("isBookTown", "Settlement", "xsd:boolean",
     "Whether the town is a recognised book town.", ["owl:FunctionalProperty"]),
    ("easting", "Place", "xsd:decimal",
     "British National Grid easting in metres (EPSG:27700). Plane "
     "coordinates, so ordinary arithmetic on them is correct.",
     ["owl:FunctionalProperty"]),
    ("northing", "Place", "xsd:decimal",
     "British National Grid northing in metres (EPSG:27700).",
     ["owl:FunctionalProperty"]),
    ("sourceKind", "Source", "xsd:string",
     "guidebook, survey, register, newspaper or self-reported.",
     ["owl:FunctionalProperty"]),
    ("rating", "Work", "xsd:integer",
     "A score out of ten. Always annotated with who gave it.", []),
    ("confidence", None, "xsd:decimal",
     "How much a claim is trusted, from 0 to 1. Stated on a Source, and on "
     "an RDF 1.2 reifier, so no domain is declared.", []),
    ("statedOn", None, None,
     "The date a claim was made. Subject is a reifier." + DATE_NOTE, []),
    ("critic", None, "xsd:string", "The reviewer's name.", []),
    ("publication", None, "xsd:string", "Where the review appeared.", []),
    ("townName", None, "xsd:string",
     "Used only by the CONSTRUCT templates in modules 07 and 12; never "
     "asserted in the shipped data.", []),
    ("countryName", None, "xsd:string", "As bs:townName.", []),
    ("specialism", None, "xsd:string", "As bs:townName.", []),
    ("eventCount", None, "xsd:integer", "As bs:townName.", []),
    ("shopCount", None, "xsd:integer", "As bs:townName.", []),
    ("workCount", None, "xsd:integer", "As bs:townName.", []),
    ("message", "DataIssue", "xsd:string",
     "What a validation finding says.", []),
    ("sameTownAs", None, None, "", []),   # replaced below; see OBJECT extras
]
DATA_PROPERTIES = [p for p in DATA_PROPERTIES if p[0] != "sameTownAs"]

# bs:sameTownAs is minted by q89 and is an object property.
OBJECT_PROPERTIES.append(
    ("sameTownAs", "Bookshop", "Bookshop",
     "Two shops in the same town. Asserted nowhere: q89 constructs it.",
     ["owl:SymmetricProperty"]))

# ---------------------------------------------------------------------------
# Annotation properties.  bs:disputes points at an RDF 1.2 triple term, which
# is not an OWL construct at all -- there is no class or datatype that can be
# its range.  An annotation property is the accurate declaration: OWL carries it
# without pretending to interpret it.
# ---------------------------------------------------------------------------
ANNOTATION_PROPERTIES = [
    ("disputes",
     "A triple term this source says is wrong. Declared an annotation "
     "property because its object is an RDF 1.2 triple term, which OWL 2 has "
     "no way to type. This is the boundary of the DL specification, and it is "
     "where the RDF 1.2 layer begins."),
]

# Properties borrowed from other vocabularies, with the kind they must be
# declared as for the profile to hold.
EXTERNAL_PROPERTIES = [
    ("object", "skos:broader", "skos:Concept", "skos:Concept"),
    ("object", "skos:narrower", "skos:Concept", "skos:Concept"),
    ("object", "skos:inScheme", "skos:Concept", "skos:ConceptScheme"),
    ("object", "skos:topConceptOf", "skos:Concept", "skos:ConceptScheme"),
    ("object", "skos:hasTopConcept", "skos:ConceptScheme", "skos:Concept"),
    ("object", "geo:hasGeometry", "geo:Feature", "geo:Geometry"),
    ("object", "geo:hasDefaultGeometry", "geo:Feature", "geo:Geometry"),
    ("data", "wgs84:lat", None, "xsd:decimal"),
    ("data", "wgs84:long", None, "xsd:decimal"),
    ("annotation", "skos:prefLabel", None, None),
    ("annotation", "skos:altLabel", None, None),
    ("annotation", "skos:scopeNote", None, None),
    ("annotation", "skos:note", None, None),
    ("annotation", "skos:notation", None, None),
    ("annotation", "dct:title", None, None),
    ("annotation", "dct:description", None, None),
    ("annotation", "dct:isPartOf", None, None),
    ("annotation", "geo:asWKT", None, None),
]
