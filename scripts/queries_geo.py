# -*- coding: utf-8 -*-
"""Modules 09-10: geography with arithmetic, then with GeoSPARQL."""

from querycat import q, DFULL, ALL, EDITOR, HOLOS, FUSEKI

# ===========================================================================
# 09  Geography with nothing but arithmetic
#
# SPARQL 1.1 has no trigonometry and no square root.  That sounds fatal for
# distance work and isn't, because two facts rescue it: a bounding box needs
# only comparisons, and ranking by distance needs only the SQUARE of the
# distance.  Everything in this module therefore runs in the browser.
# ===========================================================================

q(
    qid="q52", module="09-geo-without-geosparql",
    title="Shops in a box on the map",
    asks="Which shops lie in the south west, between 50 and 52 degrees north "
         "and west of 2 degrees?",
    how="A bounding box is four comparisons on two numbers. The dataset "
        "publishes plain wgs84:lat and wgs84:long decimals next to the WKT "
        "geometry precisely so that this works in an engine with no "
        "geospatial support at all.",
    diagram="""
        long -6         -2
          │              │
     52 ──┼──────────────┼──  lat 52
          │  ●Aberystwyth│
          │      ●Bath   │        ● inside the box -> kept
          │ ●Exeter      │        ○ outside       -> dropped
          │●Penzance     │
     50 ──┼──────────────┼──  lat 50
          │              │

    FILTER( ?lat > 50 && ?lat < 52 && ?long < -2 )

    Four numeric comparisons.  No functions, no extensions, no
    GeoSPARQL.  This runs in the browser editor unchanged.

    A box is also the right FIRST step for an expensive query: cheap
    to evaluate, and it throws away most of the candidates before
    anything costly runs.
    """,
    learn=[
        "A bounding box is the cheapest spatial filter there's, and needs "
        "nothing beyond numeric comparison.",
        "Publishing coordinates as plain decimals alongside the WKT costs a "
        "few triples and makes the data usable in engines with no geospatial "
        "support.",
        "Use a box to prefilter before an exact test. The box is wrong at the "
        "corners, but it's fast, and the exact test then fixes the corners.",
    ],
    body="""SELECT ?name ?lat ?long
WHERE {
  ?shop a           bs:Bookshop ;
        rdfs:label  ?name ;
        wgs84:lat   ?lat ;
        wgs84:long  ?long .
  FILTER( ?lat > 50.0 && ?lat < 52.0 && ?long < -2.0 )
}
ORDER BY ?lat""",
    data=DFULL,
)

q(
    qid="q53", module="09-geo-without-geosparql",
    title="The nearest shops, with no square root",
    asks="Which shops are closest to Hay-on-Wye?",
    how="Ranking by distance doesn't need the distance. If A is nearer than "
        "B then A's squared distance is smaller too, so sorting on the square "
        "gives exactly the right order -- and squaring needs only "
        "multiplication, which SPARQL 1.1 does have. Degrees of longitude are "
        "shorter than degrees of latitude, so each is scaled to kilometres "
        "before squaring.",
    diagram="""
    SPARQL 1.1 has:   + - * /  ABS ROUND FLOOR CEIL
    SPARQL 1.1 lacks: sin cos tan sqrt pow atan2

    So a real great-circle distance is out of reach.  But:

        sqrt(x) is monotonic  ⇒  ordering by x
                                 == ordering by sqrt(x)

    ┌── scale degrees to kilometres ─────────────────┐
    │  1 deg latitude  ≈ 111.19 km      (everywhere) │
    │  1 deg longitude ≈  66.70 km      (at 53 N)    │
    └────────────────────────────────────────────────┘

        dy = (?lat  - 52.0760) * 111.19
        dx = (?long + 3.1288 ) * 66.70

        ?d2 = dx*dx + dy*dy          <- squared km, never rooted

    ORDER BY ?d2   gives the true nearest-first order.

    The approximation, measured: against a proper
    haversine over all 435 pairs of settlements in this dataset, the
    median error is 0.3%, the 95th percentile 4.1%, and the worst
    case 11.4% -- Inverness to Portree, where 57 N is a long way from
    the 53 N the longitude scale assumes.  q55 shows that failure,
    and q54 avoids it.
    """,
    learn=[
        "To rank by distance you never need the square root. This is the "
        "single most useful trick for geography in a plain SPARQL engine.",
        "A degree of longitude isn't a degree of latitude. Scale them "
        "separately or every east-west distance is overstated.",
        "Know the error in your approximation before you rely on it, and say "
        "what it's.",
    ],
    body="""SELECT ?name ?squaredKm
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        wgs84:lat  ?lat ;
        wgs84:long ?long .
  BIND( (?lat  - 52.0760) * 111.19 AS ?dy )
  BIND( (?long - -3.1288) * 66.70  AS ?dx )
  BIND( ROUND(?dx * ?dx + ?dy * ?dy) AS ?squaredKm )
}
ORDER BY ?squaredKm
LIMIT 12""",
    data=DFULL,
)

