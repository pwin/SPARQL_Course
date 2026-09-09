# -*- coding: utf-8 -*-
"""Module 15: functions the SPARQL specification does not define.

Every claim in this module was measured on the three engines, not read out of
a manual.  Reproduce it with:

    python scripts/check_queries.py q100 q101 q102 q103 q104
"""

from querycat import q, D11, DFULL, ALL, EDITOR, HOLOS, FUSEKI

MOD = "15-beyond-the-standard"

q(
    qid="q100", module=MOD,
    title="Readable names without a label",
    asks="Show each shop's IRI as a short name, without joining to "
         "rdfs:label.",
    how="afn:localname splits an IRI at its last slash or hash and returns "
        "the tail; afn:namespace returns the rest. Both come from ARQ, Jena's "
        "query engine, and neither is in the SPARQL specification. They are "
        "the most useful of the extensions and the easiest to become "
        "dependent on.",
    diagram="""
    <https://example.org/bookshop-trail/shop-inkwell>
     -------------------+---------------  ------+-----
                        |                       |
       afn:namespace ---'                       '--- afn:localname
       "https://example.org/bookshop-trail/"    "shop-inkwell"

    what it's for: a diagnostic listing where the IRIs matter and
    the labels would just get in the way -- q96's namespace census
    is the same idea done with REPLACE.

    where it works, measured:

      afn:localname        editor  error    holos  yes    fuseki  yes
      afn:namespace        editor  error    holos  yes    fuseki  yes

    Comunica raises rather than returning nothing, which is the
    better of the two failure modes: you find out.
    """,
    learn=[
        "afn: is ARQ's function library. Jena has it, HOLOS implements it too, "
        "and it is not part of SPARQL.",
        "afn:localname and afn:namespace take an IRI apart, which is otherwise "
        "a REPLACE with a regular expression -- see q104.",
        "Reach for an extension when it makes a query clearer, but know you "
        "have done it. Q104 is the way back out.",
    ],
    body="""SELECT ?localName ?namespace ?name
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  BIND( afn:localname(?shop) AS ?localName )
  BIND( afn:namespace(?shop) AS ?namespace )
}
ORDER BY ?localName
LIMIT 8""",
    engines=(HOLOS, FUSEKI),
    notes="Comunica has no afn: functions and raises an error rather than "
          "returning unbound, so the editor is not claimed here.",
)

q(
    qid="q101", module=MOD,
    title="The square root module 09 could not have",
    asks="How far is each shop from York, in actual kilometres?",
    how="Module 09 ranked shops by squared distance because SPARQL 1.1 has no "
        "square root. afn:sqrt supplies one. The arithmetic is the same as "
        "q56's; the only difference is that the answer is now a distance "
        "rather than an ordering.",
    diagram="""
    module 09, portable:            here, with an extension:

      d2 = dx*dx + dy*dy              d = afn:sqrt(dx*dx + dy*dy)
      ORDER BY ?d2                    ORDER BY ?d

      ranks correctly                 ranks correctly AND
      but the number is                gives the distance
      metres squared

    +------------------+---------+
    | Endpapers        |   0.5 km|
    | The Bookwyrm     |   0.6 km|
    | The Harbour Page |  66.1 km|
    | Cotton Quarto    |  93.7 km|
    +------------------+---------+

    measured:  afn:sqrt   editor error   holos yes   fuseki yes

    Note what module 09 bought by not using this: the same query,
    without the square root, runs in the browser too. That is the
    trade in one line.
    """,
    learn=[
        "afn:sqrt, afn:pi, afn:e, afn:min and afn:max fill the gaps in "
        "SPARQL's arithmetic.",
        "Fuseki also has the XPath math: library -- math:sqrt, math:pow, "
        "math:log -- which HOLOS does not. Two engines, two different sets of "
        "extras.",
        "A ranking rarely needs the root. Take it only when you are going to "
        "show the number to somebody.",
    ],
    body="""SELECT ?name ?km
WHERE {
  bt:place-york bs:easting ?ye ; bs:northing ?yn .
  ?shop a           bs:Bookshop ;
        rdfs:label  ?name ;
        bs:easting  ?se ;
        bs:northing ?sn .
  BIND( (?se - ?ye) * (?se - ?ye) + (?sn - ?yn) * (?sn - ?yn) AS ?d2 )
  BIND( ROUND( afn:sqrt(?d2) / 100 ) / 10 AS ?km )
}
ORDER BY ?km
LIMIT 8""",
    data=DFULL,
    engines=(HOLOS, FUSEKI),
)