q(
    qid="q54", module="09-geo-without-geosparql",
    title="Exact distances, by using a flat map",
    asks="Which shop is nearest to each of the four towns that have none?",
    how="The approximation in q53 exists only because degrees aren't a "
        "length. A projected coordinate system fixes that at the source: the "
        "British National Grid is already flat and already in metres, so "
        "Pythagoras on eastings and northings is simply correct. The dataset "
        "publishes both, and this query uses the grid.",
    diagram="""
    degrees                        British National Grid
    ───────                        ─────────────────────
    lat/long on a sphere           eastings/northings on a plane
    a degree is not a length       the unit IS the metre
    scale factor varies with       scale error across Britain
    latitude                       is under 0.04%

        dx = ?e1 - ?e2                (metres, exactly)
        dy = ?n1 - ?n2
        d2 = dx*dx + dy*dy            (metres squared)

    for each town with no shop:

        Durham       ──▶  nearest shop
        Perth        ──▶  nearest shop
        Fort William ──▶  nearest shop
        Truro        ──▶  nearest shop

    The inner query finds the minimum squared distance per town; the
    outer one joins back to discover which shop that was -- the same
    "group, then join back" shape as q38.
    """,
    learn=[
        "Projecting the data once removes the need to approximate in every "
        "query. If you do geography often, store a projected coordinate.",
        "The same squared-distance trick applies, and here it's exact rather "
        "than approximate.",
        "Nearest-neighbour is 'minimum per group, then join back to find "
        "which one'.",
    ],
    body="""SELECT ?townName ?shopName ?km
WHERE {
  {
    SELECT ?town (MIN(?d2) AS ?best)
    WHERE {
      ?town a bs:Settlement ; bs:easting ?te ; bs:northing ?tn .
      FILTER NOT EXISTS { ?any bs:locatedIn ?town }
      ?shop a bs:Bookshop ; bs:easting ?se ; bs:northing ?sn .
      BIND( (?se - ?te) * (?se - ?te) + (?sn - ?tn) * (?sn - ?tn) AS ?d2 )
    }
    GROUP BY ?town
  }
  ?town a bs:Settlement ; rdfs:label ?townName ; bs:easting ?te ; bs:northing ?tn .
  ?shop a bs:Bookshop ; rdfs:label ?shopName ; bs:easting ?se ; bs:northing ?sn .
  BIND( (?se - ?te) * (?se - ?te) + (?sn - ?tn) * (?sn - ?tn) AS ?d2 )
  FILTER( ?d2 = ?best )
  FILTER( LANG(?townName) = "en" )
  BIND( ROUND(?d2 / 1000000) AS ?km )
}
ORDER BY ?townName""",
    data=DFULL,
)