q(
    qid="q102", module=MOD,
    title="SPIN's string functions, and a silent failure",
    asks="Tidy up some strings with spif:, and find out what happens where "
         "spif: is not implemented.",
    how="SPIN's spif: library has the string helpers SPARQL never grew: trim, "
        "titleCase, indexOf, buildString. HOLOS implements them. Jena does "
        "not -- and rather than complaining, it returns the row with the "
        "variable unbound, which is the failure mode this course keeps "
        "warning about.",
    diagram="""
    spif:titleCase("the inkwell")   ->  "The Inkwell"
    spif:trim("  x  ")              ->  "x"
    spif:indexOf("bookshop","shop") ->  4
    spif:buildString("{?1}-{?2}", "a", "b")  ->  "a-b"

    measured, and this is the point of the query:

      spif:trim        editor  ERROR      holos  yes    fuseki  UNBOUND
      spif:titleCase   editor  ERROR      holos  yes    fuseki  UNBOUND
      spif:indexOf     editor  ERROR      holos  yes    fuseki  UNBOUND

    +----------+-------------------------------------------+
    | Comunica | raises. You find out immediately.          |
    | Jena     | returns the row, variable unbound, HTTP    |
    |          | 200. Looks exactly like missing data.      |
    | HOLOS    | answers.                                   |
    +----------+-------------------------------------------+

    Same shape as geof:distance in metres on Jena (q57), and the
    reason the checking harness compares values rather than counting
    rows: a column of blanks and a column of answers both have the
    same number of rows.
    """,
    learn=[
        "spif: is SPIN's function library. HOLOS has it; Jena and Comunica do "
        "not.",
        "An unimplemented function is not guaranteed to be an error. Jena "
        "leaves the variable unbound and returns the row, which is "
        "indistinguishable from the data simply not being there.",
        "If a column comes back empty, suspect the function before you suspect "
        "the data.",
    ],
    body="""SELECT ?name ?titled ?trimmed ?shopAt
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  BIND( spif:titleCase( LCASE(STR(?name)) )      AS ?titled )
  BIND( spif:trim( CONCAT("  ", STR(?name), "  ") ) AS ?trimmed )
  BIND( spif:indexOf( STR(?name), "o" )          AS ?shopAt )
}
ORDER BY ?name
LIMIT 8""",
    engines=(HOLOS,),
    notes="HOLOS only. Jena parses this and returns eight rows with three "
          "empty columns; Comunica raises. Run it on Fuseki yourself -- "
          "seeing the blanks is worth more than reading about them.",
)