q(
    qid="q55", module="09-geo-without-geosparql",
    title="Where the flat-Earth shortcut breaks",
    asks="Show a pair of places where degree arithmetic and grid arithmetic "
         "disagree.",
    how="Both metrics are computed for every pair of settlements and their "
        "ratio taken. Near 53 degrees north the two agree closely; at the top "
        "of Scotland the fixed longitude scale is badly wrong, and the "
        "degree-based figure overstates the distance by more than a tenth.",
    diagram="""
    degree metric assumes:  1 deg longitude = 66.70 km   (true at 53 N)

    but a degree of longitude shrinks towards the pole:

        at 50 N  ->  71.7 km      degree metric UNDERSTATES
        at 53 N  ->  66.9 km      about right
        at 57 N  ->  60.5 km      degree metric OVERSTATES

    Inverness (57.5 N) to Portree (57.4 N), almost due west:

        true, on the grid   118 km
        degree metric       132 km        +11.4%

    ┌──────────────┬───────────┬───────────┬───────┐
    │ pair         │ grid km   │ degree km │ ratio │
    ├──────────────┼───────────┼───────────┼───────┤
    │ Inverness -  │    118    │    132    │ 1.114 │
    │ Portree      │           │           │       │
    └──────────────┴───────────┴───────────┴───────┘

    The lesson is not "never approximate".  It is "know where your
    approximation fails, and check whether your data lives there".
    """,
    learn=[
        "An approximation that's fine in the middle of your data can be badly "
        "wrong at its edges.",
        "East-west distances at high latitude are where a fixed longitude "
        "scale fails first.",
        "Comparing two methods on the same data is the cheapest way to find "
        "out whether the simpler one is good enough.",
        "Keep intermediate values small and give them names. Dividing by a "
        "ten-digit expression inline left ?ratio unbound on one of the three "
        "engines; dividing the two rounded kilometre figures instead works "
        "everywhere and reads better.",
        "An unbound ORDER BY key doesn't raise an error. It just stops "
        "sorting, and the top of your result is then whatever the engine "
        "happened to produce first.",
    ],
    body="""SELECT ?fromName ?toName ?gridKm2 ?degreeKm2 ?ratio
WHERE {
  ?a a bs:Settlement ; rdfs:label ?fromName ;
     bs:easting ?ae ; bs:northing ?an ; wgs84:lat ?alat ; wgs84:long ?alon .
  ?b a bs:Settlement ; rdfs:label ?toName ;
     bs:easting ?be ; bs:northing ?bn ; wgs84:lat ?blat ; wgs84:long ?blon .
  FILTER( STR(?fromName) < STR(?toName) )
  FILTER( LANG(?fromName) = "en" && LANG(?toName) = "en" )

  BIND( (?be - ?ae) * (?be - ?ae) + (?bn - ?an) * (?bn - ?an) AS ?gridM2 )
  BIND( ((?blat - ?alat) * 111.19) AS ?dy )
  BIND( ((?blon - ?alon) * 66.70)  AS ?dx )
  BIND( ?dx * ?dx + ?dy * ?dy AS ?degKm2 )

  FILTER( ?gridM2 > 100000000 )
  BIND( ROUND(?gridM2 / 1000000.0) AS ?gridKm2 )
  BIND( ROUND(?degKm2)             AS ?degreeKm2 )
  # Divide the two small rounded values, not the raw squared metres. Dividing
  # by a ten-digit decimal expression inline left ?ratio unbound on one of the
  # three engines -- and an unbound sort key means ORDER BY has nothing to
  # work with, so the "worst" rows were not the worst at all.
  BIND( ROUND(?degreeKm2 * 1000.0 / ?gridKm2) / 1000.0 AS ?ratio )
}
ORDER BY DESC(?ratio)
LIMIT 8""",
    data=DFULL,
)

q(
    qid="q56", module="09-geo-without-geosparql",
    title="Everything within fifty kilometres",
    asks="Which shops are within 50 km of York, and how far is each?",
    how="A radius test is a comparison against a squared threshold: rather "
        "than rooting the distance, square the limit. 50 km is 50,000 metres, "
        "so the test is d2 < 2,500,000,000 -- and no square root is needed "
        "anywhere.",
    diagram="""
    want:   sqrt(dx² + dy²)  <  50000
    but no sqrt available, so square both sides:

            dx² + dy²        <  50000²
            dx² + dy²        <  2 500 000 000

    ┌──────────────────────────────────────┐
    │              ╭─────────╮             │
    │           ╱  ●York      ╲            │
    │          │   ● Endpapers │           │
    │          │   ● Bookwyrm  │  r = 50km │
    │           ╲             ╱            │
    │              ╰─────────╯             │
    │        ○ Whitby's shop (58 km)       │
    └──────────────────────────────────────┘

    Squaring the threshold instead of rooting the distance is the
    same trick as q53, used the other way round.  It is exact, not
    an approximation.
    """,
    learn=[
        "Compare against a squared threshold rather than taking a square root. "
        "The answer is exact.",
        "This makes radius queries available in any engine that can multiply.",
        "Add a bounding box first when the dataset is large: it removes most "
        "candidates before the multiplication runs.",
    ],
    body="""SELECT ?name ?approxKm
WHERE {
  bt:place-york bs:easting ?ye ; bs:northing ?yn .
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        bs:easting ?se ;
        bs:northing ?sn .
  BIND( (?se - ?ye) * (?se - ?ye) + (?sn - ?yn) * (?sn - ?yn) AS ?d2 )
  FILTER( ?d2 < 2500000000 )
  BIND( ROUND(?d2 / 100000) / 10 AS ?approxKm )
}
ORDER BY ?d2""",
    data=DFULL,
)

# ===========================================================================
# 10  GeoSPARQL proper
# ===========================================================================

q(
    qid="q57", module="10-geosparql",
    title="The same question, one function",
    asks="How far is each shop from Hay-on-Wye, in kilometres?",
    how="geof:distance takes two geometries and a unit and returns a real "
        "great-circle distance. Everything q53 approximated with scaling and "
        "squaring becomes a single function call -- provided the engine "
        "implements it.",
    diagram="""
    q53, portable:                  q57, GeoSPARQL:

    BIND((?lat - 52.076)*111.19     geof:distance(?g1, ?g2, uom:metre)
          AS ?dy)
    BIND((?long + 3.1288)*66.70
          AS ?dx)
    BIND(?dx*?dx + ?dy*?dy
          AS ?d2)
    ORDER BY ?d2                    ORDER BY ?metres

    squared kilometres,             metres, exact,
    approximate,                    on the ellipsoid
    runs everywhere                 needs GeoSPARQL

    The geometry lives on a separate node, which is why the path has
    two steps:

        ?shop ──geo:hasDefaultGeometry──▶ ?g ──geo:asWKT──▶ "POINT(...)"
    """,
    learn=[
        "geof:distance replaces a page of arithmetic, and is exact.",
        "GeoSPARQL puts the geometry on its own node: reach the literal with "
        "geo:hasDefaultGeometry/geo:asWKT.",
        "The unit is an argument. Ask for metres and you get metres; there's "
        "no implicit default worth relying on.",
    ],
    body="""SELECT ?name (ROUND(?metres / 100) / 10 AS ?km)
WHERE {
  bt:place-hay-on-wye geo:hasDefaultGeometry/geo:asWKT ?origin .
  ?shop a          bs:Bookshop ;
        rdfs:label ?name ;
        geo:hasDefaultGeometry/geo:asWKT ?here .
  BIND( geof:distance(?origin, ?here, <http://www.opengis.net/def/uom/OGC/1.0/metre>) AS ?metres )
}
ORDER BY ?metres
LIMIT 12""",
    data=DFULL,
    engines=(HOLOS,),
    notes="HOLOS only, and for a precise reason. Comunica has no geof: "
          "functions at all. Jena does have them -- run "
          "scripts/setup-geosparql.ps1 and the whole library appears -- but "
          "in this 6.2.0 build every function that returns a LINEAR measure "
          "comes back unbound: geof:distance in metres or kilometres, "
          "geof:area, geof:length. No error, no warning, HTTP 200, just an "
          "empty column. geof:distance in degrees or radians does work, as do "
          "all the topological functions and all the geometry constructors. "
          "So q58 runs on Fuseki and this one doesn't. Module 09 answers the "
          "same question with arithmetic, on every engine.",
)