q(
    qid="q103", module=MOD,
    title="The XPath library, under different names",
    asks="Do the same string work with fn: instead of the SPARQL built-ins.",
    how="The fn: library is XPath and XQuery Functions and Operators, which "
        "SPARQL borrowed from without adopting wholesale. Several fn: "
        "functions duplicate a SPARQL built-in exactly, and the built-in is "
        "the one to use -- but you will meet fn: in other people's queries, "
        "and the indexing differs in a way that bites.",
    diagram="""
    the same operation, two spellings:

      UCASE(?s)               fn:upper-case(?s)
      STRLEN(?s)              fn:string-length(?s)
      SUBSTR(?s, 1, 4)        fn:substring(?s, 1, 4)
      CONTAINS(?s, "x")       fn:contains(?s, "x")
      YEAR(?d)                fn:year-from-dateTime(?d)

    and one that is NOT the same:

      fn:substring   is 1-based, like SUBSTR
      afn:substr     is 0-based, with an END index, not a length

        SUBSTR("bookshop", 1, 4)      ->  "book"
        afn:substr("bookshop", 0, 4)  ->  "book"
                                ^  ^
                                |  '-- end, not length
                                '----- counts from zero

    measured:  fn:  editor error   holos yes   fuseki yes

    Prefer the built-in every time. It is shorter, it is in the
    specification, and it runs in the browser.
    """,
    learn=[
        "fn: is the XPath function library. Where a SPARQL built-in does the "
        "same job, use the built-in.",
        "Two functions that look equivalent may index differently: "
        "fn:substring counts from 1 and takes a length, afn:substr counts "
        "from 0 and takes an end position.",
        "Knowing fn: is for reading other people's queries. Writing it into "
        "your own only costs you portability.",
    ],
    body="""SELECT ?name ?upper ?length ?firstFour
WHERE {
  ?shop a          bs:Bookshop ;
        rdfs:label ?name .
  BIND( fn:upper-case( STR(?name) )         AS ?upper )
  BIND( fn:string-length( STR(?name) )      AS ?length )
  BIND( fn:substring( STR(?name), 1, 4 )    AS ?firstFour )
}
ORDER BY ?name
LIMIT 8""",
    engines=(HOLOS, FUSEKI),
)

q(
    qid="q104", module=MOD,
    title="The same query, with nothing but the standard",
    asks="Get the local name, the namespace and a real distance using only "
         "SPARQL 1.1.",
    how="Everything the previous four queries needed an extension for, done "
        "with built-ins. REPLACE takes an IRI apart. A square root is "
        "unavailable, so the distance stays squared -- and the row is ordered "
        "correctly regardless, because that is all a ranking needs.",
    diagram="""
    afn:localname(?iri)
        -> REPLACE(STR(?iri), "^.*[/#]", "")

    afn:namespace(?iri)
        -> REPLACE(STR(?iri), "[^/#]*$", "")

    spif:titleCase(?s)
        -> no built-in. CONCAT(UCASE(SUBSTR(?s,1,1)), SUBSTR(?s,2))
           does the first word, which is usually what was meant.

    afn:sqrt(?d2)
        -> nothing. Rank on ?d2 instead, or compare against a
           squared threshold (q53, q56).

    +----------------------------------------------------------+
    |  runs on the editor, HOLOS and Fuseki                     |
    |  no library, no engine lock-in, no silent unbound column  |
    +----------------------------------------------------------+

    That is the trade this module exists to show. The extensions
    are real and they are useful; the standard is the thing that
    travels.
    """,
    learn=[
        "REPLACE with a small regular expression replaces afn:localname and "
        "afn:namespace, and runs everywhere.",
        "Some extensions have no standard equivalent at all -- a square root "
        "is the clearest -- and then the question is whether you need the "
        "value or only the order.",
        "Write the standard version first. Reach for an extension when the "
        "standard one is genuinely worse, and leave a comment saying which "
        "engine you have just tied the query to.",
    ],
    body="""SELECT ?localName ?namespace ?squaredMetres
WHERE {
  bt:place-york bs:easting ?ye ; bs:northing ?yn .
  ?shop a           bs:Bookshop ;
        bs:easting  ?se ;
        bs:northing ?sn .
  BIND( REPLACE(STR(?shop), "^.*[/#]", "")  AS ?localName )
  BIND( REPLACE(STR(?shop), "[^/#]*$", "")  AS ?namespace )
  BIND( ROUND( (?se - ?ye) * (?se - ?ye)
             + (?sn - ?yn) * (?sn - ?yn) )  AS ?squaredMetres )
}
ORDER BY ?squaredMetres
LIMIT 8""",
    data=DFULL,
)