q(
    qid="q58", module="10-geosparql",
    title="Which area is this point inside",
    asks="Verify that every settlement really does fall inside the polygon of "
         "the council area it claims to be in.",
    how="geof:sfWithin tests one geometry against another using the Simple "
        "Features relation. Here it checks the dataset against itself: the "
        "bs:within link says a town is in a council area, and the geometry "
        "should agree. Zero rows means the data is consistent.",
    diagram="""
    two independent statements about the same fact:

      symbolic:   bt:place-york  bs:within  bt:place-north-yorkshire
      geometric:  POINT(-1.0873 53.96)  inside  POLYGON((...))

    this query asks whether they ever disagree:

      ?s bs:within ?c
      FILTER( !geof:sfWithin(?pointOfS, ?polygonOfC) )
               ▲
               └── NOT within -> a contradiction

    result: 0 rows.  The polygons were computed from the settlements
    they contain, so containment is true by construction -- and this
    query is how you prove it rather than assert it.

    The Simple Features family: sfWithin, sfContains, sfIntersects,
    sfOverlaps, sfTouches, sfCrosses, sfDisjoint, sfEquals.
    """,
    learn=[
        "Topological relations are functions returning a boolean, usable "
        "directly in a FILTER.",
        "A query that should return zero rows is a test. Keep it and run it "
        "whenever the data changes.",
        "sfWithin, sfContains and sfIntersects cover most needs; the Egenhofer "
        "and RCC8 families are there when you need finer distinctions.",
    ],
    body="""SELECT ?settlement ?area
WHERE {
  ?s a bs:Settlement ;
     rdfs:label ?settlement ;
     bs:within ?c ;
     geo:hasDefaultGeometry/geo:asWKT ?point .
  ?c a bs:CouncilArea ;
     rdfs:label ?area ;
     geo:hasDefaultGeometry/geo:asWKT ?polygon .
  FILTER( LANG(?settlement) = "en" )
  FILTER( !geof:sfWithin(?point, ?polygon) )
}""",
    data=DFULL,
    engines=(HOLOS, FUSEKI),
    notes="Returns zero rows when the data is sound, which is the point. Runs "
          "on Fuseki as well as HOLOS once scripts/setup-geosparql.ps1 has "
          "been run: Jena's GeoSPARQL handles the topological functions "
          "(sfWithin, sfIntersects, sfContains and the rest) perfectly well. "
          "Check it with the positive form -- FILTER(geof:sfWithin(...)) "
          "without the negation -- which finds all 30 settlements.",
)

q(
    qid="q59", module="10-geosparql",
    title="How long is the trail",
    asks="Measure each trail segment from its geometry, and compare with the "
         "distance recorded in the data.",
    how="geof:length measures a LineString. The dataset also stores "
        "bs:distanceKm, computed when the data was built as the straight-line "
        "distance between the endpoints. The segment geometry bends through a "
        "midpoint, so the measured length should be a little longer -- and if "
        "it weren't, something would be wrong.",
    diagram="""
    the geometry is a three-point line, deliberately bent:

        shop A ●─────────╮
                          ●  midpoint, nudged sideways
                 ╭────────╯
        shop B ●─╯

    bs:distanceKm   = straight line A to B      (stored)
    geof:length     = along the bent line       (measured)

    measured  >  stored,  always, by the amount of the bend.

    Two numbers that should differ in a known direction are a good
    consistency check: if the sign ever flips, a geometry has been
    written wrongly.
    """,
    learn=[
        "geof:length, geof:area and geof:perimeter measure geometries; "
        "geof:envelope, geof:convexHull, geof:buffer and geof:boundary derive "
        "new ones.",
        "Storing a derived number and measuring it are different things. "
        "Comparing them catches errors.",
        "Deriving geometry in the query rather than storing it keeps the data "
        "smaller, at the cost of doing the work every time.",
    ],
    body="""SELECT ?label ?storedKm ?measuredKm
WHERE {
  ?seg a bs:TrailSegment ;
       rdfs:label ?label ;
       bs:distanceKm ?storedKm ;
       geo:hasDefaultGeometry/geo:asWKT ?line .
  BIND( ROUND(geof:length(?line) / 100) / 10 AS ?measuredKm )
}
ORDER BY DESC(?storedKm)
LIMIT 10""",
    data=DFULL,
    engines=(HOLOS,),
    notes="geof:length is a linear measure, so it shares q57's fate on Jena: "
          "registered, callable, and unbound on return. HOLOS answers it.",
)

q(
    qid="q60", module="10-geosparql",
    title="Two coordinate systems, one query",
    asks="Confirm that the National Grid geometry and the WGS84 geometry "
         "describe the same place.",
    how="Each settlement carries two geometries: a CRS84 point in degrees and "
        "an EPSG:27700 point in metres. An engine that reads the CRS URI at "
        "the front of a WKT literal will convert before comparing, and find "
        "the distance between them is essentially zero. An engine that "
        "assumes everything is CRS84 will compute a nonsensical answer, "
        "because it will read 425000 as a longitude.",
    diagram="""
    the CRS is part of the literal, not metadata about it:

    "<...CRS84> POINT(-1.0873 53.96)"^^geo:wktLiteral
     ─────┬────       ──┬───  ──┬──
          │             │       └── latitude, degrees
          │             └────────── longitude, degrees
          └── the reference system

    "<...EPSG/0/27700> POINT(460000.0 452000.0)"^^geo:wktLiteral
     ────────┬───────         ───┬───  ───┬───
             │                   │        └── northing, metres
             │                   └─────────── easting, metres
             └── a different system entirely

    geof:distance between them, correctly handled:  ~0 metres
    the same, if 460000 is read as a longitude:     nonsense

    HOLOS reads CRS84, EPSG:4326, EPSG:27700 and EPSG:3857, and
    refuses a system it does not know rather than guessing.  Check
    what your own engine does before you trust a mixed dataset.
    """,
    learn=[
        "The coordinate reference system is part of the WKT literal's value.",
        "Mixing systems in one dataset is normal; whether your engine copes is "
        "the question to ask before you rely on it.",
        "An engine that silently assumes CRS84 won't error. It will give "
        "you a wrong number, which is worse.",
        "Use !sameTerm to say 'a different term'. Inequality on two literals "
        "of a datatype the engine can't order is an error, and an error in a "
        "FILTER removes the row -- so the obvious spelling of this query "
        "returns nothing at all.",
    ],
    body="""SELECT ?name (ROUND(?separation) AS ?metresApart)
WHERE {
  ?place a bs:Settlement ;
         rdfs:label ?name ;
         geo:hasDefaultGeometry/geo:asWKT ?wgs84 .
  ?place geo:hasGeometry ?bngGeom .
  ?bngGeom geo:asWKT ?bng .
  # !sameTerm, not !=. Two geo:wktLiteral values are not a datatype SPARQL
  # knows how to compare, so `?wgs84 != ?bng` errors and the FILTER drops
  # every row -- the q07 trap once more, this time on a geometry.
  FILTER( !sameTerm(?wgs84, ?bng) )
  FILTER( LANG(?name) = "en" )
  BIND( geof:distance(?wgs84, ?bng,
        <http://www.opengis.net/def/uom/OGC/1.0/metre>) AS ?separation )
}
ORDER BY DESC(?separation)
LIMIT 10""",
    data=DFULL,
    engines=(HOLOS,),
    notes="HOLOS-specific in practice: it's the engine among the three that "
          "reads EPSG:27700. The lesson -- that a CRS URI is part of the "
          "value and must be honoured -- is general.",
)
